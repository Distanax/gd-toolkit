import asyncio

import pytest

from gd_bridge_mcp.client import BridgeClient
from gd_bridge_mcp.mock import MockBridge
from gd_bridge_mcp.server import build_server


@pytest.fixture
def mock():
    with MockBridge() as m:
        yield m


@pytest.fixture
def client(mock):
    return BridgeClient(mock.discovery_path, timeout=5)


@pytest.fixture
def call_tool(client):
    """call_tool(name, **args) -> CallToolResult, through a real in-process MCP client."""
    from mcp import Client

    server = build_server(client)

    def _call(tool_name, /, **args):
        async def run():
            async with Client(server) as c:
                return await c.call_tool(tool_name, args)

        return asyncio.run(run())

    return _call
