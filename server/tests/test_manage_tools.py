def data(result):
    assert not result.is_error, result.content
    return result.structured_content


def error_text(result):
    assert result.is_error, result.structured_content
    return " ".join(getattr(c, "text", "") for c in result.content)


def test_create_level_forces_prefix_and_opens(call_tool, mock):
    r = data(call_tool("create_level", name="fresh", song_id=1502369))
    assert r["created"]["name"] == "CLAUDE fresh"
    assert mock.saved_levels["CLAUDE test"] is not None  # the open CLAUDE level was saved before switching
    assert mock.state["level"]["name"] == r["created"]["name"]
    assert data(call_tool("get_music"))["song_id"] == 1502369


def test_create_refuses_to_leave_users_level(call_tool, mock):
    mock.state["level"]["name"] = "My Masterpiece"
    assert "level_protected" in error_text(call_tool("create_level", name="new one"))
    assert mock.state["level"]["name"] == "My Masterpiece"


def test_open_level_rules(call_tool, mock):
    mock.saved_levels.update({"Distanax Level": "kA2,0;", "CLAUDE other": "kA2,0;1,1,2,15,3,15;"})
    assert "not_found" in error_text(call_tool("open_level", name="nope"))
    assert "level_protected" in error_text(call_tool("open_level", name="Distanax Level"))
    r = data(call_tool("open_level", name="CLAUDE other"))
    assert r["opened"]["name"] == "CLAUDE other" and len(mock.objects) == 1
    names = [lv["name"] for lv in data(call_tool("list_levels", claude_only=True))["levels"]]
    assert "Distanax Level" not in names and "CLAUDE other" in names


def test_save_level(call_tool, mock):
    call_tool("add_objects", objects=["1,1,2,15,3,15"])
    assert data(call_tool("save_level"))["saved"]
    assert mock.saved_levels["CLAUDE test"].endswith("1,1,2,15,3,15;")


def test_backups_list_and_restore(call_tool, mock):
    call_tool("add_objects", objects=["1,1,2,15,3,15"])      # backup #0: empty level
    call_tool("add_objects", objects=["1,8,2,45,3,15"])      # backup #1: one block
    files = data(call_tool("list_backups"))["backups"]
    assert len(files) == 2 and files[0]["file"].startswith("000001")  # newest first
    oldest = files[-1]["file"]
    r = data(call_tool("restore_backup", file=oldest))
    assert r["restored"] == oldest and mock.objects == []
    assert "invalid_params" in error_text(call_tool("restore_backup", file="../../etc"))


def test_undo_redo(call_tool, mock):
    mock.undo_stack.append("kA2,0;")
    call_tool("add_objects", objects=["1,1,2,15,3,15"])
    assert data(call_tool("undo"))["undone"] and mock.objects == []
    assert data(call_tool("redo"))["redone"] and len(mock.objects) == 1
    assert data(call_tool("redo"))["redone"] is False
