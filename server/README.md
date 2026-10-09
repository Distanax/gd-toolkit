# gd-bridge-mcp

MCP server (stdio) that controls the Geometry Dash level editor through the **GD Bridge** Geode mod
(`../mod`). Install, configuration and the tool list: the repository README and CLAUDE.md in
[Distanax/gd-toolkit](https://github.com/Distanax/gd-toolkit).

```
pip install "git+https://github.com/Distanax/gd-toolkit#subdirectory=server"
gd-bridge-mcp            # speaks MCP over stdio; normally started by Claude
```

Development: `pip install -e "server[test]"` then `pytest server/tests` (uses a mock bridge, no GD needed).
