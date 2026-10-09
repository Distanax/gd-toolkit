import pytest

from gd_bridge_mcp.objects import encode, encode_select, encode_set, parse


def data(result):
    assert not result.is_error, result.content
    return result.structured_content


def error_text(result):
    assert result.is_error, result.structured_content
    return " ".join(getattr(c, "text", "") for c in result.content)


# ---- objects.py ---------------------------------------------------------------------------

def test_encode_friendly_dict():
    s = encode({"id": "spike", "x": 45, "y": 15, "rotation": 90, "groups": [3, 7], "keys": {"36": 1}})
    assert parse(s) == {"1": "8", "2": "45", "3": "15", "6": "90", "57": "3.7", "36": "1"}


def test_encode_trigger_names():
    p = parse(encode({"id": "move_trigger", "x": 0, "y": 0, "move_x": 30, "duration": 0.5, "target_group": 2}))
    assert p["1"] == "901" and p["28"] == "30" and p["10"] == "0.5" and p["51"] == "2"


def test_encode_raw_string_passthrough_and_validation():
    assert encode("1,1,2,15,3,15;") == "1,1,2,15,3,15"
    for bad in ("2,15,3,15", "1,1;1,8", {"id": "nope", "x": 0, "y": 0}, {"x": 1, "y": 2}):
        with pytest.raises(ValueError):
            encode(bad)


def test_encode_set_and_select():
    assert encode_set({"rotation": 45, "groups": [1, 2], "64": None}) == {"6": "45", "57": "1.2", "64": None}
    with pytest.raises(ValueError):
        encode_set({"1": 9})
    assert encode_select({"ids": ["spike", 1], "groups": 4}) == {"ids": [8, 1], "groups": [4]}


# ---- tools against the mock bridge ----------------------------------------------------------

def test_add_list_modify_remove_roundtrip(call_tool, mock):
    added = data(call_tool("add_objects", objects=[
        {"id": "block", "x": 15, "y": 15},
        {"id": "spike", "x": 45, "y": 15},
        "1,36,2,105,3,75",
    ]))
    assert added["added"] == 3 and len(added["uids"]) == 3
    assert mock.backups[-1][1] == "add_objects"

    spikes = data(call_tool("list_objects", select={"ids": ["spike"]}))
    assert spikes["total"] == 1 and spikes["objects"][0]["x"] == 45

    mod = data(call_tool("modify_objects", select={"ids": ["spike"]}, set={"rotation": 180}, move={"dx": 30}))
    assert mod["modified"] == 1
    s = data(call_tool("list_objects", select={"ids": [8]}, object_strings=True))["objects"][0]
    assert s["x"] == 75 and parse(s["object_string"])["6"] == "180"

    gone = data(call_tool("remove_objects", select={"region": {"x1": 0, "y1": 0, "x2": 30, "y2": 30}}))
    assert gone["removed"] == 1
    assert data(call_tool("list_objects"))["total"] == 2


def test_empty_selector_refused(call_tool):
    assert "selector" in error_text(call_tool("remove_objects", select={}))


def test_unknown_name_is_a_tool_error(call_tool):
    assert "unknown object name" in error_text(call_tool("add_objects", objects=[{"id": "banana", "x": 0, "y": 0}]))


def test_protected_level_needs_confirm_name(call_tool, mock):
    mock.state["level"]["name"] = "My Real Level"
    msg = error_text(call_tool("add_objects", objects=["1,1,2,15,3,15"]))
    assert "level_protected" in msg
    assert mock.objects == []
    ok = data(call_tool("add_objects", objects=["1,1,2,15,3,15"], confirm_name="My Real Level"))
    assert ok["added"] == 1


def test_level_string_roundtrip(call_tool, mock):
    data(call_tool("add_objects", objects=["1,1,2,15,3,15"]))
    ls = data(call_tool("get_level_string"))
    assert ls["object_count"] == 1 and ls["level_string"].endswith("1,1,2,15,3,15;")
    new = "kA2,0;1,8,2,45,3,15;1,8,2,75,3,15;"
    r = data(call_tool("set_level_string", level_string=new))
    assert r["reloaded"] and data(call_tool("get_level_string"))["object_count"] == 2
    assert mock.backups[-1][2].endswith("1,1,2,15,3,15;")  # previous version was backed up


def test_get_triggers_by_name(call_tool):
    data(call_tool("add_objects", objects=[
        {"id": "move_trigger", "x": 0, "y": 0, "target_group": 1},
        {"id": "color_trigger", "x": 30, "y": 0},
        {"id": "block", "x": 60, "y": 15},
    ]))
    t = data(call_tool("get_triggers", type="move"))
    assert t["count"] == 1 and parse(t["triggers"][0]["object_string"])["51"] == "1"
    assert data(call_tool("get_triggers"))["count"] == 2


def test_not_in_editor(call_tool, mock):
    mock.state["scene"] = "MenuLayer"
    assert "not_in_editor" in error_text(call_tool("list_objects"))
