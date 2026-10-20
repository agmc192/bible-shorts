"""Psalm 1 Short, version 2: faster cuts, zoom/whip transitions, parallax, grading,
light rays, kinetic words, camera dive, seamless loop. Reuses the v1 art library."""
import math, random, subprocess, sys, os
import numpy as np
import cairo
from PIL import Image, ImageDraw
import render as R
from render import (W, H, FPS, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein,
                    draw_text, draw_surf, text_surf, bez_pts, polyline, rounded, cam,
                    F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB, F_CAP, GROUND_Y)

DUR = 50.0


def back_out(x, s=1.9):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


# ---------------------------------------------------------------- word timing
def word_times():
    out = []
    for a, b, g in R.CHUNKS:
        lens = [len(w) + 1 for w in g]
        tot, t = sum(lens), a
        for w, l in zip(g, lens):
            out.append((t, R.clean(w).lower().strip("?")))
            t += (b - a) * l / tot
    return out


WT = word_times()


def wt(word, n=1):
    k = 0
    for t, w in WT:
        if w == word:
            k += 1
            if k == n:
                return t
    raise KeyError(word)


T_STEADY = wt("steady")
T_CRACKED = wt("cracked")
T_STREAM = wt("stream", 1)
T_GREEN = wt("green")
T_HAGAH = wt("hagah")
T_LION = wt("lion")
T_CHEW = wt("chewing")
T_DEVOTED = wt("devoted")
T_HUNGRY = wt("hungry")
T_CHAFF = wt("chaff")
T_ROOTS2 = wt("roots", 2)
T_ROOTED = wt("rooted")

# ---------------------------------------------------------------- global camera events
ZOOMS = [(T_STEADY, 0.10), (T_CRACKED, 0.08), (T_GREEN, 0.07), (22.2, 0.12), (27.07, 0.10),
         (T_DEVOTED, 0.05), (T_HUNGRY, 0.05), (T_CHAFF, 0.10), (T_ROOTS2, 0.08), (T_ROOTED, 0.06)]
SHAKES = [(0.12, 20, 0.5), (0.45, 8, 1.0), (T_STEADY, 6, 0.3), (T_CRACKED, 7, 0.4), (9.7, 8, 0.5),
          (22.2, 14, 0.5), (24.25, 9, 2.0), (27.07, 7, 0.3), (T_CHAFF, 8, 0.4), (36.0, 5, 1.2),
          (42.9, 10, 0.8), (44.4, 6, 0.3), (T_ROOTED, 4, 0.3)]
FLASHES = [(0.12, (1, 1, 1), 0.55, 0.25), (9.7, (0.85, 0.95, 1.0), 0.35, 0.4), (22.2, (1, 0.85, 0.5), 0.3, 0.4),
           (42.9, (1, 1, 1), 0.75, 0.35), (44.4, (1, 1, 1), 0.9, 0.35)]
BLUR = [(3.85, 4.5), (7.4, 8.25), (12.0, 12.5), (14.05, 14.65), (18.7, 19.4), (26.45, 27.05),
        (31.0, 31.6), (33.25, 33.95), (39.1, 39.7), (39.8, 41.4), (41.75, 42.5)]
# the v2 scenes start at absolute time; captions from R.CHUNKS
ZC = (540, 860)


def zoom_amt(t):
    z = 0.0
    for t0, a in ZOOMS:
        u = t - t0
        if 0 <= u < 1.2:
            z += a * (ease(u / 0.07) if u < 0.07 else math.exp(-(u - 0.07) * 5))
    return 1 + z


def shake_amt(t):
    dx = dy = rot = 0.0
    for t0, amp, dur in SHAKES:
        u = t - t0
        if 0 <= u < dur:
            k = amp * (1 - u / dur) ** 2
            dx += k * math.sin(u * 61 + t0)
            dy += k * math.sin(u * 47 + 1.3 * t0)
            rot += k * 0.0009 * math.sin(u * 53)
    return dx, dy, rot


# ---------------------------------------------------------------- effects
def grade(ctx, desat=0.0, warm=0.0, cool=0.0, rect=None):
    ctx.save()
    if rect:
        ctx.rectangle(*rect)
        ctx.clip()
    if desat > 0.01:
        ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
        ctx.set_source_rgba(0.5, 0.5, 0.5, desat)
        ctx.paint()
    if warm > 0.01:
        ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
        ctx.set_source_rgba(1.0, 0.55, 0.18, warm)
        ctx.paint()
    if cool > 0.01:
        ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
        ctx.set_source_rgba(0.25, 0.42, 0.62, cool)
        ctx.paint()
    ctx.restore()


def rays(ctx, cx, cy, a0, a1, n, length, alpha, rot=0.0, color=(1.0, 0.86, 0.55), spread=0.06):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    for i in range(n):
        a = a0 + (a1 - a0) * (i + 0.5) / n + 0.08 * math.sin(rot + i * 1.7)
        w = spread * (0.6 + 0.4 * math.sin(i * 2.3 + rot * 0.7))
        g = cairo.RadialGradient(cx, cy, 0, cx, cy, length)
        k = alpha * (0.5 + 0.5 * math.sin(rot * 1.3 + i))
        g.add_color_stop_rgba(0, *color, 0.28 * k)
        g.add_color_stop_rgba(1, *color, 0)
        ctx.set_source(g)
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a - w) * length, cy + math.sin(a - w) * length)
        ctx.line_to(cx + math.cos(a + w) * length, cy + math.sin(a + w) * length)
        ctx.close_path()
        ctx.fill()
    ctx.restore()


_dr = random.Random(21)
DUST = [(_dr.uniform(0, W), _dr.uniform(0, 1400), _dr.uniform(0, 6.28), _dr.uniform(2, 6)) for _ in range(70)]


