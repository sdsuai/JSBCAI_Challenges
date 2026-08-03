// gamma.hpp — the difference between "the number you chose" and "the light you get".
//
// Read the long explanation at the top of examples/python/gamma.py. It applies
// here verbatim; this is the same maths in C++ so a mixed-language submission
// produces identical output.
//
// Short version: an LED panel's PWM duty cycle is linear in PHOTONS. Your eye
// is not. Writing a linear 0->255 ramp to a panel gives a fade that rushes to
// bright and then plateaus. Gamma-encode first:
//
//     duty = 255 * (srgb/255)^2.2
//
// Build the LUT once. Do not call std::pow per pixel per frame.

#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

namespace lm {

constexpr double kGamma = 2.2;

inline uint8_t srgb_to_duty(double c, double gamma = kGamma) {
    c = std::clamp(c, 0.0, 255.0);
    return static_cast<uint8_t>(std::lround(255.0 * std::pow(c / 255.0, gamma)));
}

inline uint8_t duty_to_srgb(double d, double gamma = kGamma) {
    d = std::clamp(d, 0.0, 255.0);
    return static_cast<uint8_t>(std::lround(255.0 * std::pow(d / 255.0, 1.0 / gamma)));
}

using Lut = std::array<uint8_t, 256>;

inline Lut build_lut(double gamma = kGamma) {
    Lut t{};
    for (int i = 0; i < 256; ++i) t[i] = srgb_to_duty(i, gamma);
    return t;
}

inline Lut build_inverse_lut(double gamma = kGamma) {
    Lut t{};
    for (int i = 0; i < 256; ++i) t[i] = duty_to_srgb(i, gamma);
    return t;
}

// WCAG relative luminance, 0.0..1.0. Needs LINEAR light, hence the decode.
// Used by the contrast check and by the full-field flash audit.
inline double relative_luminance(uint8_t r, uint8_t g, uint8_t b) {
    auto lin = [](uint8_t v) {
        double c = v / 255.0;
        return c <= 0.04045 ? c / 12.92 : std::pow((c + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

inline double contrast_ratio(double l1, double l2) {
    double lo = std::min(l1, l2), hi = std::max(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
}

}  // namespace lm
