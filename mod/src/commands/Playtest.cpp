// Editor playtests and frame capture during them.

#include "../Capture.hpp"
#include "../Level.hpp"
#include "../Rpc.hpp"

#include <map>
#include <mutex>
#include <thread>
#include <vector>

#include <algorithm>

#include <Geode/Geode.hpp>
#include <Geode/modify/LevelEditorLayer.hpp>
#include <Geode/utils/file.hpp>

using namespace geode::prelude;
using namespace bridge;

namespace {

// uid of the temporary start position placed by playtest(from_x); removed when the playtest stops.
int g_tempStartPosUid = 0;
constexpr int TEMP_START_ORDER = 1000000;  // beats any start position the level already has

GameObject* findByUid(LevelEditorLayer* lel, int uid) {
	if (!lel->m_objects || uid <= 0) return nullptr;
	for (auto obj : CCArrayExt<GameObject*>(lel->m_objects))
		if (obj->m_uniqueID == uid) return obj;
	return nullptr;
}

void removeTempStartPos(LevelEditorLayer* lel) {
	if (auto obj = findByUid(lel, g_tempStartPosUid)) lel->removeObject(obj, true);
	g_tempStartPosUid = 0;
}

char const* modeName(LevelEditorLayer* lel) {
	switch (lel->m_playbackMode) {
		case PlaybackMode::Playing: return "playing";
		case PlaybackMode::Paused: return "paused";
		default: return "not";
	}
}

// ---- frame capture jobs ---------------------------------------------------------------

struct Job {
	std::string state = "running";  // running | done | failed
	std::string error;
	std::vector<std::string> frames;
	int requested = 0;
	int pendingWrites = 0;
};

std::mutex g_jobsMutex;
std::map<std::string, Job> g_jobs;
int g_jobCounter = 0;

// requested drops to 0 when the scheduler stops capturing; the job is done once every PNG is written.
void finishIfComplete(Job& job) {
	if (job.state == "running" && job.requested == 0 && job.pendingWrites == 0) job.state = "done";
}

// Ticks on the main thread via the scheduler. Reads pixels on the main thread (fast) and encodes PNGs
// on a worker thread, so the playtest being recorded doesn't stutter on PNG compression.
class FrameJob : public CCObject {
public:
	std::string id;
	int remaining = 0;
	bool hideUI = false;
	int index = 0;

	void tick(float) {
		bool stop = false;
		auto lel = LevelEditorLayer::get();
		if (!lel || lel->m_playbackMode == PlaybackMode::Not) stop = true;
		if (!stop && remaining > 0) {
			try {
				captureOne();
			} catch (std::exception const& e) {
				std::lock_guard lock(g_jobsMutex);
				auto& job = g_jobs[id];
				job.state = "failed";
				job.error = e.what();
				stop = true;
			}
			--remaining;
		}
		if (stop || remaining <= 0) {
			{
				std::lock_guard lock(g_jobsMutex);
				auto& job = g_jobs[id];
				job.requested = 0;
				if (stop && job.state == "running" && job.frames.empty() && job.pendingWrites == 0) {
					job.state = "failed";
					job.error = "playtest was not running";
				}
				finishIfComplete(job);
			}
			CCDirector::sharedDirector()->getScheduler()->unscheduleAllForTarget(this);
			// Not from inside our own scheduler callback: free it next frame.
			queueInMainThread([self = this] { self->release(); });
		}
	}

private:
	void captureOne() {
		auto director = CCDirector::sharedDirector();
		auto scene = director->getRunningScene();
		auto size = director->getWinSize();
		EditorUI* ui = nullptr;
		bool uiVisible = false;
		if (hideUI) {
			if (auto lel = LevelEditorLayer::get(); lel && lel->m_editorUI) {
				ui = lel->m_editorUI;
				uiVisible = ui->isVisible();
				ui->setVisible(false);
			}
		}
		auto rt = CCRenderTexture::create((int)size.width, (int)size.height, kCCTexture2DPixelFormat_RGBA8888);
		rt->begin();
		scene->visit();
		rt->end();
		if (ui) ui->setVisible(uiVisible);
		CCImage* image = rt->newCCImage(true);
		if (!image) throw std::runtime_error("could not read back frame");

		auto dir = Mod::get()->getSaveDir() / "captures" / id;
		(void)file::createDirectoryAll(dir);
		auto path = dir / fmt::format("frame_{:03d}.png", index++);
		auto pathStr = utils::string::pathToString(path);
		{
			std::lock_guard lock(g_jobsMutex);
			g_jobs[id].pendingWrites++;
		}
		std::thread([image, pathStr, jobId = id] {
			bool ok = image->saveToFile(pathStr.c_str(), false);
			image->release();
			std::lock_guard lock(g_jobsMutex);
			auto& job = g_jobs[jobId];
			job.pendingWrites--;
			if (ok) job.frames.push_back(pathStr);
			else if (job.error.empty()) job.error = "could not write " + pathStr;
			finishIfComplete(job);
		}).detach();
	}
};

matjson::Value jobJson(std::string const& id, Job const& job) {
	auto frames = matjson::Value::array();
	auto sorted = job.frames;
	std::sort(sorted.begin(), sorted.end());
	for (auto const& f : sorted) frames.push(f);
	return matjson::makeObject({
		{"job", id},
		{"state", job.state},
		{"error", job.error.empty() ? matjson::Value(nullptr) : matjson::Value(job.error)},
		{"frames", frames},
	});
}

}  // namespace

