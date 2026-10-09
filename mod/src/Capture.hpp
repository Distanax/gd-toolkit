#pragma once

// Screen capture to PNG and editor camera helpers. Main thread only.

#include <filesystem>
#include <string>

#include <Geode/Geode.hpp>

namespace bridge {

struct CaptureResult {
	std::filesystem::path path;
	int width = 0;   // pixels
	int height = 0;
};

// Renders the running scene into an offscreen texture and writes <save dir>/captures/<name>.png.
// hideEditorUI hides the editor's toolbars for the shot (restored afterwards). Throws RpcError.
CaptureResult captureScreen(std::string const& name, bool hideEditorUI);

struct Camera {
	float x = 0;     // GD units at the centre of the view
	float y = 0;
	float zoom = 1;  // editor zoom (object layer scale)
};

Camera getCamera(LevelEditorLayer* lel);
void setCamera(LevelEditorLayer* lel, Camera const& cam);

// Unique, sortable file stem: <UTC yyyymmddThhmmssmmmZ>_<counter>.
std::string timestampName(std::string const& prefix);

}  // namespace bridge
