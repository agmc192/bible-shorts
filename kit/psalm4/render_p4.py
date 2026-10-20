"""Psalm 4 Short, timed to the ElevenLabs voiceover (vomap.json). Reuses the Psalm 1-3 libraries."""
import sys, os, math, random, json, re, subprocess
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm2")
sys.path.insert(0, "/home/claude/psalm3")
import cairo
import render as R
import render_v2 as V
import render_p2 as P
import render_p3 as Q
from render import (W, H, FPS, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, draw_surf,
                    text_surf, rounded, cam, F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword

MAP = json.load(open("/home/claude/psalm4/vomap.json"))
DUR = MAP["video_dur"]
_clean = lambda w: re.sub(r"[^A-Za-z0-9]", "", w).lower()


def wt(word, n=1):
    k = 0
    for a, b, w in MAP["words"]:
        if _clean(w) == word:
            k += 1
            if k == n:
                return a
    raise KeyError(word)


T_REPLAYED = wt("replayed"); T_ARGUMENT = wt("argument"); T_HOURS = wt("hours")
T_DAVID = wt("david", 1); T_PSALM = wt("psalm"); T_HONOR = wt("honor"); T_SHAME = wt("shame")
T_CHASING = wt("chasing"); T_LIES = wt("lies"); T_WRITES = wt("writes")
T_ANGRY1 = wt("angry", 1); T_SIN1 = wt("sin", 1); T_BED = wt("bed"); T_HEART = wt("heart"); T_STILL = wt("still")
T_KEY = wt("key"); T_HEBREW = wt("hebrew"); T_RIGZU = wt("rigzu"); T_TREMBLE = wt("tremble"); T_SHAKE = wt("shake")
T_PAUL = wt("paul"); T_LINE = wt("line"); T_ADDS = wt("adds"); T_SUN1 = wt("sun", 1); T_ANGER1 = wt("anger", 1)
T_FEELING2 = wt("feeling", 2); T_SIN2 = wt("sin", 2); T_FEEDING = wt("feeding")
T_TRUST = wt("trust"); T_FILLS = wt("fills"); T_JOY = wt("joy"); T_HARVEST = wt("harvest"); T_PEACE = wt("peace")
T_LIE = wt("lie"); T_SLEEP = wt("sleep")
T_SUN2 = wt("sun", 2); T_TODAY = wt("today"); T_HAND = wt("hand"); T_GOD = wt("god", 2); T_FEEL = wt("feel")
T_FEED = wt("feed")

B1 = 0.0
B2 = 3.55          # David
B3 = 12.05         # "Be angry..."
B4 = 18.35         # nugget
B5 = 25.6          # Paul + sunset
B6 = 32.15         # feel vs feed
B7 = 35.9          # trust, joy, peace
B8 = 45.75         # close

ZOOMS = [(0.1, 0.10), (T_HOURS, 0.06), (T_SHAME, 0.08), (T_ANGRY1, 0.10), (T_STILL, 0.04), (T_RIGZU, 0.12),
         (T_SHAKE, 0.08), (T_LINE, 0.06), (T_FEEDING, 0.10), (T_JOY, 0.08), (T_PEACE, 0.05), (T_FEED, 0.08)]
SHAKES = [(0.1, 14, 0.6), (1.0, 4, 2.2), (T_SHAME, 7, 0.4), (T_ANGRY1, 12, 1.2), (T_RIGZU, 10, 0.5),
          (T_TREMBLE, 6, 0.9), (T_SHAKE, 14, 0.8), (T_FEEDING, 9, 0.6), (T_FEED, 6, 0.4)]
FLASHES = [(0.1, (1, 1, 1), 0.35, 0.3), (T_SHAME, (0.6, 0.6, 0.6), 0.25, 0.3), (T_STILL, (1, 1, 1), 0.2, 0.5),
           (T_RIGZU, (1, 0.85, 0.5), 0.3, 0.4), (T_JOY, (1, 0.9, 0.6), 0.35, 0.4), (T_FEED, (1, 0.95, 0.85), 0.3, 0.35)]
BLUR = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6, B7, B8)]
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


# ---------------------------------------------------------------- helpers
def heart_path(ctx, cx, cy, s):
    ctx.move_to(cx, cy + 0.9 * s)
    ctx.curve_to(cx - 1.4 * s, cy - 0.1 * s, cx - 0.8 * s, cy - 1.1 * s, cx, cy - 0.45 * s)
    ctx.curve_to(cx + 0.8 * s, cy - 1.1 * s, cx + 1.4 * s, cy - 0.1 * s, cx, cy + 0.9 * s)
    ctx.close_path()


