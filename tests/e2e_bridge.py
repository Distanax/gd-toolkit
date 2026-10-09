"""End-to-end test of gd-bridge: MCP tools -> bridge client -> GD Bridge mod -> Geometry Dash.

Run with GD open (any screen) and the mod installed:
    py tests/e2e_bridge.py
Checks the whole chain on a level named "CLAUDE test" (created if missing, emptied if it exists):
add blocks, spikes, an orb and a move trigger, read them back, screenshot the editor, playtest 3 s
with frame capture, save. Writes out/e2e/<timestamp>/ (report.json, screenshot.png, frame_*.png).

    py tests/e2e_bridge.py --mock    # same script against the in-process mock bridge (no GD needed)

Needs the MCP server package: py -m pip install "git+https://github.com/Distanax/gd-toolkit#subdirectory=server"
(or run from a checkout with server/src on the path, which this script adds automatically).
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "server" / "src"))  # use this checkout's server if not pip-installed

from mcp import Client  # noqa: E402

from gd_bridge_mcp.client import BridgeClient  # noqa: E402
from gd_bridge_mcp.server import build_server  # noqa: E402

LEVEL = "CLAUDE test"

# Layout (GD units; 30 = 1 block, ground row y = 15): a short floor of blocks, two spikes, a yellow orb
# above the gap, and a move trigger that slides one marked block (group 1) up by two blocks.
OBJECTS = (
    [{"id": "block", "x": x, "y": 15} for x in range(315, 615, 30)]          # 10 blocks
    + [{"id": "spike", "x": 705, "y": 15}, {"id": "spike", "x": 735, "y": 15}]
    + [{"id": "yellow_orb", "x": 720, "y": 105}]
    + [{"id": "block", "x": 885, "y": 75, "groups": [1]}]                     # the moving block
    + [{"id": "move_trigger", "x": 345, "y": 165, "target_group": 1, "move_x": 0, "move_y": 60,
        "duration": 1.0}]
)
EXPECTED = {1: 11, 8: 2, 36: 1, 901: 1}


class Steps:
    def __init__(self, out: Path):
        self.out = out
        self.results: list[dict] = []

    def record(self, name: str, ok: bool, detail: object = None) -> None:
        self.results.append({"step": name, "ok": ok, "detail": detail})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail is not None and not ok else ""))
        sys.stdout.flush()


def content_json(result) -> dict:
    """structured_content for JSON tools, else the last text block parsed as JSON (image tools)."""
    if result.structured_content is not None:
        return result.structured_content
    texts = [c for c in result.content if type(c).__name__ == "TextContent"]
    return json.loads(texts[-1].text)


def tool_error(result) -> str | None:
    if not result.is_error:
        return None
    return " ".join(getattr(c, "text", "") for c in result.content)


def save_images(result, out: Path, stem: str) -> list[str]:
    paths = []
    for i, c in enumerate(c for c in result.content if type(c).__name__ == "ImageContent"):
        p = out / f"{stem}_{i:03d}.png"
        p.write_bytes(base64.b64decode(c.data))
        paths.append(p.name)
    return paths


async def run(client: BridgeClient, out: Path, steps: Steps, settle: float) -> None:
    async with Client(build_server(client)) as c:
        async def call(tool: str, /, **args):
            r = await c.call_tool(tool, args)
            err = tool_error(r)
            if err:
                raise RuntimeError(f"{tool}: {err}")
            return r

        # 1. GD reachable
        st = content_json(await call("status"))
        steps.record("status: GD + mod reachable", st.get("running") is True, st)
        if not st.get("running"):
            return
        steps.record("versions", True, st.get("versions"))

        # 2. open or create "CLAUDE test"
        levels = content_json(await call("list_levels", claude_only=True))["levels"]
        if any(lv["name"] == LEVEL for lv in levels):
            if not (st.get("in_editor") and (st.get("level") or {}).get("name") == LEVEL):
                await call("open_level", name=LEVEL)
            how = "opened existing"
        else:
            await call("create_level", name=LEVEL)
            how = "created"
        deadline = time.monotonic() + 20
        while True:
            st = content_json(await call("status"))
            if st.get("in_editor") and (st.get("level") or {}).get("name") == LEVEL:
                break
            if time.monotonic() > deadline:
                raise RuntimeError(f"editor did not open {LEVEL!r}: {st}")
            await asyncio.sleep(0.5)
        await asyncio.sleep(settle)  # let the editor finish its scene transition
        steps.record(f"level '{LEVEL}' {how} and open in the editor", True)

        # 3. start from an empty level
        if st["level"]["object_count"]:
            await call("remove_objects", select={"all": True})
        n = content_json(await call("list_objects"))["total"]
        steps.record("level emptied", n == 0, n)

        # 4. add objects
        added = content_json(await call("add_objects", objects=OBJECTS))
        steps.record("add_objects", added["added"] == len(OBJECTS), added)

        # 5. read back
        listed = content_json(await call("list_objects", limit=5000))
        counts: dict[int, int] = {}
        for o in listed["objects"]:
            counts[o["id"]] = counts.get(o["id"], 0) + 1
        steps.record("list_objects counts match", counts == EXPECTED, {"got": counts, "want": EXPECTED})
        orb = [o for o in listed["objects"] if o["id"] == 36]
        steps.record("orb position", bool(orb) and (orb[0]["x"], orb[0]["y"]) == (720, 105), orb)
        trig = content_json(await call("get_triggers", type="move"))
        fields = dict(zip(*[iter(trig["triggers"][0]["object_string"].split(","))] * 2)) if trig["count"] else {}
        steps.record("move trigger settings (target group 1, move_y 60)",
                     fields.get("51") == "1" and fields.get("29") == "60", fields)
        level_string = content_json(await call("get_level_string"))["level_string"]
        (out / "level_string.txt").write_text(level_string, encoding="utf-8")
        steps.record("get_level_string", level_string.count(";") >= len(OBJECTS) + 1, len(level_string))

        # 6. screenshot of the layout
        shot = await call("screenshot", region={"x1": 270, "y1": 0, "x2": 960, "y2": 240})
        saved = save_images(shot, out, "screenshot")
        meta = content_json(shot)
        steps.record("screenshot", len(saved) == 1 and meta["width"] > 0, {"files": saved, **meta})

        # 7. playtest 3 s with frame capture
        await call("playtest", action="start")
        frames = await call("capture_frames", count=6, interval_ms=500)
        await call("playtest", action="stop")
        fsaved = save_images(frames, out, "frame")
        fmeta = content_json(frames)
        steps.record("playtest 3 s + capture_frames", fmeta["state"] == "done" and len(fsaved) == 6,
                     {"files": fsaved, "state": fmeta["state"], "error": fmeta.get("error")})
        st = content_json(await call("status"))
        steps.record("playtest stopped", st.get("playtest") == "not", st.get("playtest"))

        # 8. save
        saved_level = content_json(await call("save_level"))
        steps.record("save_level", saved_level.get("saved") is True, saved_level)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mock", action="store_true", help="run against the mock bridge instead of GD")
    ap.add_argument("--settle", type=float, default=2.0, help="seconds to wait after the editor opens")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPO / "out" / "e2e" / (stamp + ("_mock" if args.mock else ""))
    out.mkdir(parents=True, exist_ok=True)
    steps = Steps(out)
    print(f"gd-bridge end-to-end test -> {out}")

    try:
        if args.mock:
            from gd_bridge_mcp.mock import MockBridge
            with MockBridge() as mock:
                mock.state["scene"] = "MenuLayer"
                asyncio.run(run(BridgeClient(mock.discovery_path), out, steps, 0))
        else:
            asyncio.run(run(BridgeClient(), out, steps, args.settle))
    except Exception as e:  # report, don't hide
        steps.record("unexpected error", False, f"{type(e).__name__}: {e}")
        traceback.print_exc()

    ok = bool(steps.results) and all(s["ok"] for s in steps.results)
    report = {"ok": ok, "when": stamp, "mock": args.mock, "steps": steps.results}
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{'ALL PASSED' if ok else 'FAILED'} - report: {out / 'report.json'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
