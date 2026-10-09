// Whole-level read/replace.

#include "../Level.hpp"
#include "../Rpc.hpp"

#include <Geode/Geode.hpp>

using namespace geode::prelude;
using namespace bridge;

// The open level as GD's raw (uncompressed) level string: header ";" then one object per ";".
BRIDGE_COMMAND(get_level_string) {
	auto lel = requireEditor();
	std::string str = lel->getLevelString();
	return matjson::makeObject({
		{"name", levelName(lel)},
		{"object_count", lel->m_objects ? (int)lel->m_objects->count() : 0},
		{"level_string", str},
	});
}

// Replaces the whole open level (header + objects) and reloads the editor so GD re-parses everything,
// including colours and level settings. Backs up first; undo history does not survive the reload.
BRIDGE_COMMAND(set_level_string) {
	auto lel = requireEditor();
	requireNotPlaytesting(lel);
	requireWritable(lel, params);
	auto str = paramString(params, "level_string");
	if (str.find(';') == std::string::npos)
		throw RpcError("invalid_params", "level_string must be a raw level string (header;objects;...)");

	auto backup = backupLevel(lel, "set_level_string");
	auto level = lel->m_level;
	level->m_levelString = ZipUtils::compressString(str, false, 0);
	CCDirector::sharedDirector()->replaceScene(LevelEditorLayer::scene(level, false));
	return matjson::makeObject({
		{"name", levelName(lel)},
		{"backup", utils::string::pathToString(backup)},
		{"reloaded", true},
	});
}