def dust(ctx, t, alpha, color="gold2", vx=14, vy=-22):
    if alpha <= 0.01:
        return
    ctx.save()
    for x0, y0, ph, s in DUST:
        x = (x0 + vx * t + 18 * math.sin(t * 0.7 + ph)) % W
        y = (y0 + vy * t) % 1400
        a = alpha * (0.35 + 0.35 * math.sin(t * 1.8 + ph))
        ctx.set_source_rgba(*col(color)[:3], a)
        ctx.arc(x, y, s, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()


def kword(ctx, txt, t, t0, cx, cy, size=200, color="#E3B04B", dur=1.1, path=F_SERIF):
    u = t - t0
    if u < 0 or u > dur + 0.3:
        return
    sc = lerp(1.9, 1.0, ein(seg(u, 0, 0.14))) if u < 0.14 else 1 + 0.06 * math.exp(-(u - 0.14) * 9) * math.sin((u - 0.14) * 30)
    sc *= 1 + 0.04 * seg(u, 0.14, dur)
    a = seg(u, 0, 0.05) * (1 - seg(u, dur, dur + 0.3))
    s = text_surf(txt, path, size, color, stroke=7, stroke_color="#2A1D14")
    sh = text_surf(txt, path, size, "#2A1D14", stroke=7, stroke_color="#2A1D14")
    draw_surf(ctx, sh, cx + 8, cy + 12, a * 0.45, sc)
    draw_surf(ctx, s, cx, cy, a, sc)


def hills(ctx, base, amp, color, off, seed, freq=1.0):
    r = random.Random(seed)
    ph = [r.uniform(0, 6) for _ in range(3)]
    ctx.set_source_rgba(*color)
    ctx.move_to(-300, H)
    for i in range(0, 61):
        x = -300 + i * (W + 600) / 60
        xx = x + off
        y = base - amp * (0.55 * math.sin(xx / 210 * freq + ph[0]) + 0.3 * math.sin(xx / 97 * freq + ph[1])
                          + 0.15 * math.sin(xx / 43 + ph[2]))
        ctx.line_to(x, y)
    ctx.line_to(W + 300, H)
    ctx.close_path()
    ctx.fill()


def fg_grass(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c)
    for a, l in [(-0.5, 120), (-0.25, 170), (0.0, 200), (0.2, 150), (0.45, 110), (-0.1, 140)]:
        ex, ey = math.sin(a) * l, -math.cos(a) * l
        ctx.move_to(-10, 0)
        ctx.curve_to(ex * 0.3 - 6, ey * 0.5, ex * 0.9, ey * 0.9, ex, ey)
        ctx.curve_to(ex * 0.9 + 4, ey * 0.85, ex * 0.3 + 10, ey * 0.45, 10, 0)
        ctx.close_path()
        ctx.fill()
    ctx.restore()


def tuft(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c)
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for a in (-0.6, -0.3, 0, 0.3, 0.6):
        ctx.move_to(0, 0)
        ctx.curve_to(a * 10, -14, a * 26, -26, a * 34, -40 + abs(a) * 10)
        ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- living world with parallax
BANK_TUFTS = [(x, R.STREAM[min(len(R.STREAM) - 1, int((x + 60) / (W + 120) * 160))][1] + side * 42, side)
              for x in range(-20, W + 40, 64) for side in (-1, 1)]


def world2(ctx, t, px=0.0, *, crack=1.0, shrubs_dead=1.0, shrub_alpha=1.0, tree_grow=1.0, stream_prog=1.0,
           sun_a=1.0, shimmer_a=0.0, roots=0.0, tree_alpha=1.0, glow=0.0, sway=0.0, lush=1.0, fg=True):
    R.bg(ctx, col("cream"))
    ctx.save()
    ctx.translate(px * 0.15, 0)
    R.sun(ctx, t, sun_a)
    ctx.restore()
    R.shimmer(ctx, t, shimmer_a)
    hills(ctx, 930, 70, hexc("#E7D6B6"), -px * 0.25, 1)
    hills(ctx, 975, 45, lerpc(hexc("#DCC9A4"), hexc("#B9C7A0"), lush), -px * 0.45, 2, 1.4)
    ctx.save()
    ctx.translate(px * 0.7, 0)
    R.ground(ctx)
    R.cracks(ctx, crack)
    R.stream(ctx, t, stream_prog)
    # bank grass pops in following the water
    if lush > 0:
        for i, (x, y, side) in enumerate(BANK_TUFTS):
            d = (x + 60) / (W + 120)
            p = back_out(seg(lush * 1.4 - d * 0.4, 0, 0.35))
            if p > 0:
                tuft(ctx, x, y + (8 if side > 0 else 0), 0.9 * p, col("leaf2" if i % 3 else "leaf"))
    if roots > 0:
        R.roots_simple(ctx, roots)
    for x, y, s in R.SHRUBS:
        R.shrub(ctx, x, y, s, shrubs_dead, shrub_alpha)
    R.tree(ctx, 540, GROUND_Y + 4, tree_grow, 1.0, sway, tree_alpha, glow)
    ctx.restore()
    if fg:
        gc = lerpc(col("dead"), col("leafdark"), lush)
        ctx.save()
        ctx.translate(px * 1.4, 0)
        fg_grass(ctx, 40, 1400, 1.6, gc)
        fg_grass(ctx, 1040, 1420, 1.4, gc)
        ctx.restore()


# ---------------------------------------------------------------- scene 1: the world shatters
S1C = (540, 860)
FIG_Y = 1060


def make_shards():
    r = random.Random(2)
    n = 13
    angs = sorted((i + r.uniform(-0.3, 0.3)) * 2 * math.pi / n for i in range(n))
    radii = [0, 150, 330, 570, 880, 1300, 1900]
    V = [[None] * n for _ in radii]
    for i, rad in enumerate(radii):
        for j, a in enumerate(angs):
            rr = rad * (1 + (r.uniform(-0.12, 0.12) if i else 0))
            aa = a + (r.uniform(-0.06, 0.06) if i else 0)
            V[i][j] = (S1C[0] + math.cos(aa) * rr, S1C[1] + math.sin(aa) * rr)
    cells = []
    for i in range(len(radii) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            poly = [V[i][j], V[i][j2], V[i + 1][j2], V[i + 1][j]]
            cx = sum(p[0] for p in poly) / 4
            cy = sum(p[1] for p in poly) / 4
            cells.append(dict(poly=poly, c=(cx, cy), ring=i, st=0.42 + i * 0.06 + r.uniform(0, 0.14),
                              spin=r.uniform(-2.5, 2.5), sp=r.uniform(0.8, 1.3)))
    edges = []
    for i in range(1, len(radii)):
        for j in range(n):
            edges.append((V[i][j], V[i][(j + 1) % n], radii[i]))
            edges.append((V[i - 1][j], V[i][j], radii[i]))
    return cells, edges


SHARDS, EDGES = make_shards()
MIN_ST = min(d['st'] for d in SHARDS)


def intact(ctx):
    ctx.set_source_rgba(*col("cream"))
    ctx.rectangle(-400, -400, W + 800, FIG_Y + 400)
    ctx.fill()
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(-400, FIG_Y, W + 800, H)
    ctx.fill()
    ctx.set_source_rgba(*col("brown2", 0.5))
    ctx.set_line_width(3)
    ctx.move_to(-400, FIG_Y)
    ctx.line_to(W + 400, FIG_Y)
    ctx.stroke()


def scene1(ctx, lt):
    ctx.save()
    push = 1.0 + 0.16 * ease(lt / 4.0)
    dive = 1 + 4.0 * ein(seg(lt, 3.85, 4.25))
    ctx.translate(540, 900)
    ctx.rotate(0.06 * ease(seg(lt, 0.4, 4.0)) - 0.03)
    ctx.scale(push, push)
    ctx.translate(-540, -900)
    if dive > 1:
        cam(ctx, 540, 1085, dive)
    # what lies behind the world
    R.bg(ctx, col("dark"))
    gl = ease(seg(lt, 0.45, 1.2))
    rg = cairo.RadialGradient(540, 860, 30, 540, 860, 760)
    rg.add_color_stop_rgba(0, *col("gold2")[:3], 0.75 * gl)
    rg.add_color_stop_rgba(0.45, *col("gold")[:3], 0.25 * gl)
    rg.add_color_stop_rgba(1, *col("dark")[:3], 0)
    ctx.set_source(rg)
    ctx.paint()
    rays(ctx, 540, 860, 0, 2 * math.pi, 16, 1100, gl * 0.8, lt * 0.6)
    dust(ctx, lt, gl)
    # the shards of the world (drawn whole until the first piece moves, so no seams)
    if lt < MIN_ST:
        intact(ctx)
    for d in (SHARDS if lt >= MIN_ST else []):
        u = lt - d["st"]
        cx, cy = d["c"]
        if u > 0:
            ox, oy = cx - S1C[0], cy - S1C[1]
            dist0 = math.hypot(ox, oy) + 1
            sw = (0.5 * u + 0.18 * u * u) * d["sp"]
            ca, sa = math.cos(sw), math.sin(sw)
            rx, ry = ox * ca - oy * sa, ox * sa + oy * ca
            push_o = (220 * u + 200 * u * u) * d["sp"]
            nx, ny = S1C[0] + rx + rx / dist0 * push_o, S1C[1] + ry + ry / dist0 * push_o
            rot = d["spin"] * u
            scl = 1 - 0.3 * clamp(u / 2.0)
            a = 1 - seg(math.hypot(nx - S1C[0], ny - S1C[1]), 1100, 1700)
        else:
            nx, ny, rot, scl, a = cx, cy, 0, 1, 1
        if a <= 0:
            continue
        ctx.save()
        ctx.translate(nx, ny)
        ctx.rotate(rot)
        ctx.scale(scl, scl)
        ctx.translate(-cx, -cy)
        ctx.push_group()

        def poly_path():
            ctx.new_path()
            ctx.move_to(*d["poly"][0])
            for p in d["poly"][1:]:
                ctx.line_to(*p)
            ctx.close_path()

        ctx.save()
        poly_path()
        ctx.clip()
        intact(ctx)
        ctx.restore()
        if u > 0:
            poly_path()
            ctx.set_source_rgba(1, 0.97, 0.9, 0.9)
            ctx.set_line_width(3)
            ctx.stroke()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        ctx.restore()
    # cracks racing out from the centre
    cr = 1900 * eout(seg(lt, 0.12, 0.42))
    fade = 1 - seg(lt, 0.42, 0.7)
    if cr > 0 and fade > 0:
        ctx.save()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for p1, p2, rad in EDGES:
            if rad <= cr:
                ctx.set_source_rgba(1, 1, 1, fade)
                ctx.set_line_width(5)
                ctx.move_to(*p1)
                ctx.line_to(*p2)
                ctx.stroke()
                ctx.set_source_rgba(*col("brown", fade * 0.6))
                ctx.set_line_width(1.5)
                ctx.move_to(*p1)
                ctx.line_to(*p2)
                ctx.stroke()
        ctx.restore()
    # leaves caught in the swirl
    for i, d in enumerate(R.DEBRIS[:28]):
        u = lt - 0.5 - d["start"] * 0.6
        if u <= 0 or d["kind"] != "leaf":
            continue
        rr = 200 + 120 * u * d["speed"]
        ang = d["ang"] + u * 1.6 * d["speed"]
        x, y = 540 + math.cos(ang) * rr, 860 + math.sin(ang) * rr * 0.75
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(d["spin"] * u)
        ctx.scale(1.2, 0.55)
        ctx.set_source_rgba(*col(d["col"], clamp(u / 0.3)))
        ctx.arc(0, 0, 20, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    # the steady one, standing on the only ground that holds
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(445, FIG_Y, 190, 52)
    ctx.fill()
    ctx.set_source_rgba(*col("sand2"))
    ctx.rectangle(445, FIG_Y + 44, 190, 8)
    ctx.fill()
    R.figure(ctx, 540, FIG_Y, 1.6, col("brown"))
    ctx.restore()
    kword(ctx, "STEADY", lt, T_STEADY - 0.05, 540, 330, 190)


# ---------------------------------------------------------------- scene 2: drought, then the stream
def scene2(ctx, lt):
    ctx.save()
    pull = 1.0 + 2.4 * (1 - eout(seg(lt, 0.0, 1.0)))
    cam(ctx, 540, 1180, pull)
    cam(ctx, 540, 900, 1.0 + 0.05 * ease(lt / 9))
    px = 60 - 120 * ease(lt / 9)
    flood = ease(seg(lt, 5.5, 6.4))
    world2(ctx, lt + 4.2, px,
           crack=ease(seg(lt, 2.5, 4.4)), shrubs_dead=ease(seg(lt, 2.6, 6.0)),
           shrub_alpha=ease(seg(lt, 1.6, 2.4)), tree_grow=seg(lt, 3.0, 5.2),
           stream_prog=eout(seg(lt, 5.5, 6.1)), sun_a=ease(seg(lt, 0.6, 1.6)),
           shimmer_a=ease(seg(lt, 0.8, 1.6)) * (1 - 0.6 * flood),
           glow=math.sin(math.pi * seg(lt + 4.2, T_GREEN - 0.2, T_GREEN + 1.4)),
           sway=0.015 * math.sin(lt * 1.3), lush=flood)
    # splash at the stream's leading edge
    sp = seg(lt, 5.5, 6.1)
    if 0 < sp < 1:
        n = len(R.STREAM)
        hx, hy = R.STREAM[min(n - 1, int(n * eout(sp)))]
        hx += px * 0.7
        ctx.set_source_rgba(*col("water2", 0.9))
        for k in range(10):
            a = -math.pi * (0.1 + 0.8 * k / 9)
            rr = 30 + 40 * ((lt * 7 + k * 0.37) % 1.0)
            ctx.arc(hx + math.cos(a) * rr * 0.6, hy + math.sin(a) * rr, 7, 0, 2 * math.pi)
            ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.arc(hx, hy, 26, 0, 2 * math.pi)
        ctx.fill()
    # sparkles on "stay green"
    g = seg(lt + 4.2, T_GREEN - 0.1, T_GREEN + 1.6)
    if 0 < g < 1:
        r = random.Random(4)
        for k in range(18):
            ph = (g * 2 + k / 18) % 1
            x, y = 540 + r.uniform(-230, 230) + px * 0.7, r.uniform(450, 800)
            s = 10 * math.sin(math.pi * ph)
            ctx.set_source_rgba(1, 0.97, 0.75, 0.9 * math.sin(math.pi * ph))
            R.star_path(ctx, x, y, s, s * 0.3, 4)
            ctx.fill()
    dust(ctx, lt, 0.6 * (1 - flood), "gold")
    ctx.restore()
    grade(ctx, desat=0.78 * (1 - flood), warm=0.38 * (1 - flood) + 0.06)
    a = ease(seg(lt, 0.6, 1.2)) * (1 - ease(seg(lt, 2.6, 3.2)))
    draw_text(ctx, "PSALM 1", F_SERIF, 118, "#3B2A1E", 540, 230, a, 0.94 + 0.06 * back_out(seg(lt, 0.6, 1.0)))
    draw_text(ctx, "The opening song", F_SERIF_I, 54, "#6E5039", 540, 335, a * ease(seg(lt, 0.9, 1.5)))


# ---------------------------------------------------------------- scene 3: the person who delights
def scene3(ctx, lt):
    k = ease(seg(lt, 0.2, 1.4)) * (1 - ease(seg(lt, 3.5, 4.8)))
    ctx.save()
    dive = 1 + 7 * ein(seg(lt, 5.5, 6.15))
    cam(ctx, 540, 840, dive)
    orbit = 0.02 * math.sin(lt * 0.6)
    ctx.translate(540, 900)
    ctx.rotate(orbit)
    ctx.translate(-540, -900)
    cam(ctx, 540, 900, 1.06 + 0.06 * ease(lt / 5.5))
    world2(ctx, lt + 13.2, -60 + 60 * ease(lt / 6), crack=1, shrubs_dead=1, tree_grow=1, stream_prog=1,
           sun_a=1, shimmer_a=0.2, roots=ease(seg(lt, 0.0, 1.2)), tree_alpha=1 - 0.8 * k,
           sway=0.015 * math.sin((lt + 9) * 1.3), lush=1)
    rays(ctx, 860, 300, math.radians(100), math.radians(170), 7, 1300, 0.7 + 0.3 * k, lt * 0.5)
    if k > 0:
        ctx.push_group()
        g = cairo.RadialGradient(540, 820, 20, 540, 820, 320)
        g.add_color_stop_rgba(0, *col("gold2")[:3], 0.45)
        g.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(g)
        ctx.arc(540, 820, 320, 0, 2 * math.pi)
        ctx.fill()
        R.figure(ctx, 540, GROUND_Y + 4, 2.0, col("brown"), arms=back_out(seg(lt, 0.5, 1.5), 1.2))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)
    # glowing scroll with sparkles
    sa = back_out(seg(lt, 1.3, 1.8))
    if sa > 0:
        ctx.save()
        ctx.translate(820, 1062)
        pulse = 0.65 + 0.35 * math.sin(lt * 4)
        g = cairo.RadialGradient(0, 0, 10, 0, 0, 220)
        g.add_color_stop_rgba(0, *col("gold2")[:3], 0.7 * clamp(sa) * pulse)
        g.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(g)
        ctx.arc(0, 0, 220, 0, 2 * math.pi)
        ctx.fill()
        ctx.scale(max(0.01, sa), max(0.01, sa))
        ctx.set_source_rgba(*col("cream2"))
        ctx.rectangle(-70, -38, 140, 76)
        ctx.fill()
        ctx.set_source_rgba(*col("dry"))
        for sx in (-1, 1):
            ctx.rectangle(sx * 70 - 9, -46, 18, 92)
            ctx.fill()
        ctx.set_source_rgba(*col("brown2", 0.6))
        ctx.set_line_width(3)
        for j in range(4):
            ctx.move_to(-48, -20 + j * 13)
            ctx.line_to(48, -20 + j * 13)
        ctx.stroke()
        r = random.Random(8)
        for j in range(8):
            ph = (lt * 0.8 + j / 8) % 1
            x, y = r.uniform(-110, 110), -40 - ph * 140
            s = 9 * math.sin(math.pi * ph)
            ctx.set_source_rgba(1, 0.95, 0.7, math.sin(math.pi * ph))
            R.star_path(ctx, x, y, s, s * 0.3, 4)
            ctx.fill()
        ctx.restore()
    ctx.restore()
    grade(ctx, warm=0.08)


# ---------------------------------------------------------------- scene 4: hagah
def scene4(ctx, lt):
    R.bg(ctx, col("dark"))
    iris = eout(seg(lt, 0.0, 0.8))
    g = cairo.RadialGradient(540, 680, 20, 540, 680, 120 + 800 * iris)
    g.add_color_stop_rgba(0, *col("brown2")[:3], 0.7)
    g.add_color_stop_rgba(1, *col("dark")[:3], 0)
    ctx.set_source(g)
    ctx.paint()

    ctx.save()
    # lion close-up that pulls out
    la = ease(seg(lt, 4.3, 4.6)) * (1 - ease(seg(lt, 7.0, 7.4)))
    lionz = 1 + 1.4 * (1 - eout(seg(lt, 4.3, 5.3)))
    chew = ease(seg(lt, 7.85, 8.1))
    linez = 1 + 0.25 * eout(seg(lt, 7.9, 8.3)) + 5 * ein(seg(lt, 11.95, 12.45))
    dust(ctx, lt, 0.8 * (1 - seg(lt, 11.8, 12.3)), "gold2", 6, -12)

    # Beat A: the Hebrew word burns in
    hdr = ease(seg(lt, 3.8, 4.3))
    ha = ease(seg(lt, 0.3, 0.6)) * (1 - ease(seg(lt, 11.8, 12.2)))
    reveal = ease(seg(lt, 1.2, 2.95))
    hy, hs = lerp(640, 230, hdr), lerp(1.0, 0.5, hdr)
    rays(ctx, 540, hy, 0, 2 * math.pi, 18, 900 * hs + 200, ha * (0.5 + 0.5 * seg(lt, 2.8, 3.1)) * (1 - 0.6 * hdr), lt * 0.4)
    if ha > 0:
        s = text_surf("הָגָה", F_HEB, 320, "#E3B04B", rtl=True, glow=16)
        ww, hh = s.get_width(), s.get_height()
        ctx.save()
        ctx.translate(540, hy)
        ctx.scale(hs, hs)
        ctx.rectangle(ww / 2 - ww * reveal, -hh / 2, ww * reveal, hh)
        ctx.clip()
        ctx.set_source_surface(s, -ww / 2, -hh / 2)
        ctx.paint_with_alpha(ha)
        ctx.restore()
        if 0 < reveal < 1:
            fx = 540 + (ww / 2 - ww * reveal) * hs
            ctx.save()
            ctx.set_operator(cairo.OPERATOR_ADD)
            lg = cairo.LinearGradient(fx - 40, 0, fx + 40, 0)
            lg.add_color_stop_rgba(0, 1, 0.8, 0.4, 0)
            lg.add_color_stop_rgba(0.5, 1, 0.92, 0.65, 0.9)
            lg.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
            ctx.set_source(lg)
            ctx.rectangle(fx - 40, hy - hh * hs / 2, 80, hh * hs)
            ctx.fill()
            ctx.restore()
            r = random.Random(int(lt * 30))
            for _ in range(10):
                ctx.set_source_rgba(1, 0.85, 0.45, r.uniform(0.4, 1))
                ctx.arc(fx + r.uniform(-20, 30), hy + r.uniform(-120, 120) * hs * 2, r.uniform(2, 5), 0, 2 * math.pi)
                ctx.fill()
    sub = ease(seg(lt, 2.9, 3.3)) * (1 - ease(seg(lt, 3.8, 4.1)))
    draw_text(ctx, "hagah", F_SERIF_I, 104, "#FBF6EC", 540, 900, sub, 0.9 + 0.1 * back_out(seg(lt, 2.9, 3.3)))
    draw_text(ctx, "to meditate · to murmur", F_SERIF_R, 56, "#DCC59D", 540, 1000, sub)
    draw_text(ctx, "hagah · to meditate", F_SERIF_I, 48, "#DCC59D", 540, 340, hdr * (1 - ease(seg(lt, 11.8, 12.2))))

    # Beat B: lion
    if la > 0:
        ctx.save()
        cam(ctx, 330, 820, lionz)
        growl = seg(lt, 5.0, 7.2)
        breath = (math.sin(lt * 11) * 0.5 + 0.5) * growl
        R.lion(ctx, 690, 820, 1.0, la, breath)
        if growl > 0:
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            mx, my = 318, 820
            for kk in range(5):
                u = ((lt - 5.0) * 1.1 + kk * 0.2) % 1.0
                rr = 40 + u * 300
                ctx.set_source_rgba(*col("gold2", la * (1 - u)))
                ctx.set_line_width(12 * (1 - u) + 3)
                ctx.arc(mx, my, rr, math.pi - 0.6, math.pi + 0.6)
                ctx.stroke()
        ctx.restore()
        tag = back_out(seg(lt, 4.7, 5.1))
        ctx.save()
        ctx.translate(850, 1217)
        ctx.scale(max(0.01, tag), max(0.01, tag))
        ctx.set_source_rgba(*col("gold", la))
        rounded(ctx, -150, -37, 300, 74, 37)
        ctx.fill()
        ctx.restore()
        draw_text(ctx, "Isaiah 31:4", F_SERIF, 44, "#2A1D14", 850, 1217, la * clamp(tag))

    # Beat C: skimming, then chewing
    pa = ease(seg(lt, 7.1, 7.4)) * (1 - ease(seg(lt, 12.2, 12.5)))
    if pa > 0:
        ctx.save()
        cam(ctx, 540, 818, linez)
        pulse = 0.4 * max(0, math.sin(lt * 5)) + 0.7 * math.exp(-((lt + 19.2 - T_DEVOTED) ** 2) * 8) \
            + 0.7 * math.exp(-((lt + 19.2 - T_HUNGRY) ** 2) * 8)
        R.page_card(ctx, 540, 800, lt * 1.6, chew, clamp(pulse), pa)
        ctx.restore()
        draw_text(ctx, "skimming", F_SERIF_I, 70, "#DCC59D", 540, 470, pa * (1 - chew) * (1 - seg(lt, 7.85, 7.95)))
    kword(ctx, "CHEWING", lt + 19.2, T_CHEW - 0.05, 540, 1260, 150, "#E3B04B", 3.3)
    ctx.restore()

    # Beat D: macro on the roots drinking, pulls back
    wa = ease(seg(lt, 12.15, 12.6))
    if wa > 0:
        mz = lerp(3.0, 1.18, eout(seg(lt, 12.15, 13.3)))
        ctx.push_group()
        ctx.save()
        whip = -1300 * ein(seg(lt, 14.05, 14.4))
        ctx.translate(whip, 0)
        cam(ctx, lerp(470, 540, eout(seg(lt, 12.15, 13.3))), lerp(1090, 1000, eout(seg(lt, 12.15, 13.3))), mz)
        world2(ctx, lt, 0, crack=0.5, shrubs_dead=1, tree_grow=1, stream_prog=1, sun_a=0.8,
               roots=1, sway=0.012 * math.sin(lt * 1.3), lush=1)
        R.droplets(ctx, lt, 1.0)
        ctx.restore()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(wa)


# ---------------------------------------------------------------- scene 5: chaff
def chaff_particles():
    im = Image.new("L", (900, 300), 0)
    f = R.font(F_SERIF, 170)
    d = ImageDraw.Draw(im)
    d.text((450, 150), "CHAFF", font=f, fill=255, anchor="mm")
    a = np.asarray(im)
    ys, xs = np.nonzero(a[::5, ::5] > 128)
    r = random.Random(13)
    pts = []
    xmin, xmax = xs.min(), xs.max()
    for x, y in zip(xs, ys):
        px, py = x * 5 - 450, y * 5 - 150
        delay = 0.55 * (x - xmin) / (xmax - xmin) + r.uniform(0, 0.25)
        pts.append((px, py, delay, r.uniform(350, 750), r.uniform(-220, 60), r.uniform(0, 6.28)))
    return pts


CHAFF_PTS = chaff_particles()


def scene5(ctx, lt):
    ctx.save()
    whip = 1300 * (1 - eout(seg(lt, -0.1, 0.3)))
    ctx.translate(whip, 0)
    zin = 1 + 3.5 * ein(seg(lt, 5.45, 5.85))
    cam(ctx, 270, 1000, zin)
    R.bg(ctx, col("cream"))
    hills(ctx, 950, 50, hexc("#E7D6B6"), lt * 10, 3)
    R.ground(ctx)
    ctx.save()
    ctx.rectangle(0, 0, 540, H)
    ctx.clip()
    ctx.save()
    ctx.translate(270, GROUND_Y)
    ctx.scale(0.62, 0.62)
    ctx.translate(-540, -GROUND_Y)
    R.stream(ctx, lt + 33.6, 1.0)
    for x, y, side in BANK_TUFTS:
        tuft(ctx, x, y, 0.9, col("leaf2"))
    R.roots_simple(ctx, 1.0)
    R.tree(ctx, 540, GROUND_Y + 4, 1, 1, 0.01 * math.sin(lt), 1, 0.35)
    ctx.restore()
    rays(ctx, 120, 200, math.radians(40), math.radians(90), 5, 1100, 0.6, lt * 0.5)
    ctx.restore()
    gust = seg(lt + 33.6, T_CHAFF - 0.4, T_CHAFF)
    ctx.save()
    ctx.rectangle(540, 0, 540, H)
    ctx.clip()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(9):
        ph = (lt * 1.1 + k * 0.13) % 1.0
        a = math.sin(math.pi * ph) * 0.5 * gust
        y = 520 + k * 62
        x0 = 480 + ph * 760
        ctx.set_source_rgba(*col("brown2", a))
        ctx.set_line_width(5)
        ctx.move_to(x0, y)
        ctx.curve_to(x0 + 70, y - 16, x0 + 140, y + 16, x0 + 230, y)
        ctx.stroke()
    for d in R.WHEAT:
        bx, by = d["x"], GROUND_Y + 6
        bend = d["lean"] + 0.14 * gust * math.sin(lt * 3.5 + d["ph"])
        u = lt - (d["t"] * 0.8 + 0.6)
        stalk_a = 1 - ease(seg(u, 0.3, 1.0))
        tx, ty = bx + math.sin(bend) * d["h"], by - math.cos(bend) * d["h"]
        if stalk_a > 0:
            ctx.set_source_rgba(*col("dry", stalk_a))
            ctx.set_line_width(5)
            ctx.move_to(bx, by)
            ctx.curve_to(bx, by - d["h"] * 0.5, tx, ty + 30, tx, ty)
            ctx.stroke()
        if u < 0:
            hx, hy, rot, ha = tx, ty, bend, 1.0
        else:
            hx = tx + d["vx"] * 1.3 * u + 60 * u * u
            hy = ty + d["vy"] * u + 30 * math.sin(u * 5 + d["ph"])
            rot, ha = bend + d["spin"] * u, 1 - seg(u, 0.5, 1.3)
        if ha > 0:
            ctx.save()
            ctx.translate(hx, hy)
            ctx.rotate(rot)
            ctx.set_source_rgba(*col("gold" if u < 0 else "sand2", ha))
            for j in range(5):
                ctx.save()
                ctx.translate(0, -j * 13)
                ctx.scale(0.55, 1)
                ctx.arc(0, 0, 12, 0, 2 * math.pi)
                ctx.restore()
                ctx.fill()
            ctx.restore()
    ctx.restore()
    grade(ctx, desat=0.55, warm=0.3, rect=(540, 0, 540, H))
    # divider
    dv = eout(seg(lt, 0.25, 0.8))
    ctx.set_source_rgba(*col("gold"))
    ctx.set_line_width(5)
    ctx.move_to(540, 380)
    ctx.line_to(540, 380 + 1000 * dv)
    ctx.stroke()
    draw_text(ctx, "rooted", F_SERIF_I, 66, "#466E2E", 270, 300, ease(seg(lt, 0.4, 0.9)), 0.9 + 0.1 * back_out(seg(lt, 0.4, 0.8)))
    # CHAFF slams in, then blows away as dust
    tc = lt + 33.6
    u = tc - (T_CHAFF - 0.05)
    cx, cy = 810, 660
    blow = u - 1.0
    if 0 <= u and blow < 0:
        sc = lerp(1.9, 1.0, ein(seg(u, 0, 0.14))) if u < 0.14 else 1.0
        s = text_surf("CHAFF", F_SERIF, 170, "#A9472F", stroke=6, stroke_color="#2A1D14")
        draw_surf(ctx, s, cx, cy, seg(u, 0, 0.05), sc * 0.6)
    elif blow >= 0:
        ctx.set_source_rgba(*col("rust"))
        for px, py, dl, vx, vy, ph in CHAFF_PTS:
            v = blow - dl
            if v < 0:
                x, y, a = px, py, 1.0
            else:
                x = px + vx * v + 120 * v * v
                y = py + vy * v + 25 * math.sin(v * 6 + ph)
                a = 1 - seg(v, 0.3, 1.1)
            if a <= 0:
                continue
            c = lerpc(col("rust"), col("sand2"), clamp(v * 2) if v > 0 else 0)
            ctx.set_source_rgba(*c[:3], a)
            ctx.rectangle(cx + x * 0.6 - 3, cy + y * 0.6 - 3, 6, 6)
            ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- scene 6: dive to the roots, storm
DEEP_TIP = max(R.DEEP, key=lambda s: s[3])


def scene6(ctx, lt):
    tipx, tipy = DEEP_TIP[2], DEEP_TIP[3]
    a1 = eout(seg(lt, -0.1, 0.35))
    dv = ease(seg(lt, 0.35, 1.9))
    po = eout(seg(lt, 2.35, 3.3))
    cx = lerp(lerp(lerp(270, 540, a1), tipx, dv), 540, po)
    cy = lerp(lerp(lerp(1000, 704, a1), tipy - 30, dv), 950, po)
    sc = lerp(lerp(lerp(3.5, 1.6, a1), 2.4, dv), 0.72, po)
    ctx.save()
    ctx.translate(540, 700)
    ctx.scale(sc, sc)
    ctx.translate(-cx, -cy)
    storm = ease(seg(lt, 2.6, 3.2))
    ctx.set_source_rgba(*lerpc(col("cream"), hexc("#A79C8C"), storm))
    ctx.rectangle(-900, -900, 2900, 1604)
    ctx.fill()
    hills(ctx, 690, 40, lerpc(hexc("#B9C7A0"), hexc("#8E957E"), storm), 0, 2, 1.4)
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(-900, 700, 2900, 2600)
    ctx.fill()
    for k in range(6):
        ctx.set_source_rgba(*col("sand2", 0.8))
        ctx.rectangle(-900, 860 + k * 160, 2900, 5 + k)
        ctx.fill()
    r = random.Random(17)
    ctx.set_source_rgba(*col("sand2"))
    for _ in range(120):
        ctx.arc(r.uniform(-300, 1400), r.uniform(720, 1700), r.uniform(4, 14), 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgba(*col("brown2", 0.6))
    ctx.set_line_width(4)
    ctx.move_to(-900, 700)
    ctx.line_to(2000, 700)
    ctx.stroke()
    ctx.set_source_rgba(*col("water", 0.95))
    ctx.rectangle(-900, 1470, 2900, 90)
    ctx.fill()
    ctx.set_source_rgba(*col("water2", 0.9))
    ctx.set_line_width(6)
    for k in range(14):
        x = ((lt * 120 + k * 210) % 2900) - 900
        ctx.move_to(x, 1500 + (k % 2) * 30)
        ctx.line_to(x + 90, 1500 + (k % 2) * 30)
        ctx.stroke()
    g = 0.6 + seg(lt, 0.0, 1.8) * 1.0
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*col("brown2"))
    for x, y, x2, y2, w, t0, dep in R.DEEP:
        p = clamp((g - t0) / 0.3)
        if p <= 0:
            continue
        ctx.set_line_width(w)
        ctx.move_to(x, y)
        ctx.line_to(lerp(x, x2, p), lerp(y, y2, p))
        ctx.stroke()
    # macro droplet climbing into the root tip
    da = seg(lt, 1.6, 1.9) * (1 - seg(lt, 2.6, 2.9))
    if da > 0:
        for kk in range(3):
            u = ((lt - 1.6) * 0.7 + kk / 3) % 1.0
            x, y = lerp(tipx, DEEP_TIP[0], u * 0.9), lerp(1480, DEEP_TIP[1], u * 0.9)
            ctx.set_source_rgba(*col("water2", da * math.sin(math.pi * u)))
            ctx.arc(x, y, 9, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgba(1, 1, 1, 0.8 * da * math.sin(math.pi * u))
            ctx.arc(x - 3, y - 3, 3, 0, 2 * math.pi)
            ctx.fill()
    sway = storm * 0.05 * math.sin(lt * 4.2)
    R.tree(ctx, 540, 704, 1, 1, sway, 1, 0, 300)
    if storm > 0:
        ctx.set_source_rgba(*hexc("#5E544A", 0.9 * storm))
        for x, y, rr in [(220, 20, 110), (390, -10, 140), (580, 0, 130), (770, 20, 110), (480, 60, 110),
                         (300, 70, 90), (680, 70, 90), (900, 40, 90), (100, 50, 80)]:
            ctx.arc(x + 30 * math.sin(lt), y, rr, 0, 2 * math.pi)
            ctx.fill()
        ctx.set_source_rgba(*hexc("#7A8C95", 0.8 * storm))
        ctx.set_line_width(5)
        rr_ = random.Random(int(lt * 15))
        for _ in range(90):
            x = rr_.uniform(-100, 1180)
            y = rr_.uniform(140, 690)
            ctx.move_to(x, y)
            ctx.line_to(x - 24, y + 64)
        ctx.stroke()
        bolt = seg(lt + 39.4, 42.9, 43.15)
        if 0 < bolt < 1:
            ctx.set_source_rgba(1, 1, 0.9, 1 - bolt)
            ctx.set_line_width(8)
            pts = [(820, 80), (780, 200), (830, 240), (760, 380), (800, 410), (740, 560)]
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.stroke()
    ctx.restore()
    grade(ctx, desat=0.35 * storm, cool=0.25 * storm)
    kword(ctx, "ROOTS", lt + 39.4, T_ROOTS2 - 0.05, 540, 1300, 170, "#E3B04B", 1.0)


# ---------------------------------------------------------------- scene 7: next step, end card, loop
def scene7(ctx, lt):
    R.bg(ctx, col("cream"))
    end = ease(seg(lt + 44.4, T_ROOTED + 0.3, T_ROOTED + 0.7))
    body = 1 - end
    rays(ctx, 540, 600, 0, 2 * math.pi, 14, 900, 0.35, lt * 0.4)
    if body > 0:
        ctx.push_group()
        pop = back_out(seg(lt, 0.0, 0.35), 1.4)
        ctx.save()
        ctx.translate(540, 600)
        ctx.scale(max(0.01, 1.25 - 0.25 * pop), max(0.01, 1.25 - 0.25 * pop))
        ctx.rotate(-0.04 * (1 - clamp(pop)))
        ctx.set_source_rgba(0, 0, 0, 0.1)
        rounded(ctx, -290, -316, 600, 660, 26)
        ctx.fill()
        ctx.set_source_rgba(*col("cream2"))
        rounded(ctx, -300, -330, 600, 660, 26)
        ctx.fill()
        ctx.set_source_rgba(*col("gold"))
        ctx.set_line_width(5)
        rounded(ctx, -300, -330, 600, 660, 26)
        ctx.stroke()
        ctx.restore()
        draw_text(ctx, "Psalm 1:2", F_SERIF, 76, "#3B2A1E", 540, 360, clamp(pop))
        ctx.set_source_rgba(*col("gold", clamp(pop)))
        ctx.rectangle(470, 418, 140, 4)
        ctx.fill()
        for i, line in enumerate(["Their joy is", "God's word.", "They chew on it", "day and night."]):
            a = ease(seg(lt, 0.35 + i * 0.18, 0.7 + i * 0.18))
            draw_text(ctx, line, F_SERIF_I, 58, "#6E5039", 540, 510 + i * 84 + 20 * (1 - a), a)
        ctx.set_source_rgba(*col("sand"))
        rounded(ctx, 240, 1060, 600, 120, 30)
        ctx.fill()
        sg = back_out(seg(lt, 1.0, 2.0), 1.2)
        rg = eout(seg(lt, 1.7, 3.0))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(*col("leaf"))
        ctx.set_line_width(10)
        ctx.move_to(540, 1064)
        ctx.curve_to(540, 1064 - 50 * sg, 548, 1064 - 90 * sg, 540, 1064 - 120 * sg)
        ctx.stroke()
        if sg > 0.5:
            la = back_out(seg(sg, 0.5, 1.0))
            for sx in (-1, 1):
                ctx.save()
                ctx.translate(540, 1064 - 110 * sg)
                ctx.rotate(sx * 0.6)
                ctx.scale(max(0.01, la), max(0.01, la))
                ctx.save()
                ctx.scale(1.6, 0.7)
                ctx.arc(sx * 22, 0, 22, 0, 2 * math.pi)
                ctx.restore()
                ctx.fill()
                ctx.restore()
        if rg > 0:
            ctx.set_source_rgba(*col("brown2"))
            ctx.set_line_width(6)
            if polyline(ctx, bez_pts([(540, 1066), (536, 1100), (548, 1130), (532, 1170)], 20), rg):
                ctx.stroke()
            ctx.set_line_width(4)
            if polyline(ctx, bez_pts([(540, 1100), (520, 1112), (505, 1130), (494, 1150)], 12), seg(rg, 0.5, 1)):
                ctx.stroke()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(body)
    if end > 0:
        u = lt + 44.4 - (T_ROOTED + 0.3)
        sc = 0.92 + 0.08 * back_out(seg(u, 0, 0.4))
        draw_text(ctx, "PSALM 1", F_SERIF, 50, "#6E5039", 540, 700, end)
        ctx.set_source_rgba(*col("gold", end))
        ctx.rectangle(490, 750, 100, 4)
        ctx.fill()
        draw_text(ctx, "Be rooted in", F_SERIF, 100, "#3B2A1E", 540, 850, end, sc)
        draw_text(ctx, "God's word.", F_SERIF, 100, "#3B2A1E", 540, 975, end, sc)
        # roots growing down out of the words
        rr = eout(seg(u, 0.2, 1.4))
        if rr > 0:
            ctx.set_source_rgba(*col("brown2", end))
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            for i, x in enumerate([330, 430, 540, 650, 750]):
                pts = bez_pts([(x, 1030), (x + 10 * (i - 2), 1080), (x - 30 * (i - 2), 1140), (540 + (x - 540) * 0.4, 1220)], 24)
                ctx.set_line_width(7 - abs(i - 2))
                if polyline(ctx, pts, seg(rr, i * 0.05, 1)):
                    ctx.stroke()
    # seamless loop: fade into the very first frame
    lp = ease(seg(lt, 5.05, 5.6))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


SCENES = [
    (0.0, 4.2, scene1),
    (4.2, 13.2, scene2),
    (13.2, 19.2, scene3),
    (19.2, 33.6, scene4),
    (33.6, 39.4, scene5),
    (39.4, 44.4, scene6),
    (44.4, 50.0, scene7),
]
XF = 0.12


def content(ctx, t):
    active = [(a, b, f) for a, b, f in SCENES if a - XF <= t < b + XF]
    for i, (a, b, f) in enumerate(active):
        alpha = 1.0 if i == 0 else ease(seg(t, a - XF, a + XF))
        ctx.save()
        if alpha < 1:
            ctx.push_group()
            f(ctx, t - a)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(alpha)
        else:
            f(ctx, t - a)
        ctx.restore()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    R.bg(ctx, col("dark"))
    dx, dy, rot = shake_amt(t)
    z = zoom_amt(t)
    ctx.save()
    ctx.translate(ZC[0] + dx, ZC[1] + dy)
    ctx.rotate(rot)
    ctx.scale(z, z)
    ctx.translate(-ZC[0], -ZC[1])
    blur = any(a <= t < b for a, b in BLUR)
    if blur:
        for k, ts in enumerate([t - 2 / 90, t - 1 / 90, t]):
            ctx.push_group()
            content(ctx, ts)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(1 / (k + 1))
    else:
        content(ctx, t)
    ctx.restore()
    for t0, c, a, d in FLASHES:
        u = t - t0
        if 0 <= u < d:
            ctx.set_source_rgba(*c, a * (1 - u / d) ** 2)
            ctx.paint()
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_surface(R.PAPER, 0, 0)
    ctx.paint_with_alpha(0.5)
    ctx.restore()
    R.vignette(ctx)
    if t < 48.2 and os.environ.get("CAPTIONS", "1") == "1":
        R.draw_captions(ctx, t)
    surf.flush()
    return surf


def video(path, n0, n1):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n0, n1):
        p.stdin.write(bytes(render_frame(i / FPS).get_data()))
        if i % 150 == 0:
            print(f"frame {i}", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        os.makedirs("/home/claude/psalm1/stills2", exist_ok=True)
        for t in map(float, sys.argv[2:]):
            render_frame(t).write_to_png(f"/home/claude/psalm1/stills2/t{t:05.2f}.png")
    elif sys.argv[1] == "times":
        for k in ["T_STEADY", "T_CRACKED", "T_STREAM", "T_GREEN", "T_HAGAH", "T_LION", "T_CHEW",
                  "T_DEVOTED", "T_HUNGRY", "T_CHAFF", "T_ROOTS2", "T_ROOTED"]:
            print(k, round(globals()[k], 2))
    else:
        video(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
