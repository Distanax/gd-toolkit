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
// Off-thread: the reload leaves the editor and reopens it, waiting for GD between the steps.
BRIDGE_COMMAND_OFF_THREAD(set_level_string) {
	auto str = paramString(params, "level_string");
	if (str.find(';') == std::string::npos)
		throw RpcError("invalid_params", "level_string must be a raw level string (header;objects;...)");
	return reloadOpenLevel(params, "set_level_string", [str](LevelEditorLayer*) { return str; });
}
