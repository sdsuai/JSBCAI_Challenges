// matrix_sim.hpp — a 64x32 RGB LED matrix, simulated in your terminal. C++17,
// header-only, no dependencies.
//
// Same design as examples/python/matrix_sim.py — read that file's header for
// the full explanation. Summary:
//
// The glyph U+2580 "UPPER HALF BLOCK" paints its FOREGROUND color on the top
// half of a character cell and its BACKGROUND color on the bottom half. So one
// terminal character is two vertically stacked pixels, and a 64x32 matrix fits
// in 64 columns x 16 rows of an ordinary terminal. No SDL, no windowing, no
// hardware.
//
//     +------------+
//     |  fg color  |  <- pixel (x, y)
//     |  bg color  |  <- pixel (x, y+1)
//     +------------+
//
// `Matrix` is the DRIVER INTERFACE: set_pixel / fill / show / close. A real
// HUB75 panel is another implementation of the same four methods. Your
// animation code must talk to the interface and must not know which backend it
// is holding — that is worth marks in Part B.
//
//     Panel::Srgb  buffer holds perceptual sRGB, displayed as-is ("what a
//                  monitor does"). Good for composing your layout.
//     Panel::Led   buffer is interpreted as LINEAR PWM DUTY, exactly like real
//                  hardware. Run your fade in this mode, watch it break, then
//                  fix it with lm::build_lut(). See gamma.hpp.
//
// Usage:
//     lm::TerminalMatrix m(64, 32, lm::Panel::Led);
//     m.fill(0,0,0);
//     m.set_pixel(10, 4, 255, 40, 40);
//     m.show();

#pragma once
#include <algorithm>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <vector>

#include "gamma.hpp"

#ifdef _WIN32
#  include <windows.h>
#else
#  include <sys/ioctl.h>
#  include <unistd.h>
#endif

namespace lm {

enum class Panel { Srgb, Led };

inline void enable_vt_mode() {
#ifdef _WIN32
    // Windows consoles need ANSI escape processing switched on explicitly.
    // Without this you see raw escape codes instead of color.
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD mode = 0;
    if (GetConsoleMode(h, &mode))
        SetConsoleMode(h, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
    SetConsoleOutputCP(CP_UTF8);
#endif
}

inline void terminal_size(int& cols, int& rows) {
    cols = 80; rows = 24;
#ifdef _WIN32
    CONSOLE_SCREEN_BUFFER_INFO info;
    if (GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &info)) {
        cols = info.srWindow.Right - info.srWindow.Left + 1;
        rows = info.srWindow.Bottom - info.srWindow.Top + 1;
    }
#else
    struct winsize ws{};
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 && ws.ws_col > 0) {
        cols = ws.ws_col; rows = ws.ws_row;
    }
#endif
}

// ---------------------------------------------------------------------------
// The driver interface. Your animation code should only ever see this.
// ---------------------------------------------------------------------------
class Matrix {
public:
    Matrix(int width, int height) : width_(width), height_(height) {}
    virtual ~Matrix() = default;

    virtual void set_pixel(int x, int y, uint8_t r, uint8_t g, uint8_t b) = 0;
    virtual void fill(uint8_t r = 0, uint8_t g = 0, uint8_t b = 0) = 0;
    virtual void show(double t = -1.0) = 0;   // push framebuffer; once per frame
    virtual void close() {}

    int width()  const { return width_; }
    int height() const { return height_; }

