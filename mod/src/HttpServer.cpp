// Geode's precompiled header has already included <Windows.h> (without WIN32_LEAN_AND_MEAN), which
// pulls in the legacy <winsock.h>; including <winsock2.h> after it redefines sockaddr and fails.
// winsock.h has everything this file needs except two constants, defined below. ws2_32 is linked by
// Geode's CMake for every mod.
#include <Geode/Geode.hpp>
#include <winsock.h>
#ifndef SO_EXCLUSIVEADDRUSE
#define SO_EXCLUSIVEADDRUSE ((int)(~SO_REUSEADDR))
#endif
#ifndef SD_SEND
#define SD_SEND 0x01
#endif

#include "HttpServer.hpp"

#include <algorithm>
#include <cctype>
#include <optional>
#include <string_view>



using namespace geode;

namespace bridge {

namespace {

constexpr DWORD RECV_TIMEOUT_MS = 5000;

std::string lower(std::string_view s) {
	std::string out(s);
	std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c) { return (char)std::tolower(c); });
	return out;
}

std::string_view trim(std::string_view s) {
	while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
	while (!s.empty() && (s.back() == ' ' || s.back() == '\t' || s.back() == '\r')) s.remove_suffix(1);
	return s;
}

char const* reason(int status) {
	switch (status) {
		case 200: return "OK";
		case 400: return "Bad Request";
		case 401: return "Unauthorized";
		case 403: return "Forbidden";
		case 404: return "Not Found";
		case 405: return "Method Not Allowed";
		case 413: return "Payload Too Large";
		case 500: return "Internal Server Error";
		default: return "Unknown";
	}
}

void sendAll(SOCKET s, std::string const& data) {
	std::size_t sent = 0;
	while (sent < data.size()) {
		int chunk = (int)std::min<std::size_t>(data.size() - sent, 1 << 20);
		int n = ::send(s, data.data() + sent, chunk, 0);
		if (n <= 0) return;
		sent += (std::size_t)n;
	}
}

void sendResponse(SOCKET s, HttpResponse const& res) {
	std::string head = fmt::format(
		"HTTP/1.1 {} {}\r\nContent-Type: {}\r\nContent-Length: {}\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n",
		res.status, reason(res.status), res.contentType, res.body.size());
	sendAll(s, head + res.body);
}

HttpResponse errorResponse(int status, std::string_view message) {
	return {status, fmt::format("{{\"ok\":false,\"error\":{{\"code\":\"http_{}\",\"message\":\"{}\"}}}}", status, message)};
}

// Reads one request. Returns an error response (status != 0) if the request is unusable.
std::optional<HttpResponse> readRequest(SOCKET s, HttpRequest& req) {
	std::string buf;
	char tmp[8192];
	std::size_t headerEnd = std::string::npos;
	while (headerEnd == std::string::npos) {
		int n = ::recv(s, tmp, sizeof(tmp), 0);
		if (n <= 0) return errorResponse(400, "connection closed before headers");
		buf.append(tmp, (std::size_t)n);
		headerEnd = buf.find("\r\n\r\n");
		if (headerEnd == std::string::npos && buf.size() > HttpServer::MAX_HEADER_BYTES)
			return errorResponse(400, "headers too large");
	}

	std::string_view head(buf.data(), headerEnd);
	auto lineEnd = head.find("\r\n");
	std::string_view requestLine = head.substr(0, lineEnd);
	auto sp1 = requestLine.find(' ');
	auto sp2 = requestLine.find(' ', sp1 == std::string_view::npos ? 0 : sp1 + 1);
	if (sp1 == std::string_view::npos || sp2 == std::string_view::npos)
		return errorResponse(400, "malformed request line");
	req.method = std::string(requestLine.substr(0, sp1));
	req.path = std::string(requestLine.substr(sp1 + 1, sp2 - sp1 - 1));

	std::size_t pos = lineEnd == std::string_view::npos ? head.size() : lineEnd + 2;
	while (pos < head.size()) {
		auto end = head.find("\r\n", pos);
		if (end == std::string_view::npos) end = head.size();
		std::string_view line = head.substr(pos, end - pos);
		auto colon = line.find(':');
		if (colon != std::string_view::npos)
			req.headers[lower(trim(line.substr(0, colon)))] = std::string(trim(line.substr(colon + 1)));
		pos = end + 2;
	}

	std::size_t contentLength = 0;
	if (auto cl = req.header("content-length")) {
		try {
			contentLength = std::stoull(*cl);
		} catch (...) {
			return errorResponse(400, "bad Content-Length");
		}
	}
	if (contentLength > HttpServer::MAX_BODY_BYTES) return errorResponse(413, "body too large");

	req.body = buf.substr(headerEnd + 4);
	while (req.body.size() < contentLength) {
		int n = ::recv(s, tmp, sizeof(tmp), 0);
		if (n <= 0) return errorResponse(400, "connection closed mid-body");
		req.body.append(tmp, (std::size_t)n);
	}
	req.body.resize(contentLength);
	return std::nullopt;
}

}  // namespace

