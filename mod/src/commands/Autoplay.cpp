// Scripted inputs during editor playtests ("autoplay"), death log and position trace.
//
// Lets the MCP side verify that a planned input sequence actually clears a section in the real engine
// (the same check creators get from a macro bot). Inputs are keyed by the player's X position and
// applied every physics step (GJBaseGameLayer::processCommands runs once per 1/240 s step), so they
// don't depend on the render frame rate. Proves "possible with these inputs", not "fair" or "fun".

#include "../Level.hpp"
#include "../Rpc.hpp"

#include <algorithm>
#include <cmath>
#include <mutex>
#include <vector>

#include <Geode/Geode.hpp>
#include <Geode/modify/GJBaseGameLayer.hpp>

using namespace geode::prelude;
using namespace bridge;

namespace {

struct InputEvent {
	float x;
	bool press;
};

struct TracePoint {
	float x, y, vy;
	int mode;  // 0 cube, 1 ship, 2 ball, 3 ufo, 4 wave, 5 robot, 6 spider, 7 swing
	bool upsideDown, onGround;
};

struct AutoplayState {
	bool armed = false;
	bool stopOnDeath = true;
	std::vector<InputEvent> events;
	std::size_t next = 0;
	bool pressed = false;
	bool wasDead = false;
	bool active = true;  // false after the first death when stopOnDeath
	std::vector<float> deaths;  // level-string x of each death
	std::vector<float> deathYs;
	float maxX = 0;
	int traceEvery = 0;  // steps between trace points (0 = off)
	int stepCounter = 0;
	std::vector<TracePoint> trace;
};

std::mutex g_mutex;
AutoplayState g_auto;

constexpr std::size_t MAX_TRACE = 60000;

int modeOf(PlayerObject* p) {
	if (p->m_isShip) return 1;
	if (p->m_isBall) return 2;
	if (p->m_isBird) return 3;
	if (p->m_isDart) return 4;
	if (p->m_isRobot) return 5;
	if (p->m_isSpider) return 6;
	if (p->m_isSwing) return 7;
	return 0;
}

}  // namespace

class $modify(BridgeAutoplayLayer, GJBaseGameLayer) {
	void processCommands(float dt, bool isHalfTick, bool isLastTick) {
		bool editorPlay = typeinfo_cast<LevelEditorLayer*>(this) != nullptr && m_player1;
		if (editorPlay) {
			std::lock_guard lock(g_mutex);
			if (g_auto.armed && g_auto.active && !m_player1->m_isDead) {
				float x = m_player1->getPositionX();
				while (g_auto.next < g_auto.events.size() && x >= g_auto.events[g_auto.next].x) {
					bool press = g_auto.events[g_auto.next].press;
					if (press != g_auto.pressed) {
						this->handleButton(press, 1, true);
						g_auto.pressed = press;
					}
					++g_auto.next;
				}
			}
		}
		GJBaseGameLayer::processCommands(dt, isHalfTick, isLastTick);
		if (!editorPlay) return;

		std::lock_guard lock(g_mutex);
		if (!g_auto.armed) return;
		auto p = m_player1;
		auto pos = toLevel(p->getPosition());
		if (p->m_isDead && !g_auto.wasDead) {
			g_auto.wasDead = true;
			g_auto.deaths.push_back(pos.x);
			g_auto.deathYs.push_back(pos.y);
			if (g_auto.pressed) {
				this->handleButton(false, 1, true);
				g_auto.pressed = false;
			}
			if (g_auto.stopOnDeath) g_auto.active = false;
			g_auto.next = 0;  // a respawn starts the script from the beginning
		} else if (!p->m_isDead && g_auto.wasDead) {
			g_auto.wasDead = false;
		}
		if (!p->m_isDead) {
			g_auto.maxX = std::max(g_auto.maxX, pos.x);
			if (g_auto.traceEvery > 0 && g_auto.active && ++g_auto.stepCounter % g_auto.traceEvery == 0 &&
				g_auto.trace.size() < MAX_TRACE)
				g_auto.trace.push_back({pos.x, pos.y, (float)p->m_yVelocity, modeOf(p), p->m_isUpsideDown, p->m_isOnGround});
		}
	}
};

// params: inputs [[x, press(bool)], ...] in level-string x (sorted or not), stop_on_death? (default true),
// trace_every? (physics steps between trace points; 0 = off, 4 = every 1/60 s).
// Arms the script; start the run with playtest action=start (from_x allowed: events before it are skipped).
BRIDGE_COMMAND(autoplay) {
	requireEditor();
	auto inputs = optField(params, "inputs");
	if (!inputs || !inputs->isArray()) throw RpcError("invalid_params", "'inputs' must be a list of [x, press]");
	std::vector<InputEvent> events;
	for (auto const& e : inputs->asArray().unwrap()) {
		if (!e.isArray() || e.size() != 2 || !e[0].isNumber())
			throw RpcError("invalid_params", "each input must be [x, true|false]");
		events.push_back({(float)e[0].asDouble().unwrap(), e[1].isBool() ? e[1].asBool().unwrap() : e[1].asInt().unwrapOr(0) != 0});
	}
	std::stable_sort(events.begin(), events.end(), [](auto const& a, auto const& b) { return a.x < b.x; });
	std::lock_guard lock(g_mutex);
	g_auto = AutoplayState{};
	g_auto.armed = true;
	g_auto.events = std::move(events);
	g_auto.stopOnDeath = optBool(params, "stop_on_death").value_or(true);
	g_auto.traceEvery = std::max(0, (int)optNumber(params, "trace_every").value_or(0));
	return matjson::makeObject({{"armed", true}, {"events", (int)g_auto.events.size()}});
}

// params: trace? (bool). Off the main thread: only reads the state under the mutex.
BRIDGE_COMMAND_OFF_THREAD(autoplay_status) {
	bool withTrace = optBool(params, "trace").value_or(false);
	std::lock_guard lock(g_mutex);
	auto deaths = matjson::Value::array();
	for (std::size_t i = 0; i < g_auto.deaths.size(); ++i)
		deaths.push(matjson::makeObject({{"x", g_auto.deaths[i]}, {"y", g_auto.deathYs[i]}}));
	auto out = matjson::makeObject({
		{"armed", g_auto.armed},
		{"active", g_auto.active},
		{"events", (int)g_auto.events.size()},
		{"next_event", (int)g_auto.next},
		{"deaths", deaths},
		{"max_x", g_auto.maxX},
		{"trace_points", (int)g_auto.trace.size()},
	});
	if (withTrace) {
		// compact columns: x, y, vy, mode, upside_down, on_ground
		auto t = matjson::Value::array();
		for (auto const& p : g_auto.trace) {
			auto row = matjson::Value::array();
			row.push(std::round(p.x * 100) / 100);
			row.push(std::round(p.y * 100) / 100);
			row.push(std::round(p.vy * 1000) / 1000);
			row.push(p.mode);
			row.push(p.upsideDown ? 1 : 0);
			row.push(p.onGround ? 1 : 0);
			t.push(row);
		}
		out["trace"] = t;
	}
	return out;
}

BRIDGE_COMMAND(autoplay_clear) {
	std::lock_guard lock(g_mutex);
	if (g_auto.pressed) {
		if (auto lel = LevelEditorLayer::get()) lel->handleButton(false, 1, true);
	}
	g_auto = AutoplayState{};
	return matjson::makeObject({{"cleared", true}});
}