// However a playtest ends (our stop command or GD's own stop button), the temporary start position must
// not stay in the level, or it would be saved with it.
class $modify(BridgePlaytestLEL, LevelEditorLayer) {
	void onStopPlaytest() {
		LevelEditorLayer::onStopPlaytest();
		removeTempStartPos(this);
	}
};

// params: action = "start" | "stop" | "pause" | "resume" | "status", from_x? (start only), from_y?
// from_x places a temporary start position (removed again on stop); it is a write, so it follows the
// CLAUDE-name rule. Without it the editor's normal rule applies (level start or its own start positions).
BRIDGE_COMMAND(playtest) {
	auto lel = requireEditor();
	auto ui = lel->m_editorUI;
	if (!ui) throw RpcError("not_in_editor", "editor UI not ready");
	auto action = optString(params, "action").value_or("status");

	if (action == "start") {
		if (lel->m_playbackMode != PlaybackMode::Not) throw RpcError("busy", "a playtest is already running");
		if (auto fromX = optNumber(params, "from_x")) {
			requireWritable(lel, params);
			backupLevel(lel, "playtest_from_x");
			removeTempStartPos(lel);
			double fromY = optNumber(params, "from_y").value_or(15);
			auto created = lel->createObjectsFromString(fmt::format("1,31,2,{},3,{};", *fromX, fromY), true, true);
			if (created && created->count() > 0) {
				auto sp = static_cast<StartPosObject*>(created->objectAtIndex(0));
				if (sp->m_startSettings) sp->m_startSettings->m_targetOrder = TEMP_START_ORDER;
				g_tempStartPosUid = sp->m_uniqueID;
			}
		}
		ui->onPlaytest(nullptr);
	} else if (action == "stop") {
		if (lel->m_playbackMode != PlaybackMode::Not) ui->onStopPlaytest(nullptr);
		removeTempStartPos(lel);
	} else if (action == "pause") {
		if (lel->m_playbackMode != PlaybackMode::Playing) throw RpcError("not_in_playtest", "nothing is playing");
		lel->onPausePlaytest();
	} else if (action == "resume") {
		if (lel->m_playbackMode != PlaybackMode::Paused) throw RpcError("not_in_playtest", "playtest isn't paused");
		lel->onResumePlaytest();
	} else if (action != "status") {
		throw RpcError("invalid_params", "action must be start, stop, pause, resume or status");
	}
	return matjson::makeObject({
		{"playtest", modeName(lel)},
		{"temp_start_pos", g_tempStartPosUid > 0},
	});
}

// params: count (1-120), interval_ms (>= 16), hide_ui? (default true). Starts a job and returns at once:
// {"job": id}. Frames are captured while the playtest runs; poll job_status.
BRIDGE_COMMAND(capture_frames) {
	auto lel = requireEditor();
	if (lel->m_playbackMode == PlaybackMode::Not)
		throw RpcError("not_in_playtest", "start a playtest first (playtest action=start)");
	int count = (int)optNumber(params, "count").value_or(10);
	int interval = (int)optNumber(params, "interval_ms").value_or(250);
	if (count < 1 || count > 120) throw RpcError("invalid_params", "count must be 1-120");
	if (interval < 16) throw RpcError("invalid_params", "interval_ms must be >= 16");

	auto job = new FrameJob();  // released by itself when finished
	job->id = fmt::format("frames_{}_{}", timestampName("job"), ++g_jobCounter);
	job->remaining = count;
	job->hideUI = optBool(params, "hide_ui").value_or(true);
	{
		std::lock_guard lock(g_jobsMutex);
		auto& j = g_jobs[job->id];
		j.requested = count;
	}
	CCDirector::sharedDirector()->getScheduler()->scheduleSelector(
		schedule_selector(FrameJob::tick), job, interval / 1000.f, kCCRepeatForever, 0.f, false);
	return matjson::makeObject({{"job", job->id}, {"count", count}, {"interval_ms", interval}});
}

// params: job. Safe off the main thread (only reads job bookkeeping).
BRIDGE_COMMAND_OFF_THREAD(job_status) {
	auto id = paramString(params, "job");
	std::lock_guard lock(g_jobsMutex);
	auto it = g_jobs.find(id);
	if (it == g_jobs.end()) throw RpcError("not_found", "no such job");
	return jobJson(id, it->second);
}
