#pragma once

// RPC command registry and helpers. Commands are plain functions from params to a JSON result;
// failures are reported by throwing RpcError with a protocol error code (docs/PROTOCOL.md).

#include <chrono>
#include <functional>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

#include <matjson.hpp>

namespace bridge {

struct RpcError : std::runtime_error {
	std::string code;
	RpcError(std::string code, std::string const& message) : std::runtime_error(message), code(std::move(code)) {}
};

using CommandFn = std::function<matjson::Value(matjson::Value const& params)>;

struct CommandOptions {
	// Most commands touch game state and must run on the main thread. Pure helpers (ping, job polling)
	// may run on the socket thread.
	bool mainThread = true;
	std::chrono::milliseconds timeout = std::chrono::seconds(10);
};

void registerCommand(std::string name, CommandFn fn, CommandOptions opts = {});

// Runs a command by name: on the main thread if required, waiting up to its timeout. Throws RpcError.
matjson::Value dispatch(std::string const& method, matjson::Value const& params);

// Registers commands from a translation unit at static-init time:
//   BRIDGE_COMMAND(ping) { return matjson::makeObject({{"pong", true}}); }
#define BRIDGE_COMMAND_IMPL(name, opts)                                                                  \
	static matjson::Value bridgeCmd_##name(matjson::Value const& params);                                \
	static bool const bridgeCmdReg_##name = (::bridge::registerCommand(#name, bridgeCmd_##name, opts), true); \
	static matjson::Value bridgeCmd_##name([[maybe_unused]] matjson::Value const& params)
#define BRIDGE_COMMAND(name) BRIDGE_COMMAND_IMPL(name, ::bridge::CommandOptions{})
#define BRIDGE_COMMAND_OFF_THREAD(name) BRIDGE_COMMAND_IMPL(name, (::bridge::CommandOptions{.mainThread = false}))

// ---- parameter helpers (throw RpcError("invalid_params", ...)) ----
std::string paramString(matjson::Value const& p, std::string_view key);
std::optional<std::string> optString(matjson::Value const& p, std::string_view key);
double paramNumber(matjson::Value const& p, std::string_view key);
std::optional<double> optNumber(matjson::Value const& p, std::string_view key);
std::optional<bool> optBool(matjson::Value const& p, std::string_view key);
matjson::Value const* optField(matjson::Value const& p, std::string_view key);

}  // namespace bridge
