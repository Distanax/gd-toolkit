import json


def error_text(result):
    assert result.is_error, result.content
    return " ".join(getattr(c, "text", "") for c in result.content)


def test_playtest_lifecycle(call_tool, mock):
    assert call_tool("playtest").structured_content["playtest"] == "not"
    assert call_tool("playtest", action="start").structured_content["playtest"] == "playing"
    assert "busy" in error_text(call_tool("playtest", action="start"))
    assert call_tool("playtest", action="pause").structured_content["playtest"] == "paused"
    assert call_tool("playtest", action="resume").structured_content["playtest"] == "playing"
    assert call_tool("playtest", action="stop").structured_content["playtest"] == "not"


def test_playtest_from_x_respects_safety(call_tool, mock):
    mock.state["level"]["name"] = "Someone Else"
    assert "level_protected" in error_text(call_tool("playtest", action="start", from_x=900))
    r = call_tool("playtest", action="start", from_x=900, confirm_name="Someone Else")
    assert r.structured_content["temp_start_pos"] is True
    assert call_tool("playtest", action="stop").structured_content["temp_start_pos"] is False


def test_capture_frames_needs_playtest(call_tool):
    assert "not_in_playtest" in error_text(call_tool("capture_frames", count=3))


def test_capture_frames_returns_images_in_order(call_tool, mock):
    call_tool("playtest", action="start")
    r = call_tool("capture_frames", count=4, interval_ms=100)
    assert not r.is_error, r.content
    images = [c for c in r.content if type(c).__name__ == "ImageContent"]
    meta = json.loads([c for c in r.content if type(c).__name__ == "TextContent"][-1].text)
    assert len(images) == 4 and meta["state"] == "done"
    assert meta["size"] == [640, 360]  # 1920x1080 mock frames downscaled
    assert meta["frames"] == sorted(meta["frames"])