    // Convenience built on the primitives.
    void rect(int x, int y, int w, int h, uint8_t r, uint8_t g, uint8_t b,
              bool filled = true) {
        if (filled) {
            for (int yy = y; yy < y + h; ++yy)
                for (int xx = x; xx < x + w; ++xx) set_pixel(xx, yy, r, g, b);
        } else {
            for (int xx = x; xx < x + w; ++xx) {
                set_pixel(xx, y, r, g, b);
                set_pixel(xx, y + h - 1, r, g, b);
            }
            for (int yy = y; yy < y + h; ++yy) {
                set_pixel(x, yy, r, g, b);
                set_pixel(x + w - 1, yy, r, g, b);
            }
        }
    }
    void hline(int x, int y, int w, uint8_t r, uint8_t g, uint8_t b) {
        for (int xx = x; xx < x + w; ++xx) set_pixel(xx, y, r, g, b);
    }
    void vline(int x, int y, int h, uint8_t r, uint8_t g, uint8_t b) {
        for (int yy = y; yy < y + h; ++yy) set_pixel(x, yy, r, g, b);
    }

protected:
    int width_, height_;
};

// ---------------------------------------------------------------------------
// Half-block terminal backend.
// ---------------------------------------------------------------------------
class TerminalMatrix : public Matrix {
public:
    TerminalMatrix(int width = 64, int height = 32, Panel panel = Panel::Srgb,
                   const std::string& luma_log = "", bool alt_screen = true)
        : Matrix(width, height), panel_(panel), alt_screen_(alt_screen),
          buf_(static_cast<size_t>(width) * height * 3, 0) {
        if (height % 2 != 0) {
            std::fprintf(stderr, "height must be even (two pixels share one cell)\n");
            std::exit(2);
        }
        if (panel_ == Panel::Led) display_lut_ = build_inverse_lut();

        if (!luma_log.empty()) {
            luma_.open(luma_log);
            luma_ << "t,mean_luminance\n";
        }

        enable_vt_mode();
        check_size();

        instance_ = this;
        std::signal(SIGINT, &TerminalMatrix::on_sigint);
        std::atexit(&TerminalMatrix::on_exit);

        std::string init;
        if (alt_screen_) init += "\x1b[?1049h";
        init += "\x1b[?25l";
        std::fwrite(init.data(), 1, init.size(), stdout);
        std::fflush(stdout);
        t0_ = now_seconds();
    }

    ~TerminalMatrix() override { close(); }

    void set_pixel(int x, int y, uint8_t r, uint8_t g, uint8_t b) override {
        if (x < 0 || y < 0 || x >= width_ || y >= height_) return;  // clip, not an error
        size_t i = (static_cast<size_t>(y) * width_ + x) * 3;
        buf_[i] = r; buf_[i + 1] = g; buf_[i + 2] = b;
    }

    void fill(uint8_t r = 0, uint8_t g = 0, uint8_t b = 0) override {
        for (size_t i = 0; i < buf_.size(); i += 3) {
            buf_[i] = r; buf_[i + 1] = g; buf_[i + 2] = b;
        }
    }

    // One frame -> one write() call. Two things keep this smooth:
    //   1. Build the whole frame into one string and write it once. Per-cell
    //      writes make the terminal flush 1024 times and it crawls.
    //   2. Only emit a color escape when the color changes from the previous
    //      cell. Flat regions collapse to a few bytes.
    void show(double t = -1.0) override {
        out_.clear();
        out_ += "\x1b[H";
        int last_fg[3] = {-1, -1, -1}, last_bg[3] = {-1, -1, -1};

        for (int row = 0; row < height_ / 2; ++row) {
            size_t top = static_cast<size_t>(row) * 2 * width_ * 3;
            size_t bot = top + static_cast<size_t>(width_) * 3;
            for (int x = 0; x < width_; ++x) {
                int fr = buf_[top + x*3], fg = buf_[top + x*3 + 1], fb = buf_[top + x*3 + 2];
                int br = buf_[bot + x*3], bg = buf_[bot + x*3 + 1], bb = buf_[bot + x*3 + 2];
                if (panel_ == Panel::Led) {
                    fr = display_lut_[fr]; fg = display_lut_[fg]; fb = display_lut_[fb];
                    br = display_lut_[br]; bg = display_lut_[bg]; bb = display_lut_[bb];
                }
                if (fr != last_fg[0] || fg != last_fg[1] || fb != last_fg[2]) {
                    append_color(out_, 38, fr, fg, fb);
                    last_fg[0] = fr; last_fg[1] = fg; last_fg[2] = fb;
                }
                if (br != last_bg[0] || bg != last_bg[1] || bb != last_bg[2]) {
                    append_color(out_, 48, br, bg, bb);
                    last_bg[0] = br; last_bg[1] = bg; last_bg[2] = bb;
                }
                out_ += "\xe2\x96\x80";   // U+2580 UPPER HALF BLOCK, UTF-8
            }
            // Position the next row explicitly rather than emitting a newline:
            // a newline on the last row scrolls the screen and shears the frame.
            char pos[24];
            std::snprintf(pos, sizeof pos, "\x1b[0m\x1b[%d;1H", row + 2);
            out_ += pos;
            last_fg[0] = last_fg[1] = last_fg[2] = -1;
            last_bg[0] = last_bg[1] = last_bg[2] = -1;
        }

        std::fwrite(out_.data(), 1, out_.size(), stdout);
        std::fflush(stdout);
        ++frames_;

        if (luma_.is_open()) {
            double stamp = (t >= 0.0) ? t : (now_seconds() - t0_);
            luma_ << stamp << "," << mean_luminance() << "\n";
        }
    }

