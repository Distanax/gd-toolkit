"""Physics lab: run scripted inputs in real GD via gd-bridge autoplay and collect traces.

Usage (GD open with the bridge):  py levels/lab/lab.py cube
Results go to out/lab/<experiment>.json (trace rows: x, y, vy, mode, upside_down, on_ground).
"""
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "server" / "src"))

from gd_bridge_mcp.client import BridgeClient  # noqa: E402
from toolkit.gdlib import Level  # noqa: E402

LAB = "CLAUDE physics lab"
OUT = pathlib.Path(__file__).resolve().parents[2] / "out" / "lab"


def header() -> str:
    return Level("lab").level_string().split(";")[0]


def ensure_lab(b: BridgeClient) -> None:
    names = [lv["name"] for lv in b.call("list_levels", claude_only=True)["levels"]]
    st = b.call("status")
    if st.get("in_editor") and (st.get("level") or {}).get("name") == LAB:
        return
    if LAB in names:
        b.call("open_level", name=LAB)
    else:
        b.call("create_level", name="physics lab")


def run(b: BridgeClient, name: str, objects: list[str], inputs: list[list], seconds: float,
        from_x: float | None = None, trace_every: int = 1) -> dict:
    ensure_lab(b)
    b.call("set_level_string", level_string=header() + ";" + "".join(o + ";" for o in objects))
    b.call("autoplay", inputs=inputs, trace_every=trace_every, stop_on_death=True)
    b.call("playtest", action="start", from_x=from_x)
    time.sleep(seconds)
    st = b.call("autoplay_status", trace=True)
    b.call("playtest", action="stop")
    b.call("autoplay_clear")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(st), encoding="utf-8")
    print(name, "deaths", st["deaths"], "max_x", round(st["max_x"]), "trace", st["trace_points"],
          "events fired", st["next_event"], "/", st["events"])
    return st


EXPERIMENTS = {
    # one cube jump at x=300 on flat ground, then a spike at x=1200 with no input -> death expected
    "cube": dict(objects=["1,8,2,1215,3,15"], inputs=[[300, True], [310, False]], seconds=4.5),
    # portal at x=150; hold/release blocks to measure acceleration, caps and the corridor bounds
    "ship": dict(objects=["1,13,2,150,3,45"], inputs=[[300, True], [700, False], [1100, True], [1300, False],
                                                    [1500, True], [2200, False]], seconds=8.5),
    "ball": dict(objects=["1,47,2,150,3,45"], inputs=[[400, True], [405, False], [800, True], [805, False],
                                                    [1000, True], [1005, False]], seconds=4.5),
    "ufo": dict(objects=["1,111,2,150,3,45"], inputs=[[400, True], [405, False], [600, True], [605, False],
                                                    [650, True], [655, False], [700, True], [705, False]], seconds=4.5),
    "wave": dict(objects=["1,660,2,150,3,45"], inputs=[[300, True], [500, False], [700, True], [1300, False]],
                 seconds=5.5),
    "spider": dict(objects=["1,1331,2,150,3,45"], inputs=[[400, True], [405, False], [700, True], [705, False]],
                   seconds=4.0),
    "swing": dict(objects=["1,1933,2,150,3,45"], inputs=[[400, True], [405, False], [800, True], [805, False]],
                  seconds=4.0),
    # speed portals: same cube jump at 0.5x / 2x / 3x / 4x (speed portal at x=100)
    "cube05": dict(objects=["1,200,2,100,3,45"], inputs=[[300, True], [306, False]], seconds=3.0),
    "cube2": dict(objects=["1,202,2,100,3,45"], inputs=[[300, True], [306, False]], seconds=2.5),
    "cube3": dict(objects=["1,203,2,100,3,45"], inputs=[[300, True], [306, False]], seconds=2.0),
    "cube4": dict(objects=["1,1334,2,100,3,45"], inputs=[[300, True], [306, False]], seconds=2.0),
}

if __name__ == "__main__":
    b = BridgeClient()
    for name in sys.argv[1:] or ["cube"]:
        run(b, name, **EXPERIMENTS[name])
