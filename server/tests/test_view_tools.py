import json


def payload(result):
    """(image blocks, metadata dict) of an image-returning tool."""
    assert not result.is_error, result.content
    images = [c for c in result.content if type(c).__name__ == "ImageContent"]
    texts = [c for c in result.content if type(c).__name__ == "TextContent"]
    return images, json.loads(texts[0].text)


def test_screenshot_returns_png_downscaled(call_tool):
    images, meta = payload(call_tool("screenshot", region={"x1": 0, "y1": 0, "x2": 600, "y2": 300}))
    assert len(images) == 1 and images[0].mime_type == "image/png"
    assert (meta["captured_width"], meta["width"], meta["height"]) == (1920, 1280, 720)
    assert meta["camera"]["x"] == 300


def test_screenshot_full_size(call_tool):
    _, meta = payload(call_tool("screenshot", max_width=4000))
    assert (meta["width"], meta["height"]) == (1920, 1080)


def test_screenshot_restores_camera_by_default(call_tool, mock):
    before = dict(mock.camera)
    payload(call_tool("screenshot", x=900, y=100))
    assert mock.camera == before
    payload(call_tool("screenshot", x=900, y=100, restore_camera=False))
    assert mock.camera["x"] == 900


def test_move_camera_and_read(call_tool):
    r = call_tool("move_camera", x=450, zoom=0.5)
    assert r.structured_content["x"] == 450 and r.structured_content["zoom"] == 0.5
    assert call_tool("move_camera").structured_content["x"] == 450
