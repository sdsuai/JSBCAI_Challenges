// scenario.hpp — replays scenario/scenario.jsonl against a wall clock. C++17,
// header-only, no JSON library required.
//
// scenario.jsonl is deliberately FLAT: every value is a number or a plain
// string, no nesting, no arrays, no escapes beyond the ordinary. That is why
// the ~40-line parser below is enough and you do not need to vendor nlohmann.
// (You may vendor it if you prefer — this is a convenience, not a constraint.)
//
// The player is PULL-BASED. It does not own a loop, does not call you back,
// does not sleep. Your render loop stays in charge and asks "what is true
// now?" once per frame:
//
//     lm::ScenarioPlayer p("../../scenario/scenario.jsonl", 1.0, true);
//     while (true) {
//         const lm::Tick& tk = p.poll();
//         for (auto& [t, note] : p.drain_notes()) log.push_back(note);
//         render(tk, dt);
//     }
//
// Why this shape matters for grading: it forces you to separate
//     STATE  (what is true now — drives the layout)  from
//     EVENTS (what just happened — drives the log and the animations).
// A design that conflates them either loses transient faults or animates
// things that did not change. The 3.5-second comms dropout at t=26 is the
// test case.

#pragma once
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace lm {

struct Tick {
    double t = 0;
    std::string state;
    double battery_pct = 0;
    double x = 0, y = 0, heading = 0, speed = 0;
    std::string lidar, imu, comms;
    std::string task;
    int task_idx = 0, task_total = 0;
    int estop = 0;
    std::string note;

    // Convenience only. NOTE: we deliberately do NOT give you an "alarm" field
    // or a severity ranking. Deciding what counts as an alarm, how to rank two
    // simultaneous ones, and what the operator sees first IS the design work
    // being assessed.
    bool moving() const { return speed > 0.01; }
    std::vector<std::string> sensors_down() const {
        std::vector<std::string> v;
        if (lidar == "down") v.push_back("lidar");
        if (imu   == "down") v.push_back("imu");
        if (comms == "down" || comms == "lost") v.push_back("comms");
        return v;
    }
};

namespace detail {

// Find "key": and return the raw value token that follows.
inline bool field(const std::string& line, const std::string& key, std::string& out) {
    std::string pat = "\"" + key + "\":";
    size_t p = line.find(pat);
    if (p == std::string::npos) return false;
    p += pat.size();
    while (p < line.size() && line[p] == ' ') ++p;
    if (p >= line.size()) return false;
    if (line[p] == '"') {
        size_t end = line.find('"', p + 1);
        if (end == std::string::npos) return false;
        out = line.substr(p + 1, end - p - 1);
    } else {
        size_t end = line.find_first_of(",}", p);
        out = line.substr(p, end - p);
    }
    return true;
}

inline double num(const std::string& line, const std::string& key, double dflt = 0) {
    std::string v;
    return field(line, key, v) ? std::atof(v.c_str()) : dflt;
}

inline std::string str(const std::string& line, const std::string& key) {
    std::string v;
    return field(line, key, v) ? v : std::string{};
}

}  // namespace detail

inline Tick parse_tick(const std::string& line) {
    Tick tk;
    tk.t           = detail::num(line, "t");
    tk.state       = detail::str(line, "state");
    tk.battery_pct = detail::num(line, "battery_pct");
    tk.x           = detail::num(line, "x");
    tk.y           = detail::num(line, "y");
    tk.heading     = detail::num(line, "heading");
    tk.speed       = detail::num(line, "speed");
    tk.lidar       = detail::str(line, "lidar");
    tk.imu         = detail::str(line, "imu");
    tk.comms       = detail::str(line, "comms");
    tk.task        = detail::str(line, "task");
    tk.task_idx    = static_cast<int>(detail::num(line, "task_idx"));
    tk.task_total  = static_cast<int>(detail::num(line, "task_total"));
    tk.estop       = static_cast<int>(detail::num(line, "estop"));
    tk.note        = detail::str(line, "note");
    return tk;
}

class ScenarioPlayer {
public:
    using Note = std::pair<double, std::string>;

    explicit ScenarioPlayer(const std::string& path, double speed = 1.0,
                            bool loop = false, double start = 0.0)
        : speed_(speed), start_offset_(start), loop_(loop) {
        std::ifstream f(path);
        if (!f) throw std::runtime_error("cannot open " + path);
        std::string line;
        while (std::getline(f, line))
            if (line.find('{') != std::string::npos) ticks_.push_back(parse_tick(line));
        if (ticks_.empty()) throw std::runtime_error(path + " is empty");
        duration_ = ticks_.back().t;
        t0_ = now();
    }

    double scenario_time() const {
        double el = (now() - t0_) * speed_ + start_offset_;
        if (loop_ && duration_ > 0) el = std::fmod(el, duration_);
        return el;
    }
    bool running() const { return !finished_; }
    double duration() const { return duration_; }
    const std::vector<Tick>& ticks() const { return ticks_; }

    void restart() { t0_ = now(); idx_ = 0; pending_.clear(); finished_ = false; }
    void nudge_clock(double seconds) { t0_ += seconds; }   // used to implement pause

    // Latest tick at or before the current scenario time. Advances through
    // every intervening tick so no note is skipped, even if your frame rate is
    // below the 5 Hz data rate or you stalled.
    const Tick& poll() {
        double n = scenario_time();
        if (loop_ && idx_ > 0 && ticks_[idx_].t > n) idx_ = 0;   // wrapped
        while (idx_ + 1 < ticks_.size() && ticks_[idx_ + 1].t <= n) {
            ++idx_;
            if (!ticks_[idx_].note.empty())
                pending_.emplace_back(ticks_[idx_].t, ticks_[idx_].note);
        }
        if (!loop_ && n >= duration_) finished_ = true;
        return ticks_[idx_];
    }

    // Discrete events since the previous call. Call exactly once per frame.
    std::vector<Note> drain_notes() {
        std::vector<Note> out;
        out.swap(pending_);
        return out;
    }

    // State at an arbitrary time. Handy for tests and for screenshotting a
    // specific moment for your DESIGN.md.
    const Tick& at(double t) const {
        size_t lo = 0, hi = ticks_.size() - 1;
        while (lo < hi) {
            size_t mid = (lo + hi + 1) / 2;
            if (ticks_[mid].t <= t) lo = mid; else hi = mid - 1;
        }
        return ticks_[lo];
    }

    static double now() {
        // Fully qualified: this class has a duration() member, which would
        // otherwise shadow std::chrono::duration here.
        return std::chrono::duration<double>(
                   std::chrono::steady_clock::now().time_since_epoch()).count();
    }

private:
    std::vector<Tick> ticks_;
    std::vector<Note> pending_;
    double speed_, start_offset_, duration_ = 0, t0_ = 0;
    bool loop_, finished_ = false;
    size_t idx_ = 0;
};

}  // namespace lm
