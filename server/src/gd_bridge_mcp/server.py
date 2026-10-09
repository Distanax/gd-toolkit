"""The MCP server: tools that forward to the GD Bridge mod."""
from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import __version__
from .client import BridgeClient, BridgeError

INSTRUCTIONS = """\
Controls the Geometry Dash level editor on this PC through the GD Bridge Geode mod.
Safety: only levels whose name starts with "CLAUDE " can be modified unless a tool call passes
confirm_name=<exact level name>; every write is backed up first. Coordinates are GD units
(30 units = 1 block, ground row y = 15). Call `status` first to see what is open."""

F = TypeVar("F", bound=Callable[..., Any])


def bridge_errors(fn: F) -> F:
    """Report mod/connection failures as tool errors the model can read and act on."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except BridgeError as e:
            raise ToolError(f"[{e.code}] {e.message}") from None

    return wrapper  # type: ignore[return-value]


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

    mcp.bridge = bridge  # type: ignore[attr-defined]  (handy in tests)
    return mcp


def main() -> None:
    build_server().run(transport="stdio")
