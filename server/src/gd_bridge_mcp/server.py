"""The MCP server: tools that forward to the GD Bridge mod."""
from __future__ import annotations

import time
from typing import Any, Callable

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import __version__
from .client import BridgeClient, BridgeError
from .images import load_png
from .objects import encode, encode_select, encode_set, object_id

INSTRUCTIONS = """\
Controls the Geometry Dash level editor on this PC through the GD Bridge Geode mod.
Safety: only levels whose name starts with "CLAUDE " can be modified unless a tool call passes
confirm_name=<exact level name>; every write is backed up first. Coordinates are GD units
(30 units = 1 block, ground row y = 15). Call `status` first to see what is open."""

def build_server(client: BridgeClient | None = None) -> MCPServer:
    """Create the MCP server. `client` is injectable for tests (mock bridge)."""
    bridge = client or BridgeClient()
    mcp = MCPServer("gd-bridge", version=__version__, instructions=INSTRUCTIONS)

    @mcp.tool()
    def status() -> dict[str, Any]:
        """Is Geometry Dash running with the bridge mod, which scene is showing, whether the editor is
        open, and the open level's name, ID, song and object count. Call this first."""
        try:
            result = bridge.call("status")
        except BridgeError as e:
            if e.code == "not_running":
                return {"running": False, "message": e.message}
            raise ToolError(f"[{e.code}] {e.message}") from None
        return {"running": True, **result}

    def call(method: str, **params: Any) -> Any:
        try:
            return bridge.call(method, **params)
        except BridgeError as e:
            raise ToolError(f"[{e.code}] {e.message}") from None

    def friendly(fn: Callable[[], Any]) -> Any:
        """Turn bad friendly arguments (unknown names, malformed strings) into tool errors."""
        try:
            return fn()
        except ValueError as e:
            raise ToolError(f"[invalid_params] {e}") from None

    # ---- whole level -----------------------------------------------------------------
    @mcp.tool()
    def get_level_string() -> dict[str, Any]:
        """The open editor level as GD's raw level string ("<header>;<object>;<object>;..."), plus its
        name and object count. Parse it with toolkit/gdparse.py-style splitting if needed."""
        return call("get_level_string")

    @mcp.tool()
    def set_level_string(level_string: str, confirm_name: str | None = None) -> dict[str, Any]:
        """Replace the whole open level (header and all objects) with `level_string` (raw, uncompressed,
        e.g. from toolkit/gdlib.py Level.level_string()). The editor reloads; undo history is lost but the
        previous version is backed up first (path returned). Only allowed on levels named "CLAUDE ..."
        unless confirm_name is the exact level name."""
        return call("set_level_string", level_string=level_string, confirm_name=confirm_name)

    # ---- objects -------------------------------------------------------------------------
    @mcp.tool()
    def add_objects(objects: list[str | dict[str, Any]], confirm_name: str | None = None) -> dict[str, Any]:
        """Add objects to the open level. Each item is either a GD object string ("1,8,2,45,3,15") or a
        dict: {"id": "spike" | 8, "x": 45, "y": 15, "rotation": 90, "scale": 1.5, "groups": [1, 2],
        "color": 3, "keys": {"<gd key>": value}}. Names: block, spike, yellow_orb, yellow_pad,
        ship_portal, speed_2x, move_trigger, ... (see CLAUDE.md). Trigger settings go in friendly names
        (duration, move_x, move_y, easing, target_group) or raw keys. Coordinates: GD units, object
        centre, 30 = 1 block, ground row y = 15. Returns the new objects' uids."""
        strings = friendly(lambda: [encode(o) for o in objects])
        return call("add_objects", objects=strings, confirm_name=confirm_name)

    @mcp.tool()
    def remove_objects(select: dict[str, Any], confirm_name: str | None = None) -> dict[str, Any]:
        """Remove objects matching `select` (criteria are ANDed): {"uids": [..], "ids": ["spike", 1],
        "groups": [..], "region": {"x1","y1","x2","y2"}, "triggers": true, "all": true}. An empty
        selector is refused unless all=true."""
        sel = friendly(lambda: encode_select(select))
        return call("remove_objects", select=sel, confirm_name=confirm_name)

    @mcp.tool()
    def modify_objects(select: dict[str, Any], set: dict[str, Any] | None = None,
                       move: dict[str, float] | None = None, confirm_name: str | None = None) -> dict[str, Any]:
        """Change objects matching `select` (same form as remove_objects). `set` maps property names
        (x, y, rotation, scale, groups, color, duration, move_x, target_group, ...) or raw GD keys
        ("6") to new values; null removes the key. `move` = {"dx": .., "dy": ..} shifts them. Objects
        are re-created, so their uids change (new uids returned in order)."""
        sel = friendly(lambda: encode_select(select))
        enc = friendly(lambda: encode_set(set)) if set else None
        return call("modify_objects", select=sel, set=enc, move=move, confirm_name=confirm_name)

    @mcp.tool()
    def list_objects(select: dict[str, Any] | None = None, offset: int = 0, limit: int = 500,
                     object_strings: bool = False) -> dict[str, Any]:
        """List objects in the open level (uid, id, x, y, rotation, scale, groups, trigger), optionally
        filtered by `select` (same form as remove_objects) and paged with offset/limit (max 5000).
        object_strings=true adds each object's full GD string."""
        sel = friendly(lambda: encode_select(select))
        return call("list_objects", select=sel, offset=offset, limit=limit, object_strings=object_strings)

    @mcp.tool()
    def get_triggers(type: str | int | None = None) -> dict[str, Any]:
        """All triggers in the open level with their full object strings (all settings). `type` filters
        by trigger name ("move", "color", "spawn", ...) or object ID (901)."""
        tid = friendly(lambda: object_id(type)) if type is not None else None
        return call("get_triggers", id=tid)

    # ---- camera + screenshots ---------------------------------------------------------------
    @mcp.tool()
    def move_camera(x: float | None = None, y: float | None = None, zoom: float | None = None) -> dict[str, Any]:
        """Point the editor camera: x/y = GD units at the centre of the view, zoom = editor zoom (1 is
        default; the editor clamps it). Omitted values stay as they are. Returns the resulting camera.
        Call with no arguments to just read the camera."""
        if x is None and y is None and zoom is None:
            return call("get_camera")
        return call("move_camera", x=x, y=y, zoom=zoom)

    # structured_output=False: the result is content blocks (image + JSON text), not a JSON value.
    @mcp.tool(structured_output=False)
    def screenshot(x: float | None = None, y: float | None = None, zoom: float | None = None,
                   region: dict[str, float] | None = None, hide_ui: bool = True,
                   restore_camera: bool = True, max_width: int = 1280) -> list[Any]:
        """Screenshot of the game window as a PNG image. In the editor you can aim it first: x/y/zoom
        (camera centre in GD units) or region {"x1","y1","x2","y2"} to fit an area; the camera goes back
        afterwards unless restore_camera=false. hide_ui hides the editor toolbars for the shot. Images
        wider than max_width are downscaled. Also works outside the editor (captures what's on screen)."""
        shot = call("screenshot", x=x, y=y, zoom=zoom, region=region, hide_ui=hide_ui,
                    restore_camera=restore_camera)
        img, w, h = load_png(shot["path"], max_width)
        return [img, {"path": shot["path"], "width": w, "height": h,
                      "captured_width": shot["width"], "captured_height": shot["height"],
                      "camera": shot.get("camera")}]

    # ---- playtest -------------------------------------------------------------------------
    @mcp.tool()
    def playtest(action: str = "status", from_x: float | None = None, from_y: float | None = None,
                 confirm_name: str | None = None) -> dict[str, Any]:
        """Editor playtest. action: "start" | "stop" | "pause" | "resume" | "status". start with from_x
        (GD units; from_y defaults to 15) starts from that x by placing a temporary start position that
        is removed again when the playtest stops (counts as an edit: CLAUDE-named levels or
        confirm_name). The start position uses default settings (cube, 1x), so starting inside a ship or
        2x section plays it as cube 1x."""
        return call("playtest", action=action, from_x=from_x, from_y=from_y, confirm_name=confirm_name)

    @mcp.tool(structured_output=False)
    def capture_frames(count: int = 10, interval_ms: int = 250, hide_ui: bool = True,
                       max_width: int = 640) -> list[Any]:
        """Capture `count` frames every `interval_ms` while a playtest runs (start one with playtest first)
        and return them as images in order, so you can see gameplay in motion. Frames are downscaled to
        max_width. Waits until all frames are written (about count * interval_ms)."""
        job = call("capture_frames", count=count, interval_ms=interval_ms, hide_ui=hide_ui)["job"]
        deadline = time.monotonic() + count * interval_ms / 1000 + 20
        status = call("job_status", job=job)
        while status["state"] == "running" and time.monotonic() < deadline:
            time.sleep(0.25)
            status = call("job_status", job=job)
        if status["state"] == "running":
            raise ToolError(f"[timeout] frame capture {job} still running after {deadline:.0f}s")
        out: list[Any] = []
        sizes = []
        for path in status["frames"]:
            img, w, h = load_png(path, max_width)
            out.append(img)
            sizes.append((w, h))
        out.append({"job": job, "state": status["state"], "error": status.get("error"),
                    "frames": status["frames"], "size": sizes[0] if sizes else None,
                    "interval_ms": interval_ms})
        return out

    # ---- level management + music ----------------------------------------------------------
    @mcp.tool()
    def save_level(confirm_name: str | None = None) -> dict[str, Any]:
        """Save the open editor level to GD's level list and to disk (backup first)."""
        return call("save_level", confirm_name=confirm_name)

    @mcp.tool()
    def create_level(name: str, song_id: int | None = None, audio_track: int | None = None) -> dict[str, Any]:
        """Create a new local level and open it in the editor. The name always gets the "CLAUDE " prefix.
        song_id = Newgrounds/custom song ID, audio_track = official song index. Refused while you're
        editing one of your own (non-CLAUDE) levels, so unsaved work is never discarded; a CLAUDE level
        that is open gets backed up and saved first. Returns once the new level is open in the editor."""
        return call("create_level", name=name, song_id=song_id, audio_track=audio_track)

    @mcp.tool()
    def open_level(name: str, confirm_name: str | None = None) -> dict[str, Any]:
        """Open a local level in the editor by exact name (see list_levels). Levels not named
        "CLAUDE ..." need confirm_name=<exact name>. Same rules as create_level about leaving the editor."""
        return call("open_level", name=name, confirm_name=confirm_name)

    @mcp.tool()
    def list_levels(claude_only: bool = False, limit: int = 200) -> dict[str, Any]:
        """The local (created) levels: name, song, and whether it's a CLAUDE level."""
        return call("list_levels", claude_only=claude_only, limit=limit)

    @mcp.tool()
    def get_music() -> dict[str, Any]:
        """Music of the open level: song_id (custom) or audio_track (official), song offset, fade in/out,
        and the guidelines (time + colour markers, usually placed on beats)."""
        return call("get_music")

    # ---- undo / redo / backups ---------------------------------------------------------------
    @mcp.tool()
    def undo(confirm_name: str | None = None) -> dict[str, Any]:
        """Undo the last editor action in GD's own undo history. Use it for edits made by hand in GD,
        not for edits made through these tools: GD records the objects a tool removes but not the ones
        it creates, so undoing a tool edit leaves duplicates. To revert a tool edit use list_backups +
        restore_backup; every write tool makes a backup first."""
        return call("undo", confirm_name=confirm_name)

    @mcp.tool()
    def redo(confirm_name: str | None = None) -> dict[str, Any]:
        """Redo the last undone editor action (GD's own history; see undo)."""
        return call("redo", confirm_name=confirm_name)

    @mcp.tool()
    def list_backups(level: str | None = None, limit: int = 50) -> dict[str, Any]:
        """Backups of a level (default: the open one), newest first. Every write tool creates one."""
        return call("list_backups", level=level, limit=limit)

    @mcp.tool()
    def restore_backup(file: str, level: str | None = None, confirm_name: str | None = None) -> dict[str, Any]:
        """Replace the open level with a backup (file name from list_backups; `level` picks another
        level's backup folder). The current state is backed up first, so a restore can be undone the
        same way."""
        return call("restore_backup", file=file, level=level, confirm_name=confirm_name)

    # ---- autoplay (scripted inputs during a playtest) ---------------------------------------
    @mcp.tool()
    def autoplay(inputs: list[list[Any]], stop_on_death: bool = True, trace_every: int = 0) -> dict[str, Any]:
        """Arm a scripted input run for the next editor playtest: inputs = [[x, press], ...] where x is a
        level-string x and press is true (press/hold) or false (release). Inputs fire on the physics step
        the player reaches x. Then call playtest(action="start") and later autoplay_status. Proves a planned
        input sequence clears the level in the real engine; it does not prove fairness or fun."""
        return call("autoplay", inputs=inputs, stop_on_death=stop_on_death, trace_every=trace_every)

    @mcp.tool()
    def autoplay_status(trace: bool = False) -> dict[str, Any]:
        """Result of the armed autoplay run: deaths [{x, y}], max_x reached, events fired; trace=true adds
        [x, y, vy, mode, upside_down, on_ground] samples (if trace_every was set)."""
        return call("autoplay_status", trace=trace)

    mcp.bridge = bridge  # type: ignore[attr-defined]  (handy in tests)
    return mcp


def main() -> None:
    build_server().run(transport="stdio")
