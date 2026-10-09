// Level management: save, create, open, list; music info.

#include "../Level.hpp"
#include "../Rpc.hpp"

#include <Geode/Geode.hpp>

using namespace geode::prelude;
using namespace bridge;

namespace {

bool isSafeName(std::string const& name) {
	return name.starts_with(SAFE_PREFIX);
}

std::vector<GJGameLevel*> localLevels() {
	std::vector<GJGameLevel*> out;
	auto llm = LocalLevelManager::sharedState();
	if (!llm || !llm->m_localLevels) return out;
	for (auto lvl : CCArrayExt<GJGameLevel*>(llm->m_localLevels)) out.push_back(lvl);
	return out;
}

GJGameLevel* findLevel(std::string const& name) {
	for (auto lvl : localLevels())
		if (std::string(lvl->m_levelName) == name) return lvl;
	return nullptr;
}

// Switching levels from inside the editor would discard unsaved edits. Claude never saves or discards
// Distanax's own levels, so that is only allowed from a "CLAUDE " level, which is backed up and saved first.
void prepareToLeave() {
	if (PlayLayer::get()) throw RpcError("busy", "a level is being played; exit it first");
	if (auto lel = LevelEditorLayer::get()) {
		requireNotPlaytesting(lel);
		auto name = levelName(lel);
		if (!isSafeName(name))
			throw RpcError("level_protected",
				fmt::format("the editor has '{}' open; save and exit it yourself first (Claude never saves or "
					"discards your own levels)", name));
		backupLevel(lel, "auto_save_before_switch");
		saveEditorLevel(lel);
	}
}

void openInEditor(GJGameLevel* level) {
	CCDirector::sharedDirector()->replaceScene(CCTransitionFade::create(0.3f, LevelEditorLayer::scene(level, false)));
}

matjson::Value levelSummary(GJGameLevel* lvl) {
	return matjson::makeObject({
		{"name", std::string(lvl->m_levelName)},
		{"song_id", lvl->m_songID},
		{"audio_track", lvl->m_audioTrack},
		{"claude", isSafeName(std::string(lvl->m_levelName))},
	});
}

}  // namespace

// params: confirm_name? Saves the open level to GD's level list and to disk.
BRIDGE_COMMAND(save_level) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	auto backup = backupLevel(lel, "save_level");
	saveEditorLevel(lel);
	return matjson::makeObject({
		{"name", levelName(lel)},
		{"saved", true},
		{"object_count", lel->m_objects ? (int)lel->m_objects->count() : 0},
		{"backup", utils::string::pathToString(backup)},
	});
}

// params: name (gets the "CLAUDE " prefix if missing), song_id? (Newgrounds/custom), audio_track? (official)
BRIDGE_COMMAND(create_level) {
	auto name = paramString(params, "name");
	if (!isSafeName(name)) name = std::string(SAFE_PREFIX) + name;
	if (name.size() > 64) throw RpcError("invalid_params", "name too long (max 64 characters)");
	if (findLevel(name)) throw RpcError("invalid_params", fmt::format("a level named '{}' already exists; use open_level", name));
	prepareToLeave();

	auto level = GameLevelManager::sharedState()->createNewLevel();
	if (!level) throw RpcError("internal", "GameLevelManager::createNewLevel failed");
	level->m_levelName = name;
	if (auto song = optNumber(params, "song_id"); song && *song > 0) level->m_songID = (int)*song;
	if (auto track = optNumber(params, "audio_track")) level->m_audioTrack = (int)*track;
	LocalLevelManager::sharedState()->save();
	openInEditor(level);
	return matjson::makeObject({{"created", levelSummary(level)}, {"opening_editor", true}});
}

// params: name (exact), confirm_name? (required for levels not named "CLAUDE ...")
BRIDGE_COMMAND(open_level) {
	auto name = paramString(params, "name");
	auto level = findLevel(name);
	if (!level) throw RpcError("not_found", fmt::format("no local level named '{}' (see list_levels)", name));
	if (!isSafeName(name) && optString(params, "confirm_name") != name)
		throw RpcError("level_protected", fmt::format("'{}' is not a CLAUDE level; pass confirm_name=\"{}\" to open it", name, name));
	if (auto lel = LevelEditorLayer::get(); lel && lel->m_level == level)
		return matjson::makeObject({{"opened", levelSummary(level)}, {"already_open", true}});
	prepareToLeave();
	openInEditor(level);
	return matjson::makeObject({{"opened", levelSummary(level)}, {"opening_editor", true}});
}

// params: claude_only? (default false), limit? (default 200)
BRIDGE_COMMAND(list_levels) {
	bool claudeOnly = optBool(params, "claude_only").value_or(false);
	int limit = std::clamp((int)optNumber(params, "limit").value_or(200), 1, 2000);
	auto out = matjson::Value::array();
	int total = 0;
	for (auto lvl : localLevels()) {
		if (claudeOnly && !isSafeName(std::string(lvl->m_levelName))) continue;
		if (total++ < limit) out.push(levelSummary(lvl));
	}
	return matjson::makeObject({{"total", total}, {"levels", out}});
}

// Song and timing info of the open level. Guidelines are GD's "time~colour~..." markers (often BPM beats).
BRIDGE_COMMAND(get_music) {
	auto lel = requireEditor();
	auto lvl = lel->m_level;
	auto s = lel->m_levelSettings;
	auto guidelines = matjson::Value::array();
	std::string raw = s ? std::string(s->m_guidelineString) : "";
	auto parts = utils::string::split(raw, "~");
	for (std::size_t i = 0; i + 1 < parts.size(); i += 2) {
		if (parts[i].empty()) continue;
		guidelines.push(matjson::makeObject({{"time", utils::numFromString<double>(parts[i]).unwrapOr(0.0)},
			{"color", utils::numFromString<double>(parts[i + 1]).unwrapOr(0.0)}}));
	}
	return matjson::makeObject({
		{"song_id", lvl->m_songID},
		{"audio_track", lvl->m_audioTrack},
		{"custom_song", lvl->m_songID > 0},
		{"song_ids", std::string(lvl->m_songIDs)},
		{"offset", s ? s->m_songOffset : 0.f},
		{"fade_in", s ? s->m_fadeIn : false},
		{"fade_out", s ? s->m_fadeOut : false},
		{"guideline_count", (int)guidelines.size()},
		{"guidelines", guidelines},
	});
}
