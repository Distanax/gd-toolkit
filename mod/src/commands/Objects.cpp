// Object-level editing: add, select, remove, modify, list, triggers.
//
// Objects are exchanged as GD object strings ("1,8,2,45,3,15,...": key,value pairs, key 1 = object ID,
// 2/3 = x/y) — the same format as the level string and toolkit/gdlib.py, so nothing is lost in
// translation. modify_objects edits keys on that string and re-creates the object, which works for
// every property (including trigger settings) at the cost of a new uid.

#include "../Level.hpp"
#include "../Rpc.hpp"

#include <map>
#include <set>
#include <vector>

#include <Geode/Geode.hpp>

using namespace geode::prelude;
using namespace bridge;

namespace {

constexpr int MAX_LIST = 5000;

// Ordered key -> value map of one object string (keys kept as strings: some GD keys are "kA..").
using ObjectProps = std::vector<std::pair<std::string, std::string>>;

ObjectProps parseObject(std::string_view s) {
	ObjectProps props;
	while (!s.empty() && (s.back() == ';' || s.back() == ' ')) s.remove_suffix(1);
	std::size_t pos = 0;
	while (pos < s.size()) {
		auto k = s.find(',', pos);
		if (k == std::string_view::npos) break;
		auto v = s.find(',', k + 1);
		if (v == std::string_view::npos) v = s.size();
		props.emplace_back(std::string(s.substr(pos, k - pos)), std::string(s.substr(k + 1, v - k - 1)));
		pos = v + 1;
	}
	return props;
}

std::string joinObject(ObjectProps const& props) {
	std::string out;
	for (auto const& [k, v] : props) {
		if (!out.empty()) out += ',';
		out += k;
		out += ',';
		out += v;
	}
	return out;
}

void setProp(ObjectProps& props, std::string const& key, std::optional<std::string> const& value) {
	auto it = std::find_if(props.begin(), props.end(), [&](auto const& p) { return p.first == key; });
	if (!value) {
		if (it != props.end()) props.erase(it);
	} else if (it != props.end()) {
		it->second = *value;
	} else {
		props.emplace_back(key, *value);
	}
}

std::string jsonScalarToString(matjson::Value const& v, std::string const& key) {
	if (v.isString()) return v.asString().unwrap();
	if (v.isBool()) return v.asBool().unwrap() ? "1" : "0";
	if (v.isNumber()) {
		double d = v.asDouble().unwrap();
		if (d == (double)(long long)d) return fmt::format("{}", (long long)d);
		return fmt::format("{}", d);
	}
	if (v.isArray()) {  // group lists etc.: GD joins with '.'
		std::string out;
		for (auto const& e : v.asArray().unwrap()) {
			if (!out.empty()) out += '.';
			out += jsonScalarToString(e, key);
		}
		return out;
	}
	throw RpcError("invalid_params", fmt::format("value for key {} must be a string, number, bool or list", key));
}

std::vector<GameObject*> allObjects(LevelEditorLayer* lel) {
	std::vector<GameObject*> out;
	if (!lel->m_objects) return out;
	for (auto obj : CCArrayExt<GameObject*>(lel->m_objects)) out.push_back(obj);
	return out;
}

std::vector<int> groupsOf(GameObject* obj) {
	std::vector<int> g;
	if (!obj->m_groups) return g;
	for (int i = 0; i < obj->m_groupCount && i < 10; ++i) {
		int id = (*obj->m_groups)[i];
		if (id > 0) g.push_back(id);
	}
	return g;
}

std::set<int> intSet(matjson::Value const& p, std::string_view key) {
	std::set<int> out;
	auto v = optField(p, key);
	if (!v) return out;
	if (v->isNumber()) {
		out.insert((int)v->asInt().unwrapOr(0));
		return out;
	}
	if (!v->isArray()) throw RpcError("invalid_params", fmt::format("'{}' must be a number or list of numbers", key));
	for (auto const& e : v->asArray().unwrap()) {
		if (!e.isNumber()) throw RpcError("invalid_params", fmt::format("'{}' must contain numbers", key));
		out.insert((int)e.asInt().unwrapOr(0));
	}
	return out;
}

struct Selector {
	std::set<int> uids, ids, groups;
	std::optional<CCRect> region;  // in GD units, by object position (centre)
	bool triggersOnly = false;
	bool all = false;

	bool empty() const { return uids.empty() && ids.empty() && groups.empty() && !region && !triggersOnly; }

