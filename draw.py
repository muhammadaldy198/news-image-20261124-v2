#!/usr/bin/env python3
"""Render Tuesday 24 November 2026 as one broadsheet, 1024x1024.
Fresh layout for the rebuild: masthead is the date itself, 3 heroes with
red banners inside the art, 10 minis, 25 also-on briefs in two columns,
a numbered world map, a UTC timeline, an IN NUMBERS strip and a DATE CHECK.
Deterministic: fixed layout, fixed fonts, no randomness, no network.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = 1024
MARGIN = 12
GUTTER = 8
INK = (24, 24, 22)
PAPER = (250, 247, 238)
RED = (178, 38, 30)
DARK = (28, 30, 34)
GREY = (110, 108, 100)
RULE = (180, 176, 164)
FDIR = "/usr/share/fonts/truetype/noto"

BUDGET = [("kicker", 18), ("masthead", 80), ("numbers", 32), ("timeline", 26),
          ("heroes", 212), ("minis", 278), ("alsoon", 284), ("datecheck", 70),
          ("footer", 24)]
assert sum(h for _, h in BUDGET) == W, "budget must sum to 1024"

def F(name, size):
    return ImageFont.truetype(f"{FDIR}/{name}", size)

def cols(x0, total, n, gutter=GUTTER):
    """Column x positions + widths; remainder pixels go to the first columns."""
    w = (total - gutter * (n - 1)) // n
    rem = total - gutter * (n - 1) - w * n
    xs, ws = [], []
    x = x0
    for i in range(n):
        wi = w + (1 if i < rem else 0)
        xs.append(x); ws.append(wi); x += wi + gutter
    return xs, ws

def wrap(draw, text, font, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def fit_lines(draw, text, font, width, max_lines, what):
    lines = wrap(draw, text, font, width)
    assert len(lines) <= max_lines, f"{what}: {len(lines)} lines > {max_lines}: {text!r}"
    return lines

def banner(draw, x, y, w, text, font, h=20):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=RED)
    draw.text((x + 6, y + (h - font.size) // 2 - 1), text, font=font, fill=(255, 255, 255))

# ---------------------------------------------------------------- painters
def sky(draw, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        draw.line([(x, y + i), (x + w - 1, y + i)], fill=c)

def paint_shanghai(d, x, y, w, h):
    sky(d, x, y, w, h, (28, 44, 74), (64, 92, 128))
    d.ellipse([x + w - 58, y + 8, x + w - 30, y + 36], fill=(232, 214, 150))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(22, 34, 58))
    for bx, bw, bh in [(4, 16, 52), (24, 12, 70), (40, 18, 44), (62, 12, 84), (78, 16, 58)]:
        d.rectangle([x + bx, y + h - 22 - bh, x + bx + bw, y + h - 22], fill=(16, 26, 48))
    # Oriental Pearl: two spheres on a needle
    cx = x + w // 2
    d.line([(cx, y + 14), (cx, y + h - 22)], fill=(200, 210, 220), width=3)
    d.ellipse([cx - 13, y + 26, cx + 13, y + 52], fill=(214, 72, 54))
    d.ellipse([cx - 8, y + 62, cx + 8, y + 78], fill=(214, 72, 54))
    for wy in (y + 30, y + 48, y + 66):
        for wx in range(x + 8, x + w - 8, 14):
            d.rectangle([wx, wy, wx + 4, wy + 3], fill=(240, 220, 130))
    d.line([(x, y + h - 22), (x + w, y + h - 22)], fill=(240, 220, 130), width=2)

def paint_court(d, x, y, w, h):
    sky(d, x, y, w, h, (52, 58, 66), (96, 100, 108))
    # courthouse: pediment + columns + steps
    d.polygon([(x + w // 2 - 46, y + 12), (x + w // 2 + 46, y + 12), (x + w // 2, y + 34)], fill=(226, 220, 204))
    d.rectangle([x + 14, y + 34, x + w - 14, y + h - 20], fill=(210, 203, 184))
    for i in range(5):
        cx = x + 24 + i * (w - 48) // 4
        d.rectangle([cx - 5, y + 38, cx + 5, y + h - 26], fill=(240, 236, 222))
    d.rectangle([x + w // 2 - 16, y + h - 44, x + w // 2 + 16, y + h - 20], fill=(40, 36, 30))
    d.ellipse([x + w // 2 - 7, y + h - 40, x + w // 2 - 1, y + h - 34], fill=(240, 220, 130))
    d.ellipse([x + w // 2 + 1, y + h - 40, x + w // 2 + 7, y + h - 34], fill=(240, 220, 130))
    for sy in range(3):
        d.rectangle([x + 8, y + h - 18 + sy * 5, x + w - 8, y + h - 15 + sy * 5], fill=(190, 184, 168))
    # scales of justice, small, top right
    sx, sy = x + w - 34, y + 16
    d.line([(sx, sy), (sx, sy + 22)], fill=(240, 220, 130), width=2)
    d.line([(sx - 12, sy + 4), (sx + 12, sy + 4)], fill=(240, 220, 130), width=2)
    d.ellipse([sx - 16, sy + 8, sx - 8, sy + 16], fill=(240, 220, 130))
    d.ellipse([sx + 8, sy + 8, sx + 16, sy + 16], fill=(240, 220, 130))

def paint_zaporizhzhia(d, x, y, w, h):
    sky(d, x, y, w, h, (30, 38, 56), (70, 78, 96))
    # smoke + fire glow
    d.ellipse([x + w // 2 - 34, y + 6, x + w // 2 + 26, y + 46], fill=(226, 120, 40))
    d.ellipse([x + w // 2 - 18, y + 16, x + w // 2 + 12, y + 40], fill=(240, 190, 90))
    for i, (sx, sy, r) in enumerate([(w // 2 - 40, 8, 12), (w // 2 - 22, 2, 15), (w // 2 + 4, 6, 13)]):
        d.ellipse([x + sx - r, y + sy, x + sx + r, y + sy + r], fill=(120, 118, 112))
    # damaged apartment block
    d.rectangle([x + 10, y + 34, x + w - 10, y + h], fill=(96, 90, 82))
    d.polygon([(x + 10, y + 34), (x + w // 2, y + 34), (x + w // 2 - 14, y + 58), (x + 10, y + 58)], fill=(60, 56, 50))
    for row in range(4):
        for col in range(6):
            wx = x + 18 + col * 15
            wy = y + 62 + row * 13
            if wx + 8 < x + w - 14:
                d.rectangle([wx, wy, wx + 8, wy + 7], fill=(240, 210, 120) if (row + col) % 3 else (52, 48, 44))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(40, 38, 34))

def paint_sanofi(d, x, y, w, h):
    sky(d, x, y, w, h, (240, 244, 248), (200, 214, 226))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(30, 60, 90))
    # lab flasks + pill
    d.rectangle([x + 12, y + 12, x + 34, y + h - 26], fill=(120, 170, 200))
    d.polygon([(x + 12, y + 34), (x + 34, y + 34), (x + 40, y + h - 26), (x + 6, y + h - 26)], fill=(90, 150, 185))
    d.ellipse([x + w - 46, y + 10, x + w - 10, y + 34], fill=(214, 72, 54))
    d.rectangle([x + w - 46, y + 18, x + w - 10, y + 26], fill=(255, 255, 255))
    d.line([(x + 44, y + 20), (x + w - 52, y + 20)], fill=(120, 140, 160), width=2)
    for i in range(4):
        d.ellipse([x + 48 + i * 16, y + 30 + (i % 2) * 8, x + 56 + i * 16, y + 38 + (i % 2) * 8], fill=(214, 72, 54))

def paint_dow(d, x, y, w, h):
    sky(d, x, y, w, h, (16, 40, 60), (30, 70, 96))
    # rising chart line + bars
    base = y + h - 18
    bars = [10, 16, 12, 22, 18, 30, 26, 38]
    bw = (w - 16) // len(bars)
    for i, bh in enumerate(bars):
        bx = x + 8 + i * bw
        d.rectangle([bx, base - bh, bx + bw - 3, base], fill=(46, 140, 90) if i < 6 else (240, 190, 90))
    pts = [(x + 8 + i * bw + bw // 2, base - bh) for i, bh in enumerate(bars)]
    d.line(pts, fill=(255, 255, 255), width=3)
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4], fill=(255, 255, 255))
    d.text((x + 8, y + 4), "50,019", font=F("NotoSans-Bold.ttf", 15), fill=(255, 255, 255))

def paint_ariane(d, x, y, w, h):
    sky(d, x, y, w, h, (18, 30, 52), (44, 70, 104))
    for sx in range(x + 10, x + w - 6, 18):
        d.ellipse([sx, y + 6 + (sx % 23), sx + 2, y + 8 + (sx % 23)], fill=(220, 225, 235))
    # flame + rocket
    cx = x + w // 2
    d.polygon([(cx - 10, y + 30), (cx + 10, y + 30), (cx, y + 62)], fill=(240, 160, 40))
    d.polygon([(cx - 6, y + 34), (cx + 6, y + 34), (cx, y + 52)], fill=(250, 220, 120))
    d.rectangle([cx - 9, y + 6, cx + 9, y + 32], fill=(235, 235, 230))
    d.polygon([(cx - 9, y + 6), (cx + 9, y + 6), (cx, y - 6)], fill=(214, 72, 54))
    d.rectangle([cx - 9, y + 14, cx + 9, y + 18], fill=(214, 72, 54))
    d.polygon([(cx - 9, y + 28), (cx - 16, y + 40), (cx - 9, y + 40)], fill=(200, 60, 44))
    d.polygon([(cx + 9, y + 28), (cx + 16, y + 40), (cx + 9, y + 40)], fill=(200, 60, 44))
    # boosters + launch pad + smoke
    d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 6], fill=(120, 118, 110))
    for sx in (x + 14, x + w - 30):
        d.ellipse([sx, y + h - 26, sx + 16, y + h - 10], fill=(200, 198, 190))
    # satellite dots trailing up-right
    for i in range(4):
        d.ellipse([cx + 22 + i * 12, y + 8 + i * 6, cx + 27 + i * 12, y + 13 + i * 6], fill=(240, 220, 130))

def paint_riyadh(d, x, y, w, h):
    sky(d, x, y, w, h, (226, 190, 140), (200, 150, 100))
    # twisted tower + city
    cx = x + w // 2
    for i in range(5):
        yy = y + 8 + i * 11
        off = (i % 2) * 6 - 3
        d.rectangle([cx - 16 + off, yy, cx + 16 + off, yy + 10], fill=(90, 80, 70))
    d.polygon([(cx - 10, y + 2), (cx + 10, y + 2), (cx, y + 12)], fill=(70, 60, 52))
    for bx, bh in [(6, 30), (w - 22, 38), (w - 40, 24)]:
        d.rectangle([x + bx, y + h - 14 - bh, x + bx + 16, y + h - 14], fill=(110, 98, 84))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(60, 52, 44))
    d.ellipse([cx - 22, y + 38, cx + 22, y + h - 14], fill=(226, 120, 40))
    d.ellipse([cx - 12, y + 44, cx + 12, y + h - 16], fill=(240, 190, 90))

def paint_taiex(d, x, y, w, h):
    sky(d, x, y, w, h, (20, 60, 50), (40, 110, 80))
    base = y + h - 16
    pts = [(x + 6, base - 6), (x + w // 4, base - 16), (x + w // 2, base - 12),
           (x + 3 * w // 4, base - 30), (x + w - 8, base - 44)]
    d.line(pts, fill=(120, 220, 140), width=4)
    d.polygon(pts + [(x + w - 8, base), (x + 6, base)], fill=(60, 160, 90))
    d.polygon([(x + w - 8, base - 44), (x + w - 8, base - 30), (x + w - 22, base - 44)], fill=(120, 220, 140))
    d.text((x + 6, y + 4), "+8.99%", font=F("NotoSans-Bold.ttf", 15), fill=(255, 255, 255))
    for i in range(5):
        d.rectangle([x + 8 + i * 12, base - 4 - i, x + 12 + i * 12, base], fill=(240, 220, 130))

def paint_senegal(d, x, y, w, h):
    sky(d, x, y, w, h, (30, 90, 50), (60, 140, 80))
    # pitch + trophy + ball
    d.rectangle([x, y + h - 24, x + w, y + h], fill=(40, 120, 60))
    d.line([(x + 8, y + h - 12), (x + w - 8, y + h - 12)], fill=(255, 255, 255), width=1)
    cx = x + w // 2
    d.polygon([(cx - 12, y + 10), (cx + 12, y + 10), (cx + 8, y + 30), (cx - 8, y + 30)], fill=(240, 200, 60))
    d.rectangle([cx - 10, y + 30, cx + 10, y + 34], fill=(240, 200, 60))
    d.rectangle([cx - 14, y + 34, cx + 14, y + 38], fill=(200, 160, 40))
    d.ellipse([x + 12, y + h - 40, x + 30, y + h - 22], fill=(255, 255, 255))
    d.polygon([(x + 21, y + h - 40), (x + 26, y + h - 34), (x + 21, y + h - 28), (x + 16, y + h - 34)], fill=(30, 30, 30))
    for sx in (x + w - 30, x + w - 48):
        d.ellipse([sx, y + 12, sx + 8, y + 20], fill=(255, 220, 120))

def paint_solomons(d, x, y, w, h):
    sky(d, x, y, w, h, (30, 80, 110), (70, 130, 160))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(20, 70, 100))
    # island + palm + torn pact paper
    d.ellipse([x + w // 2 - 40, y + h - 30, x + w // 2 + 40, y + h - 8], fill=(40, 120, 70))
    d.line([(x + w // 2, y + h - 28), (x + w // 2, y + 22)], fill=(90, 60, 30), width=3)
    for dx, dy in [(-16, -6), (16, -6), (-12, -14), (12, -14)]:
        d.line([(x + w // 2, y + 24), (x + w // 2 + dx, y + 24 + dy)], fill=(50, 140, 70), width=3)
    d.rectangle([x + 10, y + 12, x + 34, y + 30], fill=(245, 242, 230))
    d.rectangle([x + 36, y + 12, x + 60, y + 30], fill=(245, 242, 230))
    d.line([(x + 34, y + 12), (x + 36, y + 30)], fill=(178, 38, 30), width=2)
    for wy in (y + 17, y + 23):
        d.line([(x + 14, wy), (x + 30, wy)], fill=(120, 116, 104), width=1)

def paint_kadiz(d, x, y, w, h):
    sky(d, x, y, w, h, (24, 40, 66), (58, 88, 122))
    # jets + radar sweep + island
    for jx, jy in [(w // 3, 18), (2 * w // 3, 30)]:
        d.polygon([(x + jx, y + jy), (x + jx + 22, y + jy + 6), (x + jx, y + jy + 12)], fill=(220, 220, 215))
        d.polygon([(x + jx + 4, y + jy + 12), (x + jx + 10, y + jy + 20), (x + jx + 12, y + jy + 12)], fill=(180, 180, 175))
    d.ellipse([x + 8, y + h - 34, x + 44, y + h - 6], fill=(40, 90, 60))
    d.line([(x + 26, y + h - 30), (x + 26, y + h - 14)], fill=(240, 220, 130), width=2)
    d.arc([x + w - 40, y + h - 40, x + w - 4, y + h - 4], 180, 270, fill=(240, 90, 70), width=3)
    d.arc([x + w - 52, y + h - 52, x + w + 8, y + h + 8], 180, 270, fill=(240, 90, 70), width=2)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(22, 34, 58))

def paint_gaza(d, x, y, w, h):
    sky(d, x, y, w, h, (40, 34, 30), (90, 74, 58))
    # skyline + smoke column + searchlight
    for bx, bw, bh in [(4, 18, 40), (26, 14, 56), (44, 20, 34), (68, 16, 48)]:
        d.rectangle([x + bx, y + h - 12 - bh, x + bx + bw, y + h - 12], fill=(52, 46, 40))
        for wy in range(y + h - 12 - bh + 6, y + h - 14, 12):
            d.rectangle([x + bx + 4, wy, x + bx + 8, wy + 5], fill=(240, 210, 120))
    d.polygon([(x + w - 20, y + h - 12), (x + w - 34, y + 8), (x + w - 8, y + 8)], fill=(240, 230, 180))
    for i, (sx, sy, r) in enumerate([(w // 2 - 6, 4, 10), (w // 2 + 6, 12, 12), (w // 2 - 2, 22, 9)]):
        d.ellipse([x + sx - r, y + sy, x + sx + r, y + sy + r], fill=(130, 124, 114))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(36, 32, 28))

def paint_cikande(d, x, y, w, h):
    sky(d, x, y, w, h, (52, 44, 38), (96, 80, 62))
    # factory + tents + smoke
    d.rectangle([x + 6, y + 26, x + w - 6, y + h - 10], fill=(70, 62, 54))
    d.polygon([(x + 6, y + 26), (x + w // 2, y + 12), (x + w - 6, y + 26)], fill=(50, 44, 38))
    for i in range(3):
        d.rectangle([x + 14 + i * 22, y + 36, x + 24 + i * 22, y + 52], fill=(240, 210, 120))
    d.rectangle([x + w - 30, y + 8, x + w - 24, y + 26], fill=(60, 54, 48))
    for i, (sx, sy, r) in enumerate([(w - 26, 2, 9), (w - 34, 8, 11), (w - 18, 10, 8)]):
        d.ellipse([x + sx - r, y + sy, x + sx + r, y + sy + r], fill=(120, 116, 108))
    for tx in (x + 12, x + 44):
        d.polygon([(tx, y + h - 10), (tx + 12, y + h - 26), (tx + 24, y + h - 10)], fill=(240, 236, 222))
        d.polygon([(tx + 10, y + h - 10), (tx + 14, y + h - 18), (tx + 18, y + h - 10)], fill=(40, 40, 38))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(44, 40, 36))

PAINTERS = {"shanghai": paint_shanghai, "court": paint_court, "zaporizhzhia": paint_zaporizhzhia,
            "sanofi": paint_sanofi, "dow": paint_dow, "ariane": paint_ariane, "riyadh": paint_riyadh,
            "taiex": paint_taiex, "senegal": paint_senegal, "solomons": paint_solomons,
            "kadiz": paint_kadiz, "gaza": paint_gaza, "cikande": paint_cikande}

# ---------------------------------------------------------------- map
CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-120, 72), (-95, 69), (-80, 62), (-70, 45), (-75, 35), (-80, 26), (-90, 20), (-97, 16), (-105, 22), (-117, 32), (-125, 42), (-125, 49), (-150, 60), (-168, 66)],
    "SA": [(-80, 10), (-60, 5), (-50, 0), (-40, -10), (-48, -28), (-58, -38), (-70, -52), (-73, -40), (-78, -20), (-80, -5), (-80, 10)],
    "EU": [(-10, 37), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55), (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (40, 68), (45, 60), (40, 50), (30, 45), (28, 41), (23, 36), (15, 38), (8, 39), (3, 42), (-10, 37)],
    "AF": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (51, 11), (48, -1), (40, -15), (35, -25), (28, -33), (18, -35), (15, -27), (12, -18), (9, -1), (-8, 4), (-17, 15)],
    "AS": [(40, 68), (60, 70), (80, 73), (100, 77), (130, 72), (160, 70), (178, 65), (162, 60), (142, 50), (140, 40), (130, 33), (122, 31), (110, 20), (105, 10), (100, 8), (95, 16), (90, 22), (80, 8), (77, 8), (72, 20), (66, 25), (58, 25), (52, 27), (48, 30), (44, 39), (40, 42), (40, 68)],
    "OC": [(114, -22), (122, -14), (132, -11), (142, -11), (146, -19), (153, -27), (150, -37), (140, -38), (130, -32), (122, -34), (115, -32), (114, -22)],
}
PINS = {1: (121.5, 31.2), 2: (-74.0, 40.7), 3: (35.1, 47.8), 4: (2.35, 48.85),
        5: (-74.0, 40.7), 6: (-52.8, 5.2), 7: (46.7, 24.7), 8: (121.6, 25.0),
        9: (-17.4, 14.7), 10: (160.0, -9.4), 11: (130.9, 37.5), 12: (34.5, 31.5),
        13: (106.4, -6.2)}
PIN_OFF = {1: (-18, 6), 5: (16, 14), 7: (16, 10), 8: (14, 10), 2: (-14, -12)}

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(233, 230, 220), outline=RULE)
    lon0, lon1, lat0, lat1 = -180, 180, 75, -55
    def proj(lon, lat):
        px = x + 6 + (lon - lon0) / (lon1 - lon0) * (w - 12)
        py = y + 6 + (lat0 - lat) / (lat0 - lat1) * (h - 12)
        return px, py
    for poly in CONTINENTS.values():
        d.polygon([proj(lo, la) for lo, la in poly], fill=(196, 190, 172), outline=(150, 144, 128))
    fpin = F("NotoSans-Bold.ttf", 11)
    for n, (lo, la) in PINS.items():
        px, py = proj(lo, la)
        ox, oy = PIN_OFF.get(n, (0, 0))
        px, py = px + ox, py + oy
        if n in PIN_OFF:
            bx, by = proj(lo, la)
            d.line([(bx, by), (px, py)], fill=RED, width=1)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255), width=1)
        tw = d.textlength(str(n), font=fpin)
        d.text((px - tw / 2, py - 6), str(n), font=fpin, fill=(255, 255, 255))

# ---------------------------------------------------------------- render
def render(data, out):
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)
    ys = {}
    y = 0
    for name, h in BUDGET:
        ys[name] = (y, h); y += h

    f_kick = F("NotoSansMono-Bold.ttf", 11)
    f_date = F("NotoSerifDisplay-Black.ttf", 50)
    f_sub = F("NotoSans-Bold.ttf", 13)
    f_num_v = F("NotoSerifDisplay-Bold.ttf", 19)
    f_num_l = F("NotoSans-Regular.ttf", 10)
    f_tl = F("NotoSansMono-Regular.ttf", 10)
    f_h_head = F("NotoSerifDisplay-Bold.ttf", 19)
    f_h_deck = F("NotoSerif-Regular.ttf", 12)
    f_h_src = F("NotoSans-Regular.ttf", 10)
    f_m_head = F("NotoSerifDisplay-Bold.ttf", 14)
    f_m_deck = F("NotoSans-Regular.ttf", 10)
    f_m_src = F("NotoSans-Regular.ttf", 9)
    f_b_head = F("NotoSans-Bold.ttf", 11)
    f_b_body = F("NotoSans-Regular.ttf", 11)
    f_sec = F("NotoSans-Bold.ttf", 10)
    f_foot = F("NotoSans-Regular.ttf", 10)
    f_banner = F("NotoSans-Bold.ttf", 13)
    f_banner_s = F("NotoSans-Bold.ttf", 10)

    # kicker
    y0, h0 = ys["kicker"]
    d.rectangle([0, y0, W - 1, y0 + h0 - 1], fill=DARK)
    t = data["kicker"]
    d.text(((W - d.textlength(t, font=f_kick)) / 2, y0 + 3), t, font=f_kick, fill=(255, 255, 255))

    # masthead: the date IS the headline
    y0, h0 = ys["masthead"]
    date = "Tuesday 24 November 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, y0 + 4), date, font=f_date, fill=INK)
    sub = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, y0 + 64), sub, font=f_sub, fill=RED)
    d.line([(MARGIN, y0 + h0 - 2), (W - MARGIN, y0 + h0 - 2)], fill=INK, width=2)
    d.text((MARGIN, y0 + 8), "THE WORLD", font=f_sub, fill=INK)
    d.text((W - MARGIN - d.textlength("ONE DAY · ONE PAGE", font=f_sub), y0 + 8),
           "ONE DAY · ONE PAGE", font=f_sub, fill=INK)

    # IN NUMBERS
    y0, h0 = ys["numbers"]
    xs, ws = cols(MARGIN, W - 2 * MARGIN, 6)
    for (val, lab), cx, cw in zip(data["numbers"], xs, ws):
        d.text((cx, y0 + 1), val, font=f_num_v, fill=RED)
        d.text((cx, y0 + 20), lab, font=f_num_l, fill=INK)
        if cx > MARGIN:
            d.line([(cx - 4, y0 + 2), (cx - 4, y0 + h0 - 4)], fill=RULE, width=1)
    d.line([(MARGIN, y0 + h0 - 1), (W - MARGIN, y0 + h0 - 1)], fill=RULE, width=1)

    # timeline UTC
    y0, h0 = ys["timeline"]
    xs, ws = cols(MARGIN, W - 2 * MARGIN, 7)
    for (tm, ev), cx, cw in zip(data["timeline"], xs, ws):
        d.text((cx, y0 + 4), tm, font=F("NotoSansMono-Bold.ttf", 10), fill=RED)
        lines = fit_lines(d, ev, f_tl, cw - 34, 2, f"timeline {tm}")
        d.text((cx + 34, y0 + 4), lines[0], font=f_tl, fill=INK)
        if len(lines) > 1:
            d.text((cx + 34, y0 + 14), lines[1], font=f_tl, fill=INK)
    d.line([(MARGIN, y0 + h0 - 1), (W - MARGIN, y0 + h0 - 1)], fill=INK, width=1)

    # heroes
    y0, h0 = ys["heroes"]
    xs, ws = cols(MARGIN, W - 2 * MARGIN, 3)
    art_h = 110
    for hero, cx, cw in zip(data["heroes"], xs, ws):
        PAINTERS[hero["art"]](d, cx, y0, cw, art_h)
        banner(d, cx, y0 + art_h - 20, cw, hero["banner"], f_banner, 20)
        ty = y0 + art_h + 4
        d.text((cx, ty), f"{hero['n']} · {hero['place']} — {hero['section']}", font=f_sec, fill=RED)
        ty += 13
        lines = fit_lines(d, hero["headline"], f_h_head, cw, 2, f"hero {hero['n']} headline")
        for ln in lines:
            d.text((cx, ty), ln, font=f_h_head, fill=INK); ty += 21
        lines = fit_lines(d, hero["deck"], f_h_deck, cw, 2, f"hero {hero['n']} deck")
        for ln in lines:
            d.text((cx, ty), ln, font=f_h_deck, fill=INK); ty += 13
        src = f"{hero['tag']} · {hero['source']}"
        d.text((cx, y0 + h0 - 12), src, font=f_h_src, fill=GREY)
        assert ty <= y0 + h0 - 14, f"hero {hero['n']} overflow"

    # minis: 2 rows x 5
    y0, h0 = ys["minis"]
    xs, ws = cols(MARGIN, W - 2 * MARGIN, 5)
    row_h = h0 // 2
    art_h = 60
    for i, mini in enumerate(data["minis"]):
        row, col = divmod(i, 5)
        cx, cw = xs[col], ws[col]
        my = y0 + row * row_h
        PAINTERS[mini["art"]](d, cx, my, cw, art_h)
        banner(d, cx, my + art_h - 16, cw, mini["banner"], f_banner_s, 16)
        ty = my + art_h + 3
        d.text((cx, ty), f"{mini['n']} · {mini['place']}", font=f_sec, fill=RED)
        ty += 12
        lines = fit_lines(d, mini["headline"], f_m_head, cw, 2, f"mini {mini['n']} headline")
        for ln in lines:
            d.text((cx, ty), ln, font=f_m_head, fill=INK); ty += 14
        lines = fit_lines(d, mini["deck"], f_m_deck, cw, 2, f"mini {mini['n']} deck")
        for ln in lines:
            d.text((cx, ty), ln, font=f_m_deck, fill=INK); ty += 11
        d.text((cx, my + row_h - 11), f"{mini['tag']} · {mini['source']}", font=f_m_src, fill=GREY)
        assert ty <= my + row_h - 12, f"mini {mini['n']} overflow"

    # also-on + map
    y0, h0 = ys["alsoon"]
    d.text((MARGIN, y0 + 2), "ALSO ON — 25 MORE", font=f_sec, fill=INK)
    d.line([(MARGIN, y0 + 16), (MARGIN + 620, y0 + 16)], fill=INK, width=1)
    bx0, bw = MARGIN, 306
    pitch = 20
    for ci in range(2):
        col = data["briefs"][ci * 13:(ci + 1) * 13] if ci == 0 else data["briefs"][13:25]
        cx = bx0 + ci * (bw + 8)
        by = y0 + 22
        for n, place, head, body, tag in col:
            d.text((cx, by), f"{n}", font=F("NotoSans-Bold.ttf", 11), fill=RED)
            d.text((cx + 22, by), place, font=f_b_head, fill=INK)
            d.text((cx + 22, by + 11), head, font=f_b_body, fill=GREY)
            by += pitch
    mx = MARGIN + 620 + 8
    mw = W - MARGIN - mx
    d.text((mx, y0 + 2), "WHERE IT HAPPENED · PINS 1–13", font=f_sec, fill=INK)
    draw_map(d, mx, y0 + 18, mw, h0 - 44)
    d.text((mx, y0 + h0 - 22), "Pins 1–13 = the heroes and minis above.", font=f_foot, fill=GREY)

    # date check
    y0, h0 = ys["datecheck"]
    d.rectangle([MARGIN, y0, MARGIN + 5, y0 + h0 - 1], fill=RED)
    tx = MARGIN + 12
    d.text((tx, y0 + 2), "DATE CHECK — LEFT OUT AS ANOTHER DAY'S NEWS", font=f_sec, fill=RED)
    lines = fit_lines(d, data["datecheck"]["leftout"], f_foot, W - MARGIN - tx, 2, "datecheck leftout")
    ty = y0 + 16
    for ln in lines:
        d.text((tx, ty), ln, font=f_foot, fill=INK); ty += 12
    d.text((tx, ty + 2), "NOT YET:  ", font=F("NotoSans-Bold.ttf", 10), fill=INK)
    d.text((tx + 52, ty + 2), data["datecheck"]["notyet"], font=f_foot, fill=INK)
    d.line([(MARGIN, y0 + h0 - 1), (W - MARGIN, y0 + h0 - 1)], fill=RULE, width=1)

    # footer
    y0, h0 = ys["footer"]
    d.text((MARGIN, y0 + 2), "HOW SURE:  " + data["legend"], font=f_foot, fill=GREY)
    d.text((MARGIN, y0 + 13), data["footer"], font=f_foot, fill=GREY)

    img.save(out, "PNG", optimize=True)

if __name__ == "__main__":
    data = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "stories.json").read_text())
    render(data, sys.argv[2] if len(sys.argv) > 2 else "entry.png")
