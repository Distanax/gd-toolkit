# GD Bridge

Local-only bridge between Geometry Dash and an MCP server (`server/` in
[Distanax/gd-toolkit](https://github.com/Distanax/gd-toolkit)), so Claude can read and edit levels in
the editor, take screenshots and run playtests.

- Listens on 127.0.0.1 only and requires a random token stored in the mod's save folder.
- Only edits levels whose name starts with `CLAUDE ` unless the caller confirms the exact level name.
- Backs up the level before every change. Never uploads anything.
