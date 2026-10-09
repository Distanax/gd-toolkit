"""HTTP client for the GD Bridge mod (protocol: docs/PROTOCOL.md)."""
from __future__ import annotations

import itertools
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PROTOCOL = 1
MOD_ID = "distanax.gd-bridge"


class BridgeError(Exception):
    """An error reported by the mod, or a failure to reach it. `code` follows docs/PROTOCOL.md."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def default_discovery_path() -> Path:
    """Where the mod writes bridge.json: <LOCALAPPDATA>/GeometryDash/geode/mods/<mod id>/bridge.json."""
    override = os.environ.get("GD_BRIDGE_FILE")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "GeometryDash" / "geode" / "mods" / MOD_ID / "bridge.json"


NOT_RUNNING = (
    "Can't reach Geometry Dash. Start GD with the GD Bridge mod installed and enabled "
    "(see TESTING.md in Distanax/gd-toolkit)."
)


class BridgeClient:
    def __init__(self, discovery_path: Path | None = None, timeout: float = 60.0):
        self.discovery_path = discovery_path or default_discovery_path()
        self.timeout = timeout
        self._ids = itertools.count(1)
        self._info: dict[str, Any] | None = None

    # -- discovery -------------------------------------------------------------
    def _load(self) -> dict[str, Any]:
        try:
            info = json.loads(self.discovery_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise BridgeError("not_running", f"{NOT_RUNNING} (no {self.discovery_path})") from None
        except (OSError, ValueError) as e:
            raise BridgeError("not_running", f"Unreadable {self.discovery_path}: {e}") from None
        if info.get("protocol") != PROTOCOL:
            raise BridgeError("protocol_mismatch",
                              f"Mod speaks protocol {info.get('protocol')}, this server speaks {PROTOCOL}. "
                              "Update both from the same release.")
        self._info = info
        return info

    def _post(self, info: dict[str, Any], body: bytes, timeout: float) -> dict[str, Any]:
        req = urllib.request.Request(
            f"http://127.0.0.1:{info['port']}/rpc", data=body, method="POST",
            headers={"Content-Type": "application/json", "X-GD-Bridge-Token": info["token"]})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            try:
                err = json.loads(e.read()).get("error", {})
            except ValueError:
                err = {}
            code = "unauthorized" if e.code == 401 else err.get("code", f"http_{e.code}")
            raise BridgeError(code, err.get("message", str(e))) from None
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            raise BridgeError("not_running", f"{NOT_RUNNING} ({e})") from None

    # -- calls -----------------------------------------------------------------
    def call(self, method: str, timeout: float | None = None, **params: Any) -> Any:
        """Call a mod method and return its result. Raises BridgeError."""
        params = {k: v for k, v in params.items() if v is not None}
        body = json.dumps({"id": next(self._ids), "method": method, "params": params}).encode()
        timeout = timeout or self.timeout
        info = self._info or self._load()
        try:
            reply = self._post(info, body, timeout)
        except BridgeError as e:
            # GD restarted: new port/token. Re-read bridge.json once and retry.
            if e.code not in ("unauthorized", "not_running"):
                raise
            reply = self._post(self._load(), body, timeout)
        if not reply.get("ok"):
            err = reply.get("error") or {}
            raise BridgeError(err.get("code", "internal"), err.get("message", "unknown error"))
        return reply.get("result")
