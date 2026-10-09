"""Turning capture files written by the mod into MCP images."""
from __future__ import annotations

import io
from pathlib import Path

from mcp.server.mcpserver import Image
from PIL import Image as PILImage


def load_png(path: str | Path, max_width: int | None) -> tuple[Image, int, int]:
    """Read a PNG the mod wrote (same machine) and return (MCP image, width, height), downscaled to
    max_width if wider. Raises FileNotFoundError if the mod's file isn't there."""
    data = Path(path).read_bytes()
    with PILImage.open(io.BytesIO(data)) as im:
        w, h = im.size
        if max_width and w > max_width:
            nh = max(1, round(h * max_width / w))
            out = io.BytesIO()
            im.convert("RGB").resize((max_width, nh), PILImage.LANCZOS).save(out, format="PNG", optimize=True)
            return Image(data=out.getvalue(), format="png"), max_width, nh
    return Image(data=data, format="png"), w, h


def tiny_png(width: int = 8, height: int = 6, rgb: tuple[int, int, int] = (40, 20, 70)) -> bytes:
    """A solid-colour PNG (used by the mock bridge)."""
    out = io.BytesIO()
    PILImage.new("RGB", (width, height), rgb).save(out, format="PNG")
    return out.getvalue()
