#include "Level.hpp"

#include <algorithm>
#include <chrono>
#include <vector>

#include <Geode/utils/file.hpp>

#include "Rpc.hpp"

using namespace geode::prelude;

namespace bridge {

LevelEditorLayer* requireEditor() {
	auto lel = LevelEditorLayer::get();
	if (!lel || !lel->m_level) throw RpcError("not_in_editor", "open a level in the editor first");
	return lel;
}

void requireNotPlaytesting(LevelEditorLayer* lel) {
	if (lel->m_playbackMode != PlaybackMode::Not)
		throw RpcError("busy", "a playtest is running; stop it first (playtest action=stop)");
}

std::string levelName(LevelEditorLayer* lel) {
	return std::string(lel->m_level->m_levelName);
}

void requireWritable(LevelEditorLayer* lel, matjson::Value const& params) {
	auto name = levelName(lel);
	if (name.starts_with(SAFE_PREFIX)) return;
	auto confirm = optString(params, "confirm_name");
	if (confirm && *confirm == name) return;
	throw RpcError("level_protected",
		fmt::format("level '{}' doesn't start with \"{}\"; pass confirm_name=\"{}\" to modify it anyway", name,
			SAFE_PREFIX, name));
}

std::filesystem::path backupRoot() {
	return Mod::get()->getSaveDir() / "backups";
}

std::string sanitizeFileName(std::string const& name) {
	std::string out;
	for (unsigned char c : name) {
		if (std::isalnum(c) || c == '-' || c == '_') out.push_back((char)c);
		else if (c == ' ') out.push_back('_');
		else out.push_back('~');
	}
	if (out.empty()) out = "unnamed";
	if (out.size() > 80) out.resize(80);
	return out;
}

std::filesystem::path backupLevel(LevelEditorLayer* lel, std::string const& reason) {
	auto dir = backupRoot() / sanitizeFileName(levelName(lel));
	if (auto r = file::createDirectoryAll(dir); !r) throw RpcError("internal", "backup dir: " + r.unwrapErr());

	auto now = std::chrono::system_clock::now();
	auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count() % 1000;
	auto stamp = fmt::format("{:%Y%m%dT%H%M%S}{:03d}Z", std::chrono::floor<std::chrono::seconds>(now), (int)ms);
	auto path = dir / fmt::format("{}_{}.txt", stamp, sanitizeFileName(reason));

	std::string levelString = lel->getLevelString();
	if (auto r = file::writeStringSafe(path, levelString); !r) throw RpcError("internal", "backup write: " + r.unwrapErr());

	// Keep the newest MAX_BACKUPS (names sort chronologically).
	std::vector<std::filesystem::path> files;
	std::error_code ec;
	for (auto const& e : std::filesystem::directory_iterator(dir, ec))
		if (e.is_regular_file() && e.path().extension() == ".txt") files.push_back(e.path());
	if (files.size() > MAX_BACKUPS) {
		std::sort(files.begin(), files.end());
		for (std::size_t i = 0; i + MAX_BACKUPS < files.size(); ++i) std::filesystem::remove(files[i], ec);
	}
	return path;
}

}  // namespace bridge
