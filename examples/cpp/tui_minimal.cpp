// tui_minimal.cpp — the mechanics of a TUI that does not fall apart. ncurses.
//
// This is NOT a design. It is deliberately ugly. It exists so you never have
// to debug the four things that make people give up on curses, and can spend
// your time on the part we are actually grading. The Python twin is
// examples/python/tui_minimal.py — same structure, same comments.
//
//   1. RESIZE. Terminals change size while you are running. ncurses delivers
//      KEY_RESIZE; ignore it and your layout is corrupt for the rest of the
//      session. Drag your terminal edge while this runs.
//
//   2. TOO SMALL. At some point the window cannot hold your layout. Garbling
//      is not acceptable and neither is crashing. Say so, in words, and
//      recover the moment there is room again.
//
//   3. NO COLOR. `NO_COLOR=1 ./tui_minimal` must still be fully usable, and so
//      must a monochrome terminal. Roughly 1 in 12 men has a color vision
//      deficiency, and your operator may be on a washed-out projector. Every
//      state here carries a TEXT marker as well as a color. Never encode
//      meaning in color alone.
//
//   4. INPUT LATENCY. nodelay() makes getch() non-blocking so the render loop
//      never stalls waiting for a keypress. A TUI that pauses its animation
//      while you hold a key feels broken.
//
// Build:  make tui        (needs ncurses: apt install libncurses-dev,
//                          brew install ncurses, or use FTXUI on Windows)
// Keys:   q quit   ? help   space pause   r restart

#include <ncurses.h>

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <string>
#include <thread>
#include <vector>

#include "scenario.hpp"

using namespace lm;

// Semantic names, not color names. When you decide FAULT should be orange
// instead of red you change one line and nothing else mentions a color. This
// is the smallest possible design-token file — yours will be bigger and
// SHARED WITH ALL THREE SURFACES.
enum Token { TOK_NOMINAL = 1, TOK_DEGRADED, TOK_FAULT, TOK_MUTED };
static const char* MARK[] = {"", "[ OK ]", "[WARN]", "[FAIL]", "      "};

static constexpr int MIN_W = 60, MIN_H = 16;

struct App {
    ScenarioPlayer& player;
    bool use_color = false, paused = false, show_help = false;
    std::deque<ScenarioPlayer::Note> log;
    int h = 0, w = 0;
    double pause_started = 0;

    explicit App(ScenarioPlayer& p) : player(p) {
        use_color = has_colors() && std::getenv("NO_COLOR") == nullptr;
        curs_set(0);
        nodelay(stdscr, TRUE);          // (4) never block the loop on input
        keypad(stdscr, TRUE);
        if (use_color) {
            start_color();
            use_default_colors();
            init_pair(TOK_NOMINAL,  COLOR_GREEN,  -1);
            init_pair(TOK_DEGRADED, COLOR_YELLOW, -1);
            init_pair(TOK_FAULT,    COLOR_RED,    -1);
            init_pair(TOK_MUTED,    COLOR_CYAN,   -1);
        }
        on_resize();
    }

    void on_resize() { getmaxyx(stdscr, h, w); clear(); }   // (1)

    int attr(Token t) const {
        if (!use_color) return (t == TOK_FAULT) ? A_BOLD : A_NORMAL;
        return COLOR_PAIR(t);
    }

    // Clipped write. ncurses errors if you write off-screen, so clip, always.
    void put(int y, int x, const std::string& s, Token t = TOK_MUTED, bool bold = false) {
        if (y < 0 || y >= h || x >= w) return;
        std::string txt = s.substr(0, std::max(0, w - x - 1));
        if (txt.empty()) return;
        int a = attr(t) | (bold ? A_BOLD : 0);
        attron(a); mvaddstr(y, x, txt.c_str()); attroff(a);
    }

    static Token sensor_token(const std::string& v) {
        if (v == "ok") return TOK_NOMINAL;
        if (v == "degraded") return TOK_DEGRADED;
        if (v == "down" || v == "lost") return TOK_FAULT;
        return TOK_MUTED;
    }

    void draw_too_small() {                                  // (2)
        erase();
        char msg[96];
        std::snprintf(msg, sizeof msg, "Window too small: %dx%d, need %dx%d", w, h, MIN_W, MIN_H);
        put(h / 2, std::max(0, (w - int(strlen(msg))) / 2), msg, TOK_DEGRADED, true);
        const char* hint = "resize the terminal or press q";
        put(h / 2 + 1, std::max(0, (w - int(strlen(hint))) / 2), hint);
        refresh();
    }

