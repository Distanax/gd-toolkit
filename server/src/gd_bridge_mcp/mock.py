"""A fake GD Bridge mod for tests and offline development.

Speaks the real wire protocol (docs/PROTOCOL.md) over HTTP on 127.0.0.1 and writes its own
bridge.json, so the real BridgeClient is exercised end to end. Commands are a dict of
name -> function(params) -> result; tests can add or override entries.
"""
from __future__ import annotations

import json
import secrets
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from .client import PROTOCOL


class MockError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


Command = Callable[[dict[str, Any]], Any]


class MockBridge:
    """Use as a context manager: `with MockBridge() as mock: BridgeClient(mock.discovery_path)`."""

    def __init__(self, directory: Path | None = None):
        self._tmp = None if directory else tempfile.TemporaryDirectory()
        self.directory = Path(directory or self._tmp.name)
        self.discovery_path = self.directory / "bridge.json"
        self.token = secrets.token_hex(32)
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.state: dict[str, Any] = {
            "scene": "LevelEditorLayer",
            "level": {"name": "CLAUDE test", "id": 0, "song_id": 0, "objects": []},
            "playtest": "not",
        }
        self.commands: dict[str, Command] = {
            "ping": lambda p: {"pong": True, "mod_version": "mock", "protocol": PROTOCOL},
            "status": self._status,
        }
        self._server: ThreadingHTTPServer | None = None

    # -- default commands --------------------------------------------------------
    def _status(self, p: dict[str, Any]) -> dict[str, Any]:
        lvl = self.state["level"]
        in_editor = self.state["scene"] == "LevelEditorLayer"
        return {
            "scene": self.state["scene"],
            "in_editor": in_editor,
            "playtest": self.state["playtest"],
            "level": {"name": lvl["name"], "id": lvl["id"], "song_id": lvl["song_id"],
                      "object_count": len(lvl["objects"])} if in_editor else None,
            "versions": {"mod": "mock", "geode": "mock", "gd": "2.2081", "protocol": PROTOCOL},
        }

    # -- server --------------------------------------------------------------------
    def __enter__(self) -> "MockBridge":
        mock = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a: Any) -> None:  # keep test output clean
                pass

            def _send(self, status: int, payload: dict[str, Any]) -> None:
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self) -> None:
                if self.path == "/health":
                    self._send(200, {"ok": True, "protocol": PROTOCOL})
                else:
                    self._send(404, {"ok": False, "error": {"code": "not_found", "message": "unknown path"}})

            def do_POST(self) -> None:
                if self.headers.get("Origin"):
                    return self._send(403, {"ok": False, "error": {"code": "forbidden", "message": "Origin"}})
                if self.path != "/rpc":
                    return self._send(404, {"ok": False, "error": {"code": "not_found", "message": "unknown path"}})
                if self.headers.get("X-GD-Bridge-Token") != mock.token:
                    return self._send(401, {"ok": False, "error": {"code": "unauthorized", "message": "bad token"}})
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                rid, method, params = body.get("id"), body.get("method"), body.get("params") or {}
                mock.calls.append((method, params))
                fn = mock.commands.get(method)
                if fn is None:
                    return self._send(200, {"id": rid, "ok": False,
                                            "error": {"code": "unknown_method", "message": f"no method '{method}'"}})
                try:
                    result = fn(params)
                except MockError as e:
                    return self._send(200, {"id": rid, "ok": False, "error": {"code": e.code, "message": e.message}})
                self._send(200, {"id": rid, "ok": True, "result": result})

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        self.write_discovery()
        return self

    def write_discovery(self) -> None:
        port = self._server.server_address[1] if self._server else 0
        self.discovery_path.write_text(json.dumps(
            {"protocol": PROTOCOL, "port": port, "token": self.token, "pid": 0, "mod_version": "mock"}))

    def rotate_token(self) -> None:
        """Simulate a GD restart: new token, same port."""
        self.token = secrets.token_hex(32)
        self.write_discovery()

    def __exit__(self, *exc: Any) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._tmp:
            self._tmp.cleanup()
