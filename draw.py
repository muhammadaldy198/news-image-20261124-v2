#!/usr/bin/env python3
"""Render Tuesday 24 November 2026 as one broadsheet page, 1024x1024.

Deterministic: no clock, no randomness, no network. Reads stories.json
in this directory and writes entry.png next to it.
Layout budget (single table, sums to 1024):
  margin 12 all sides, gutter 8, content width 1000
  masthead 12..100 | numbers 108..146 | regions 154..172
  timeline 180..206 | heroes 214..444 | minis r1 452..584 | minis r2 592..724
  also-on+map 732..916 | date-check 924..976 | footer 984..1012
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = 1024
H = 1024
MARGIN = 12
GUT = 8
CW = W - 2 * MARGIN  # 1000

INK = (18, 18, 18)
PAPER = (250, 247, 238)
RED = (176, 0, 32)
DARKRED = (140, 0, 24)
RULE = (120, 110, 95)
FAINT = (90, 84, 72)

TAG_FILL = {
    "CONFIRMED": (26, 122, 58),
    "OFFICIAL": (31, 78, 140),
    "REPORTED": (154, 106, 0),
    "CLAIM": (176, 0, 32),
    "ONGOING": (106, 61, 154),
}

F_SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
F_SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
F_SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
F_SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
F_SANS_BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
F_MONO = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
F_MONO_BOLD = "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, s, f, max_w, max_lines=None):
    """Wrap s; assert it fits in max_w and (optionally) max_lines."""
    lines = wrap(draw, s, f, max_w)
    if max_lines is not None:
        assert len(lines) <= max_lines, "TEXT OVERFLOW %r -> %d lines" % (s, len(lines))
    return lines


def draw_lines(draw, lines, x, y, f, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def tag_chip(draw, x, y, tag, h=13):
    """Draw a verification tag chip; return its width."""
    f = font(F_SANS_BOLD, 8)
    w = int(draw.textlength(tag, font=f)) + 8
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2,
                           fill=TAG_FILL[tag])
    draw.text((x + 4, y + 2), tag, font=f, fill=(255, 255, 255))
    return w


def banner(draw, box, text, size=15):
    """Red banner strip inside art, bottom-anchored, white bold text."""
    x0, y0, x1, y1 = box
    f = font(F_SANS_BLACK, size)
    tw = draw.textlength(text, font=f)
    assert tw <= (x1 - x0 - 8), "BANNER TOO WIDE: %r" % text
    bh = size + 10
    draw.rectangle([x0, y1 - bh, x1, y1], fill=RED)
    draw.text((x0 + 4, y1 - bh + 5), text, font=f, fill=(255, 255, 255))
    return bh


# ---------------------------------------------------------------- art scenes
# Every hero scene is layered (>=5 elements), flat vector, NO halftone.
# Art boxes exclude the red banner strip at their bottom.

def art_shanghai(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(24, 38, 66))
    for i, c in enumerate([(32, 52, 88), (40, 64, 104), (48, 76, 120)]):
        draw.rectangle([x0, y0 + 14 + i * 8, x1, y0 + 26 + i * 8], fill=c)
    # skyline silhouettes
    base = y1
    towers = [(0, 62, 30), (34, 96, 22), (60, 52, 26), (90, 110, 30),
              (124, 70, 24), (152, 88, 26), (182, 58, 24), (210, 92, 26),
              (240, 66, 22), (266, 84, 24), (292, 60, 22)]
    for dx, th, tw in towers:
        draw.rectangle([x0 + dx, base - th, x0 + dx + tw, base], fill=(12, 20, 36))
    # Oriental Pearl Tower: two spheres on a stem
    px = x0 + 150
    draw.rectangle([px - 2, base - 118, px + 2, base], fill=(12, 20, 36))
    draw.ellipse([px - 13, base - 118, px + 13, base - 92], fill=(150, 30, 40))
    draw.ellipse([px - 9, base - 78, px + 9, base - 60], fill=(150, 30, 40))
    draw.polygon([(px - 2, base - 118), (px - 16, base - 132),
                  (px + 16, base - 132)], fill=(12, 20, 36))
    # lit windows
    for wx in range(x0 + 8, x1 - 8, 14):
        for wy in range(base - 96, base - 32, 12):
            if (wx * 7 + wy * 3) % 5 == 0:
                draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(240, 200, 90))
    # red seal stamp
    cx, cy = x1 - 42, y0 + 34
    draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=(200, 40, 55),
                 width=3)
    draw.ellipse([cx - 19, cy - 19, cx + 19, cy + 19], outline=(200, 40, 55),
                 width=1)
    sf = font(F_SANS_BLACK, 11)
    draw.text((cx - 14, cy - 14), "PROBE", font=sf, fill=(200, 40, 55))
    draw.text((cx - 12, cy - 1), "2026", font=sf, fill=(200, 40, 55))
    # document strip at foot
    draw.rectangle([x0 + 10, base - 42, x0 + 120, base - 30], fill=(250, 247, 238))
    draw.line([x0 + 16, base - 38, x0 + 114, base - 38], fill=(120, 110, 95), width=1)
    draw.line([x0 + 16, base - 34, x0 + 90, base - 34], fill=(120, 110, 95), width=1)


def art_huawei(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(30, 32, 52))
    # courthouse columns
    for cx in range(x0 + 18, x1 - 10, 46):
        draw.rectangle([cx, y0 + 18, cx + 16, y1], fill=(58, 60, 88))
        draw.rectangle([cx - 3, y0 + 12, cx + 19, y0 + 18], fill=(72, 74, 104))
        draw.rectangle([cx - 3, y1 - 6, cx + 19, y1], fill=(72, 74, 104))
    # pediment
    draw.polygon([(x0, y0 + 12), (x1, y0 + 12), ((x0 + x1) // 2, y0 - 2)],
                 fill=(72, 74, 104))
    # scales of justice, centre
    cx = (x0 + x1) // 2
    cy = y0 + 58
    draw.line([cx, cy - 26, cx, cy + 22], fill=(240, 200, 90), width=3)
    draw.line([cx - 34, cy - 22, cx + 34, cy - 22], fill=(240, 200, 90), width=3)
    draw.line([cx - 34, cy - 22, cx - 34, cy - 6], fill=(240, 200, 90), width=2)
    draw.line([cx + 34, cy - 22, cx + 34, cy - 6], fill=(240, 200, 90), width=2)
    draw.polygon([(cx - 46, cy - 4), (cx - 22, cy - 4), (cx - 34, cy + 6)],
                 fill=(240, 200, 90))
    draw.polygon([(cx + 22, cy - 4), (cx + 46, cy - 4), (cx + 34, cy + 6)],
                 fill=(240, 200, 90))
    draw.ellipse([cx - 5, cy - 32, cx + 5, cy - 22], fill=(240, 200, 90))
    draw.rectangle([cx - 14, cy + 22, cx + 14, y1 - 28], fill=(240, 200, 90))
    # gavel, lower left
    gx, gy = x0 + 34, y1 - 58
    draw.line([gx, gy, gx + 34, gy - 12], fill=(200, 160, 90), width=5)
    draw.rectangle([gx + 30, gy - 24, gx + 52, gy - 8], fill=(160, 110, 60))
    # verdict paper, lower right
    draw.rectangle([x1 - 92, y1 - 64, x1 - 12, y1 - 30], fill=(250, 247, 238))
    vf = font(F_SANS_BLACK, 13)
    draw.text((x1 - 84, y1 - 60), "10 OF 12", font=vf, fill=(176, 0, 32))
    draw.line([x1 - 84, y1 - 42, x1 - 20, y1 - 42], fill=(120, 110, 95), width=1)
    draw.line([x1 - 84, y1 - 36, x1 - 40, y1 - 36], fill=(120, 110, 95), width=1)


def art_zaporizhzhia(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(74, 62, 58))
    for i, c in enumerate([(96, 78, 66), (118, 94, 76), (140, 110, 88)]):
        draw.rectangle([x0, y0 + 10 + i * 7, x1, y0 + 20 + i * 7], fill=c)
    base = y1
    # apartment block, broken in the middle
    draw.rectangle([x0 + 30, base - 96, x0 + 150, base], fill=(52, 44, 42))
    draw.rectangle([x0 + 178, base - 78, x0 + 292, base], fill=(44, 38, 36))
    draw.polygon([(x0 + 150, base - 96), (x0 + 178, base - 78),
                  (x0 + 178, base - 40), (x0 + 150, base - 52)],
                 fill=(52, 44, 42))
    # windows, some dark (destroyed), some lit
    for wx in range(x0 + 40, x0 + 146, 18):
        for wy in range(base - 88, base - 8, 16):
            lit = (wx * 5 + wy * 11) % 4 != 0
            draw.rectangle([wx, wy, wx + 9, wy + 10],
                           fill=(240, 200, 90) if lit else (20, 16, 14))
    for wx in range(x0 + 188, x0 + 288, 18):
        for wy in range(base - 70, base - 8, 16):
            lit = (wx * 3 + wy * 7) % 3 != 0
            draw.rectangle([wx, wy, wx + 9, wy + 10],
                           fill=(240, 200, 90) if lit else (20, 16, 14))
    # rubble mound in the gap
    draw.polygon([(x0 + 146, base), (x0 + 182, base), (x0 + 164, base - 26)],
                 fill=(30, 26, 24))
    # smoke columns
    for sx, sw in [(x0 + 158, 16), (x0 + 178, 12)]:
        draw.ellipse([sx, y0 + 12, sx + sw, y0 + 34], fill=(150, 140, 130))
        draw.ellipse([sx + 4, y0 + 2, sx + sw - 2, y0 + 20], fill=(165, 155, 145))
    # rescue lights
    for lx in range(x0 + 20, x1 - 20, 34):
        draw.ellipse([lx, base - 34, lx + 5, base - 29], fill=(255, 220, 90))
    # searchlight beam, narrow, low alpha feel via pale colour
    draw.polygon([(x0 + 60, base - 28), (x0 + 90, y0 + 30), (x0 + 110, y0 + 30),
                  (x0 + 90, base - 28)], fill=(200, 190, 150))


MINI_BG = {
    "sanofi": (28, 78, 110), "dow": (22, 92, 58), "ariane": (30, 42, 84),
    "riyadh": (96, 74, 30), "taiex": (24, 88, 96), "senegal": (28, 110, 60),
    "solomons": (30, 96, 110), "korea": (110, 40, 40), "gaza": (88, 74, 60),
    "kurdish": (70, 60, 110),
}


def art_mini(draw, key, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=MINI_BG[key])
    cx = (x0 + x1) // 2
    cy = y0 + (y1 - y0) // 2 - 6
    if key == "sanofi":
        draw.rounded_rectangle([x0 + 52, cy - 10, x1 - 52, cy + 10], radius=10,
                               fill=(255, 255, 255))
        draw.rounded_rectangle([x0 + 52, cy - 10, cx, cy + 10], radius=10,
                               fill=(176, 0, 32))
        draw.ellipse([x0 + 14, cy - 6, x0 + 30, cy + 6], fill=(255, 220, 90))
        draw.ellipse([x1 - 30, cy - 6, x1 - 14, cy + 6], fill=(255, 220, 90))
    elif key == "dow":
        pts = [(x0 + 12, y1 - 14), (x0 + 52, y1 - 30), (x0 + 84, y1 - 22),
               (x0 + 116, y1 - 38), (x0 + 150, y1 - 48), (x1 - 12, y1 - 58)]
        draw.line(pts, fill=(255, 255, 255), width=4, joint="curve")
        draw.polygon([(x1 - 26, y1 - 58), (x1 - 8, y1 - 58), (x1 - 12, y1 - 42)],
                     fill=(255, 255, 255))
        for gx in range(x0 + 12, x1 - 8, 22):
            draw.line([gx, y0 + 8, gx, y1 - 8], fill=(60, 140, 90), width=1)
    elif key == "ariane":
        draw.rectangle([cx - 7, cy - 18, cx + 7, cy + 8], fill=(250, 247, 238))
        draw.polygon([(cx - 7, cy - 18), (cx, cy - 28), (cx + 7, cy - 18)],
                     fill=(176, 0, 32))
        draw.rectangle([cx - 12, cy - 12, cx - 7, cy + 2], fill=(200, 200, 200))
        draw.rectangle([cx + 7, cy - 12, cx + 12, cy + 2], fill=(200, 200, 200))
        draw.polygon([(cx - 6, cy + 8), (cx, cy + 20), (cx + 6, cy + 8)],
                     fill=(255, 170, 40))
        for sx, sy in [(x0 + 20, y0 + 6), (x1 - 24, y0 + 10), (x0 + 30, y0 + 16),
                       (x1 - 34, y0 + 20)]:
            draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
    elif key == "riyadh":
        draw.rectangle([cx - 10, cy - 16, cx + 10, cy + 12], fill=(30, 24, 18))
        draw.polygon([(cx - 10, cy - 16), (cx, cy - 24), (cx + 10, cy - 16)],
                     fill=(30, 24, 18))
        for wy in range(cy - 12, cy + 10, 8):
            draw.rectangle([cx - 6, wy, cx + 6, wy + 4], fill=(240, 200, 90))
        draw.ellipse([cx + 16, cy - 16, cx + 34, cy + 0], fill=(255, 170, 60))
        draw.ellipse([cx + 20, cy - 12, cx + 30, cy - 4], fill=(255, 220, 90))
    elif key == "taiex":
        draw.rectangle([x0 + 18, cy - 8, x0 + 52, cy + 14], fill=(16, 20, 36))
        draw.rectangle([x0 + 26, cy - 2, x0 + 44, cy + 10], fill=(255, 255, 255))
        for px in range(x0 + 30, x0 + 42, 5):
            draw.line([px, cy + 8, px, cy + 0], fill=(24, 88, 96), width=2)
        draw.line([(x0 + 62, cy + 12), (x0 + 100, cy - 6), (x0 + 138, cy - 16),
                   (x1 - 16, cy - 22)], fill=(255, 255, 255), width=4)
        draw.polygon([(x1 - 30, cy - 22), (x1 - 12, cy - 22), (x1 - 16, cy - 10)],
                     fill=(255, 255, 255))
    elif key == "senegal":
        draw.polygon([(cx - 14, cy - 12), (cx + 14, cy - 12), (cx + 8, cy + 4),
                      (cx - 8, cy + 4)], fill=(255, 210, 60))
        draw.rectangle([cx - 4, cy + 4, cx + 4, cy + 10], fill=(255, 210, 60))
        draw.rectangle([cx - 16, cy + 10, cx + 16, cy + 14], fill=(255, 210, 60))
        draw.ellipse([cx - 26, cy - 12, cx - 12, cy - 2], fill=(255, 210, 60))
        draw.ellipse([cx + 12, cy - 12, cx + 26, cy - 2], fill=(255, 210, 60))
    elif key == "solomons":
        draw.ellipse([x0 + 22, cy - 4, x1 - 22, cy + 14], fill=(20, 90, 70))
        draw.polygon([(x0 + 60, cy - 4), (x0 + 90, cy - 16), (x0 + 120, cy - 4)],
                     fill=(20, 90, 70))
        draw.line([cx - 30, cy - 18, cx + 30, cy - 18], fill=(255, 255, 255),
                  width=3)
        draw.line([cx - 8, cy - 24, cx + 8, cy - 10], fill=(255, 255, 255),
                  width=3)
        draw.line([cx - 8, cy - 10, cx + 8, cy - 24], fill=(255, 255, 255),
                  width=3)
    elif key == "korea":
        draw.polygon([(x0 + 30, cy + 12), (x0 + 30, cy - 8), (x0 + 78, cy - 22),
                      (x0 + 78, cy + 12)], fill=(230, 230, 230))
        draw.line([x0 + 78, cy - 22, x0 + 118, cy - 30], fill=(255, 255, 255),
                  width=2)
        draw.line([x0 + 78, cy - 22, x0 + 116, cy - 8], fill=(255, 255, 255),
                  width=2)
        draw.polygon([(x1 - 52, cy - 24), (x1 - 30, cy - 24), (x1 - 41, cy - 2)],
                     fill=(255, 200, 40))
        draw.text((x1 - 44, cy - 22), "!", font=font(F_SANS_BLACK, 16),
                  fill=(110, 40, 40))
    elif key == "gaza":
        draw.rectangle([x0 + 30, cy - 18, x0 + 110, cy + 14], fill=(52, 44, 40))
        draw.rectangle([x0 + 122, cy - 8, x1 - 30, cy + 14], fill=(44, 38, 34))
        for wx in range(x0 + 38, x0 + 104, 14):
            draw.rectangle([wx, cy - 10, wx + 7, cy - 2], fill=(240, 200, 90))
        draw.ellipse([x0 + 128, cy - 20, x0 + 150, cy - 2], fill=(150, 140, 130))
        draw.ellipse([x0 + 136, cy - 28, x0 + 152, cy - 14], fill=(165, 155, 145))
    elif key == "kurdish":
        draw.line([x0 + 30, cy + 12, x0 + 60, cy - 22], fill=(40, 34, 28), width=4)
        draw.line([x0 + 90, cy + 12, x0 + 60, cy - 22], fill=(40, 34, 28), width=4)
        draw.line([x0 + 40, cy + 2, x0 + 80, cy + 2], fill=(40, 34, 28), width=3)
        draw.rectangle([x0 + 52, cy - 30, x0 + 68, cy - 20], fill=(40, 34, 28))
        draw.ellipse([cx + 34, cy - 24, cx + 56, cy - 6], fill=(255, 170, 40))
        draw.ellipse([cx + 40, cy - 20, cx + 50, cy - 10], fill=(255, 220, 90))
        draw.rectangle([x1 - 44, cy + 6, x1 - 18, cy + 12], fill=(40, 34, 28))


HERO_ART = {"shanghai": art_shanghai, "huawei": art_huawei,
            "zaporizhzhia": art_zaporizhzhia}


# ---------------------------------------------------------------- world map
# Simplified continent outlines in lon/lat, projected linearly.
CONTINENTS = {
    "na": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
           (-80, 73), (-75, 62), (-65, 60), (-55, 52), (-60, 45), (-70, 42),
           (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29), (-97, 26),
           (-105, 22), (-110, 24), (-115, 30), (-125, 40), (-125, 48),
           (-130, 55), (-145, 60), (-155, 58), (-165, 60)],
    "sa": [(-80, 9), (-75, 11), (-62, 11), (-52, 5), (-50, 0), (-44, -3),
           (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-53, -33),
           (-58, -38), (-65, -41), (-68, -52), (-70, -54), (-73, -50),
           (-73, -40), (-72, -30), (-70, -20), (-77, -12), (-80, -5), (-81, 0)],
    "eu": [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
           (2, 51), (5, 53), (8, 57), (10, 59), (5, 60), (5, 62), (12, 65),
           (18, 69), (25, 71), (30, 70), (32, 68), (40, 68), (44, 68),
           (40, 64), (38, 60), (35, 58), (30, 60), (28, 59), (24, 58),
           (21, 55), (19, 54), (15, 54), (12, 54), (8, 55), (8, 57),
           (5, 53), (2, 51), (-2, 50), (-4, 48), (-1, 46), (-2, 44),
           (-9, 43)],
    "af": [(-17, 15), (-16, 20), (-13, 27), (-10, 31), (-5, 35), (0, 36),
           (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (34, 28),
           (35, 23), (37, 18), (40, 15), (43, 12), (48, 11), (51, 11),
           (51, 2), (48, -2), (41, -5), (40, -10), (36, -18), (33, -26),
           (28, -33), (20, -35), (17, -32), (15, -27), (13, -18), (12, -8),
           (13, -1), (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 12)],
    "as": [(32, 68), (60, 69), (90, 75), (120, 73), (150, 70), (162, 60),
           (155, 52), (142, 45), (135, 35), (127, 35), (120, 32), (108, 18),
           (103, 8), (98, 10), (92, 21), (86, 20), (80, 13), (77, 8),
           (73, 16), (66, 24), (58, 26), (52, 25), (48, 30), (43, 29),
           (39, 25), (35, 18), (33, 12), (30, 15), (28, 20), (26, 30),
           (25, 36), (28, 40), (30, 45), (30, 60)],
    "oc": [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
           (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
           (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
           (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
           (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    "id": [(95, 5), (98, 8), (100, 0), (104, -3), (106, -6), (110, -7),
           (114, -8), (118, -9), (120, -10), (122, -8), (124, -5), (126, 0),
           (128, 2), (130, -1), (128, -4), (124, -6), (120, -8), (116, -9),
           (112, -8), (108, -7), (104, -4), (100, 0), (96, 4)],
}
MAP_LON0, MAP_LON1 = -170, 190
MAP_LAT0, MAP_LAT1 = -58, 78


def map_xy(x0, y0, w, h, lon, lat):
    fx = (lon - MAP_LON0) / (MAP_LON1 - MAP_LON0)
    fy = (MAP_LAT1 - lat) / (MAP_LAT1 - MAP_LAT0)
    return x0 + fx * w, y0 + fy * h


def draw_map(draw, x0, y0, x1, y1, pins):
    draw.rectangle([x0, y0, x1, y1], fill=(232, 236, 240),
                   outline=RULE, width=1)
    mw, mh = x1 - x0, y1 - y0
    for lon in range(-150, 181, 30):
        gx, _ = map_xy(x0, y0, mw, mh, lon, 0)
        draw.line([gx, y0, gx, y1], fill=(214, 220, 228), width=1)
    for lat in range(-60, 79, 30):
        _, gy = map_xy(x0, y0, mw, mh, 0, lat)
        draw.line([x0, gy, x1, gy], fill=(214, 220, 228), width=1)
    for poly in CONTINENTS.values():
        pts = [map_xy(x0, y0, mw, mh, lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(206, 198, 178), outline=(150, 142, 126))
    placed = []
    for p in pins:
        px, py = map_xy(x0, y0, mw, mh, p["lon"], p["lat"])
        px += p.get("dx", 0)
        py += p.get("dy", 0)
        placed.append((px, py, p["n"]))
    for px, py, n in placed:
        for qx, qy, qn in placed:
            if qn > n:
                d = ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5
                assert d >= 11, "MAP PIN COLLISION %d vs %d (%.1fpx)" % (n, qn, d)
    for px, py, n in placed:
        r = 7
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        nf = font(F_SANS_BLACK, 8 if n < 10 else 7)
        tw = draw.textlength(str(n), font=nf)
        draw.text((px - tw / 2, py - 5.5), str(n), font=nf,
                  fill=(255, 255, 255))
    return placed


# ---------------------------------------------------------------- sections

def section_masthead(draw, data):
    f_kick = font(F_SANS_BOLD, 10)
    f_date = font(F_SERIF_BLACK, 54)
    f_deck = font(F_SERIF_BOLD, 13)
    kick = data["kicker"]
    tw = draw.textlength(kick, font=f_kick)
    draw.text(((W - tw) / 2, 14), kick, font=f_kick, fill=FAINT)
    date = data["edition"]
    tw = draw.textlength(date, font=f_date)
    draw.text(((W - tw) / 2, 26), date, font=f_date, fill=INK)
    deck = data["deck"]
    tw = draw.textlength(deck, font=f_deck)
    draw.text(((W - tw) / 2, 90), deck, font=f_deck, fill=RED)
    draw.line([MARGIN, 102, W - MARGIN, 102], fill=INK, width=2)


def section_numbers(draw, data):
    y0, y1 = 108, 146
    n = len(data["numbers"])
    cell = CW / n
    f_num = font(F_SANS_BLACK, 20)
    f_lab = font(F_SANS_BOLD, 8)
    for i, (num, lab) in enumerate(data["numbers"]):
        cx = MARGIN + cell * i + cell / 2
        tw = draw.textlength(num, font=f_num)
        draw.text((cx - tw / 2, y0 + 2), num, font=f_num, fill=INK)
        tw = draw.textlength(lab, font=f_lab)
        assert tw <= cell - 6, "NUMBER LABEL TOO WIDE: %r" % lab
        draw.text((cx - tw / 2, y0 + 26), lab, font=f_lab, fill=FAINT)
        if i:
            x = MARGIN + cell * i
            draw.line([x, y0 + 4, x, y1 - 4], fill=RULE, width=1)
    draw.line([MARGIN, y1, W - MARGIN, y1], fill=RULE, width=1)


def section_regions(draw, data):
    y = 154
    f = font(F_SANS_BOLD, 10)
    parts = []
    total = 0
    for name, count, colour in data["regions"]:
        label = "%s %d" % (name, count)
        w = draw.textlength(label, font=f) + 16
        parts.append((label, colour, w))
        total += w + 14
    total -= 14
    x = (W - total) / 2
    for label, colour, w in parts:
        draw.ellipse([x, y + 2, x + 8, y + 10], fill=colour)
        draw.text((x + 12, y), label, font=f, fill=INK)
        x += w + 14
    draw.line([MARGIN, 174, W - MARGIN, 174], fill=RULE, width=1)


def section_timeline(draw, data):
    y_line = 194
    draw.line([MARGIN, y_line, W - MARGIN, y_line], fill=RULE, width=1)
    n = len(data["timeline"])
    step = CW / n
    f_t = font(F_MONO_BOLD, 10)
    f_l = font(F_SANS_BOLD, 8)
    for i, (t, label) in enumerate(data["timeline"]):
        cx = MARGIN + step * i + step / 2
        tw = draw.textlength(t, font=f_t)
        draw.text((cx - tw / 2, 180), t, font=f_t, fill=RED)
        draw.ellipse([cx - 4, y_line - 4, cx + 4, y_line + 4], fill=RED)
        tw = draw.textlength(label, font=f_l)
        assert tw <= step - 6, "TIMELINE LABEL TOO WIDE: %r" % label
        draw.text((cx - tw / 2, 200), label, font=f_l, fill=INK)
    draw.line([MARGIN, 208, W - MARGIN, 208], fill=RULE, width=1)


def draw_hero(draw, hero, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], outline=RULE, width=1)
    art_y1 = y0 + 132
    HERO_ART[hero["art"]](draw, x0 + 1, y0 + 1, x1 - 1, art_y1)
    banner(draw, (x0 + 1, y0 + 1, x1 - 1, art_y1), hero["banner"], size=15)
    tx = x0 + 6
    ty = art_y1 + 5
    f_place = font(F_SANS_BOLD, 9)
    num = "%d  " % hero["n"]
    draw.text((tx, ty), num, font=font(F_SANS_BLACK, 11), fill=RED)
    px = tx + draw.textlength(num, font=font(F_SANS_BLACK, 11))
    draw.text((px, ty + 1), hero["place"], font=f_place, fill=INK)
    pw = draw.textlength(hero["place"], font=f_place)
    tag_chip(draw, px + pw + 6, ty, hero["tag"])
    hy = ty + 15
    f_head = font(F_SERIF_BOLD, 17)
    lines = fit_text(draw, hero["headline"], f_head, x1 - x0 - 12, max_lines=2)
    hy = draw_lines(draw, lines, tx, hy, f_head, INK, 19)
    f_deck = font(F_SERIF, 10)
    lines = fit_text(draw, hero["deck"], f_deck, x1 - x0 - 12, max_lines=2)
    draw_lines(draw, lines, tx, hy + 1, f_deck, (40, 38, 34), 12)
    f_src = font(F_SANS, 8)
    src = "Source: " + hero["source"]
    assert draw.textlength(src, font=f_src) <= x1 - x0 - 12, "HERO SRC TOO WIDE"
    draw.text((tx, y1 - 11), src, font=f_src, fill=FAINT)


def draw_mini(draw, mini, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], outline=RULE, width=1)
    art_y1 = y0 + 56
    art_mini(draw, mini["art"], x0 + 1, y0 + 1, x1 - 1, art_y1)
    banner(draw, (x0 + 1, y0 + 1, x1 - 1, art_y1), mini["banner"], size=11)
    tx = x0 + 5
    ty = art_y1 + 4
    f_place = font(F_SANS_BOLD, 8)
    num = "%d " % mini["n"]
    draw.text((tx, ty), num, font=font(F_SANS_BLACK, 10), fill=RED)
    px = tx + draw.textlength(num, font=font(F_SANS_BLACK, 10))
    pw = draw.textlength(mini["place"], font=f_place)
    if pw > x1 - px - 52:
        place = mini["place"].split(" · ")[0]
        pw = draw.textlength(place, font=f_place)
    else:
        place = mini["place"]
    draw.text((px, ty + 1), place, font=f_place, fill=INK)
    tag_chip(draw, x1 - 5 - 52, ty, mini["tag"], h=12)
    hy = ty + 13
    f_head = font(F_SERIF_BOLD, 12)
    lines = fit_text(draw, mini["headline"], f_head, x1 - x0 - 10, max_lines=2)
    hy = draw_lines(draw, lines, tx, hy, f_head, INK, 13)
    f_deck = font(F_SERIF, 9)
    lines = fit_text(draw, mini["deck"], f_deck, x1 - x0 - 10, max_lines=2)
    draw_lines(draw, lines, tx, hy, f_deck, (40, 38, 34), 10)
    f_src = font(F_SANS, 7)
    src = "Source: " + mini["source"]
    assert draw.textlength(src, font=f_src) <= x1 - x0 - 10, "MINI SRC TOO WIDE"
    draw.text((tx, y1 - 8), src, font=f_src, fill=FAINT)


TAG_CODE = {"CONFIRMED": "C", "OFFICIAL": "O", "REPORTED": "R",
            "CLAIM": "CL", "ONGOING": "OG"}


def section_also_on(draw, data):
    x0, y0, x1, y1 = MARGIN, 732, 652, 916
    f_h = font(F_SANS_BLACK, 12)
    draw.text((x0, y0), "ALSO ON — 24 MORE", font=f_h, fill=INK)
    f_leg = font(F_SANS, 8)
    leg = "C = CONFIRMED · O = OFFICIAL · R = REPORTED · CL = CLAIM · OG = ONGOING"
    draw.text((x0, y0 + 16), leg, font=f_leg, fill=FAINT)
    draw.line([x0, y0 + 28, x1, y0 + 28], fill=INK, width=1)
    col_w = 316
    cols = [x0, x0 + col_w + 8]
    f_b = font(F_SANS_BOLD, 9)
    f_t = font(F_SANS, 9)
    f_n = font(F_SANS_BLACK, 9)
    row_y = y0 + 34
    row_h = 13
    for i, b in enumerate(data["briefs"]):
        col = i // 12
        row = i % 12
        bx = cols[col]
        by = row_y + row * row_h
        num = "%d " % b["n"]
        draw.text((bx, by), num, font=f_n, fill=RED)
        nx = bx + draw.textlength(num, font=f_n)
        head = b["place"] + " — "
        draw.text((nx, by), head, font=f_b, fill=INK)
        hx = nx + draw.textlength(head, font=f_b)
        code = " [%s]" % TAG_CODE[b["tag"]]
        cw = draw.textlength(code, font=f_b)
        avail = bx + col_w - hx - cw
        lines = wrap(draw, b["text"], f_t, avail)
        assert len(lines) == 1, "BRIEF TOO LONG: %r" % b["text"]
        draw.text((hx, by), lines[0], font=f_t, fill=(40, 38, 34))
        tx = hx + draw.textlength(lines[0], font=f_t)
        draw.text((tx, by), code, font=f_b,
                  fill=TAG_FILL[b["tag"]])
    draw.line([x0, y1, x1, y1], fill=RULE, width=1)


def section_map(draw, data):
    x0, y0, x1, y1 = 660, 732, W - MARGIN, 916
    f_h = font(F_SANS_BLACK, 12)
    draw.text((x0, y0), "WHERE IT HAPPENED · PINS 1–18", font=f_h, fill=INK)
    f_leg = font(F_SANS, 8)
    draw.text((x0, y0 + 16), "Number = story number", font=f_leg, fill=FAINT)
    draw.line([x0, y0 + 28, x1, y0 + 28], fill=INK, width=1)
    draw_map(draw, x0, y0 + 34, x1, y1, data["map_pins"])


def section_date_check(draw, data):
    x0, y0, x1, y1 = MARGIN, 924, W - MARGIN, 976
    draw.rectangle([x0, y0, x1, y1], outline=RED, width=1)
    f_h = font(F_SANS_BLACK, 11)
    draw.text((x0 + 8, y0 + 5), "DATE CHECK — WHAT WE LEFT OUT, AND WHY",
              font=f_h, fill=RED)
    f_t = font(F_SANS, 9)
    lines = fit_text(draw, data["date_check"], f_t, x1 - x0 - 16, max_lines=3)
    draw_lines(draw, lines, x0 + 8, y0 + 22, f_t, INK, 11)


def section_footer(draw, data):
    f = font(F_SANS, 9)
    lines = fit_text(draw, data["footer"], f, CW, max_lines=1)
    draw.text((MARGIN, 984), lines[0], font=f, fill=FAINT)
    lines = fit_text(draw, data["how_sure"], f, CW, max_lines=1)
    draw.text((MARGIN, 997), lines[0], font=f, fill=FAINT)


def main():
    with open(os.path.join(HERE, "stories.json"), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data["heroes"]) == 3
    assert len(data["minis"]) == 10
    assert len(data["briefs"]) == 24
    total = (len(data["heroes"]) + len(data["minis"]) + len(data["briefs"]))
    assert total == 37, "STORY COUNT %d != 37" % total
    region_sum = sum(c for _, c, _ in data["regions"])
    assert region_sum == 37, "REGION SUM %d != 37" % region_sum
    assert len(data["map_pins"]) == 18

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    section_masthead(draw, data)
    section_numbers(draw, data)
    section_regions(draw, data)
    section_timeline(draw, data)
    hero_w = 328
    for i, hero in enumerate(data["heroes"]):
        x0 = MARGIN + i * (hero_w + GUT)
        draw_hero(draw, hero, x0, 214, x0 + hero_w, 444)
    mini_ws = [194, 194, 194, 194, 192]
    for r in range(2):
        y0 = 452 + r * 140
        x = MARGIN
        for c in range(5):
            mini = data["minis"][r * 5 + c]
            draw_mini(draw, mini, x, y0, x + mini_ws[c], y0 + 132)
            x += mini_ws[c] + GUT
    section_also_on(draw, data)
    section_map(draw, data)
    section_date_check(draw, data)
    section_footer(draw, data)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
