#pragma once

// Minimal HTTP/1.1 server for 127.0.0.1, one request per connection, served sequentially on one
// background thread. Deliberately tiny: the only client is the local gd-bridge MCP server.
// No Windows headers here, so including this never drags winsock into Geode translation units.

#include <atomic>
#include <cstdint>
#include <functional>
#include <map>
#include <string>
#include <thread>

#include <Geode/Result.hpp>

namespace bridge {

struct HttpRequest {
	std::string method;
	std::string path;
	std::map<std::string, std::string> headers;  // names lower-cased
	std::string body;

	std::string const* header(std::string const& lowerName) const {
		auto it = headers.find(lowerName);
		return it == headers.end() ? nullptr : &it->second;
	}
};

struct HttpResponse {
	int status = 200;
	std::string body;
	std::string contentType = "application/json";
};

using HttpHandler = std::function<HttpResponse(HttpRequest const&)>;

class HttpServer {
public:
	static constexpr std::size_t MAX_HEADER_BYTES = 16 * 1024;
	static constexpr std::size_t MAX_BODY_BYTES = 64 * 1024 * 1024;

	// Binds 127.0.0.1:port (falls back to an ephemeral port if it is taken) and starts serving.
	// Returns the port actually bound.
	geode::Result<uint16_t> start(uint16_t preferredPort, HttpHandler handler);

	// Never destroyed in practice (the game process just exits); the object is leaked on purpose so no
	// static destructor joins a thread blocked in accept().
	HttpServer() = default;
	HttpServer(HttpServer const&) = delete;
	HttpServer& operator=(HttpServer const&) = delete;

private:
	void run();
	void serveClient(std::uintptr_t client);

	std::uintptr_t m_listen = ~std::uintptr_t(0);
	std::thread m_thread;
	std::atomic_bool m_running = false;
	HttpHandler m_handler;
};

}  // namespace bridge
