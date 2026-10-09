#pragma once

// Per-launch secret shared with the local MCP server through bridge.json in the mod's save dir.

#include <cstdint>
#include <string>

#include <Geode/Result.hpp>

namespace bridge {

// Generates a fresh token (32 random bytes, hex) and writes bridge.json:
//   {"protocol":1,"port":<port>,"token":"...","pid":<pid>,"mod_version":"v0.1.0"}
geode::Result<> publishDiscoveryFile(uint16_t port);

// Constant-time comparison against the current token. False until publishDiscoveryFile succeeded.
bool tokenMatches(std::string const& candidate);

}  // namespace bridge