def bubble(ctx, cx, cy, w, h, c, alpha, tail=1):
    ctx.set_source_rgba(*c[:3], alpha)
    rounded(ctx, cx - w / 2, cy - h / 2, w, h, h / 2)
    ctx.fill()
    ctx.move_to(cx + tail * w * 0.2, cy + h / 2 - 4)
    ctx.line_to(cx + tail * w * 0.35, cy + h / 2 + 30)
    ctx.line_to(cx + tail * w * 0.05, cy + h / 2 - 4)
    ctx.close_path()
    ctx.fill()


def scribble(ctx, cx, cy, w, seed, alpha, c="cream2"):
    r = random.Random(seed)
    ctx.set_source_rgba(*col(c, alpha))
    ctx.set_line_width(6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    x = cx - w / 2
    ctx.move_to(x, cy)
    while x < cx + w / 2:
        x += r.uniform(10, 22)
        ctx.line_to(x, cy + r.uniform(-14, 14))
    ctx.stroke()


def head_profile(ctx, cx, cy, s, c):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c)
    ctx.move_to(-120, 260)
    ctx.curve_to(-140, 160, -210, 60, -200, -60)
    ctx.curve_to(-190, -220, -40, -280, 60, -230)
    ctx.curve_to(150, -190, 180, -110, 170, -40)
    ctx.line_to(205, 30)
    ctx.line_to(170, 45)
    ctx.curve_to(175, 80, 165, 110, 140, 120)
    ctx.curve_to(150, 150, 120, 170, 90, 170)
    ctx.curve_to(80, 210, 60, 240, 60, 260)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def clock(ctx, cx, cy, r, t, speed, alpha=1.0):
    ctx.save()
    ctx.set_source_rgba(*col("cream2", alpha))
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*col("brown", alpha))
    ctx.set_line_width(8)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.stroke()
    for k in range(12):
        a = k * math.pi / 6
        ctx.move_to(cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82)
        ctx.line_to(cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for ln, w, sp in [(0.5, 10, 1), (0.75, 6, 12)]:
        a = -math.pi / 2 + t * speed * sp
        ctx.set_line_width(w)
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a) * r * ln, cy + math.sin(a) * r * ln)
        ctx.stroke()
    ctx.restore()


def kettle(ctx, cx, cy, s, boil, t, calm=0.0):
    sh = boil * (1 - calm)
    jx = sh * 10 * math.sin(t * 47)
    jy = sh * 6 * math.sin(t * 61)
    ctx.save()
    ctx.translate(cx + jx, cy + jy)
    ctx.scale(s, s)
    # stove + flame
    ctx.set_source_rgba(*col("brown"))
    rounded(ctx, -260, 170, 520, 40, 12)
    ctx.fill()
    fl = lerp(1.0, 0.25, calm)
    for i in range(7):
        x = -150 + i * 50
        hgt = fl * (40 + 50 * boil) * (0.7 + 0.3 * math.sin(t * 14 + i))
        ctx.set_source_rgba(*lerpc(hexc("#4C7DB8"), col("rust"), boil * (1 - calm)))
        ctx.move_to(x - 14, 170)
        ctx.curve_to(x - 16, 170 - hgt * 0.5, x - 4, 170 - hgt * 0.8, x, 170 - hgt)
        ctx.curve_to(x + 4, 170 - hgt * 0.8, x + 16, 170 - hgt * 0.5, x + 14, 170)
        ctx.close_path()
        ctx.fill()
    # body
    ctx.set_source_rgba(*lerpc(col("teal"), col("rust"), 0.8 * sh))
    ctx.move_to(-170, 150)
    ctx.curve_to(-200, 40, -150, -110, 0, -120)
    ctx.curve_to(150, -110, 200, 40, 170, 150)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(150, 0)
    ctx.curve_to(230, -20, 260, -90, 300, -130)
    ctx.line_to(320, -110)
    ctx.curve_to(280, -60, 260, 30, 160, 70)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*col("brown"))
    ctx.set_line_width(22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-120, -110)
    ctx.curve_to(-120, -230, 120, -230, 120, -110)
    ctx.stroke()
    lid_jump = sh * 14 * max(0, math.sin(t * 23))
    ctx.set_source_rgba(*col("brown2"))
    rounded(ctx, -70, -140 - lid_jump, 140, 26, 12)
    ctx.fill()
    ctx.arc(0, -150 - lid_jump, 16, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    # steam from the spout
    for k in range(8):
        u = (t * (0.8 + 1.6 * sh) + k / 8) % 1.0
        a = (0.15 + 0.6 * sh) * math.sin(math.pi * u) * (1 - 0.8 * calm)
        if a <= 0.01:
            continue
        x = cx + (310 + 60 * u + 20 * math.sin(u * 8 + k)) * s
        y = cy - (130 + 360 * u) * s
        ctx.set_source_rgba(*lerpc(col("cream2"), hexc("#E8B4A0"), sh)[:3], a)
        ctx.arc(x, y, (20 + 50 * u) * s, 0, 2 * math.pi)
        ctx.fill()


def fire(ctx, cx, base, size, t, alpha=1.0):
    if alpha <= 0.01:
        return
    g = cairo.RadialGradient(cx, base - size * 0.5, 10, cx, base - size * 0.5, size * 1.4)
    g.add_color_stop_rgba(0, 1, 0.6, 0.25, 0.5 * alpha)
    g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
    ctx.set_source(g)
    ctx.arc(cx, base - size * 0.5, size * 1.4, 0, 2 * math.pi)
    ctx.fill()
    for layer, (c, k) in enumerate([("rust", 1.0), ("gold", 0.72), ("gold2", 0.45)]):
        ctx.set_source_rgba(*col(c, alpha))
        n = 5
        ctx.move_to(cx - size * 0.5 * k, base)
        for i in range(n + 1):
            x = cx - size * 0.5 * k + i * size * k / n
            hgt = size * k * (0.6 + 0.4 * math.sin(t * 9 + i * 1.7 + layer)) * (1 - abs(i - n / 2) / (n / 2) * 0.5)
            ctx.line_to(x - size * 0.05, base - hgt * 0.6)
            ctx.line_to(x, base - hgt)
        ctx.line_to(cx + size * 0.5 * k, base)
        ctx.close_path()
        ctx.fill()


def wheat_field(ctx, t, y0, alpha=1.0, seed=3):
    r = random.Random(seed)
    for i in range(46):
        x = r.uniform(-20, W + 20)
        h = r.uniform(180, 300)
        sway = 0.06 * math.sin(t * 1.6 + x * 0.01)
        tx, ty = x + math.sin(sway) * h, y0 - math.cos(sway) * h
        ctx.set_source_rgba(*col("dry", alpha))
        ctx.set_line_width(5)
        ctx.move_to(x, y0)
        ctx.line_to(tx, ty)
        ctx.stroke()
        ctx.set_source_rgba(*col("gold", alpha))
        for j in range(5):
            ctx.save()
            ctx.translate(tx, ty - j * 13)
            ctx.rotate(sway)
            ctx.scale(0.55, 1)
            ctx.arc(0, 0, 12, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()


def jar(ctx, cx, base, s, alpha=1.0):
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("rust", alpha))
    ctx.move_to(-30, -200)
    ctx.line_to(30, -200)
    ctx.curve_to(30, -170, 90, -150, 90, -90)
    ctx.curve_to(90, -30, 30, 0, 0, 0)
    ctx.curve_to(-30, 0, -90, -30, -90, -90)
    ctx.curve_to(-90, -150, -30, -170, -30, -200)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*col("brown2", alpha))
    ctx.rectangle(-40, -212, 80, 18)
    ctx.fill()
    ctx.restore()


