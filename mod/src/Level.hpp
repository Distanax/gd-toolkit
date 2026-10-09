#pragma once

// Shared helpers for commands that work on the level open in the editor: access, the safety guard
// and backups. All of these must run on the main thread.

#include <filesystem>
#include <string>

#include <Geode/Geode.hpp>
#include <matjson.hpp>

namespace bridge {

// The editor layer, or throws RpcError("not_in_editor").
LevelEditorLayer* requireEditor();

// Throws RpcError("not_in_playtest"/"busy") style errors if a playtest is running; writes need the
// editor in its normal state.
void requireNotPlaytesting(LevelEditorLayer* lel);

std::string levelName(LevelEditorLayer* lel);

// THE safety rule (docs/PROTOCOL.md): a write is allowed only if the level's name starts with
// "CLAUDE " or params.confirm_name equals the exact level name. Throws RpcError("level_protected").
void requireWritable(LevelEditorLayer* lel, matjson::Value const& params);

// Writes the current level string to <save dir>/backups/<level>/<UTC timestamp>_<reason>.txt, keeps the
// newest MAX_BACKUPS per level, and returns the file path. Throws RpcError("internal") on failure:
// a write must never proceed without its backup.
std::filesystem::path backupLevel(LevelEditorLayer* lel, std::string const& reason);

// ---- switching the editor (SOCKET THREAD ONLY: these block while GD renders frames) ----
// Building a new LevelEditorLayer while the old one is still running crashes GD (live 2026-10-09:
// EXCEPTION_ACCESS_VIOLATION in GameObject::shouldBlendColor from the old layer's updateVisibility).
// So the editor is always left through GD's own exit (EditorPauseLayer::onExitEditor, no save) and the
// next one is only built once the old one is gone and no scene transition is running.

// Leaves the editor if one is open and waits until it is gone. Throws RpcError("timeout").
void leaveEditorBlocking();
// Opens `level` in the editor (call when no editor is open) and waits until it is up. Throws on timeout.
void openEditorBlocking(GJGameLevel* level);
// leave + set m_levelString (compressed) + open: the full reload used by set_level_string/restore_backup.
void reloadEditorWith(GJGameLevel* level, std::string const& levelString);

// Socket thread. Replaces the open level's content: on the main thread checks editor / no playtest / the
// CLAUDE guard, asks `contentFor` for the new level string (may throw), backs up with `reason`; then
// reloads the editor. Returns {"name", "backup", "reloaded": true}.
matjson::Value reloadOpenLevel(matjson::Value const& params, std::string const& reason,
	std::function<std::string(LevelEditorLayer*)> contentFor);

// Saves the open editor level into GD's level list (EditorPauseLayer::saveLevel) and writes
// CCLocalLevels.dat to disk.
void saveEditorLevel(LevelEditorLayer* lel);

std::filesystem::path backupRoot();
std::string sanitizeFileName(std::string const& name);

// GD places every object 90 units higher in the scene than its level-string y (the editor ground sits at
// node y 90; level-string ground row y = 15). Measured live 2026-10-09: string y 15 -> node y 105.
// Every coordinate the bridge reports or accepts is in LEVEL-STRING space, same as toolkit/gdlib.py.
inline constexpr float LEVEL_Y_OFFSET = 90.f;
inline cocos2d::CCPoint toLevel(cocos2d::CCPoint node) { return {node.x, node.y - LEVEL_Y_OFFSET}; }
inline cocos2d::CCPoint toNode(cocos2d::CCPoint level) { return {level.x, level.y + LEVEL_Y_OFFSET}; }

inline constexpr std::size_t MAX_BACKUPS = 200;
inline constexpr char const* SAFE_PREFIX = "CLAUDE ";

}  // namespace bridge