	bool matches(GameObject* obj) const {
		if (!uids.empty() && !uids.contains(obj->m_uniqueID)) return false;
		if (!ids.empty() && !ids.contains(obj->m_objectID)) return false;
		if (triggersOnly && !obj->m_isTrigger) return false;
		if (!groups.empty()) {
			auto g = groupsOf(obj);
			if (std::none_of(g.begin(), g.end(), [&](int id) { return groups.contains(id); })) return false;
		}
		if (region && !region->containsPoint(toLevel(obj->getPosition()))) return false;
		return true;
	}
};

// params.select = {uids?, ids?, groups?, region? {x1,y1,x2,y2}, triggers?, all?}; criteria are ANDed.
Selector parseSelector(matjson::Value const& params, bool forWrite) {
	Selector s;
	matjson::Value empty = matjson::Value::object();
	auto sel = optField(params, "select");
	auto const& p = sel ? *sel : empty;
	if (sel && !sel->isObject()) throw RpcError("invalid_params", "'select' must be an object");
	s.uids = intSet(p, "uids");
	s.ids = intSet(p, "ids");
	s.groups = intSet(p, "groups");
	s.triggersOnly = optBool(p, "triggers").value_or(false);
	s.all = optBool(p, "all").value_or(false);
	if (auto r = optField(p, "region")) {
		double x1 = paramNumber(*r, "x1"), y1 = paramNumber(*r, "y1"), x2 = paramNumber(*r, "x2"), y2 = paramNumber(*r, "y2");
		s.region = CCRect(std::min(x1, x2), std::min(y1, y2), std::abs(x2 - x1), std::abs(y2 - y1));
	}
	if (forWrite && s.empty() && !s.all)
		throw RpcError("invalid_params", "empty selector: pass select criteria, or select.all=true to target every object");
	return s;
}

matjson::Value describe(GameObject* obj, LevelEditorLayer* lel, bool withString) {
	auto pos = toLevel(obj->getPosition());
	matjson::Value groups = matjson::Value::array();
	for (int g : groupsOf(obj)) groups.push(g);
	auto o = matjson::makeObject({
		{"uid", obj->m_uniqueID},
		{"id", obj->m_objectID},
		{"x", pos.x},
		{"y", pos.y},
		{"rotation", obj->getRotation()},
		{"scale_x", obj->m_scaleX},
		{"scale_y", obj->m_scaleY},
		{"groups", groups},
		{"trigger", obj->m_isTrigger},
		{"editor_layer", (int)obj->m_editorLayer},
	});
	if (withString) o["object_string"] = std::string(obj->getSaveString(lel));
	return o;
}

std::vector<std::string> objectStrings(matjson::Value const& params) {
	auto v = optField(params, "objects");
	if (!v || !v->isArray()) throw RpcError("invalid_params", "'objects' must be a list of object strings");
	std::vector<std::string> out;
	for (auto const& e : v->asArray().unwrap()) {
		if (!e.isString()) throw RpcError("invalid_params", "each object must be an object string like \"1,1,2,15,3,15\"");
		auto s = e.asString().unwrap();
		while (!s.empty() && (s.back() == ';' || s.back() == ' ')) s.pop_back();
		if (s.empty() || s.find(';') != std::string::npos || s.rfind("1,", 0) != 0)
			throw RpcError("invalid_params", fmt::format("bad object string '{}': must start with \"1,<id>\" and contain no ';'", s));
		out.push_back(std::move(s));
	}
	if (out.empty()) throw RpcError("invalid_params", "'objects' is empty");
	return out;
}

std::vector<int> createFromStrings(LevelEditorLayer* lel, std::vector<std::string> const& strings) {
	std::string joined;
	for (auto const& s : strings) {
		joined += s;
		joined += ';';
	}
	auto created = lel->createObjectsFromString(joined, true, true);
	std::vector<int> uids;
	if (created)
		for (auto obj : CCArrayExt<GameObject*>(created)) uids.push_back(obj->m_uniqueID);
	return uids;
}

matjson::Value intArray(std::vector<int> const& v) {
	auto a = matjson::Value::array();
	for (int i : v) a.push(i);
	return a;
}

}  // namespace

// params: objects: ["1,1,2,15,3,15", ...], confirm_name?
BRIDGE_COMMAND(add_objects) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	auto strings = objectStrings(params);
	auto backup = backupLevel(lel, "add_objects");
	auto uids = createFromStrings(lel, strings);
	return matjson::makeObject({
		{"added", (int)uids.size()},
		{"uids", intArray(uids)},
		{"backup", utils::string::pathToString(backup)},
	});
}

