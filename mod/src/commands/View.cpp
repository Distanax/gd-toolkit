// Camera and screenshots.

#include "../Capture.hpp"
#include "../Level.hpp"
#include "../Rpc.hpp"

#include <chrono>
#include <thread>

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
// Runs off the socket thread in steps: aim the camera on the main thread, let GD render a few frames
// (it only moves the ground/grid and un-hides objects in newly visible sections during its own update,
// so capturing in the same frame as the move shows a half-updated view), then capture and restore.
BRIDGE_COMMAND_OFF_THREAD(screenshot) {
	bool hideUI = optBool(params, "hide_ui").value_or(true);
	bool restore = optBool(params, "restore_camera").value_or(true);

	auto aimed = runOnMainThread([](matjson::Value const& p) -> matjson::Value {
		auto lel = LevelEditorLayer::get();
		if (!lel || lel->m_playbackMode != PlaybackMode::Not) return matjson::makeObject({{"moved", false}});
		std::optional<Camera> target;
		if (auto r = optField(p, "region")) target = fitRegion(*r);
		else if (optField(p, "x") || optField(p, "y") || optField(p, "zoom")) {
			auto cur = getCamera(lel);
			target = Camera{(float)optNumber(p, "x").value_or(cur.x), (float)optNumber(p, "y").value_or(cur.y),
				(float)optNumber(p, "zoom").value_or(cur.zoom)};
		}
		if (!target) return matjson::makeObject({{"moved", false}});
		auto previous = getCamera(lel);
		setCamera(lel, *target);
		return matjson::makeObject({{"moved", true}, {"previous", cameraJson(previous)}});
	}, params);
	bool moved = aimed["moved"].asBool().unwrapOr(false);
	if (moved) std::this_thread::sleep_for(std::chrono::milliseconds(150));

	auto prev = moved ? aimed["previous"] : matjson::Value(nullptr);
	return runOnMainThread([hideUI, restore, moved, prev](matjson::Value const&) -> matjson::Value {
		auto lel = LevelEditorLayer::get();
		auto cam = lel ? std::optional(getCamera(lel)) : std::nullopt;
		auto putBack = [&] {
			if (moved && restore && lel)
				setCamera(lel, Camera{(float)prev["x"].asDouble().unwrapOr(0), (float)prev["y"].asDouble().unwrapOr(0),
					(float)prev["zoom"].asDouble().unwrapOr(1)});
		};
		CaptureResult shot;
		try {
			shot = captureScreen(timestampName("shot"), hideUI);
		} catch (...) {
			putBack();
			throw;
		}
		putBack();
		return matjson::makeObject({
			{"path", utils::string::pathToString(shot.path)},
			{"width", shot.width},
			{"height", shot.height},
			{"camera", cam ? cameraJson(*cam) : matjson::Value(nullptr)},
		});
	}, params);
}