    void draw(const Tick& tk) {
        erase();
        put(0, 0, std::string(std::max(0, w - 1), '-'));
        put(0, 2, " ROVER-01  " + tk.state + " ", TOK_MUTED, true);
        char clock[64];
        std::snprintf(clock, sizeof clock, " t=%6.1fs %s ", tk.t, paused ? "[PAUSED]" : "");
        put(0, std::max(0, w - int(strlen(clock)) - 2), clock);

        // (3) every state gets a TEXT marker as well as a color
        double b = tk.battery_pct;
        Token bt = b < 8 ? TOK_FAULT : (b < 20 ? TOK_DEGRADED : TOK_NOMINAL);
        char line[128];
        std::snprintf(line, sizeof line, "BATTERY %s %5.1f%%", MARK[bt], b);
        put(2, 2, line, bt, bt == TOK_FAULT);
        int bar = std::clamp(w - 34, 10, 30);
        int filled = int(bar * b / 100.0 + 0.5);
        put(2, 30, std::string(filled, '#') + std::string(bar - filled, '.'), bt);

        int y = 4;
        const char* names[] = {"lidar", "imu", "comms"};
        const std::string vals[] = {tk.lidar, tk.imu, tk.comms};
        for (int i = 0; i < 3; ++i) {
            Token t = sensor_token(vals[i]);
            std::snprintf(line, sizeof line, "%-6s %s %s", names[i], MARK[t], vals[i].c_str());
            put(y++, 2, line, t);
        }

        ++y;
        put(y, 2, "TASK    " + (tk.task.empty() ? std::string("(none)") : tk.task));
        if (tk.task_total) {
            std::snprintf(line, sizeof line, "        %d/%d", tk.task_idx, tk.task_total);
            put(y + 1, 2, line);
        }
        std::snprintf(line, sizeof line, "POSE    x=%6.2f  y=%6.2f  hdg=%5.1f  v=%.2f",
                      tk.x, tk.y, tk.heading, tk.speed);
        put(y + 2, 2, line);

        if (tk.estop) put(y + 4, 2, "  *** EMERGENCY STOP ENGAGED ***  ", TOK_FAULT, true);

        int ly = y + 6;
        put(ly, 2, "EVENTS", TOK_MUTED, true);
        int room = std::max(1, h - ly - 3);
        int start = std::max(0, int(log.size()) - room);
        for (int i = start; i < int(log.size()); ++i) {
            std::snprintf(line, sizeof line, "%6.1f  %s", log[i].first, log[i].second.c_str());
            put(ly + 1 + (i - start), 2, line);
        }

        put(h - 1, 2, "q quit   ? help   space pause   r restart");
        if (show_help) draw_help();
        refresh();
    }

    void draw_help() {
        const std::vector<std::string> lines = {
            "KEYS", "", "  q      quit", "  ?      toggle this help",
            "  space  pause / resume", "  r      restart scenario", "",
            "  Esc or ? closes this overlay."};
        size_t bw = 0;
        for (auto& s : lines) bw = std::max(bw, s.size());
        bw += 4;
        int bh = int(lines.size()) + 2;
        int y0 = std::max(0, (h - bh) / 2), x0 = std::max(0, (w - int(bw)) / 2);
        for (int i = 0; i < bh; ++i) put(y0 + i, x0, std::string(bw, ' '));
        for (size_t i = 0; i < lines.size(); ++i)
            put(y0 + 1 + int(i), x0 + 2, lines[i], TOK_MUTED, i == 0);
    }

    void run() {
        while (true) {
            double now = ScenarioPlayer::now();
            int ch;
            while ((ch = getch()) != ERR) {
                if (ch == KEY_RESIZE) on_resize();
                else if (ch == 'q' || ch == 'Q') return;
                else if (ch == '?') show_help = !show_help;
                else if (ch == 27) show_help = false;       // Esc always backs out
                else if (ch == ' ') {
                    paused = !paused;
                    if (paused) pause_started = ScenarioPlayer::now();
                    else player.nudge_clock(ScenarioPlayer::now() - pause_started);
                } else if (ch == 'r' || ch == 'R') { player.restart(); log.clear(); }
            }

            if (w < MIN_W || h < MIN_H) {
                draw_too_small();
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
                continue;
            }

            static Tick frozen;
            const Tick* tk;
            if (!paused) {
                tk = &player.poll();
                frozen = *tk;
                for (auto& n : player.drain_notes()) {
                    log.push_back(n);
                    if (log.size() > 200) log.pop_front();
                }
            } else {
                tk = &frozen;
            }
            draw(*tk);

            double spent = ScenarioPlayer::now() - now;
            if (spent < 1.0 / 30)
                std::this_thread::sleep_for(std::chrono::duration<double>(1.0 / 30 - spent));
        }
    }
};

int main(int argc, char** argv) {
    const char* path = "../../scenario/scenario.jsonl";
    double speed = 1.0;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--file") && i + 1 < argc) path = argv[++i];
        else if (!strcmp(argv[i], "--speed") && i + 1 < argc) speed = atof(argv[++i]);
    }
    ScenarioPlayer player(path, speed, /*loop=*/true);
    initscr();
    noecho();
    cbreak();
    App app(player);
    app.run();
    endwin();
    return 0;
}