    void close() override {
        if (closed_) return;
        closed_ = true;
        std::string tail = "\x1b[0m\x1b[?25h";
        if (alt_screen_) tail += "\x1b[?1049l";
        std::fwrite(tail.data(), 1, tail.size(), stdout);
        std::fflush(stdout);
        if (luma_.is_open()) luma_.close();
    }

    // Average WCAG relative luminance of the whole panel, 0..1. Sampled every
    // 4th pixel — this runs per frame and exactness buys nothing. It is the
    // FULL-FIELD swing that matters for flash safety, not any one pixel.
    double mean_luminance() const {
        double total = 0.0; int n = 0;
        for (size_t i = 0; i + 2 < buf_.size(); i += 12) {
            total += relative_luminance(buf_[i], buf_[i+1], buf_[i+2]);
            ++n;
        }
        return n ? total / n : 0.0;
    }

    // Print a line of ordinary text under the panel. DEV AID ONLY — your
    // matrix design may not depend on it. A real panel has no caption.
    void status(const std::string& text) const {
        std::printf("\x1b[%d;1H\x1b[2K%s", height_ / 2 + 1, text.c_str());
        std::fflush(stdout);
    }

    double fps() const {
        double dt = now_seconds() - t0_;
        return dt > 0 ? frames_ / dt : 0.0;
    }

    static double now_seconds() {
        using namespace std::chrono;
        return duration<double>(steady_clock::now().time_since_epoch()).count();
    }

private:
    static void append_color(std::string& s, int which, int r, int g, int b) {
        char tmp[32];
        std::snprintf(tmp, sizeof tmp, "\x1b[%d;2;%d;%d;%dm", which, r, g, b);
        s += tmp;
    }

    void check_size() const {
        int cols, rows;
        terminal_size(cols, rows);
        int need_c = width_, need_r = height_ / 2 + 2;
        if (cols < need_c || rows < need_r) {
            std::fprintf(stderr,
                "\nTerminal is %dx%d; this matrix needs at least %dx%d.\n"
                "Make the window bigger (or zoom out) and rerun.\n\n",
                cols, rows, need_c, need_r);
            std::exit(2);
        }
    }

    static void on_sigint(int) { if (instance_) instance_->close(); std::_Exit(130); }
    static void on_exit()      { if (instance_) instance_->close(); }

    Panel panel_;
    bool alt_screen_, closed_ = false;
    std::vector<uint8_t> buf_;
    std::string out_;
    Lut display_lut_{};
    mutable std::ofstream luma_;
    double t0_ = 0.0;
    long frames_ = 0;
    static inline TerminalMatrix* instance_ = nullptr;
};

}  // namespace lm
