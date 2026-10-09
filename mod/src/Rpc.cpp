#include "Rpc.hpp"

#include <future>
#include <map>
#include <memory>
#include <mutex>

#include <Geode/Geode.hpp>

using namespace geode::prelude;

namespace bridge {

namespace {

struct Entry {
	CommandFn fn;
	CommandOptions opts;
};

// Function-local static: commands register from other translation units during static init.
std::map<std::string, Entry>& registry() {
	static std::map<std::string, Entry> r;
	return r;
}

struct Outcome {
	matjson::Value value;
	std::optional<RpcError> error;
};

Outcome runGuarded(Entry const& e, matjson::Value const& params) {
	try {
		return {e.fn(params), std::nullopt};
	} catch (RpcError const& err) {
		return {{}, err};
	} catch (std::exception const& ex) {
		log::error("command threw: {}", ex.what());
		return {{}, RpcError("internal", ex.what())};
	} catch (...) {
		return {{}, RpcError("internal", "unknown exception")};
	}
}

}  // namespace

void registerCommand(std::string name, CommandFn fn, CommandOptions opts) {
	registry()[std::move(name)] = Entry{std::move(fn), opts};
}

matjson::Value dispatch(std::string const& method, matjson::Value const& params) {
	auto it = registry().find(method);
	if (it == registry().end()) throw RpcError("unknown_method", fmt::format("no method '{}'", method));
	Entry const& entry = it->second;

	if (entry.opts.mainThread) return runOnMainThread(entry.fn, params, entry.opts.timeout);
	auto outcome = runGuarded(entry, params);
	if (outcome.error) throw *outcome.error;
	return std::move(outcome.value);
}

matjson::Value runOnMainThread(CommandFn fn, matjson::Value const& params, std::chrono::milliseconds timeout) {
	Entry entry{std::move(fn), CommandOptions{}};
	auto promise = std::make_shared<std::promise<Outcome>>();
	auto future = promise->get_future();
	// The lambda owns copies, so work that finishes after we gave up waiting is harmless.
	queueInMainThread([promise, entry, params]() mutable { promise->set_value(runGuarded(entry, params)); });
	if (future.wait_for(timeout) != std::future_status::ready)
		throw RpcError("timeout", fmt::format("the main thread did not respond within {} ms", timeout.count()));
	auto outcome = future.get();
	if (outcome.error) throw *outcome.error;
	return std::move(outcome.value);
}

// ---- parameter helpers ----

matjson::Value const* optField(matjson::Value const& p, std::string_view key) {
	if (!p.isObject() || !p.contains(key)) return nullptr;
	auto const& v = p[key];
	return v.isNull() ? nullptr : &v;
}

std::optional<std::string> optString(matjson::Value const& p, std::string_view key) {
	auto v = optField(p, key);
	if (!v) return std::nullopt;
	if (!v->isString()) throw RpcError("invalid_params", fmt::format("'{}' must be a string", key));
	return v->asString().unwrap();
}

std::string paramString(matjson::Value const& p, std::string_view key) {
	auto v = optString(p, key);
	if (!v) throw RpcError("invalid_params", fmt::format("missing '{}'", key));
	return *v;
}

std::optional<double> optNumber(matjson::Value const& p, std::string_view key) {
	auto v = optField(p, key);
	if (!v) return std::nullopt;
	if (!v->isNumber()) throw RpcError("invalid_params", fmt::format("'{}' must be a number", key));
	return v->asDouble().unwrap();
}

double paramNumber(matjson::Value const& p, std::string_view key) {
	auto v = optNumber(p, key);
	if (!v) throw RpcError("invalid_params", fmt::format("missing '{}'", key));
	return *v;
}

std::optional<bool> optBool(matjson::Value const& p, std::string_view key) {
	auto v = optField(p, key);
	if (!v) return std::nullopt;
	if (!v->isBool()) throw RpcError("invalid_params", fmt::format("'{}' must be a boolean", key));
	return v->asBool().unwrap();
}

}  // namespace bridge
