# examples/cpp — build the C++ starters.
#
#   make            build ./demo  (no dependencies beyond a C++17 compiler)
#   make tui        build ./tui_minimal  (needs ncurses)
#   make all        both
#   make run        build and run the capability probe
#   make clean
#
# ncurses:
#   Debian/Ubuntu/WSL  sudo apt install build-essential libncurses-dev
#   macOS              xcode-select --install    (ncurses ships with it)
#   Windows            build under WSL, or use FTXUI (header-only, no ncurses)
#
# Everything except tui_minimal is header-only and dependency-free, so if
# ncurses is a problem on your machine it only blocks the TUI starter, never
# the matrix work.

CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic
LDLIBS_TUI ?= -lncurses

.PHONY: all demo tui run clean

demo: demo.cpp matrix_sim.hpp gamma.hpp easing.hpp scenario.hpp
	$(CXX) $(CXXFLAGS) -o demo demo.cpp

tui: tui_minimal.cpp scenario.hpp
	$(CXX) $(CXXFLAGS) -o tui_minimal tui_minimal.cpp $(LDLIBS_TUI)

all: demo tui

run: demo
	./demo probe

clean:
	rm -f demo tui_minimal
