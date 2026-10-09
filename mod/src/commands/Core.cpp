// Core commands: liveness and game status.

#include "../Rpc.hpp"

#include <Geode/Geode.hpp>

using namespace geode::prelude;

namespace {

std::string sceneName() {
	auto scene = CCDirector::sharedDirector()->getRunningScene();
	if (!scene) return "none";
	// The scene itself is a plain CCScene (or a transition); its first child is the real layer.
	CCObject* node = scene->getChildrenCount() > 0 ? scene->getChildren()->objectAtIndex(0) : scene;
	std::string name(geode::cocos::getObjectName(node));
	for (std::string_view prefix : {"class ", "struct "})
		if (name.starts_with(prefix)) name.erase(0, prefix.size());
	return name;
}

char const* playbackName(PlaybackMode m) {
	switch (m) {
		case PlaybackMode::Playing: return "playing";
		case PlaybackMode::Paused: return "paused";
		default: return "not";
	}
}

}  // namespace

// Where the player is and what's open. Read-only; safe at any time.
BRIDGE_COMMAND(status) {
	matjson::Value level = nullptr;
	std::string playtest = "not";
	auto lel = LevelEditorLayer::get();
	if (lel && lel->m_level) {
		auto lvl = lel->m_level;
		level = matjson::makeObject({
			{"name", std::string(lvl->m_levelName)},
			{"id", lvl->m_levelID.value()},
			{"song_id", lvl->m_songID},
			{"audio_track", lvl->m_audioTrack},
			{"object_count", lel->m_objects ? (int)lel->m_objects->count() : 0},
		});
		playtest = playbackName(lel->m_playbackMode);
	}
	return matjson::makeObject({
		{"scene", sceneName()},
		{"in_editor", lel != nullptr},
		{"in_level", PlayLayer::get() != nullptr},
		{"playtest", playtest},
		{"level", level},
		{"versions", matjson::makeObject({
			{"mod", Mod::get()->getVersion().toVString()},
			{"geode", Loader::get()->getVersion().toVString()},
			{"gd", GEODE_GD_VERSION_STRING},
			{"protocol", 1},
		})},
	});
}

// Answered on the socket thread, so it works even while the main thread is busy (e.g. loading).
BRIDGE_COMMAND_OFF_THREAD(ping) {
	return matjson::makeObject({
		{"pong", true},
		{"mod_version", Mod::get()->getVersion().toVString()},
		{"protocol", 1},
	});
}
