import json

from gd_bridge_mcp.client import BridgeClient
from gd_bridge_mcp.server import build_server


def data(result):
    """Structured content of a successful tool call."""
    assert not result.is_error, result.content
    return result.structured_content


def test_status_in_editor(call_tool):
    s = data(call_tool("status"))
    assert s["running"] is True
    assert s["in_editor"] is True
    assert s["level"]["name"] == "CLAUDE test"


def test_status_when_gd_not_running(tmp_path):
    import asyncio
    from mcp import Client

    server = build_server(BridgeClient(tmp_path / "missing.json"))

    async def run():
        async with Client(server) as c:
            return await c.call_tool("status", {})

    s = data(asyncio.run(run()))
    assert s["running"] is False
    assert "GD Bridge" in s["message"]
