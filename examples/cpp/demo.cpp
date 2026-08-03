// demo.cpp — run these before you write a line of your own code.
//
//   ./demo probe     is my terminal capable? start here
//   ./demo sweep     color, half-blocks, and a delta-time animation loop
//   ./demo gamma     the gamma bug and its fix, side by side
//   ./demo easing    linear vs eased motion
//   ./demo alarm     a legibility test at 3 metres
//   ./demo scenario  read the canonical timeline and print its events
//
// Mirrors examples/python/matrix_sim.py --demo <name> exactly.

#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

#include "easing.hpp"
#include "gamma.hpp"
#include "matrix_sim.hpp"
#include "scenario.hpp"

using namespace lm;

static void hsv(double h, double s, double v, uint8_t& R, uint8_t& G, uint8_t& B) {
    int i = static_cast<int>(h * 6.0);
    double f = h * 6.0 - i, p = v * (1 - s), q = v * (1 - f * s), t = v * (1 - (1 - f) * s);
    double r, g, b;
    switch (i % 6) {
        case 0: r = v; g = t; b = p; break;
        case 1: r = q; g = v; b = p; break;
        case 2: r = p; g = v; b = t; break;
        case 3: r = p; g = q; b = v; break;
        case 4: r = t; g = p; b = v; break;
        default: r = v; g = p; b = q; break;
    }
    R = uint8_t(r * 255); G = uint8_t(g * 255); B = uint8_t(b * 255);
}

static void frame_cap(double frame_start, double fps) {
    double budget = 1.0 / fps;
    double spent = TerminalMatrix::now_seconds() - frame_start;
    if (spent < budget)
        std::this_thread::sleep_for(std::chrono::duration<double>(budget - spent));
}

// ---------------------------------------------------------------------------

static int demo_probe() {
    enable_vt_mode();
    std::printf("If you see a red, a green and a blue block below, you are good:\n");
    const int cols[3][3] = {{220,60,50},{60,200,110},{70,130,240}};
    for (auto& c : cols) {
        std::printf("\x1b[38;2;%d;%d;%dm", c[0], c[1], c[2]);
        for (int i = 0; i < 20; ++i) std::printf("\xe2\x96\x80");
        std::printf("\x1b[0m\n");
    }
    std::printf("\nIf you see escape sequences as literal text instead, your terminal\n"
                "does not have 24-bit color. On Windows use Windows Terminal or WSL.\n");
    int c, r; terminal_size(c, r);
    std::printf("\nTerminal size: %dx%d  (need >= 64x18)\n", c, r);
    return 0;
}

static int demo_sweep(Panel panel) {
    TerminalMatrix m(64, 32, panel);
    double last = TerminalMatrix::now_seconds(), t = 0;
    while (true) {
        double now = TerminalMatrix::now_seconds();
        t += now - last; last = now;
        m.fill(0, 0, 0);
        for (int x = 0; x < m.width(); ++x) {
            uint8_t r, g, b;
            hsv(std::fmod(double(x) / m.width() + t * 0.15, 1.0), 1.0, 1.0, r, g, b);
            int h = int(2 + 14 * (0.5 + 0.5 * std::sin(t * 2.0 + x * 0.2)));
            for (int y = m.height()/2 - h/2; y < m.height()/2 + h/2; ++y)
                m.set_pixel(x, y, r, g, b);
        }
        m.show();
        char buf[96];
        std::snprintf(buf, sizeof buf, "sweep  %5.1f fps   Ctrl+C to quit", m.fps());
        m.status(buf);
        frame_cap(now, 30.0);
    }
}

// The whole point of gamma.hpp, made visible.
//   TOP    raw linear values written straight to the panel
//   BOTTOM the same values pushed through the gamma LUT first
// The top ramp reaches "bright" a third of the way across and then stops
// changing. The bottom one fades evenly. That is the bug and that is the fix.
static int demo_gamma() {
    Lut lut = build_lut();
    TerminalMatrix m(64, 32, Panel::Led);
    m.fill(0, 0, 0);
    for (int x = 0; x < m.width(); ++x) {
        uint8_t v = uint8_t(std::lround(255.0 * x / (m.width() - 1)));
        for (int y = 2;  y < 13; ++y) m.set_pixel(x, y, v, v, v);          // raw  -> wrong
        for (int y = 19; y < 30; ++y) { uint8_t c = lut[v]; m.set_pixel(x, y, c, c, c); }
        m.set_pixel(x, 15, 20, 20, 30);
        m.set_pixel(x, 16, 20, 20, 30);
    }
    m.show();
    m.status("TOP = raw linear duty (bunches up, then plateaus)");
    std::printf("\n  BOTTOM = gamma-encoded (even fade)  --  Enter to quit");
    std::fflush(stdout);
    std::getchar();
    m.close();
    return 0;
}

