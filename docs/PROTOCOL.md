# gd-bridge wire protocol (v1)

The mod (`mod/`) runs a tiny HTTP/1.1 server; the MCP server (`server/`) is its only intended
client. Everything here is local to one Windows PC.

## Discovery: `bridge.json`
On load the mod writes `%LOCALAPPDATA%\GeometryDash\geode\mods\distanax.gd-bridge\bridge.json`
(the mod's Geode save dir):

```json
{"protocol": 1, "port": 47821, "token": "<64 hex chars>", "pid": 12345, "mod_version": "v0.1.0"}
```

- `token` is 32 random bytes, regenerated every GD launch. Clients must re-read the file when a
  request fails with `unauthorized` or the connection is refused (GD restarted).
- `port` is the `port` setting (default 47821). If that port is busy the mod binds an ephemeral
  port and writes that instead.
- `pid` lets the client tell a stale file (GD closed) from a live one.
- Override the file location with the `GD_BRIDGE_FILE` environment variable (tests, odd installs).

## Transport
- Listens on **127.0.0.1 only**. One request per connection (`Connection: close`).
- `POST /rpc` with `Content-Type: application/json` and header `X-GD-Bridge-Token: <token>`.
- `GET /health` needs no token and returns `{"ok": true, "protocol": 1}` (liveness only).
- Requests carrying an `Origin` header are rejected (no browser page may drive the editor), and
  `OPTIONS` is answered `405`, so CORS preflights never succeed.
- Body limit 64 MiB (large level strings). Headers limit 16 KiB.

HTTP status codes: `200` for every well-formed RPC (success or RPC error, see below), `400` bad
HTTP/JSON, `401` missing/wrong token, `403` `Origin` present, `404` unknown path, `405` wrong
method, `413` body too large.

## RPC body
Request:
```json
{"id": 7, "method": "add_objects", "params": {"objects": ["1,1,2,15,3,15"]}}
```
Response, success / error:
```json
{"id": 7, "ok": true, "result": {"added": 1, "uids": [431]}}
{"id": 7, "ok": false, "error": {"code": "level_protected", "message": "..."}}
```

Error codes:

| code | meaning |
|---|---|
| `bad_request` | body is not an object with a string `method` |
| `unknown_method` | no such method |
| `invalid_params` | missing/ill-typed parameter (message names it) |
| `not_in_editor` | method needs the level editor open |
| `not_in_playtest` / `busy` | wrong playtest state, or another long job is running |
| `level_protected` | write refused: level name doesn't start with `"CLAUDE "` and `confirm_name` doesn't match |
| `not_found` | named level / backup / job doesn't exist |
| `timeout` | the main thread didn't run the command within the deadline (default 10 s) |
| `internal` | unexpected exception (message has details; see the Geode log) |

## Execution model
- The socket thread parses and authenticates, then queues the command with
  `geode::queueInMainThread` and waits on a promise (deadline 10 s). All game state is touched on
  the main thread only.
- Long work (frame capture) runs as a **job**: the method returns `{"job": "<id>"}` immediately;
  poll `job_status` until `done`.
- Binary output (screenshots, frames) is written as PNG under `<save dir>\captures\` and returned as
  absolute paths; the client reads the files (same machine), keeping JSON small.

## Safety (enforced in the mod)
- Every write method takes optional `confirm_name`. A write is allowed only if the open level's
  name starts with `"CLAUDE "` or `confirm_name` equals the exact level name.
- Before any write the current level string is saved to
  `<save dir>\backups\<sanitised level name>\<UTC timestamp>.txt` (newest 200 kept per level).
- Nothing in the mod uploads, deletes levels, or touches levels other than the one open in the
  editor (plus `create_level`, which always prefixes `"CLAUDE "`).