Result<uint16_t> HttpServer::start(uint16_t preferredPort, HttpHandler handler) {
	if (m_running) return Err("server already running");

	WSADATA wsa;
	if (int err = WSAStartup(MAKEWORD(2, 2), &wsa)) return Err(fmt::format("WSAStartup failed: {}", err));

	SOCKET listener = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (listener == INVALID_SOCKET) return Err(fmt::format("socket() failed: {}", WSAGetLastError()));

	// Exclusive use: no other process may bind the same port while we hold it.
	BOOL exclusive = TRUE;
	::setsockopt(listener, SOL_SOCKET, SO_EXCLUSIVEADDRUSE, (char const*)&exclusive, sizeof(exclusive));

	sockaddr_in addr{};
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);  // 127.0.0.1 only, never 0.0.0.0
	addr.sin_port = htons(preferredPort);
	if (::bind(listener, (sockaddr*)&addr, sizeof(addr)) == SOCKET_ERROR) {
		log::warn("Port {} unavailable ({}), using an ephemeral port", preferredPort, WSAGetLastError());
		addr.sin_port = 0;
		if (::bind(listener, (sockaddr*)&addr, sizeof(addr)) == SOCKET_ERROR) {
			int err = WSAGetLastError();
			::closesocket(listener);
			return Err(fmt::format("bind() failed: {}", err));
		}
	}
	if (::listen(listener, 8) == SOCKET_ERROR) {
		int err = WSAGetLastError();
		::closesocket(listener);
		return Err(fmt::format("listen() failed: {}", err));
	}

	sockaddr_in bound{};
	int len = sizeof(bound);
	::getsockname(listener, (sockaddr*)&bound, &len);

	m_listen = (std::uintptr_t)listener;
	m_handler = std::move(handler);
	m_running = true;
	m_thread = std::thread([this] { this->run(); });
	m_thread.detach();
	return Ok(ntohs(bound.sin_port));
}

void HttpServer::run() {
	auto listener = (SOCKET)m_listen;
	while (m_running) {
		SOCKET client = ::accept(listener, nullptr, nullptr);
		if (client == INVALID_SOCKET) {
			log::warn("accept() failed: {}", WSAGetLastError());
			Sleep(100);
			continue;
		}
		this->serveClient((std::uintptr_t)client);
	}
}

void HttpServer::serveClient(std::uintptr_t rawClient) {
	auto client = (SOCKET)rawClient;
	DWORD timeout = RECV_TIMEOUT_MS;
	::setsockopt(client, SOL_SOCKET, SO_RCVTIMEO, (char const*)&timeout, sizeof(timeout));

	HttpRequest req;
	if (auto err = readRequest(client, req)) {
		sendResponse(client, *err);
	} else {
		HttpResponse res;
		try {
			res = m_handler(req);
		} catch (std::exception const& e) {
			log::error("HTTP handler threw: {}", e.what());
			res = errorResponse(500, "internal error");
		}
		sendResponse(client, res);
	}
	::shutdown(client, SD_SEND);
	::closesocket(client);
}

}  // namespace bridge
