"""Psalm 3 Short, timed to the ElevenLabs voiceover (vomap.json). Reuses the Psalm 1 art library,
the Psalm 1 effects engine and the Psalm 2 helpers (crown, crowd, burn_word, tag, dark_bg...)."""
import sys, os, math, random, json, re, subprocess
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm2")
import cairo
import render as R
import render_v2 as V
import render_p2 as P
from render import (W, H, FPS, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, draw_surf,
                    text_surf, rounded, cam, F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword

MAP = json.load(open("/home/claude/psalm3/vomap.json"))
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


T_SLEEP = wt("sleep"); T_HEADING = wt("heading"); T_DAVID1 = wt("david", 1); T_RUNNING = wt("running")
T_ABSALOM1 = wt("absalom", 1); T_ABSALOM2 = wt("absalom", 2); T_TURNED = wt("turned"); T_FLED = wt("fled")
T_WEEPING = wt("weeping"); T_COVERED1 = wt("covered", 1); T_GRIEF1 = wt("grief", 1)
T_ENEMIES = wt("enemies"); T_SAYING = wt("saying"); T_WONT = wt("wont")
T_PRAYS = wt("prays"); T_SHIELD = wt("shield"); T_GLORY = wt("glory"); T_LIFTS1 = wt("lifts", 1); T_HEAD2 = wt("head", 2)
T_COVERED2 = wt("covered", 2); T_LIFTS2 = wt("lifts", 2); T_SURPRISING = wt("surprising"); T_LIES = wt("lies")
T_SLEEPS = wt("sleeps"); T_WAKES = wt("wakes"); T_HELD = wt("held")
T_KEY = wt("key"); T_SALVATION1 = wt("salvation", 1); T_YESHUAH = wt("yeshuah"); T_ROOT = wt("root")
T_YESHUA = wt("yeshua"); T_JESUS = wt("jesus"); T_SAVES = wt("saves")
T_TONIGHT = wt("tonight"); T_HAND = wt("hand"); T_AWAKE = wt("awake"); T_SALVATION2 = wt("salvation", 2)
T_REST = wt("rest")

B1, B2, B3, B4, B5, B6, B7, B8, B9 = 0.0, 2.95, 8.55, 15.3, 19.85, 31.0, 38.85, 50.5, 54.3

ZOOMS = [(0.1, 0.10), (T_SLEEP, 0.08), (T_ENEMIES, 0.08), (T_SHIELD, 0.10), (T_LIFTS1, 0.07), (T_LIFTS2, 0.06),
         (T_SLEEPS, 0.05), (T_YESHUAH, 0.12), (T_YESHUA, 0.10), (T_JESUS, 0.08), (T_SALVATION2, 0.05)]
SHAKES = [(0.1, 14, 0.6), (T_SLEEP, 6, 0.3), (T_ENEMIES, 9, 0.5), (T_SHIELD, 8, 0.4), (T_YESHUAH, 11, 0.5),
          (T_YESHUA, 8, 0.4), (T_JESUS, 6, 0.4)]
FLASHES = [(0.1, (1, 1, 1), 0.35, 0.3), (T_SHIELD, (1, 0.9, 0.6), 0.4, 0.4), (T_LIFTS1, (1, 0.92, 0.7), 0.25, 0.35),
           (T_WAKES, (1, 0.95, 0.8), 0.35, 0.5), (T_YESHUAH, (1, 0.85, 0.5), 0.3, 0.4), (T_JESUS, (1, 1, 1), 0.4, 0.45)]
BLUR = [(B2 - 0.3, B2 + 0.1), (B3 - 0.3, B3 + 0.1), (B4 - 0.3, B4 + 0.1), (B5 - 0.3, B5 + 0.1),
        (B6 - 0.3, B6 + 0.1), (B7 - 0.3, B7 + 0.1), (B8 - 0.3, B8 + 0.1), (B9 - 0.3, B9 + 0.1)]
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


NIGHT = hexc("#1E2433")
NIGHT2 = hexc("#2E3A4E")
MOON = hexc("#F4E9C8")


# ---------------------------------------------------------------- helpers
def night_sky(ctx, t, k=1.0, stars=1.0):
    g = cairo.LinearGradient(0, 0, 0, 1300)
    g.add_color_stop_rgba(0, *NIGHT)
    g.add_color_stop_rgba(1, *NIGHT2)
    ctx.set_source(g)
    ctx.paint()
    r = random.Random(77)
    for _ in range(90):
        x, y, s = r.uniform(0, W), r.uniform(0, 1100), r.uniform(1.5, 4)
        tw = 0.5 + 0.5 * math.sin(t * r.uniform(1, 3) + r.uniform(0, 6))
        ctx.set_source_rgba(*MOON[:3], (0.35 + 0.55 * tw) * stars)
        ctx.arc(x, y, s, 0, 2 * math.pi)
        ctx.fill()


def moon(ctx, x, y, r, alpha=1.0):
    g = cairo.RadialGradient(x, y, r * 0.5, x, y, r * 3)
    g.add_color_stop_rgba(0, *MOON[:3], 0.35 * alpha)
    g.add_color_stop_rgba(1, *MOON[:3], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r * 3, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*MOON[:3], alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*NIGHT[:3], alpha)
    ctx.arc(x + r * 0.45, y - r * 0.2, r * 0.85, 0, 2 * math.pi)
    ctx.fill()


def person(ctx, x, y, s, c, bow=0.0, cloth=0.0, crown_a=0.0, arms=0.0, kneel=0.0, alpha=1.0):
    """Faceless figure, feet at y. bow 0..1 lowers the head; cloth 0..1 drapes a mourning cloth over it."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c[:3], alpha)
    body_h = lerp(138, 92, kneel)
    ctx.move_to(-38, -body_h)
    ctx.curve_to(-50, -body_h * 0.65, -48, -body_h * 0.3, -44, 0)
    ctx.line_to(44, 0)
    ctx.curve_to(48, -body_h * 0.3, 50, -body_h * 0.65, 38, -body_h)
    ctx.curve_to(20, -body_h - 8, -20, -body_h - 8, -38, -body_h)
    ctx.close_path()
    ctx.fill()
    hx, hy = 14 * bow, -body_h - 40 + 26 * bow
    ctx.arc(hx, hy, 32, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_width(20)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        ang = lerp(math.radians(100), math.radians(-40), arms)
        ex = sx * (40 + 80 * math.cos(ang) * 0.9)
        ey = -body_h + 10 + 80 * math.sin(ang)
        ctx.move_to(sx * 36, -body_h + 10)
        ctx.curve_to(sx * 50, -body_h + 28, ex - sx * 10, ey + 10, ex, ey)
        ctx.stroke()
    if crown_a > 0:
        P.crown(ctx, hx, hy - 40, 0.3, crown_a * alpha, 0)
    if cloth > 0:
        ctx.set_source_rgba(*col("dry", alpha * clamp(cloth * 3)))
        drop = (1 - cloth) * 120
        ctx.move_to(hx - 42, hy + 30 + drop)
        ctx.curve_to(hx - 46, hy - 30 + drop, hx - 20, hy - 46 + drop, hx, hy - 46 + drop)
        ctx.curve_to(hx + 20, hy - 46 + drop, hx + 46, hy - 30 + drop, hx + 46, hy + 30 + drop)
        ctx.line_to(hx + 56, hy + 70 + drop)
        ctx.line_to(hx - 52, hy + 70 + drop)
        ctx.close_path()
        ctx.fill()
    ctx.restore()


def bedroom(ctx, t, calm=0.0, worry=1.0, lift=0.0, toss=1.0):
    """Night bedroom: window with moon, bed, clock at 3:00, worries swirling above the sleeper."""
    R.bg(ctx, NIGHT)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hexc("#25293A"))
    g.add_color_stop_rgba(1, *hexc("#3A3446"))
    ctx.set_source(g)
    ctx.paint()
    # window
    ctx.save()
    rounded(ctx, 640, 260, 320, 420, 20)
    ctx.clip()
    night_sky(ctx, t, 1, 1)
    moon(ctx, 820, 380, 46)
    ctx.restore()
    ctx.set_source_rgba(*col("brown2"))
    ctx.set_line_width(14)
    rounded(ctx, 640, 260, 320, 420, 20)
    ctx.stroke()
    ctx.move_to(800, 260)
    ctx.line_to(800, 680)
    ctx.move_to(640, 470)
    ctx.line_to(960, 470)
    ctx.stroke()
    mg = cairo.LinearGradient(640, 680, 300, 1300)
    mg.add_color_stop_rgba(0, *MOON[:3], 0.18 + 0.12 * calm)
    mg.add_color_stop_rgba(1, *MOON[:3], 0)
    ctx.set_source(mg)
    ctx.move_to(640, 680)
    ctx.line_to(960, 680)
    ctx.line_to(700, 1300)
    ctx.line_to(140, 1300)
    ctx.close_path()
    ctx.fill()
    # floor
    ctx.set_source_rgba(*hexc("#2A2433"))
    ctx.rectangle(0, 1240, W, H)
    ctx.fill()
    # bed
    ctx.set_source_rgba(*col("brown"))
    rounded(ctx, 90, 980, 820, 300, 26)
    ctx.fill()
    ctx.set_source_rgba(*col("brown2"))
    rounded(ctx, 70, 860, 60, 440, 18)
    ctx.fill()
    ctx.set_source_rgba(*col("cream2"))
    rounded(ctx, 150, 930, 200, 90, 40)
    ctx.fill()
    # sleeper: head on pillow, blanket hump that tosses
    tossing = toss * (1 - calm)
    tz = tossing * 16 * math.sin(t * 2.6) + tossing * 10 * math.sin(t * 5.3)
    ctx.set_source_rgba(*col("dark"))
    ctx.arc(250 + tz * 0.6, 940, 46, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*col("teal"))
    ctx.move_to(250, 1010)
    ctx.curve_to(330, 930 + tz, 620, 930 - tz, 880, 990)
    ctx.line_to(880, 1060)
    ctx.line_to(250, 1060)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*lerpc(col("teal"), col("cream2"), 0.25))
    ctx.rectangle(250, 1040, 630, 22)
    ctx.fill()
    # nightstand + clock
    ctx.set_source_rgba(*col("brown2"))
    rounded(ctx, 930, 1040, 130, 220, 12)
    ctx.fill()
    ctx.set_source_rgba(*col("dark"))
    rounded(ctx, 940, 960, 110, 74, 12)
    ctx.fill()
    blink = 1.0 if (t * 2) % 2 < 1.4 else 0.3
    draw_text(ctx, "3:00", R.F_CAP, 40, "#E3685A", 995, 997, blink * (1 - calm * 0.6))
    # worries
    r = random.Random(5)
    icons = ["!", "$", "?", "!", "?", "$", "!", "?"]
    for i, ic in enumerate(icons):
        ph = r.uniform(0, 6.28)
        rad = r.uniform(160, 300)
        a = ph + t * (0.9 + 0.3 * i % 3)
        x = 520 + math.cos(a) * rad
        y = 640 + math.sin(a) * rad * 0.45
        up = ein(seg(lift, i * 0.06, 0.55 + i * 0.06))
        x = lerp(x, 800, up)
        y = lerp(y, 420, up)
        al = worry * (1 - up) * clamp(back_out(seg(t, 0.1 + i * 0.05, 0.35 + i * 0.05)))
        if al <= 0.01:
            continue
        sc = 0.6 + 0.4 * clamp(back_out(seg(t, 0.1 + i * 0.05, 0.35 + i * 0.05)))
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(sc, sc)
        ctx.set_source_rgba(*col("rust", al))
        ctx.arc(0, 0, 46, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
        draw_text(ctx, ic, F_SERIF, 60, "#FBF6EC", x, y, al, sc)
    if calm > 0:
        cg = cairo.RadialGradient(500, 960, 30, 500, 960, 560)
        cg.add_color_stop_rgba(0, *col("gold2")[:3], 0.35 * calm)
        cg.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(cg)
        ctx.paint()


def hills_night(ctx, t, torches=1.0, k=1.0):
    for base, amp, c, seed in [(980, 90, hexc("#2B3245"), 31), (1080, 70, hexc("#232838"), 32)]:
        V.hills(ctx, base, amp, c, 0, seed)
    ctx.set_source_rgba(*hexc("#1A1E2B"))
    ctx.rectangle(0, 1180, W, H)
    ctx.fill()
    if torches > 0:
        r = random.Random(9)
        for i in range(34):
            x = r.uniform(0, W)
            y = r.uniform(920, 1170)
            d = clamp(back_out(seg(torches, i / 34 * 0.6, i / 34 * 0.6 + 0.3)))
            if d <= 0.01:
                continue
            fl = 0.75 + 0.25 * math.sin(t * 12 + i)
            g = cairo.RadialGradient(x, y, 2, x, y, 42)
            g.add_color_stop_rgba(0, 1, 0.7, 0.3, 0.7 * fl * d * k)
            g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
            ctx.set_source(g)
            ctx.arc(x, y, 42, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgba(1, 0.85, 0.45, d * k)
            ctx.arc(x, y, 5, 0, 2 * math.pi)
            ctx.fill()


def dome(ctx, cx, base, rx, ry, k, alpha=1.0):
    if k <= 0.01:
        return
    dg = cairo.RadialGradient(cx, base - ry * 0.3, 30, cx, base - ry * 0.3, ry * 1.2)
    dg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.85 * k * alpha)
    dg.add_color_stop_rgba(0.6, *col("gold2")[:3], 0.45 * k * alpha)
    dg.add_color_stop_rgba(1, *col("gold2")[:3], 0)
    ctx.set_source(dg)
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(1, ry / rx)
    ctx.arc(0, 0, rx * k, math.pi, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(1, ry / rx)
    ctx.arc(0, 0, rx * k, math.pi, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(*col("gold2", 0.9 * k * alpha))
    ctx.set_line_width(6)
    ctx.stroke()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    t = lt
    ctx.save()
    cam(ctx, 540, 900, 1.0 + 0.08 * ease(lt / 3.0))
    bedroom(ctx, t, 0, 1.0, 0, 1.0)
    ctx.restore()
    kword(ctx, "CAN'T SLEEP?", t, T_SLEEP - 0.35, 540, 170, 112, "#E3B04B", B2 - T_SLEEP + 0.3)


def scene2(ctx, lt):
    t = lt + B2
    ctx.save()
    sl = 1300 * (1 - eout(seg(lt, -0.1, 0.3)))
    ctx.translate(sl, 0)
    R.bg(ctx, col("cream"))
    rays(ctx, 540, 600, 0, 2 * math.pi, 12, 900, 0.35, t * 0.4)
    draw_text(ctx, "PSALM 3", F_SERIF, 118, "#3B2A1E", 540, 300, ease(seg(lt, 0.1, 0.5)), 0.94 + 0.06 * back_out(seg(lt, 0.1, 0.45)))
    # the heading on a scroll
    un = eout(seg(t, T_HEADING - 0.2, T_HEADING + 0.6))
    ctx.save()
    w = 760 * un
    ctx.set_source_rgba(*col("cream2"))
    rounded(ctx, 540 - w / 2, 430, w, 200, 14)
    ctx.fill()
    ctx.set_source_rgba(*col("dry"))
    for sx in (-1, 1):
        rounded(ctx, 540 + sx * w / 2 - 16, 414, 32, 232, 14)
        ctx.fill()
    ctx.restore()
    ta = ease(seg(t, T_HEADING + 0.4, T_HEADING + 0.8))
    draw_text(ctx, "A psalm of David,", F_SERIF_I, 54, "#6E5039", 540, 500, ta)
    draw_text(ctx, "when he fled from Absalom his son", F_SERIF_I, 44, "#6E5039", 540, 570, ta * ease(seg(t, T_DAVID1, T_DAVID1 + 0.4)))
    # David running, Absalom's banner behind
    run = ease(seg(t, T_RUNNING - 0.3, T_RUNNING + 0.3))
    ground_y = 1180
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(0, ground_y, W, H)
    ctx.fill()
    if run > 0:
        dx = lerp(560, 300, ease(seg(t, T_RUNNING - 0.3, B3)))
        bob = 8 * abs(math.sin(t * 9))
        person(ctx, dx, ground_y - bob, 1.25, col("brown"), 0.2, 0, 1.0, 0.35, alpha=run)
        ab = ease(seg(t, T_ABSALOM1 - 0.2, T_ABSALOM1 + 0.3))
        if ab > 0:
            ax = lerp(1200, 860, ease(seg(t, T_ABSALOM1 - 0.2, B3)))
            person(ctx, ax, ground_y, 1.1, col("rust"), 0, 0, 1.0, 0.8, alpha=ab)
            P.banner(ctx, ax + 60, ground_y - 120, 330, col("rust", ab), t, 0, col("rust", 0.85 * ab))
            draw_text(ctx, "Absalom", F_SERIF_I, 52, "#A9472F", ax, ground_y + 70, ab)
        draw_text(ctx, "David", F_SERIF_I, 52, "#3B2A1E", dx, ground_y + 70, run)
    ctx.restore()


def scene3(ctx, lt):
    t = lt + B3
    flee = ease(seg(t, T_FLED - 0.5, T_FLED))
    # Beat A: Israel turns to Absalom
    if flee < 1:
        ctx.push_group()
        P.storm_sky(ctx, t, 0.8)
        ctx.set_source_rgba(*hexc("#4A3227"))
        ctx.rectangle(0, 1180, W, H)
        ctx.fill()
        turn = ease(seg(t, T_TURNED - 0.2, T_TURNED + 0.6))
        P.crowd(ctx, t, 0.3 + 0.7 * turn, eout(seg(lt, 0.0, 0.8)), 1.0)
        ab = ease(seg(lt, 0.3, 0.8))
        crown_y = 420
        P.crown(ctx, 540, crown_y, 0.6, ab, 0.4 * turn, "rust")
        draw_text(ctx, "Absalom", F_SERIF_I, 64, "#FBF6EC", 540, crown_y + 110, ab, stroke=3, stroke_color="#2A1D14")
        grade(ctx, desat=0.2, warm=0.3)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - flee)
    # Beat B: David climbs the hill weeping, head covered
    if flee > 0:
        ctx.push_group()
        g = cairo.LinearGradient(0, 0, 0, 1200)
        g.add_color_stop_rgba(0, *hexc("#5B5C6B"))
        g.add_color_stop_rgba(1, *hexc("#B98E6E"))
        ctx.set_source(g)
        ctx.paint()
        ctx.set_source_rgba(*hexc("#6F6250"))
        ctx.move_to(0, 1450)
        ctx.curve_to(400, 1300, 700, 900, W, 760)
        ctx.line_to(W, H)
        ctx.line_to(0, H)
        ctx.close_path()
        ctx.fill()
        for tx, ty, s in [(860, 790, 0.8), (980, 760, 0.7), (120, 1360, 1.0)]:
            ctx.set_source_rgba(*hexc("#4D5A3B"))
            ctx.arc(tx, ty - 60 * s, 55 * s, 0, 2 * math.pi)
            ctx.fill()
            ctx.rectangle(tx - 6 * s, ty - 60 * s, 12 * s, 60 * s)
            ctx.fill()
        u = seg(t, T_FLED - 0.5, B4 + 0.3)
        px = lerp(260, 640, u)
        ctx.save()
        cam(ctx, px, 1400 - px * 0.42 - 140, 1.45)
        py = 1400 - (px - 0) * 0.42 - 40
        bob = 5 * abs(math.sin(t * 5))
        cloth = ease(seg(t, T_COVERED1 - 0.4, T_COVERED1 + 0.2))
        ctx.save()
        ctx.translate(px, py - bob)
        ctx.rotate(-0.12)
        person(ctx, 0, 0, 1.15, col("brown"), 0.9, cloth, 1.0, 0.0)
        ctx.restore()
        for i in range(3):
            fx = px - 170 - i * 120
            fy = 1400 - fx * 0.42 - 30
            person(ctx, fx, fy, 0.8, col("dark"), 0.7, 0, 0, 0, alpha=0.8)
        # tears
        if t > T_WEEPING - 0.1:
            for k in range(3):
                v = (t * 1.3 + k / 3) % 1.0
                ctx.set_source_rgba(*col("water2", 0.8 * math.sin(math.pi * v)))
                ctx.arc(px + 30, py - 170 + v * 60, 5, 0, 2 * math.pi)
                ctx.fill()
        ctx.restore()
        grade(ctx, desat=0.45, cool=0.15)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(flee)
        P.tag(ctx, "2 Samuel 15:30", 540, 360, seg(t, T_COVERED1 - 0.2, T_COVERED1 + 0.2), flee, 380)


WHISPERS = [(330, 360, -0.08), (750, 290, 0.06), (540, 520, 0.0), (330, 660, 0.05), (750, 610, -0.05)]


def scene4(ctx, lt):
    t = lt + B4
    ctx.save()
    cam(ctx, 540, 1000, 1.05 + 0.08 * ease(lt / 4.5))
    night_sky(ctx, t, 1, 1)
    moon(ctx, 860, 220, 50)
    hills_night(ctx, t, seg(t, T_ENEMIES - 0.4, T_ENEMIES + 0.8), 1.0)
    person(ctx, 540, 1230, 0.9, col("dark"), 0.8, 1.0, 1.0, 0)
    ctx.restore()
    kword(ctx, "ENEMIES", t, T_ENEMIES - 0.03, 540, 200, 150, "#E3B04B", T_SAYING - T_ENEMIES)
    for i, (x, y, rot) in enumerate(WHISPERS):
        a = ease(seg(t, T_WONT - 0.1 + i * 0.18, T_WONT + 0.25 + i * 0.18)) * (1 - ease(seg(t, B5 - 0.4, B5)))
        drift = 10 * math.sin(t * 2 + i)
        draw_text(ctx, "“God won't save him now”", F_SERIF_I, 66 if i == 2 else 48, "#F4E9C8",
                  x, y + drift, a * (1.0 if i == 2 else 0.7), stroke=4, stroke_color="#1E2433")


def scene5(ctx, lt):
    t = lt + B5
    ctx.save()
    cam(ctx, 540, 1000, 1.12 - 0.12 * ease(lt / 11))
    night_sky(ctx, t, 1, 1)
    moon(ctx, 860, 220, 50)
    sh = eout(seg(t, T_SHIELD - 0.2, T_SHIELD + 0.5))
    hills_night(ctx, t, 1.0, 1 - 0.6 * sh)
    rays(ctx, 540, -80, math.radians(70), math.radians(110), 6, 1500, 0.5 * ease(seg(t, T_PRAYS, T_SHIELD)), t * 0.4)
    dome(ctx, 540, 1240, 380, 470, sh)
    gl = ease(seg(t, T_GLORY - 0.1, T_GLORY + 0.4))
    if gl > 0:
        g = cairo.RadialGradient(540, 1000, 20, 540, 1000, 300)
        g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.5 * gl)
        g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.set_source(g)
        ctx.arc(540, 1000, 300, 0, 2 * math.pi)
        ctx.fill()
    lift = ease(seg(t, T_HEAD2 - 0.5, T_HEAD2 + 0.2))
    lift2 = ease(seg(t, T_LIFTS2 - 0.3, T_LIFTS2 + 0.3))
    kneel = 1 - ease(seg(t, T_LIFTS2 - 0.2, T_LIFTS2 + 0.5))
    bow = (1 - lift) * 0.9 if lift2 < 1 else 0
    bow = max(0, bow - lift2)
    person(ctx, 540, 1235, 1.15, col("dark"), bow, 1 - lift, 1.0, 0.15 + 0.6 * lift2, kneel)
    ctx.restore()
    kword(ctx, "SHIELD", t, T_SHIELD - 0.03, 540, 220, 160, "#E3B04B", T_GLORY - T_SHIELD + 0.2)
    kword(ctx, "LIFTED", t, T_LIFTS1 - 0.03, 540, 220, 160, "#E3B04B", B6 - T_LIFTS1 - 0.2)


def scene6(ctx, lt):
    t = lt + B6
    dawn = ease(seg(t, T_WAKES - 0.4, T_WAKES + 0.8))
    ctx.save()
    cam(ctx, 540, 1100, 1.08)
    night_sky(ctx, t, 1, 1 - dawn)
    if dawn > 0:
        g = cairo.LinearGradient(0, 0, 0, 1200)
        g.add_color_stop_rgba(0, *hexc("#F3D9B0", dawn))
        g.add_color_stop_rgba(1, *hexc("#F2B77A", dawn))
        ctx.set_source(g)
        ctx.paint()
        sy = lerp(1160, 900, eout(seg(t, T_WAKES - 0.2, T_HELD + 0.8)))
        sg = cairo.RadialGradient(540, sy, 40, 540, sy, 400)
        sg.add_color_stop_rgba(0, 1, 0.92, 0.6, 0.9 * dawn)
        sg.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
        ctx.set_source(sg)
        ctx.arc(540, sy, 400, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(*col("gold2", dawn))
        ctx.arc(540, sy, 90, 0, 2 * math.pi)
        ctx.fill()
    # moon arcs across the sky through the night
    m = seg(t, T_LIES, T_WAKES)
    mx = lerp(120, 960, m)
    my = 520 - 300 * math.sin(math.pi * m)
    moon(ctx, mx, my, 46, 1 - dawn)
    hills_night(ctx, t, 1.0 * (1 - dawn), 1.0)
    if dawn > 0:
        for base, amp, c, seed in [(980, 90, hexc("#C99A72", dawn), 31), (1080, 70, hexc("#A87C5A", dawn), 32)]:
            V.hills(ctx, base, amp, c, 0, seed)
        ctx.set_source_rgba(*hexc("#8E6A4C", dawn))
        ctx.rectangle(0, 1180, W, H)
        ctx.fill()
    dome(ctx, 540, 1240, 380, 470, 1.0, 0.8 * (1 - 0.5 * dawn))
    # lying down -> sleeping -> waking up
    down = ease(seg(t, T_LIES - 0.3, T_LIES + 0.5))
    up = ease(seg(t, T_WAKES - 0.1, T_WAKES + 0.6))
    rot = lerp(0, -math.pi / 2, down) * (1 - up)
    ctx.save()
    ctx.translate(540, 1236)
    ctx.rotate(rot)
    person(ctx, 0, 0, 1.0, col("dark"), 0, 0, 1.0, 0.1 + 0.5 * up)
    ctx.restore()
    ctx.set_source_rgba(*col("dry", down * (1 - up)))
    rounded(ctx, 380, 1228, 320, 22, 10)
    ctx.fill()
    if 0.5 < down and up < 0.5:
        for k in range(3):
            v = (t * 0.6 + k / 3) % 1.0
            draw_text(ctx, "z", F_SERIF_I, 40 + 20 * v, "#F4E9C8", 640 + 60 * v + k * 10, 1150 - 160 * v, math.sin(math.pi * v) * 0.9)
    ctx.restore()
    kword(ctx, "SLEEPS", t, T_SLEEPS - 0.03, 540, 220, 160, "#E3B04B", T_WAKES - T_SLEEPS - 0.1)
    draw_text(ctx, "The Lord held him up", F_SERIF_I, 64, "#3B2A1E", 540, 300, ease(seg(t, T_HELD, T_HELD + 0.4)) * dawn)


def scene7(ctx, lt):
    t = lt + B7
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.7, "gold2", 6, -12)
    sa = ease(seg(t, T_KEY + 0.1, T_KEY + 0.5)) * (1 - ease(seg(t, T_YESHUAH - 0.6, T_YESHUAH - 0.3)))
    pulse = 1 + 0.08 * math.exp(-((t - T_SALVATION1) ** 2) * 10)
    rays(ctx, 540, 640, 0, 2 * math.pi, 14, 800, 0.5 * sa, t * 0.4)
    P.tag(ctx, "Psalm 3:2 \u00b7 3:8", 540, 800, seg(t, T_KEY + 0.5, T_KEY + 0.85), sa, 380)
    draw_text(ctx, "“salvation”", F_SERIF_I, 110, "#FBF6EC", 540, 640, sa, (0.9 + 0.1 * back_out(seg(t, T_KEY + 0.1, T_KEY + 0.45))) * pulse)
    fade = 1 - ease(seg(t, T_SAVES - 0.6, T_SAVES - 0.2))
    up = ease(seg(t, T_ROOT - 0.4, T_ROOT))
    hy, hs = lerp(600, 380, up), lerp(1.0, 0.7, up)
    hb = ease(seg(t, T_YESHUAH - 0.6, T_YESHUAH - 0.3)) * fade
    rays(ctx, 540, hy, 0, 2 * math.pi, 18, 900 * hs + 200, hb * (0.4 + 0.6 * seg(t, T_YESHUAH, T_YESHUAH + 0.3)) * (1 - 0.6 * up), t * 0.4)
    P.burn_word(ctx, "יְשׁוּעָה", F_HEB, 280, 540, hy, ease(seg(t, T_YESHUAH - 0.55, T_YESHUAH + 0.05)), hb, rtl=True, scale=hs)
    sub = ease(seg(t, T_YESHUAH + 0.1, T_YESHUAH + 0.5)) * fade
    draw_text(ctx, "yeshuah", F_SERIF_I, lerp(96, 70, up), "#FBF6EC", 540, lerp(840, 540, up), sub)
    draw_text(ctx, "salvation", F_SERIF_R, lerp(56, 44, up), "#DCC59D", 540, lerp(940, 610, up), sub)
    # shared root
    lk = eout(seg(t, T_ROOT - 0.1, T_ROOT + 0.4)) * fade
    if lk > 0:
        ctx.set_source_rgba(*col("gold", lk))
        ctx.set_line_width(5)
        ctx.move_to(540, 650)
        ctx.line_to(540, lerp(650, 760, lk))
        ctx.stroke()
        draw_text(ctx, "same root: “to save”", F_SERIF_I, 44, "#DCC59D", 760, 705, lk)
    yb = ease(seg(t, T_YESHUA - 0.5, T_YESHUA - 0.2)) * fade
    P.burn_word(ctx, "יֵשׁוּעַ", F_HEB, 220, 540, 900, ease(seg(t, T_YESHUA - 0.45, T_YESHUA + 0.05)), yb, rtl=True)
    draw_text(ctx, "Yeshua", F_SERIF_I, 80, "#FBF6EC", 540, 1080, ease(seg(t, T_YESHUA + 0.1, T_YESHUA + 0.4)) * fade)
    jr = ease(seg(t, T_JESUS - 0.1, T_JESUS + 0.3))
    if jr > 0:
        rays(ctx, 540, 800, 0, 2 * math.pi, 18, 1000, jr * 0.9 * (0.5 + 0.5 * fade), t * 0.5)
    kword(ctx, "JESUS", t, T_JESUS - 0.03, 540, 1240, 170, "#E3B04B", T_SAVES - T_JESUS - 0.6)
    # "the Lord saves"
    ca = ease(seg(t, T_SAVES - 0.5, T_SAVES - 0.1))
    if ca > 0:
        pop = back_out(seg(t, T_SAVES - 0.5, T_SAVES - 0.15), 1.4)
        P.verse_card(ctx, 540, 800, 720, 420, ca, max(0.01, 1.2 - 0.2 * pop))
        draw_text(ctx, "Yeshua · Jesus", F_SERIF, 60, "#3B2A1E", 540, 700, ca)
        draw_text(ctx, "“the Lord saves”", F_SERIF_I, 90, "#A8741A", 540, 820, ca)
        P.tag(ctx, "Matthew 1:21", 540, 940, seg(t, T_SAVES - 0.2, T_SAVES + 0.2), ca, 330)


def scene8(ctx, lt):
    t = lt + B8
    ctx.save()
    cam(ctx, 540, 900, 1.06 - 0.06 * ease(lt / 3.8))
    lift = seg(t, T_HAND - 0.1, T_AWAKE + 0.4)
    bedroom(ctx, t, ease(seg(t, T_AWAKE - 0.5, B9)), 1.0, lift, 1.0)
    rays(ctx, 800, 380, math.radians(100), math.radians(170), 6, 1300, 0.6 * ease(lift), t * 0.4)
    ctx.restore()


def scene9(ctx, lt):
    t = lt + B9
    night_sky(ctx, t, 1, 1)
    moon(ctx, 800, 300, 60)
    hills_night(ctx, t, 0.0, 1.0)
    dome(ctx, 540, 1240, 380, 470, 1.0, 0.85)
    ctx.save()
    ctx.translate(540, 1236)
    ctx.rotate(-math.pi / 2)
    person(ctx, 0, 0, 1.0, col("dark"), 0, 0, 0, 0.1)
    ctx.restore()
    for k in range(3):
        v = (t * 0.5 + k / 3) % 1.0
        draw_text(ctx, "z", F_SERIF_I, 40 + 20 * v, "#F4E9C8", 640 + 60 * v + k * 10, 1150 - 160 * v, math.sin(math.pi * v) * 0.8)
    a1 = ease(seg(t, T_SALVATION2 - 0.3, T_SALVATION2 + 0.2))
    draw_text(ctx, "PSALM 3", F_SERIF, 50, "#DCC59D", 540, 520, a1)
    ctx.set_source_rgba(*col("gold", a1))
    ctx.rectangle(490, 570, 100, 4)
    ctx.fill()
    draw_text(ctx, "Salvation belongs", F_SERIF_I, 72, "#F4E9C8", 540, 660, a1)
    draw_text(ctx, "to the Lord.", F_SERIF_I, 72, "#F4E9C8", 540, 745, a1)
    a2 = ease(seg(t, T_REST - 0.3, T_REST + 0.1))
    draw_text(ctx, "You can rest.", F_SERIF, 110, "#E3B04B", 540, 880, a2, 0.92 + 0.08 * back_out(seg(t, T_REST - 0.3, T_REST + 0.1)))
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


SCENES = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5),
          (B6, B7, scene6), (B7, B8, scene7), (B8, B9, scene8), (B9, DUR + 1, scene9)]
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
        os.makedirs("/home/claude/psalm3/stills", exist_ok=True)
        for t in map(float, sys.argv[2:]):
            render_frame(t).write_to_png(f"/home/claude/psalm3/stills/t{t:05.2f}.png")
    elif sys.argv[1] == "times":
        for k, v in sorted(((k, v) for k, v in globals().items() if k.startswith("T_")), key=lambda x: x[1]):
            print(f"{k:13s} {v:6.2f}")
    else:
        video(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