def sunset_sky(ctx, t, sun_y, k=1.0):
    g = cairo.LinearGradient(0, 0, 0, 1250)
    g.add_color_stop_rgba(0, *lerpc(hexc("#F3D9B0"), hexc("#5E4A6B"), 1 - k))
    g.add_color_stop_rgba(0.6, *lerpc(hexc("#F2A66A"), hexc("#B8604A"), 1 - k))
    g.add_color_stop_rgba(1, *hexc("#E07A4E"))
    ctx.set_source(g)
    ctx.paint()
    sg = cairo.RadialGradient(540, sun_y, 40, 540, sun_y, 500)
    sg.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.9)
    sg.add_color_stop_rgba(1, 1, 0.7, 0.4, 0)
    ctx.set_source(sg)
    ctx.arc(540, sun_y, 500, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*col("gold2"))
    ctx.arc(540, sun_y, 110, 0, 2 * math.pi)
    ctx.fill()


def horizon(ctx, y=1180, c="#7A4A35"):
    V.hills(ctx, y - 160, 60, hexc("#B8604A"), 0, 41)
    V.hills(ctx, y - 90, 45, hexc("#8F4E3A"), 0, 42, 1.3)
    ctx.set_source_rgba(*hexc(c))
    ctx.rectangle(0, y, W, H)
    ctx.fill()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    t = lt
    R.bg(ctx, col("cream"))
    rays(ctx, 540, 760, 0, 2 * math.pi, 12, 900, 0.3, t * 0.4)
    ctx.save()
    cam(ctx, 540, 860, 1.0 + 0.08 * ease(lt / 3.4))
    clock(ctx, 800, 520, 150, t, 2.4 + 6 * seg(t, T_HOURS - 0.6, T_HOURS + 0.2), 0.95)
    head_profile(ctx, 470, 960, 1.35, col("brown"))
    # thoughts on repeat inside the head
    for i in range(2):
        ph = (t * 1.6 + i * 0.5) % 1.0
        pop = clamp(back_out(seg(t, 0.08 + i * 0.12, 0.35 + i * 0.12)))
        a = pop * (0.6 + 0.4 * math.sin(math.pi * ph))
        cx = 470 + (-70 if i == 0 else 70)
        cy = 760 - 30 * math.sin(2 * math.pi * ph + i * math.pi)
        bubble(ctx, cx, cy, 190, 96, col("rust" if i == 0 else "gold"), a, -1 if i == 0 else 1)
        scribble(ctx, cx, cy, 120, 10 + i + int(t * 3), a)
    # replay loop
    ctx.set_source_rgba(*col("cream2", 0.95))
    ctx.set_line_width(12)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    a0 = t * 4
    ctx.arc(470, 760, 210, a0, a0 + 4.6)
    ctx.stroke()
    ex, ey = 470 + math.cos(a0 + 4.6) * 210, 760 + math.sin(a0 + 4.6) * 210
    ang = a0 + 4.6 + math.pi / 2
    ctx.move_to(ex + math.cos(ang) * 30, ey + math.sin(ang) * 30)
    ctx.line_to(ex + math.cos(ang - 2.4) * 30, ey + math.sin(ang - 2.4) * 30)
    ctx.line_to(ex + math.cos(ang + 2.4) * 30, ey + math.sin(ang + 2.4) * 30)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    kword(ctx, "ON REPEAT", t, T_ARGUMENT - 0.05, 540, 230, 140, "#E3B04B", B2 - T_ARGUMENT)


