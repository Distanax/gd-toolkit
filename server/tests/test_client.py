import json
import urllib.request

import pytest

from gd_bridge_mcp.client import BridgeClient, BridgeError


def test_ping(client):
    assert client.call("ping")["pong"] is True


def test_unknown_method(client):
    with pytest.raises(BridgeError) as e:
        client.call("no_such_thing")
    assert e.value.code == "unknown_method"


def test_none_params_are_dropped(client, mock):
    client.call("ping", a=1, b=None)
    assert mock.calls[-1] == ("ping", {"a": 1})


def test_reloads_discovery_after_restart(client, mock):
    client.call("ping")
    mock.rotate_token()  # GD restarted: old token is now rejected
    assert client.call("ping")["pong"] is True


def test_missing_discovery_file(tmp_path):
    with pytest.raises(BridgeError) as e:
        BridgeClient(tmp_path / "bridge.json").call("ping")
    assert e.value.code == "not_running"


def test_dead_port(tmp_path):
    p = tmp_path / "bridge.json"
    p.write_text(json.dumps({"protocol": 1, "port": 1, "token": "x", "pid": 0}))
    with pytest.raises(BridgeError) as e:
        BridgeClient(p, timeout=2).call("ping")
    assert e.value.code == "not_running"


def test_protocol_mismatch(tmp_path):
    p = tmp_path / "bridge.json"
    p.write_text(json.dumps({"protocol": 99, "port": 1, "token": "x"}))
    with pytest.raises(BridgeError) as e:
        BridgeClient(p).call("ping")
    assert e.value.code == "protocol_mismatch"


def test_mock_rejects_origin_and_bad_token(mock):
    info = json.loads(mock.discovery_path.read_text())
    url = f"http://127.0.0.1:{info['port']}/rpc"
    for headers, status in (({"X-GD-Bridge-Token": "nope"}, 401),
                            ({"X-GD-Bridge-Token": info["token"], "Origin": "http://evil"}, 403)):
        req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req)
        assert e.value.code == status
