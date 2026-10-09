"""Friendly object descriptions <-> GD object strings.

GD stores an object as comma-separated key,value pairs: "1,8,2,45,3,15" = object ID 8 (spike) at
x=45, y=15. Keys follow Wyliemaster/gddocs (level-string.md). IDs and conventions match
toolkit/gdlib.py: 30 units = 1 block, objects are placed by their centre, ground row y = 15.
"""
from __future__ import annotations

from typing import Any

# Common object IDs by name (same values as toolkit/gdlib.py).
OBJECT_IDS: dict[str, int] = {
    "block": 1, "spike": 8, "half_spike": 39,
    "yellow_pad": 35, "pink_pad": 140, "red_pad": 1332, "blue_pad": 67,
    "yellow_orb": 36, "pink_orb": 141, "red_orb": 1333, "blue_orb": 84, "green_orb": 1022,
    "black_orb": 1330, "dash_orb": 1704,
    "cube_portal": 12, "ship_portal": 13, "ball_portal": 47, "ufo_portal": 111, "wave_portal": 660,
    "robot_portal": 745, "spider_portal": 1331, "swing_portal": 1933,
    "gravity_down_portal": 10, "gravity_up_portal": 11, "mirror_on_portal": 45, "mirror_off_portal": 46,
    "mini_portal": 101, "normal_size_portal": 99, "dual_on_portal": 286, "dual_off_portal": 287,
    "speed_0.5x": 200, "speed_1x": 201, "speed_2x": 202, "speed_3x": 203, "speed_4x": 1334,
    "text": 914, "start_pos": 31,
    # triggers
    "color_trigger": 899, "move_trigger": 901, "pulse_trigger": 1006, "alpha_trigger": 1007,
    "toggle_trigger": 1049, "spawn_trigger": 1268, "rotate_trigger": 1346, "follow_trigger": 1347,
    "shake_trigger": 1520, "stop_trigger": 1616, "zoom_trigger": 1913,
}

TRIGGER_IDS = {k[: -len("_trigger")]: v for k, v in OBJECT_IDS.items() if k.endswith("_trigger")}

# Friendly property names -> GD object keys.
PROP_KEYS: dict[str, str] = {
    "x": "2", "y": "3", "flip_x": "4", "flip_y": "5", "rotation": "6",
    "editor_layer": "20", "color": "21", "detail_color": "22", "z_layer": "24", "z_order": "25",
    "scale": "32", "groups": "57", "dont_fade": "64", "dont_enter": "67",
    "scale_x": "128", "scale_y": "129",
    # common trigger settings (move trigger): duration, x/y offset (units), easing, target group
    "duration": "10", "move_x": "28", "move_y": "29", "easing": "30", "target_group": "51",
    "touch_triggered": "11", "spawn_triggered": "62", "multi_trigger": "87",
}


def object_id(value: int | str) -> int:
    if isinstance(value, bool):
        raise ValueError("object id can't be a boolean")
    if isinstance(value, int):
        return value
    v = str(value).strip().lower().replace(" ", "_")
    if v.isdigit():
        return int(v)
    if v in OBJECT_IDS:
        return OBJECT_IDS[v]
    if v + "_trigger" in OBJECT_IDS:
        return OBJECT_IDS[v + "_trigger"]
    raise ValueError(f"unknown object name {value!r}; use a numeric ID or one of: {', '.join(sorted(OBJECT_IDS))}")


def fmt_value(v: Any) -> str:
    """Format a value the way GD writes it (same rules as toolkit/gdlib.py _fmt)."""
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s if s not in ("", "-0") else "0"
    if isinstance(v, (list, tuple)):
        return ".".join(fmt_value(g) for g in v)
    return str(v)


def key_of(name: str) -> str:
    """A GD key from a friendly name ('rotation') or a raw key ('6')."""
    name = str(name)
    if name.isdigit():
        return name
    if name in PROP_KEYS:
        return PROP_KEYS[name]
    raise ValueError(f"unknown property {name!r}; use a GD key number or one of: {', '.join(sorted(PROP_KEYS))}")


def encode(obj: str | dict[str, Any]) -> str:
    """One object -> GD object string. Accepts a raw string ("1,8,2,45,3,15") or a dict:
    {"id": "spike" | 8, "x": 45, "y": 15, "rotation": 90, "groups": [1, 2], "keys": {"36": 1}}."""
    if isinstance(obj, str):
        s = obj.strip().rstrip(";")
        if not s.startswith("1,") or ";" in s:
            raise ValueError(f"bad object string {obj!r}: must start with '1,<id>' and contain no ';'")
        return s
    if not isinstance(obj, dict):
        raise ValueError("each object must be an object string or a dict with id/x/y")
    if "id" not in obj or "x" not in obj or "y" not in obj:
        raise ValueError(f"object {obj!r} needs id, x and y")
    props: dict[str, str] = {"1": str(object_id(obj["id"])), "2": fmt_value(float(obj["x"])),
                             "3": fmt_value(float(obj["y"]))}
    for name, value in obj.items():
        if name in ("id", "x", "y", "keys"):
            continue
        props[key_of(name)] = fmt_value(value)
    for k, value in (obj.get("keys") or {}).items():
        props[str(k)] = fmt_value(value)
    return ",".join(f"{k},{v}" for k, v in props.items())


def parse(s: str) -> dict[str, str]:
    """GD object string -> {key: value} (strings, order kept)."""
    parts = s.strip().rstrip(";").split(",")
    return {parts[i]: parts[i + 1] for i in range(0, len(parts) - 1, 2)}


def encode_set(values: dict[str, Any]) -> dict[str, Any]:
    """Friendly `set` dict for modify_objects -> GD keys (None removes a key)."""
    out: dict[str, Any] = {}
    for name, value in values.items():
        k = key_of(name)
        if k == "1":
            raise ValueError("the object ID (key 1) can't be changed; remove and add instead")
        out[k] = None if value is None else fmt_value(value)
    return out


def encode_select(select: dict[str, Any] | None) -> dict[str, Any] | None:
    """Selector with names allowed in `ids` ("spike") -> wire form."""
    if select is None:
        return None
    sel = dict(select)
    if "ids" in sel and sel["ids"] is not None:
        ids = sel["ids"] if isinstance(sel["ids"], list) else [sel["ids"]]
        sel["ids"] = [object_id(i) for i in ids]
    for k in ("uids", "groups"):
        if k in sel and sel[k] is not None and not isinstance(sel[k], list):
            sel[k] = [sel[k]]
    return sel