def scene2(ctx, lt):
    t = lt + B2
    ctx.save()
    sl = 1300 * (1 - eout(seg(lt, -0.1, 0.3)))
    ctx.translate(sl, 0)
    R.bg(ctx, col("cream"))
    sh = ease(seg(t, T_SHAME - 0.3, T_SHAME + 0.3))
    rays(ctx, 540, 640, 0, 2 * math.pi, 12, 900, 0.4 * (1 - sh), t * 0.4)
    draw_text(ctx, "PSALM 4", F_SERIF, 118, "#3B2A1E", 540, 250, ease(seg(t, T_PSALM - 0.2, T_PSALM + 0.2)),
              0.94 + 0.06 * back_out(seg(t, T_PSALM - 0.2, T_PSALM + 0.15)))
    draw_text(ctx, "A psalm of David", F_SERIF_I, 56, "#6E5039", 540, 350, ease(seg(t, T_PSALM, T_PSALM + 0.4)))
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(0, 1180, W, H)
    ctx.fill()
    # David at centre, his honor (a golden wreath) turning to grey and cracking
    Q.person(ctx, 540, 1180, 1.35, col("brown"), 0.6 * sh, 0, 1.0, 0.0)
    wc = lerpc(col("gold2"), hexc("#8A8580"), sh)
    ctx.save()
    ctx.translate(540, 1180 - 1.35 * 178 - 30)
    ctx.set_line_width(10)
    ctx.set_source_rgba(*wc)
    for sx in (-1, 1):
        for k in range(6):
            a = math.radians(200 + k * 22) if sx < 0 else math.radians(-20 - k * 22)
            x, y = math.cos(a) * 120, math.sin(a) * 120 * 0.7 + 260
            ctx.save()
            ctx.translate(x, y - 260 + 40)
            ctx.rotate(a + (math.pi / 2 if sx < 0 else -math.pi / 2))
            ctx.scale(1, 0.45)
            ctx.arc(0, 0, 22, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
    if sh > 0.3:
        ctx.set_source_rgba(*col("dark", sh))
        ctx.set_line_width(4)
        ctx.move_to(-60, -10)
        ctx.line_to(-20, 20)
        ctx.line_to(10, -5)
        ctx.line_to(50, 25)
        ctx.stroke()
    ctx.restore()
    # "David knew the feeling": the same replay loop above his head
    kf = ease(seg(lt, 0.1, 0.5)) * (1 - ease(seg(t, T_PSALM - 0.3, T_PSALM + 0.2)))
    if kf > 0:
        hy = 1180 - 1.35 * 178 - 200
        for i in range(2):
            ph = (t * 1.6 + i * 0.5) % 1.0
            bubble(ctx, 540 + (-80 if i == 0 else 80), hy - 30 * math.sin(2 * math.pi * ph + i * math.pi), 170, 86,
                   col("rust" if i == 0 else "gold"), kf * (0.6 + 0.4 * math.sin(math.pi * ph)), -1 if i == 0 else 1)
        ctx.set_source_rgba(*col("brown2", kf))
        ctx.set_line_width(10)
        a0 = t * 4
        ctx.arc(540, hy, 190, a0, a0 + 4.6)
        ctx.stroke()
    draw_text(ctx, "honor", F_SERIF_I, 64, "#A8741A", 300, 680, ease(seg(t, T_HONOR - 0.1, T_HONOR + 0.3)) * (1 - sh))
    draw_text(ctx, "shame", F_SERIF_I, 64, "#6E6A66", 780, 680, sh * (1 - ease(seg(t, T_WRITES - 0.5, T_WRITES - 0.1))))
    # whisperers chasing lies
    ch = ease(seg(t, T_CHASING - 0.3, T_CHASING + 0.2)) * (1 - ease(seg(t, T_WRITES - 0.5, T_WRITES - 0.1)))
    if ch > 0:
        for i, side in enumerate((-1, 1, -1, 1)):
            run = seg(t, T_CHASING - 0.2 + i * 0.1, B3)
            x = 540 + side * lerp(260, 420, run) + side * i * 30
            Q.person(ctx, x, 1180 - 6 * abs(math.sin(t * 9 + i)), 0.75, col("dark"), 0, 0, 0, 0.9, alpha=ch)
            for k in range(2):
                bx = x + side * (90 + 40 * k) + 20 * math.sin(t * 3 + i + k)
                by = 980 - 80 * k - 40 * run
                bubble(ctx, bx, by, 120, 60, hexc("#3E3A40"), ch * 0.9, side)
                draw_text(ctx, "lie", F_SERIF_I, 34, "#FBF6EC", bx, by, ch)
    # "So he writes:" quill
    wr = ease(seg(t, T_WRITES - 0.3, T_WRITES))
    if wr > 0:
        ctx.save()
        qx = 840 + 30 * math.sin(t * 9)
        ctx.translate(qx, 860)
        ctx.rotate(-0.6)
        ctx.set_source_rgba(*col("cream2", wr))
        ctx.move_to(0, 0)
        ctx.curve_to(40, -80, 30, -180, 0, -230)
        ctx.curve_to(-30, -180, -40, -80, 0, 0)
        ctx.fill()
        ctx.set_source_rgba(*col("brown", wr))
        ctx.set_line_width(4)
        ctx.move_to(0, 0)
        ctx.line_to(0, -230)
        ctx.stroke()
        ctx.restore()
    ctx.restore()
    grade(ctx, desat=0.4 * sh)


def scene3(ctx, lt):
    t = lt + B3
    R.bg(ctx, col("cream"))
    calm = ease(seg(t, T_STILL - 0.2, T_STILL + 0.6))
    boil = ease(seg(t, T_ANGRY1 - 0.4, T_ANGRY1 + 0.1))
    rays(ctx, 540, 900, 0, 2 * math.pi, 14, 900, 0.5 * calm, t * 0.3)
    # verse card
    vc = ease(seg(lt, 0.0, 0.3))
    P.verse_card(ctx, 540, 390, 900, 440, vc)
    P.tag(ctx, "Psalm 4:4", 540, 170, seg(lt, 0.1, 0.4), vc, 260)
    l1 = ease(seg(t, T_ANGRY1 - 0.2, T_ANGRY1 + 0.2))
    draw_text(ctx, "“Be angry,", F_SERIF_I, 70, "#A9472F", 540, 260, l1)
    draw_text(ctx, "and do not sin.", F_SERIF_I, 62, "#3B2A1E", 540, 345, ease(seg(t, T_SIN1 - 0.4, T_SIN1)))
    draw_text(ctx, "On your bed, search your heart,", F_SERIF_I, 52, "#6E5039", 540, 430, ease(seg(t, T_BED - 0.3, T_BED + 0.1)))
    draw_text(ctx, "and be still.”", F_SERIF_I, 64, "#A8741A", 540, 515, ease(seg(t, T_STILL - 0.3, T_STILL + 0.1)))
    # the kettle: boils on anger, holds its lid on "do not sin", stills at the end
    kettle(ctx, 500, 1060, 1.15, boil, t, calm)
    hold = ease(seg(t, T_SIN1 - 0.3, T_SIN1 + 0.2)) * (1 - calm)
    if hold > 0:
        ctx.set_source_rgba(*col("gold2", 0.9 * hold))
        ctx.set_line_width(8)
        ctx.arc(500, 1060 - 170, 120, math.pi * 1.1, math.pi * 1.9)
        ctx.stroke()
    # search your heart: a heart with a lantern glow
    hs = ease(seg(t, T_HEART - 0.3, T_HEART + 0.2))
    if hs > 0:
        ctx.save()
        heart_path(ctx, 880, 820, 70)
        ctx.set_source_rgba(*col("rust", hs))
        ctx.fill()
        ctx.restore()
        g = cairo.RadialGradient(880, 800, 5, 880, 800, 160)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.7 * hs)
        g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.set_source(g)
        ctx.arc(880, 800, 160, 0, 2 * math.pi)
        ctx.fill()
    if calm > 0:
        for k in range(3):
            u = (t - T_STILL) * 0.8 - k * 0.25
            if 0 <= u < 1:
                ctx.set_source_rgba(*col("teal", 0.5 * (1 - u)))
                ctx.set_line_width(5)
                ctx.save()
                ctx.translate(500, 1270)
                ctx.scale(1, 0.25)
                ctx.arc(0, 0, 120 + 420 * u, 0, 2 * math.pi)
                ctx.restore()
                ctx.stroke()
    grade(ctx, warm=0.25 * boil * (1 - calm))


