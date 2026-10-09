#include "Capture.hpp"

#include <atomic>
#include <chrono>

#include <Geode/utils/file.hpp>

#include "Rpc.hpp"

using namespace geode::prelude;

namespace bridge {

std::string timestampName(std::string const& prefix) {
	static std::atomic_int counter = 0;
	auto now = std::chrono::system_clock::now();
	auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count() % 1000;
	return fmt::format("{}_{:%Y%m%dT%H%M%S}{:03d}Z_{}", prefix, std::chrono::floor<std::chrono::seconds>(now), (int)ms,
		counter++);
}

CaptureResult captureScreen(std::string const& name, bool hideEditorUI) {
	auto director = CCDirector::sharedDirector();
	auto scene = director->getRunningScene();
	if (!scene) throw RpcError("internal", "no running scene to capture");

	auto dir = Mod::get()->getSaveDir() / "captures";
	if (auto r = file::createDirectoryAll(dir); !r) throw RpcError("internal", "captures dir: " + r.unwrapErr());
	auto path = dir / (name + ".png");

	EditorUI* ui = nullptr;
	bool uiWasVisible = false;
	if (hideEditorUI) {
		if (auto lel = LevelEditorLayer::get(); lel && lel->m_editorUI) {
			ui = lel->m_editorUI;
			uiWasVisible = ui->isVisible();
			ui->setVisible(false);
		}
	}

	// CCRenderTexture takes points and allocates points * content scale factor pixels, i.e. full resolution.
	auto size = director->getWinSize();
	auto rt = CCRenderTexture::create((int)size.width, (int)size.height, kCCTexture2DPixelFormat_RGBA8888);
	if (!rt) {
		if (ui) ui->setVisible(uiWasVisible);
		throw RpcError("internal", "could not create render texture");
	}
	rt->begin();
	scene->visit();
	rt->end();
	if (ui) ui->setVisible(uiWasVisible);

	auto image = rt->newCCImage(true);
	if (!image) throw RpcError("internal", "could not read back the render texture");
	CaptureResult res{path, image->getWidth(), image->getHeight()};
	bool ok = image->saveToFile(utils::string::pathToString(path).c_str(), false);
	image->release();
	if (!ok) throw RpcError("internal", "could not write " + utils::string::pathToString(path));
	return res;
}

Camera getCamera(LevelEditorLayer* lel) {
	auto layer = lel->m_objectLayer;
	auto win = CCDirector::sharedDirector()->getWinSize();
	float zoom = layer->getScale();
	auto pos = layer->getPosition();
	return {(win.width / 2 - pos.x) / zoom, (win.height / 2 - pos.y) / zoom, zoom};
}

void setCamera(LevelEditorLayer* lel, Camera const& cam) {
	auto layer = lel->m_objectLayer;
	if (lel->m_editorUI) lel->m_editorUI->updateZoom(cam.zoom);
	else layer->setScale(cam.zoom);
	float zoom = layer->getScale();  // the editor clamps zoom to its own range
	auto win = CCDirector::sharedDirector()->getWinSize();
	layer->setPosition({win.width / 2 - cam.x * zoom, win.height / 2 - cam.y * zoom});
}

}  // namespace bridge
