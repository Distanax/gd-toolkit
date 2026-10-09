#include <Geode/Geode.hpp>

#include "HttpServer.hpp"

using namespace geode::prelude;

namespace {

bridge::HttpResponse handle(bridge::HttpRequest const& req) {
	// No browser page may drive the editor: anything carrying an Origin header is refused outright.
	if (req.header("origin")) return {403, R"({"ok":false,"error":{"code":"forbidden","message":"Origin header not allowed"}})"};
	if (req.path == "/health") {
		if (req.method != "GET") return {405, R"({"ok":false,"error":{"code":"method_not_allowed","message":"use GET"}})"};
		return {200, R"({"ok":true,"protocol":1})"};
	}
	return {404, R"({"ok":false,"error":{"code":"not_found","message":"unknown path"}})"};
}

}  // namespace

$on_mod(Loaded) {
	auto port = (uint16_t)Mod::get()->getSettingValue<int64_t>("port");
	// Leaked on purpose: see HttpServer.hpp.
	auto server = new bridge::HttpServer();
	auto res = server->start(port, handle);
	if (!res) {
		log::error("GD Bridge could not start its server: {}", res.unwrapErr());
		return;
	}
	log::info("GD Bridge {} listening on 127.0.0.1:{}", Mod::get()->getVersion().toVString(), res.unwrap());
}