def scene4(ctx, lt):
    t = lt + B4
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.7, "gold2", 6, -12)
    hb = ease(seg(t, T_RIGZU - 0.6, T_RIGZU - 0.3))
    reveal = ease(seg(t, T_RIGZU - 0.55, T_RIGZU + 0.05))
    trem = 4 * ease(seg(t, T_TREMBLE - 0.1, T_TREMBLE + 0.3)) + 16 * ease(seg(t, T_SHAKE - 0.1, T_SHAKE + 0.2))
    trem *= 1 - ease(seg(t, B5 - 0.5, B5))
    jx, jy = trem * math.sin(t * 53), trem * math.sin(t * 71)
    rays(ctx, 540, 640, 0, 2 * math.pi, 18, 1100, hb * (0.4 + 0.6 * seg(t, T_RIGZU, T_RIGZU + 0.3)), t * 0.4)
    draw_text(ctx, "“be angry”", F_SERIF_I, 80, "#DCC59D", 540, 360, ease(seg(t, T_KEY + 0.1, T_KEY + 0.5)) * (1 - 0.4 * hb))
    P.burn_word(ctx, "רִגְזוּ", F_HEB, 320, 540 + jx, 640 + jy, reveal, hb, rtl=True)
    sub = ease(seg(t, T_RIGZU + 0.1, T_RIGZU + 0.5))
    draw_text(ctx, "rigzu", F_SERIF_I, 96, "#FBF6EC", 540, 880, sub, 0.9 + 0.1 * back_out(seg(t, T_RIGZU + 0.1, T_RIGZU + 0.45)))
    tr = ease(seg(t, T_TREMBLE - 0.1, T_TREMBLE + 0.25))
    draw_text(ctx, "to tremble", F_SERIF_R, 64, "#DCC59D", 540 + jx * 0.4, 1000, tr)
    kword(ctx, "SHAKE", t, T_SHAKE - 0.03, 540 + jx * 0.5, 1150 + jy * 0.5, 170, "#E3B04B", B5 - T_SHAKE)


