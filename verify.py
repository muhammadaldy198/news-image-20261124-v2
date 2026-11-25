#!/usr/bin/env python3
"""Verify the v2 broadsheet: counts, file gates, banner pixels, pin sanity.

Run after draw.py. Exits non-zero on any failure. No network, no clock.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RED = (176, 0, 32)
failures = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        failures.append(msg)


def main():
    with open(os.path.join(HERE, "stories.json"), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    check(len(data["heroes"]) == 3, "3 heroes")
    check(len(data["minis"]) == 10, "10 minis")
    check(len(data["briefs"]) == 24, "24 briefs")
    total = len(data["heroes"]) + len(data["minis"]) + len(data["briefs"])
    check(total == 37, "37 stories total (%d)" % total)
    check(sum(c for _, c, _ in data["regions"]) == 37, "region sum 37")
    check(len(data["map_pins"]) == 18, "18 map pins")
    nums = {b["n"] for b in data["briefs"]}
    check(nums == set(range(14, 38)), "brief numbers 14..37")
    check({h["n"] for h in data["heroes"]} == {1, 2, 3}, "hero numbers 1..3")
    check({m["n"] for m in data["minis"]} == set(range(4, 14)),
          "mini numbers 4..13")
    check({p["n"] for p in data["map_pins"]} == set(range(1, 19)),
          "pin numbers 1..18")

    path = os.path.join(HERE, "entry.png")
    check(os.path.exists(path), "entry.png exists")
    size = os.path.getsize(path)
    check(size <= 1048576, "entry.png %d bytes <= 1 MiB" % size)
    im = Image.open(path)
    check(im.size == (1024, 1024), "entry.png is 1024x1024 (%s)" % (im.size,))
    check(im.mode == "RGB", "entry.png mode RGB")
    px = im.load()

    # Red banner strip inside every hero art (bottom row of the strip,
    # away from the centred white banner text).
    for i in range(3):
        x0 = 12 + i * (328 + 8)
        check(px[x0 + 6, 214 + 132 - 3] == RED, "hero %d banner red" % (i + 1))
    # Red banner strip inside every mini art.
    mini_ws = [194, 194, 194, 194, 192]
    for r in range(2):
        y0 = 452 + r * 140
        x = 12
        for c in range(5):
            check(px[x + 6, y0 + 56 - 3] == RED,
                  "mini %d banner red" % (r * 5 + c + 4))
            x += mini_ws[c] + 8
    # Date-check box has a red border.
    check(px[12, 950] == RED, "date-check border red")
    # Masthead date ink: sample a pixel inside the big serif date.
    dark = sum(1 for x in range(200, 824, 4) for y in range(30, 84, 4)
               if sum(px[x, y]) < 150)
    check(dark > 50, "masthead date has ink (%d dark samples)" % dark)
    # Map panel exists and holds red pins.
    reds = sum(1 for x in range(660, 1012, 2) for y in range(766, 916, 2)
               if px[x, y] == RED)
    check(reds >= 18, "map holds >=18 red pin samples (%d)" % reds)

    if failures:
        print("VERIFY FAILED: %d checks" % len(failures))
        sys.exit(1)
    print("VERIFY ALL PASS")


if __name__ == "__main__":
    main()
