#include "Auth.hpp"

#include <mutex>
#include <random>

#include <Geode/Geode.hpp>
#include <Geode/utils/file.hpp>

using namespace geode::prelude;

namespace bridge {

namespace {

std::mutex g_mutex;
std::string g_token;

std::string randomHex(std::size_t bytes) {
	// MSVC's std::random_device is backed by the OS CSPRNG (rand_s), so this is suitable for a secret.
	std::random_device rd;
	static constexpr char HEX[] = "0123456789abcdef";
	std::string out;
	out.reserve(bytes * 2);
	for (std::size_t i = 0; i < bytes; ++i) {
		auto b = (unsigned)(rd() & 0xff);
		out.push_back(HEX[b >> 4]);
		out.push_back(HEX[b & 0xf]);
	}
	return out;
}

}  // namespace

Result<> publishDiscoveryFile(uint16_t port) {
	auto token = randomHex(32);
	auto doc = matjson::makeObject({
		{"protocol", 1},
		{"port", (int)port},
		{"token", token},
		{"pid", (int)GetCurrentProcessId()},
		{"mod_version", Mod::get()->getVersion().toVString()},
	});
	auto dir = Mod::get()->getSaveDir();
	GEODE_UNWRAP(file::createDirectoryAll(dir));
	GEODE_UNWRAP(file::writeStringSafe(dir / "bridge.json", doc.dump()));
	std::lock_guard lock(g_mutex);
	g_token = std::move(token);
	return Ok();
}

bool tokenMatches(std::string const& candidate) {
	std::lock_guard lock(g_mutex);
	if (g_token.empty() || candidate.size() != g_token.size()) return false;
	unsigned char diff = 0;
	for (std::size_t i = 0; i < g_token.size(); ++i) diff |= (unsigned char)(candidate[i] ^ g_token[i]);
	return diff == 0;
}

}  // namespace bridge
