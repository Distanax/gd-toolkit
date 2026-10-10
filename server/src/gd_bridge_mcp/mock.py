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
from .objects import TRIGGER_IDS, parse

SAFE_PREFIX = "CLAUDE "
DEFAULT_HEADER = "kS38,1_40_2_125_3_255_11_255_12_255_13_255_4_-1_6_1000_7_1_15_1_18_0_8_1|,kA2,0,kA4,0"


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
        self.header = DEFAULT_HEADER
        self.backups: list[tuple[str, str, str]] = []  # (level name, reason, level string)
        self._next_uid = 1
        self.commands: dict[str, Command] = {
            "ping": lambda p: {"pong": True, "mod_version": "mock", "protocol": PROTOCOL},
            "status": self._status,
            "get_level_string": self._get_level_string,
            "set_level_string": self._set_level_string,
            "add_objects": self._add_objects,
            "remove_objects": self._remove_objects,
            "modify_objects": self._modify_objects,
            "list_objects": self._list_objects,
            "get_triggers": self._get_triggers,
            "get_camera": lambda p: dict(self.camera),
            "move_camera": self._move_camera,
            "screenshot": self._screenshot,
            "playtest": self._playtest,
            "capture_frames": self._capture_frames,
            "job_status": self._job_status,
            "save_level": self._save_level,
            "create_level": self._create_level,
            "open_level": self._open_level,
            "list_levels": self._list_levels,
            "get_music": self._get_music,
            "undo": self._undo,
            "redo": self._redo,
            "list_backups": self._list_backups,
            "restore_backup": self._restore_backup,
            "autoplay": lambda p: {"armed": True, "events": len(p.get("inputs", []))},
            "autoplay_status": lambda p: {"armed": True, "active": True, "events": 0, "next_event": 0,
                                          "deaths": [], "max_x": 0.0, "trace_points": 0},
            "autoplay_clear": lambda p: {"cleared": True},
        }
        self.saved_levels: dict[str, str] = {}  # name -> saved level string (the "local levels")
        self.undo_stack: list[str] = []
        self.redo_stack: list[str] = []
        self.jobs: dict[str, dict[str, Any]] = {}
        self.temp_start_pos: float | None = None
        self.camera = {"x": 285.0, "y": 160.0, "zoom": 1.0}
        self.capture_size = (1920, 1080)
        self._server: ThreadingHTTPServer | None = None

    # -- level model (mirrors mod/src/Level.cpp + commands/*.cpp) -----------------
    @property
    def objects(self) -> list[dict[str, Any]]:
        return self.state["level"]["objects"]

    def _new_object(self, s: str) -> dict[str, Any]:
        obj = {"uid": self._next_uid, "props": parse(s)}
        self._next_uid += 1
        return obj

    def level_string(self) -> str:
        return self.header + ";" + "".join(
            ",".join(f"{k},{v}" for k, v in o["props"].items()) + ";" for o in self.objects)

    def _require_editor(self) -> None:
        if self.state["scene"] != "LevelEditorLayer":
            raise MockError("not_in_editor", "open a level in the editor first")

    def _require_write(self, p: dict[str, Any], reason: str) -> None:
        self._require_editor()
        if self.state["playtest"] != "not":
            raise MockError("busy", "a playtest is running; stop it first")
        name = self.state["level"]["name"]
        if not name.startswith(SAFE_PREFIX) and p.get("confirm_name") != name:
            raise MockError("level_protected", f"level '{name}' doesn't start with \"{SAFE_PREFIX}\"")
        self.backups.append((name, reason, self.level_string()))

    def _backup_path(self) -> str:
        return f"mock-backups/{len(self.backups)}.txt"

    def _select(self, p: dict[str, Any], for_write: bool) -> list[dict[str, Any]]:
        sel = p.get("select") or {}
        if for_write and not any(sel.get(k) for k in ("uids", "ids", "groups", "region", "triggers")) \
                and not sel.get("all"):
            raise MockError("invalid_params", "empty selector")
        out = []
        for o in self.objects:
            pr = o["props"]
            oid, x, y = int(pr["1"]), float(pr.get("2", 0)), float(pr.get("3", 0))
            groups = {int(g) for g in pr.get("57", "").split(".") if g}
            if sel.get("uids") and o["uid"] not in sel["uids"]:
                continue
            if sel.get("ids") and oid not in sel["ids"]:
                continue
            if sel.get("triggers") and oid not in TRIGGER_IDS.values():
                continue
            if sel.get("groups") and not groups & set(sel["groups"]):
                continue
            r = sel.get("region")
            if r and not (min(r["x1"], r["x2"]) <= x <= max(r["x1"], r["x2"])
                          and min(r["y1"], r["y2"]) <= y <= max(r["y1"], r["y2"])):
                continue
            out.append(o)
        return out

    def _describe(self, o: dict[str, Any], with_string: bool) -> dict[str, Any]:
        pr = o["props"]
        d = {"uid": o["uid"], "id": int(pr["1"]), "x": float(pr.get("2", 0)), "y": float(pr.get("3", 0)),
             "rotation": float(pr.get("6", 0)), "scale_x": 1.0, "scale_y": 1.0,
             "groups": [int(g) for g in pr.get("57", "").split(".") if g],
             "trigger": int(pr["1"]) in TRIGGER_IDS.values(), "editor_layer": int(pr.get("20", 0))}
        if with_string:
            d["object_string"] = ",".join(f"{k},{v}" for k, v in pr.items())
        return d

    def _get_level_string(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        return {"name": self.state["level"]["name"], "object_count": len(self.objects),
                "level_string": self.level_string()}

    def _set_level_string(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_write(p, "set_level_string")
        s = p.get("level_string")
        if not isinstance(s, str) or ";" not in s:
            raise MockError("invalid_params", "level_string must be a raw level string")
        header, *objs = s.split(";")
        self.header = header
        self.objects[:] = [self._new_object(o) for o in objs if o.strip()]
        return {"name": self.state["level"]["name"], "backup": self._backup_path(), "reloaded": True}

    def _add_objects(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_write(p, "add_objects")
        strings = p.get("objects")
        if not isinstance(strings, list) or not strings:
            raise MockError("invalid_params", "'objects' must be a non-empty list of object strings")
        new = [self._new_object(s) for s in strings]
        self.objects.extend(new)
        return {"added": len(new), "uids": [o["uid"] for o in new], "backup": self._backup_path()}

    def _remove_objects(self, p: dict[str, Any]) -> dict[str, Any]:
        victims = self._select(p, True)
        self._require_write(p, "remove_objects")
        ids = {id(o) for o in victims}
        self.objects[:] = [o for o in self.objects if id(o) not in ids]
        return {"removed": len(victims), "backup": self._backup_path()}

    def _modify_objects(self, p: dict[str, Any]) -> dict[str, Any]:
        targets = self._select(p, True)
        self._require_write(p, "modify_objects")
        move, setv = p.get("move") or {}, p.get("set") or {}
        uids = []
        for o in targets:
            pr = o["props"]
            if move:
                pr["2"] = f"{float(pr.get('2', 0)) + move.get('dx', 0):g}"
                pr["3"] = f"{float(pr.get('3', 0)) + move.get('dy', 0):g}"
            for k, v in setv.items():
                if v is None:
                    pr.pop(k, None)
                else:
                    pr[k] = str(v)
            o["uid"] = self._next_uid  # re-created in the real mod
            self._next_uid += 1
            uids.append(o["uid"])
        return {"modified": len(uids), "uids": uids, "backup": self._backup_path()}

    def _list_objects(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        matched = self._select(p, False)
        off, lim = int(p.get("offset", 0)), int(p.get("limit", 500))
        return {"total": len(matched), "offset": off,
                "objects": [self._describe(o, bool(p.get("object_strings"))) for o in matched[off:off + lim]]}

    def _get_triggers(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        out = [self._describe(o, True) for o in self.objects
               if int(o["props"]["1"]) in TRIGGER_IDS.values()
               and (p.get("id") is None or int(o["props"]["1"]) == int(p["id"]))]
        return {"count": len(out), "triggers": out}

    def _move_camera(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        for k in ("x", "y", "zoom"):
            if p.get(k) is not None:
                self.camera[k] = float(p[k])
        return dict(self.camera)

    def capture(self, name: str) -> str:
        from .images import tiny_png
        path = self.directory / "captures" / f"{name}.png"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(tiny_png(*self.capture_size))
        return str(path)

    def _screenshot(self, p: dict[str, Any]) -> dict[str, Any]:
        cam = dict(self.camera)
        if self.state["scene"] == "LevelEditorLayer":
            r = p.get("region")
            if r:
                cam = {"x": (r["x1"] + r["x2"]) / 2, "y": (r["y1"] + r["y2"]) / 2, "zoom": 0.5}
            for k in ("x", "y", "zoom"):
                if p.get(k) is not None:
                    cam[k] = float(p[k])
            if not p.get("restore_camera", True):
                self.camera = dict(cam)
        path = self.capture(f"shot_{len(self.calls)}")
        w, h = self.capture_size
        return {"path": path, "width": w, "height": h, "camera": cam}

    def _playtest(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        action, mode = p.get("action", "status"), self.state["playtest"]
        if action == "start":
            if mode != "not":
                raise MockError("busy", "a playtest is already running")
            if p.get("from_x") is not None:
                name = self.state["level"]["name"]
                if not name.startswith(SAFE_PREFIX) and p.get("confirm_name") != name:
                    raise MockError("level_protected", "from_x places a temporary start position")
                self.temp_start_pos = float(p["from_x"])
            self.state["playtest"] = "playing"
        elif action == "stop":
            self.state["playtest"] = "not"
            self.temp_start_pos = None
        elif action == "pause":
            if mode != "playing":
                raise MockError("not_in_playtest", "nothing is playing")
            self.state["playtest"] = "paused"
        elif action == "resume":
            if mode != "paused":
                raise MockError("not_in_playtest", "playtest isn't paused")
            self.state["playtest"] = "playing"
        elif action != "status":
            raise MockError("invalid_params", "bad action")
        return {"playtest": self.state["playtest"], "temp_start_pos": self.temp_start_pos is not None}

    def _capture_frames(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        if self.state["playtest"] == "not":
            raise MockError("not_in_playtest", "start a playtest first")
        count = int(p.get("count", 10))
        if not 1 <= count <= 120:
            raise MockError("invalid_params", "count must be 1-120")
        job = f"job{len(self.jobs) + 1}"
        frames = [self.capture(f"{job}_frame_{i:03d}") for i in range(count)]
        self.jobs[job] = {"job": job, "state": "done", "error": None, "frames": frames}
        return {"job": job, "count": count, "interval_ms": p.get("interval_ms", 250)}

    def _job_status(self, p: dict[str, Any]) -> dict[str, Any]:
        if p.get("job") not in self.jobs:
            raise MockError("not_found", "no such job")
        return self.jobs[p["job"]]

    # level management ------------------------------------------------------------
    def _load(self, name: str, s: str, clear_history: bool = True) -> None:
        header, *objs = s.split(";")
        self.header = header
        self.state["level"]["name"] = name
        self.objects[:] = [self._new_object(o) for o in objs if o.strip()]
        if clear_history:
            self.undo_stack.clear()
            self.redo_stack.clear()

    def _save_level(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_write(p, "save_level")
        name = self.state["level"]["name"]
        self.saved_levels[name] = self.level_string()
        return {"name": name, "saved": True, "object_count": len(self.objects), "backup": self._backup_path()}

    def _prepare_to_leave(self) -> None:
        if self.state["scene"] == "LevelEditorLayer":
            if self.state["playtest"] != "not":
                raise MockError("busy", "playtest running")
            name = self.state["level"]["name"]
            if not name.startswith(SAFE_PREFIX):
                raise MockError("level_protected", f"the editor has '{name}' open; save and exit it yourself first")
            self.backups.append((name, "auto_save_before_switch", self.level_string()))
            self.saved_levels[name] = self.level_string()

    def _create_level(self, p: dict[str, Any]) -> dict[str, Any]:
        name = p["name"] if p["name"].startswith(SAFE_PREFIX) else SAFE_PREFIX + p["name"]
        if name in self.saved_levels:
            raise MockError("invalid_params", f"a level named '{name}' already exists")
        self._prepare_to_leave()
        self.saved_levels[name] = DEFAULT_HEADER + ";"
        self.state["scene"] = "LevelEditorLayer"
        self._load(name, self.saved_levels[name])
        self.state["level"]["song_id"] = int(p.get("song_id") or 0)
        return {"created": {"name": name, "song_id": self.state["level"]["song_id"], "audio_track": 0,
                            "claude": True}, "opening_editor": True}

    def _open_level(self, p: dict[str, Any]) -> dict[str, Any]:
        name = p["name"]
        if name not in self.saved_levels:
            raise MockError("not_found", f"no local level named '{name}'")
        if not name.startswith(SAFE_PREFIX) and p.get("confirm_name") != name:
            raise MockError("level_protected", f"'{name}' is not a CLAUDE level")
        self._prepare_to_leave()
        self.state["scene"] = "LevelEditorLayer"
        self._load(name, self.saved_levels[name])
        return {"opened": {"name": name, "claude": name.startswith(SAFE_PREFIX)}, "opening_editor": True}

    def _list_levels(self, p: dict[str, Any]) -> dict[str, Any]:
        names = [n for n in self.saved_levels if not p.get("claude_only") or n.startswith(SAFE_PREFIX)]
        return {"total": len(names), "levels": [{"name": n, "song_id": 0, "audio_track": 0,
                                                 "claude": n.startswith(SAFE_PREFIX)} for n in names]}

    def _get_music(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        sid = self.state["level"]["song_id"]
        return {"song_id": sid, "audio_track": 0, "custom_song": sid > 0, "song_ids": "", "offset": 0.0,
                "fade_in": False, "fade_out": False, "guideline_count": 0, "guidelines": []}

    def _undo(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_write(p, "undo")
        did = bool(self.undo_stack)
        if did:
            self.redo_stack.append(self.level_string())
            self._load(self.state["level"]["name"], self.undo_stack.pop(), False)
        return {"undone": did, "object_count": len(self.objects)}

    def _redo(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_write(p, "redo")
        did = bool(self.redo_stack)
        if did:
            self.undo_stack.append(self.level_string())
            self._load(self.state["level"]["name"], self.redo_stack.pop(), False)
        return {"redone": did, "object_count": len(self.objects)}

    def _backup_names(self, level: str) -> list[str]:
        return [f"{i:06d}_{reason}.txt" for i, (name, reason, _) in enumerate(self.backups) if name == level][::-1]

    def _list_backups(self, p: dict[str, Any]) -> dict[str, Any]:
        self._require_editor()
        names = self._backup_names(p.get("level") or self.state["level"]["name"])
        return {"dir": "mock", "total": len(names), "backups": [{"file": n, "bytes": 0} for n in names[:p.get("limit", 50)]]}

    def _restore_backup(self, p: dict[str, Any]) -> dict[str, Any]:
        f = p["file"]
        if "/" in f or "\\" in f or ".." in f:
            raise MockError("invalid_params", "bare file name only")
        level = p.get("level") or self.state["level"]["name"]
        if f not in self._backup_names(level):
            raise MockError("not_found", f"no backup '{f}'")
        content = self.backups[int(f.split("_")[0])][2]
        self._require_write(p, "before_restore")
        self._load(self.state["level"]["name"], content)
        return {"restored": f, "backup": self._backup_path(), "reloaded": True}

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