static int demo_easing(Panel panel) {
    struct Row { const char* name; double (*fn)(double); uint8_t c[3]; };
    const Row rows[] = {
        {"linear",        ease::linear,       {120, 120, 120}},
        {"out_cubic",     ease::out_cubic,    { 80, 200, 255}},
        {"in_out_cubic",  ease::in_out_cubic, {120, 255, 140}},
        {"out_back",      ease::out_back,     {255, 170,  60}},
    };
    TerminalMatrix m(64, 32, panel);
    double last = TerminalMatrix::now_seconds(), t = 0, period = 2.2;
    while (true) {
        double now = TerminalMatrix::now_seconds();
        t += now - last; last = now;
        m.fill(4, 4, 8);
        double p = ease::ping_pong(std::fmod(t, period) / period);
        for (int i = 0; i < 4; ++i) {
            double v = rows[i].fn(p);
            int x = int(std::lround(2 + v * (m.width() - 8)));
            m.rect(x, 3 + i * 7, 4, 4, rows[i].c[0], rows[i].c[1], rows[i].c[2]);
        }
        m.show();
        m.status("linear / out_cubic / in_out_cubic / out_back");
        frame_cap(now, 30.0);
    }
}

// A legibility probe, not a design to copy.
//
// Stand up and walk 3 metres away. Squint. Can you still tell these three
// states apart? That is the bar Part B has to clear, and it is why color alone
// will not save you: the shapes and the MOTION differ too, so the states
// survive both distance and colorblindness.
//
// Note the pulse rate: 1.2 Hz, deliberately far below the 3-60 Hz band that
// can trigger photosensitive seizures. See README Part B.
static int demo_alarm(Panel panel) {
    struct St { const char* name; uint8_t c[3]; double hz; int kind; };  // kind 0 steady 1 pulse 2 sweep
    const St states[] = {
        {"NOMINAL",  { 40, 200, 120}, 0.30, 0},
        {"DEGRADED", {240, 170,  40}, 1.20, 1},
        {"FAULT",    {255,  60,  50}, 1.20, 2},
    };
    TerminalMatrix m(64, 32, panel);
    double last = TerminalMatrix::now_seconds(), t = 0;
    while (true) {
        double now = TerminalMatrix::now_seconds();
        t += now - last; last = now;
        const St& s = states[int(t / 3.0) % 3];
        m.fill(2, 2, 4);
        double phase = std::fmod(t * s.hz, 1.0);
        double k = (s.kind == 1) ? 0.35 + 0.65 * ease::smoothstep(ease::ping_pong(phase)) : 1.0;
        uint8_t r = uint8_t(s.c[0]*k), g = uint8_t(s.c[1]*k), b = uint8_t(s.c[2]*k);

        if (s.kind == 0) {
            m.rect(24, 12, 16, 8, r, g, b);
        } else if (s.kind == 1) {
            m.rect(22, 10, 20, 12, r, g, b, false);
            m.rect(26, 14, 12, 4, r, g, b);
        } else {
            m.rect(20, 8, 24, 16, r, g, b, false);
            for (int i = -6; i <= 6; ++i) {
                m.set_pixel(32 + i, 16 + i, r, g, b);
                m.set_pixel(32 + i, 16 - i, r, g, b);
            }
            int x = int(ease::in_out_cubic(ease::ping_pong(phase)) * (m.width() - 1));
            m.vline(x, 0, m.height(), 90, 20, 20);
        }
        m.show();
        char buf[96];
        std::snprintf(buf, sizeof buf, "%-9s — walk 3 m back. Still unambiguous?", s.name);
        m.status(buf);
        frame_cap(now, 30.0);
    }
}

static int demo_scenario(const char* path) {
    ScenarioPlayer p(path);
    std::printf("%zu ticks, %.1fs\n\n", p.ticks().size(), p.duration());
    std::printf("%7s  %-9s %6s  %-9s%-7s%-7s %s\n",
                "t", "state", "batt", "lidar", "imu", "comms", "event");
    for (const auto& tk : p.ticks()) {
        if (tk.note.empty()) continue;
        std::printf("%7.1f  %-9s %5.1f%%  %-9s%-7s%-7s %s\n",
                    tk.t, tk.state.c_str(), tk.battery_pct, tk.lidar.c_str(),
                    tk.imu.c_str(), tk.comms.c_str(), tk.note.c_str());
    }
    return 0;
}

int main(int argc, char** argv) {
    std::string which = argc > 1 ? argv[1] : "sweep";
    Panel panel = Panel::Srgb;
    const char* scenario = "../../scenario/scenario.jsonl";
    for (int i = 2; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--led"))  panel = Panel::Led;
        if (!std::strcmp(argv[i], "--file") && i + 1 < argc) scenario = argv[++i];
    }
    if (which == "probe")    return demo_probe();
    if (which == "sweep")    return demo_sweep(panel);
    if (which == "gamma")    return demo_gamma();
    if (which == "easing")   return demo_easing(panel);
    if (which == "alarm")    return demo_alarm(panel);
    if (which == "scenario") return demo_scenario(scenario);
    std::fprintf(stderr, "usage: %s [probe|sweep|gamma|easing|alarm|scenario] [--led] [--file P]\n", argv[0]);
    return 2;
}