def scene5(ctx, lt):
    t = lt + B5
    sunset = ease(seg(t, T_SUN1 - 0.6, T_SUN1 - 0.1))
    if sunset < 1:
        ctx.push_group()
        R.bg(ctx, col("cream"))
        rays(ctx, 540, 640, 0, 2 * math.pi, 14, 900, 0.4, t * 0.4)
        for i, (cx, label, line2) in enumerate([(290, "Psalm 4:4", "David"), (790, "Ephesians 4:26", "Paul")]):
            u = back_out(seg(t, B5 + 0.1 + i * 0.5 + (T_PAUL - B5 - 0.4 if i else 0), B5 + 0.45 + i * 0.5 + (T_PAUL - B5 - 0.4 if i else 0)), 1.3)
            if u <= 0.01:
                continue
            P.verse_card(ctx, cx, 760, 440, 480, 1.0, max(0.01, u))
            draw_text(ctx, label, F_SERIF, 50 if i == 0 else 44, "#3B2A1E", cx, 580, clamp(u))
            draw_text(ctx, line2, F_SERIF_I, 44, "#6E5039", cx, 640, clamp(u))
            hl = ease(seg(t, T_LINE - 0.3, T_LINE + 0.1))
            draw_text(ctx, "Be angry", F_SERIF_I, 56, "#A9472F" if hl > 0.5 else "#6E5039", cx, 760, clamp(u))
            draw_text(ctx, "and do not sin", F_SERIF_I, 56, "#A9472F" if hl > 0.5 else "#6E5039", cx, 830, clamp(u))
        br = eout(seg(t, T_LINE - 0.2, T_LINE + 0.3))
        if br > 0:
            ctx.set_source_rgba(*col("gold"))
            ctx.set_line_width(7)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            pts = R.bez_pts([(290, 500), (380, 400), (700, 400), (790, 500)], 40)
            R.polyline(ctx, pts, br)
            ctx.stroke()
            draw_text(ctx, "same line", F_SERIF_I, 46, "#A8741A", 540, 380, br)
        ad = ease(seg(t, T_ADDS - 0.2, T_ADDS + 0.2))
        draw_text(ctx, "+ his own words", F_SERIF_I, 52, "#3B2A1E", 790, 1080, ad)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - sunset)
    if sunset > 0:
        ctx.push_group()
        sy = lerp(560, 1080, ease(seg(t, T_SUN1 - 0.4, T_ANGER1 + 0.8)))
        sunset_sky(ctx, t, sy, 1 - ease(seg(t, T_SUN1, T_ANGER1 + 0.8)) * 0.6)
        horizon(ctx)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(sunset)
        draw_text(ctx, "“Don't let the sun go down", F_SERIF_I, 62, "#FBF6EC", 540, 300, sunset, stroke=3, stroke_color="#5E3424")
        draw_text(ctx, "on your anger.”", F_SERIF_I, 62, "#FBF6EC", 540, 385, ease(seg(t, T_ANGER1 - 0.5, T_ANGER1)), stroke=3, stroke_color="#5E3424")
        P.tag(ctx, "Ephesians 4:26", 540, 500, seg(t, T_ANGER1 - 0.2, T_ANGER1 + 0.2), sunset, 360)


