// easing.hpp — motion that reads as intentional instead of mechanical.
//
// Identical curves to examples/python/easing.py; read the commentary there for
// which curve means what. The one-line version: linear motion is the tell of
// an animation nobody designed, and choosing a curve is a design decision you
// will be asked to defend.
//
// Everything takes normalized time t in [0,1] and returns progress in [0,1]
// (ease_out_back and ease_out_elastic deliberately leave that range mid-flight
// — that is the overshoot).

#pragma once
#include <algorithm>
#include <cmath>

namespace lm::ease {

constexpr double kPi = 3.14159265358979323846;

inline double linear(double t)          { return t; }
inline double in_quad(double t)         { return t * t; }
inline double out_quad(double t)        { return 1.0 - (1.0 - t) * (1.0 - t); }
inline double in_out_quad(double t)     { return t < 0.5 ? 2*t*t : 1.0 - std::pow(-2*t + 2, 2)/2.0; }
inline double in_cubic(double t)        { return t * t * t; }
inline double out_cubic(double t)       { return 1.0 - std::pow(1.0 - t, 3); }
inline double in_out_cubic(double t)    { return t < 0.5 ? 4*t*t*t : 1.0 - std::pow(-2*t + 2, 3)/2.0; }
inline double smoothstep(double t)      { return t * t * (3.0 - 2.0 * t); }

inline double out_back(double t) {
    constexpr double c1 = 1.70158, c3 = c1 + 1.0;
    return 1.0 + c3 * std::pow(t - 1.0, 3) + c1 * std::pow(t - 1.0, 2);
}

inline double out_elastic(double t) {
    if (t <= 0.0) return 0.0;
    if (t >= 1.0) return 1.0;
    constexpr double c4 = (2.0 * kPi) / 3.0;
    return std::pow(2.0, -10.0 * t) * std::sin((t * 10.0 - 0.75) * c4) + 1.0;
}

inline double out_bounce(double t) {
    constexpr double n1 = 7.5625, d1 = 2.75;
    if (t < 1.0 / d1)      { return n1 * t * t; }
    else if (t < 2.0 / d1) { t -= 1.5   / d1; return n1 * t * t + 0.75; }
    else if (t < 2.5 / d1) { t -= 2.25  / d1; return n1 * t * t + 0.9375; }
    else                   { t -= 2.625 / d1; return n1 * t * t + 0.984375; }
}

inline double clamp01(double t) { return std::clamp(t, 0.0, 1.0); }
inline double lerp(double a, double b, double t) { return a + (b - a) * t; }

// Map a looping 0..1 onto 0..1..0 — for breathing/pulsing, so the loop does
// not snap back to the start.
inline double ping_pong(double t) { return 1.0 - std::abs(2.0 * t - 1.0); }

// A single value animated against a CLOCK, not against a frame counter.
// The bug this prevents: a loop that sleeps 1/60s per step runs at a different
// speed on every machine and stutters whenever anything else blocks.
class Tween {
public:
    using Fn = double (*)(double);

    Tween(double start = 0.0, double end = 1.0, double duration = 1.0,
          Fn fn = smoothstep, bool loop = false)
        : start_(start), end_(end), duration_(duration > 0 ? duration : 1e-9),
          fn_(fn), loop_(loop) {}

    double update(double dt) {
        elapsed_ += dt;
        if (elapsed_ >= duration_) {
            if (loop_) elapsed_ = std::fmod(elapsed_, duration_);
            else       elapsed_ = duration_;
        }
        return value();
    }

    double value() const {
        return lerp(start_, end_, fn_(clamp01(elapsed_ / duration_)));
    }

    bool done() const { return !loop_ && elapsed_ >= duration_; }
    void reset()      { elapsed_ = 0.0; }

private:
    double start_, end_, duration_, elapsed_ = 0.0;
    Fn fn_;
    bool loop_;
};

}  // namespace lm::ease
