// Undo/redo and the on-disk backup history.

#include "../Level.hpp"
#include "../Rpc.hpp"

#include <algorithm>
#include <vector>

#include <Geode/Geode.hpp>
#include <Geode/utils/file.hpp>

using namespace geode::prelude;
using namespace bridge;

namespace {

matjson::Value afterEdit(LevelEditorLayer* lel, char const* key, bool did) {
	return matjson::makeObject({
		{key, did},
		{"object_count", lel->m_objects ? (int)lel->m_objects->count() : 0},
	});
}

std::filesystem::path backupDirFor(LevelEditorLayer* lel, matjson::Value const& params) {
	auto level = optString(params, "level").value_or(levelName(lel));
	return backupRoot() / sanitizeFileName(level);
}

std::vector<std::filesystem::path> backupFiles(std::filesystem::path const& dir) {
	std::vector<std::filesystem::path> files;
	std::error_code ec;
	for (auto const& e : std::filesystem::directory_iterator(dir, ec))
		if (e.is_regular_file() && e.path().extension() == ".txt") files.push_back(e.path());
	std::sort(files.rbegin(), files.rend());  // newest first (names start with a UTC timestamp)
	return files;
}

}  // namespace

// Undo / redo one editor action (GD's own history, same as the toolbar buttons).
BRIDGE_COMMAND(undo) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	bool can = lel->m_undoObjects && lel->m_undoObjects->count() > 0;
	if (can) {
		backupLevel(lel, "undo");
		lel->m_editorUI->undoLastAction(nullptr);
	}
	return afterEdit(lel, "undone", can);
}

BRIDGE_COMMAND(redo) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	bool can = lel->m_redoObjects && lel->m_redoObjects->count() > 0;
	if (can) {
		backupLevel(lel, "redo");
		lel->m_editorUI->redoLastAction(nullptr);
	}
	return afterEdit(lel, "redone", can);
}

// params: level? (defaults to the open level's name), limit? (default 50)
BRIDGE_COMMAND(list_backups) {
	auto lel = requireEditor();
	auto dir = backupDirFor(lel, params);
	int limit = std::clamp((int)optNumber(params, "limit").value_or(50), 1, (int)MAX_BACKUPS);
	auto out = matjson::Value::array();
	auto files = backupFiles(dir);
	for (int i = 0; i < (int)files.size() && i < limit; ++i) {
		std::error_code ec;
		auto size = std::filesystem::file_size(files[i], ec);
		out.push(matjson::makeObject({
			{"file", utils::string::pathToString(files[i].filename())},
			{"bytes", (double)size},
		}));
	}
	return matjson::makeObject({
		{"dir", utils::string::pathToString(dir)},
		{"total", (int)files.size()},
		{"backups", out},
	});
}

// params: file (a name from list_backups), level? (backup folder; defaults to the open level), confirm_name?
// Restoring is itself a write: the current state is backed up first.
BRIDGE_COMMAND(restore_backup) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	auto fileName = paramString(params, "file");
	if (fileName.find_first_of("/\\") != std::string::npos || fileName.find("..") != std::string::npos)
		throw RpcError("invalid_params", "file must be a bare backup file name from list_backups");
	auto path = backupDirFor(lel, params) / fileName;
	auto content = file::readString(path);
	if (!content) throw RpcError("not_found", fmt::format("no backup '{}'", fileName));
	auto backup = backupLevel(lel, "before_restore");
	replaceLevelString(lel, content.unwrap());
	return matjson::makeObject({
		{"restored", fileName},
		{"backup", utils::string::pathToString(backup)},
		{"reloaded", true},
	});
}
