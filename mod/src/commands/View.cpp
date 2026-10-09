// Camera and screenshots.

#include "../Capture.hpp"
#include "../Level.hpp"
#include "../Rpc.hpp"

#include <Geode/Geode.hpp>

using namespace geode::prelude;
using namespace bridge;

namespace {

matjson::Value cameraJson(Camera const& c) {
	return matjson::makeObject({{"x", c.x}, {"y", c.y}, {"zoom", c.zoom}});
}

// Camera that fits region {x1,y1,x2,y2} (GD units) into the window with a small margin.
Camera fitRegion(matjson::Value const& r) {
	double x1 = paramNumber(r, "x1"), y1 = paramNumber(r, "y1"), x2 = paramNumber(r, "x2"), y2 = paramNumber(r, "y2");
	double w = std::max(std::abs(x2 - x1), 30.0), h = std::max(std::abs(y2 - y1), 30.0);
	auto win = CCDirector::sharedDirector()->getWinSize();
	float zoom = (float)std::min(win.width / (w * 1.05), win.height / (h * 1.05));
	return {(float)((x1 + x2) / 2), (float)((y1 + y2) / 2), zoom};
}

}  // namespace

BRIDGE_COMMAND(get_camera) {
	return cameraJson(getCamera(requireEditor()));
}

// params: x, y (GD units at the view centre), zoom? (editor clamps it to its own range)
BRIDGE_COMMAND(move_camera) {
	auto lel = requireEditor();
	auto cur = getCamera(lel);
	Camera cam{(float)optNumber(params, "x").value_or(cur.x), (float)optNumber(params, "y").value_or(cur.y),
		(float)optNumber(params, "zoom").value_or(cur.zoom)};
	if (cam.zoom <= 0) throw RpcError("invalid_params", "zoom must be > 0");
	setCamera(lel, cam);
	return cameraJson(getCamera(lel));
}

// params: x?, y?, zoom? or region? {x1,y1,x2,y2}; hide_ui? (default true); restore_camera? (default true)
// Works outside the editor too (then it just captures the current screen).
BRIDGE_COMMAND(screenshot) {
	bool hideUI = optBool(params, "hide_ui").value_or(true);
	auto lel = LevelEditorLayer::get();
	std::optional<Camera> previous;
	if (lel && lel->m_playbackMode == PlaybackMode::Not) {
		std::optional<Camera> target;
		if (auto r = optField(params, "region")) target = fitRegion(*r);
		else if (optField(params, "x") || optField(params, "y") || optField(params, "zoom")) {
			auto cur = getCamera(lel);
			target = Camera{(float)optNumber(params, "x").value_or(cur.x), (float)optNumber(params, "y").value_or(cur.y),
				(float)optNumber(params, "zoom").value_or(cur.zoom)};
		}
		if (target) {
			previous = getCamera(lel);
			setCamera(lel, *target);
		}
	}
	auto cam = lel ? std::optional(getCamera(lel)) : std::nullopt;
	CaptureResult shot;
	try {
		shot = captureScreen(timestampName("shot"), hideUI);
	} catch (...) {
		if (previous && lel) setCamera(lel, *previous);
		throw;
	}
	if (previous && optBool(params, "restore_camera").value_or(true)) setCamera(lel, *previous);
	return matjson::makeObject({
		{"path", utils::string::pathToString(shot.path)},
		{"width", shot.width},
		{"height", shot.height},
		{"camera", cam ? cameraJson(*cam) : matjson::Value(nullptr)},
	});
}
