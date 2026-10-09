#include <chrono>
#include <filesystem>

#include <Geode/Geode.hpp>

#include "Auth.hpp"
#include "HttpServer.hpp"
#include "Rpc.hpp"

using namespace geode::prelude;

namespace {

bridge::HttpResponse httpError(int status, std::string_view code, std::string_view message) {
	auto body = matjson::makeObject({
		{"ok", false},
		{"error", matjson::makeObject({{"code", std::string(code)}, {"message", std::string(message)}})},
	});
	return {status, body.dump(matjson::NO_INDENTATION)};
}

bridge::HttpResponse handleRpc(bridge::HttpRequest const& req) {
	auto token = req.header("x-gd-bridge-token");
	if (!token || !bridge::tokenMatches(*token)) return httpError(401, "unauthorized", "missing or wrong X-GD-Bridge-Token");

	auto parsed = matjson::parse(req.body);
	if (!parsed) return httpError(400, "bad_request", "body is not valid JSON");
	auto const body = parsed.unwrap();
	bool const isObj = body.isObject();
	matjson::Value id = isObj && body.contains("id") ? body["id"] : matjson::Value(nullptr);

	matjson::Value reply;
	std::optional<std::string> method;
	if (isObj && body.contains("method") && body["method"].isString()) method = body["method"].asString().unwrap();
	if (!method) {
		reply = matjson::makeObject({{"id", id}, {"ok", false},
			{"error", matjson::makeObject({{"code", "bad_request"}, {"message", "body needs a string 'method'"}})}});
	} else {
		matjson::Value params = body.contains("params") ? body["params"] : matjson::Value::object();
		try {
			auto result = bridge::dispatch(*method, params);
			reply = matjson::makeObject({{"id", id}, {"ok", true}, {"result", result}});
		} catch (bridge::RpcError const& e) {
			reply = matjson::makeObject({{"id", id}, {"ok", false},
				{"error", matjson::makeObject({{"code", e.code}, {"message", std::string(e.what())}})}});
		}
	}
	return {200, reply.dump(matjson::NO_INDENTATION)};
}

bridge::HttpResponse handle(bridge::HttpRequest const& req) {
	// No browser page may drive the editor: anything carrying an Origin header is refused outright.
	if (req.header("origin")) return httpError(403, "forbidden", "Origin header not allowed");
	if (req.path == "/health") {
		if (req.method != "GET") return httpError(405, "method_not_allowed", "use GET");
		return {200, R"({"ok":true,"protocol":1})"};
	}
	if (req.path == "/rpc") {
		if (req.method != "POST") return httpError(405, "method_not_allowed", "use POST");
		return handleRpc(req);
	}
	return httpError(404, "not_found", "unknown path");
}

// Screenshots and playtest frames are only needed while Claude reads them; drop anything older than a few
// days so the captures folder can't grow without bound. Backups are separate and never touched here.
void pruneCaptures() {
	auto dir = Mod::get()->getSaveDir() / "captures";
	auto cutoff = std::filesystem::file_time_type::clock::now() - std::chrono::hours(24 * 3);
	std::error_code ec;
	int removed = 0;
	for (auto const& entry : std::filesystem::directory_iterator(dir, ec)) {
		auto when = entry.last_write_time(ec);
		if (!ec && when < cutoff) removed += (int)std::filesystem::remove_all(entry.path(), ec);
	}
	if (removed) log::info("GD Bridge pruned {} old capture files", removed);
}

}  // namespace

$on_mod(Loaded) {
	pruneCaptures();
	auto port = (uint16_t)Mod::get()->getSettingValue<int64_t>("port");
	// Leaked on purpose: see HttpServer.hpp.
	auto server = new bridge::HttpServer();
	auto res = server->start(port, handle);
	if (!res) {
		log::error("GD Bridge could not start its server: {}", res.unwrapErr());
		return;
	}
	if (auto pub = bridge::publishDiscoveryFile(res.unwrap()); !pub) {
		log::error("GD Bridge could not write bridge.json: {}", pub.unwrapErr());
		return;
	}
	log::info("GD Bridge {} listening on 127.0.0.1:{}", Mod::get()->getVersion().toVString(), res.unwrap());
}
