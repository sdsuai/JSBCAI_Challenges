"""
contrast.py — is your palette actually readable, or does it just look nice on
your laptop at full brightness in a dark room?

Contrast ratio is the WCAG measure of how far apart two colors are in
luminance. It runs from 1:1 (identical) to 21:1 (black on white).

    >= 4.5 : normal body text            (WCAG AA)
    >= 3.0 : large/bold text, and the boundary of any UI element or graphic
             whose shape carries meaning (WCAG AA, SC 1.4.11)
    >= 7.0 : AAA, worth aiming for on anything safety-relevant

Why this belongs in a design challenge and not just an accessibility checklist:
low-contrast dim grey on dark grey is the single most common way a good-looking
UI becomes unusable in daylight, on a projector, on a cheap panel, or for an
operator over forty. Passing this check is cheap. Failing it is invisible to
you and obvious to everyone else.

Contrast is a property of a PAIR, never of a single color. A token is only
"readable" relative to a background, and if your UI paints the same red on both
the page background and a raised panel, it has to pass against BOTH. So the
palette mode checks every foreground against every surface and reports the
worst case -- which is the only number that matters, because the worst case is
the one your operator will hit.

Use:
    python contrast.py "#e6e9ef" "#12141a"          # one pair
    python contrast.py --palette tokens.json        # every fg x every surface

`tokens.json` format -- and yes, exporting your design tokens as data that a
tool can check is itself part of the point:

    {
      "surfaces": {"bg": "#12141a", "surface": "#1b1f28"},
      "colors":   {"text": "#e6e9ef", "fault": "#e04b45"}
    }

A single `"bg": "#12141a"` key is also accepted as shorthand for one surface.
"""

import argparse
import json
import sys

from gamma import relative_luminance


def parse_hex(s):
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"bad hex color: {s!r}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def contrast_ratio(c1, c2):
    """WCAG 2.x contrast ratio. Order does not matter."""
    l1, l2 = relative_luminance(c1), relative_luminance(c2)
    lo, hi = sorted((l1, l2))
    return (hi + 0.05) / (lo + 0.05)


def grade(ratio):
    if ratio >= 7.0:
        return "AAA", "text and UI, everywhere"
    if ratio >= 4.5:
        return "AA ", "body text ok"
    if ratio >= 3.0:
        return "AA-large", "large/bold text and UI boundaries only"
    return "FAIL", "not usable as a foreground"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("colors", nargs="*", help="two hex colors, e.g. '#fff' '#000'")
    ap.add_argument("--palette", help="JSON file: {bg, colors:{name:hex}}")
    args = ap.parse_args()

    if args.palette:
        with open(args.palette) as f:
            data = json.load(f)

        surfaces = dict(data.get("surfaces") or {})
        if "bg" in data and isinstance(data["bg"], str):
            surfaces.setdefault("bg", data["bg"])
        if not surfaces:
            raise SystemExit("palette needs a 'surfaces' object (or a 'bg' string)")

        fgs = {k: v for k, v in data["colors"].items() if k not in surfaces}
        names = list(surfaces)

        head = f"{'token':<12}{'hex':<10}" + "".join(f"{('on ' + n):>12}" for n in names)
        print("surfaces: " + ",  ".join(f"{n} {h}" for n, h in surfaces.items()) + "\n")
        print(head + f"{'worst':>9}  grade")
        print("-" * len(head + "     worst  grade"))

        worst_overall, failures = 99.0, []
        for name, hexv in fgs.items():
            ratios = [contrast_ratio(parse_hex(hexv), parse_hex(s)) for s in surfaces.values()]
            w = min(ratios)
            worst_overall = min(worst_overall, w)
            g, _ = grade(w)
            if w < 3.0:
                failures.append((name, w))
            row = f"{name:<12}{hexv:<10}" + "".join(f"{r:>10.2f}:1" for r in ratios)
            print(f"{row}{w:>8.2f}  {g}" + ("   <-- FAILS" if w < 3.0 else ""))

        print(f"\nworst pair anywhere: {worst_overall:.2f}:1")
        if failures:
            print("\nBelow 3.0:1 and therefore not usable as a foreground:")
            for name, w in failures:
                print(f"  {name}  ({w:.2f}:1)")
            print("\nEither darken the surface, brighten the token, or stop painting")
            print("that token on that surface. Do not just lower the bar.")
        # Nonzero exit means this is usable as a check in CI or a pre-commit hook.
        sys.exit(0 if not failures else 1)

    if len(args.colors) != 2:
        ap.error("give two hex colors, or use --palette")
    c1, c2 = (parse_hex(c) for c in args.colors)
    r = contrast_ratio(c1, c2)
    g, why = grade(r)
    print(f"{args.colors[0]} on {args.colors[1]}: {r:.2f}:1  -> {g}  ({why})")
    sys.exit(0 if r >= 3.0 else 1)


if __name__ == "__main__":
    main()