def scene6(ctx, lt):
    t = lt + B6
    R.bg(ctx, col("cream"))
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(0, 1180, W, H)
    ctx.fill()
    # left: a feeling held (a small flame in open hands); right: a fire being fed
    fa = ease(seg(t, T_FEELING2 - 0.3, T_FEELING2 + 0.1))
    fd = ease(seg(t, T_FEEDING - 0.3, T_FEEDING + 0.1))
    ctx.set_source_rgba(*col("gold"))
    ctx.set_line_width(5)
    ctx.move_to(540, 420)
    ctx.line_to(540, 420 + 760 * eout(seg(lt, 0.0, 0.5)))
    ctx.stroke()
    Q.person(ctx, 270, 1180, 1.0, col("brown"), 0, 0, 0, 0.55, alpha=fa)
    fire(ctx, 270, 1180 - 150, 60, t, fa)
    draw_text(ctx, "feel it", F_SERIF_I, 70, "#466E2E", 270, 520, fa)
    draw_text(ctx, "✓", F_CAP_SAFE, 90, "#466E2E", 270, 640, fa)
    size = lerp(80, 330, ease(seg(t, T_FEEDING, T_FEEDING + 1.2)))
    fire(ctx, 820, 1180, size, t, fd)
    for i in range(2):
        u = ((t - T_FEEDING) * 1.2 + i * 0.5) % 1.0
        if t < T_FEEDING:
            continue
        lx = lerp(1000, 860, u)
        ly = lerp(1060, 1120, u)
        ctx.save()
        ctx.translate(lx, ly)
        ctx.rotate(-0.4)
        ctx.set_source_rgba(*col("brown2", fd * (1 - u)))
        rounded(ctx, -60, -14, 120, 28, 12)
        ctx.fill()
        ctx.restore()
    Q.person(ctx, 1010, 1180, 0.9, col("dark"), 0, 0, 0, 0.6, alpha=fd)
    draw_text(ctx, "feed it", F_SERIF_I, 70, "#A9472F", 810, 520, fd)
    draw_text(ctx, "✗", F_CAP_SAFE, 90, "#A9472F", 810, 640, fd)
    kword(ctx, "FEEDING", t, T_FEEDING - 0.03, 540, 300, 150, "#E3B04B", B7 - T_FEEDING)
    grade(ctx, warm=0.3 * fd, rect=(540, 0, 540, H))


