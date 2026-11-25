#!/usr/bin/env python3
"""Verify the rebuild: deterministic render, size, dimensions, story counts.
Usage: python3 verify.py  (run from the entry dir)
"""
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


data = json.loads((HERE / "stories.json").read_text())
n = len(data["heroes"]) + len(data["minis"]) + len(data["briefs"])
check(n == 38, f"38 stories total (got {n})")
check(len(data["heroes"]) == 3, "3 heroes")
check(len(data["minis"]) == 10, "10 minis")
check(len(data["briefs"]) == 25, "25 also-on briefs")
nums = [h["n"] for h in data["heroes"]] + [m["n"] for m in data["minis"]] + [b[0] for b in data["briefs"]]
check(nums == list(range(1, 39)), "stories numbered 1..38")
check(sum(data["regions"].values()) == 38, "region counts sum to 38")
check(len(data["regions"]) == 10, "10 regions")
check(len(data["numbers"]) == 6, "6 IN NUMBERS")
check(len(data["timeline"]) == 7, "7 timeline points")
check(data["kicker"].startswith("38 STORIES"), "kicker names 38 stories")

subprocess.run([sys.executable, "draw.py", "stories.json", "/tmp/vfy1.png"], cwd=HERE, check=True)
subprocess.run([sys.executable, "draw.py", "stories.json", "/tmp/vfy2.png"], cwd=HERE, check=True)
check(sha("/tmp/vfy1.png") == sha("/tmp/vfy2.png"), "render deterministic 2x")
check(sha("/tmp/vfy1.png") == sha(HERE / "entry.png"), "entry.png matches fresh render")
im = Image.open(HERE / "entry.png")
check(im.size == (1024, 1024), f"1024x1024 (got {im.size})")
size = (HERE / "entry.png").stat().st_size
check(size <= 1048576, f"entry.png <= 1 MiB ({size} bytes)")
g = im.convert("L")
px = list(g.getdata())
check(150 < statistics.mean(px) < 245, f"mean brightness sane ({statistics.mean(px):.1f})")

print("FAILURES:" if fails else "ALL PASS", len(fails))
sys.exit(1 if fails else 0)