// params: select {...}, confirm_name?
BRIDGE_COMMAND(remove_objects) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	auto sel = parseSelector(params, true);
	std::vector<GameObject*> victims;
	for (auto obj : allObjects(lel))
		if (sel.matches(obj)) victims.push_back(obj);
	auto backup = backupLevel(lel, "remove_objects");
	if (auto ui = lel->m_editorUI) ui->deselectAll();
	for (auto obj : victims) lel->removeObject(obj, true);
	return matjson::makeObject({
		{"removed", (int)victims.size()},
		{"backup", utils::string::pathToString(backup)},
	});
}

// params: select {...}, set {key: value|null}, move {dx, dy}?, confirm_name?
// `set` keys are GD object keys as strings ("2" = x, "3" = y, "6" = rotation, "57" = groups, ...);
// null removes the key. Objects are re-created, so their uids change (returned in order).
BRIDGE_COMMAND(modify_objects) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	auto sel = parseSelector(params, true);
	auto set = optField(params, "set");
	auto move = optField(params, "move");
	if (set && !set->isObject()) throw RpcError("invalid_params", "'set' must be an object of key: value");
	if (!set && !move) throw RpcError("invalid_params", "nothing to do: pass 'set' and/or 'move'");
	double dx = move ? optNumber(*move, "dx").value_or(0) : 0, dy = move ? optNumber(*move, "dy").value_or(0) : 0;
	if (set && (set->contains("1")))
		throw RpcError("invalid_params", "key 1 (object ID) can't be changed; remove and add instead");

	std::vector<GameObject*> targets;
	for (auto obj : allObjects(lel))
		if (sel.matches(obj)) targets.push_back(obj);
	auto backup = backupLevel(lel, "modify_objects");
	if (auto ui = lel->m_editorUI) ui->deselectAll();

	std::vector<std::string> rebuilt;
	for (auto obj : targets) {
		auto props = parseObject(std::string(obj->getSaveString(lel)));
		if (move) {
			// Level-string coordinates (not the node position, which sits LEVEL_Y_OFFSET higher).
			auto pos = toLevel(obj->getPosition());
			setProp(props, "2", fmt::format("{}", pos.x + dx));
			setProp(props, "3", fmt::format("{}", pos.y + dy));
		}
		if (set) {
			for (auto const& [key, value] : *set) {
				if (value.isNull()) setProp(props, key, std::nullopt);
				else setProp(props, key, jsonScalarToString(value, key));
			}
		}
		rebuilt.push_back(joinObject(props));
	}
	for (auto obj : targets) lel->removeObject(obj, true);
	auto uids = rebuilt.empty() ? std::vector<int>{} : createFromStrings(lel, rebuilt);
	return matjson::makeObject({
		{"modified", (int)uids.size()},
		{"uids", intArray(uids)},
		{"backup", utils::string::pathToString(backup)},
	});
}

// params: select {...}?, offset?, limit? (default 500, max 5000), object_strings? (bool)
BRIDGE_COMMAND(list_objects) {
	auto lel = requireEditor();
	auto sel = parseSelector(params, false);
	int offset = (int)optNumber(params, "offset").value_or(0);
	int limit = std::clamp((int)optNumber(params, "limit").value_or(500), 1, MAX_LIST);
	bool withStrings = optBool(params, "object_strings").value_or(false);
	auto out = matjson::Value::array();
	int matched = 0;
	for (auto obj : allObjects(lel)) {
		if (!sel.matches(obj)) continue;
		if (matched >= offset && matched < offset + limit) out.push(describe(obj, lel, withStrings));
		++matched;
	}
	return matjson::makeObject({
		{"total", matched},
		{"offset", offset},
		{"objects", out},
	});
}

// params: id? (trigger object ID, e.g. 901 = move), group?  -> every trigger with its full object string
BRIDGE_COMMAND(get_triggers) {
	auto lel = requireEditor();
	auto id = optNumber(params, "id");
	auto out = matjson::Value::array();
	for (auto obj : allObjects(lel)) {
		if (!obj->m_isTrigger) continue;
		if (id && obj->m_objectID != (int)*id) continue;
		out.push(describe(obj, lel, true));
	}
	return matjson::makeObject({{"count", (int)out.size()}, {"triggers", out}});
}