F_CAP_SAFE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def scene7(ctx, lt):
    t = lt + B7
    night = ease(seg(t, T_PEACE - 0.4, T_PEACE + 0.4))
    R.bg(ctx, col("cream"))
    if night < 1:
        ctx.push_group()
        g = cairo.LinearGradient(0, 0, 0, 1200)
        g.add_color_stop_rgba(0, *col("cream2"))
        g.add_color_stop_rgba(1, *col("gold2")[:3], 0.5)
        ctx.set_source(g)
        ctx.paint()
        rays(ctx, 540, -60, math.radians(55), math.radians(125), 9, 1700, 0.8 * ease(seg(t, T_TRUST - 0.3, T_TRUST + 0.3)), t * 0.4)
        hv = ease(seg(t, T_FILLS - 0.2, T_HARVEST - 0.6))
        ctx.set_source_rgba(*col("sand"))
        ctx.rectangle(0, 1180, W, H)
        ctx.fill()
        if hv > 0:
            wheat_field(ctx, t, 1180, hv * (1 - 0.5 * ease(seg(t, T_HARVEST, T_HARVEST + 0.6))))
            for x in (130, 950):
                jar(ctx, x, 1300, 0.9, hv * (1 - 0.5 * ease(seg(t, T_HARVEST, T_HARVEST + 0.6))))
        kneel = ease(seg(t, T_TRUST - 0.3, T_TRUST + 0.2))
        Q.person(ctx, 540, 1300, 1.3, col("brown"), 0.2 * (1 - kneel), 0, 1.0, 0.7 * kneel, kneel)
        jo = ease(seg(t, T_JOY - 0.2, T_JOY + 0.3))
        if jo > 0:
            hy = 1300 - 1.3 * 70
            g2 = cairo.RadialGradient(540, hy, 10, 540, hy, 500 * jo)
            g2.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.95)
            g2.add_color_stop_rgba(0.4, *col("gold2")[:3], 0.55)
            g2.add_color_stop_rgba(1, *col("gold2")[:3], 0)
            ctx.set_source(g2)
            ctx.arc(540, hy, 500 * jo, 0, 2 * math.pi)
            ctx.fill()
            heart_path(ctx, 540, hy, 32 + 6 * math.sin(t * 6))
            ctx.set_source_rgba(*col("rust"))
            ctx.fill()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - night)
        kword(ctx, "TRUST", t, T_TRUST - 0.03, 540, 260, 160, "#E3B04B", T_JOY - T_TRUST - 0.4)
        kword(ctx, "JOY", t, T_JOY - 0.03, 540, 260, 190, "#E3B04B", T_PEACE - T_JOY - 0.5)
    if night > 0:
        ctx.push_group()
        Q.night_sky(ctx, t, 1, 1)
        Q.moon(ctx, 820, 300, 56)
        Q.hills_night(ctx, t, 0.0, 1.0)
        Q.dome(ctx, 540, 1240, 380, 470, 1.0, 0.6)
        down = ease(seg(t, T_LIE - 0.3, T_LIE + 0.5))
        ctx.save()
        ctx.translate(540, 1236)
        ctx.rotate(-math.pi / 2 * down)
        Q.person(ctx, 0, 0, 1.0, col("dark"), 0, 0, 1.0, 0.1)
        ctx.restore()
        if down > 0.6:
            for k in range(3):
                v = (t * 0.6 + k / 3) % 1.0
                draw_text(ctx, "z", F_SERIF_I, 40 + 20 * v, "#F4E9C8", 640 + 60 * v + k * 10, 1150 - 160 * v, math.sin(math.pi * v) * 0.9)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(night)
        kword(ctx, "PEACE", t, T_PEACE - 0.03, 540, 260, 170, "#E3B04B", B8 - T_PEACE)


def scene8(ctx, lt):
    t = lt + B8
    sy = lerp(700, 1110, ease(seg(t, B8, T_FEEL)))
    sunset_sky(ctx, t, sy, 1 - 0.5 * ease(seg(t, B8, DUR)))
    horizon(ctx)
    # hand the anger to God: an ember rises from open hands into the setting sun
    hand = ease(seg(t, T_HAND - 0.3, T_HAND + 0.2))
    Q.person(ctx, 540, 1180, 1.25, col("dark"), 0, 0, 0, 0.55 + 0.4 * hand)
    lift = ein(seg(t, T_HAND, T_GOD + 0.6))
    ex, ey = 540, lerp(1180 - 1.25 * 200, sy, lift)
    ea = (1 - seg(lift, 0.8, 1.0))
    if ea > 0:
        fire(ctx, ex, ey + 30, lerp(70, 40, lift), t, ea)
    end = ease(seg(t, T_FEEL - 0.4, T_FEEL))
    draw_text(ctx, "PSALM 4", F_SERIF, 50, "#FBF6EC", 540, 380, end, stroke=3, stroke_color="#5E3424")
    ctx.set_source_rgba(*col("cream2", end))
    ctx.rectangle(490, 430, 100, 4)
    ctx.fill()
    draw_text(ctx, "Feel it.", F_SERIF, 110, "#FBF6EC", 540, 540, end, 0.92 + 0.08 * back_out(seg(t, T_FEEL - 0.4, T_FEEL)), stroke=4, stroke_color="#5E3424")
    fd = ease(seg(t, T_FEED - 0.3, T_FEED + 0.1))
    draw_text(ctx, "Don't feed it.", F_SERIF, 110, "#FBF6EC", 540, 680, fd, 0.92 + 0.08 * back_out(seg(t, T_FEED - 0.3, T_FEED + 0.1)), stroke=4, stroke_color="#5E3424")
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


SCENES = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5),
          (B6, B7, scene6), (B7, B8, scene7), (B8, DUR + 1, scene8)]
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
    if any(a <= t < b for a, b in BLUR):
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
    surf.flush()
    return surf


def video(path, n0, n1):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n0, n1):
        p.stdin.write(bytes(render_frame(i / FPS).get_data()))
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        os.makedirs("/home/claude/psalm4/stills", exist_ok=True)
        for t in map(float, sys.argv[2:]):
            render_frame(t).write_to_png(f"/home/claude/psalm4/stills/t{t:05.2f}.png")
    elif sys.argv[1] == "times":
        for k, v in sorted(((k, v) for k, v in globals().items() if k.startswith("T_")), key=lambda x: x[1]):
            print(f"{k:12s} {v:6.2f}")
    else:
        video(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
