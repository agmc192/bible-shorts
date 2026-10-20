"""Psalm 6 Short, timed to the ElevenLabs voiceover (vomap.json). Reuses the Psalm 1-4 libraries.
Central image: a bed flooded with tears at night; the turn at verse 8; tears heard, rising as light."""
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

MAP = json.load(open("/home/claude/psalm6/vomap.json"))
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


T_CRIED = wt("cried"); T_SLEEP = wt("sleep"); T_ANYONE = wt("anyone"); T_NOTICED = wt("noticed")
T_PSALM = wt("psalm"); T_PRAYER1 = wt("prayer", 1); T_DAVID1 = wt("david", 1); T_RAW = wt("raw")
T_WORN = wt("worn"); T_GROANING = wt("groaning"); T_EVERY = wt("every"); T_NIGHT = wt("night"); T_FLOODS = wt("floods")
T_BED = wt("bed"); T_TEARS1 = wt("tears", 1)
T_BONES = wt("bones"); T_ACHE = wt("ache"); T_SOUL = wt("soul"); T_SHAKEN = wt("shaken"); T_ENEMIES = wt("enemies")
T_LET = wt("let")
T_THEN = wt("then"); T_END = wt("end"); T_EVERYTHING = wt("everything"); T_TURNS = wt("turns")
T_LORD1 = wt("lord", 1); T_HEARD1 = wt("heard", 1); T_SOUND = wt("sound"); T_WEEPING = wt("weeping")
T_LORD2 = wt("lord", 2); T_ACCEPTS = wt("accepts"); T_PRAYER2 = wt("prayer", 2)
T_NOTHING = wt("nothing"); T_CHANGED = wt("changed"); T_YET = wt("yet"); T_DAVID2 = wt("david", 2)
T_KNOWS = wt("knows"); T_TEARS2 = wt("tears", 2); T_HEARD2 = wt("heard", 2)
T_LOOK = wt("look"); T_THREE = wt("three"); T_HEBREW = wt("hebrew"); T_CRIES = wt("cries")
T_YOU2 = wt("you", 2); T_LORD3 = wt("lord", 3); T_ADMATAI = wt("ahdmahtie"); T_UNTIL = wt("until"); T_WHEN = wt("when")
T_FINISH = wt("finish"); T_SENTENCE1 = wt("sentence", 1); T_GOD1 = wt("god", 1); T_HEARS = wt("hears")
T_TONIGHT = wt("tonight"); T_WORDS = wt("words"); T_COME = wt("come"); T_GIVE1 = wt("give", 1); T_HALF = wt("half")
T_SENTENCE2 = wt("sentence", 2); T_GIVE2 = wt("give", 2); T_TEARS3 = wt("tears", 3)
T_YOUR = wt("your"); T_TEARS4 = wt("tears", 4); T_HEARD3 = wt("heard", 3)

B1 = 0.0
B2 = T_PSALM - 0.3      # title, "raw"
B3 = T_WORN - 0.3       # worn out, flooded bed
B4 = T_BONES - 0.3      # bones, soul, enemies
B5 = T_THEN - 0.35      # the turn at verse 8
B6 = T_LORD1 - 0.35     # "The Lord has heard"
B7 = T_NOTHING - 0.4    # nothing changed yet
B8 = T_LOOK - 0.35      # nugget: verse 3
B9 = 41.2           # the unfinished sentence
B10 = T_TONIGHT - 0.35  # close

ZOOMS = [(0.1, 0.12), (T_ANYONE, 0.06), (T_RAW, 0.10), (T_FLOODS, 0.08), (T_SHAKEN, 0.06), (T_ENEMIES, 0.07),
         (T_TURNS, 0.12), (T_HEARD1, 0.06), (T_HEARD2, 0.07), (T_ADMATAI, 0.12), (T_WHEN, 0.05), (T_HEARS, 0.07),
         (T_TEARS4, 0.06)]
SHAKES = [(0.1, 16, 0.6), (T_RAW, 12, 0.5), (T_FLOODS, 6, 0.6), (T_ACHE, 5, 0.5), (T_SHAKEN, 14, 0.9),
          (T_ENEMIES, 7, 0.5), (T_TURNS, 12, 0.6), (T_ADMATAI, 11, 0.5), (T_FINISH + 0.4, 9, 0.4)]
FLASHES = [(0.1, (0.8, 0.9, 1.0), 0.4, 0.35), (T_RAW, (1, 0.95, 0.9), 0.3, 0.3), (T_TURNS, (1, 0.9, 0.6), 0.5, 0.5),
           (T_HEARD1, (1, 0.92, 0.7), 0.2, 0.4), (T_ADMATAI, (1, 0.85, 0.5), 0.3, 0.4), (T_HEARS, (1, 0.92, 0.7), 0.3, 0.45),
           (T_TEARS4, (1, 0.95, 0.85), 0.3, 0.4)]
BLUR = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6, B7, B8, B9, B10)]
ZC = (540, 860)

IND = hexc("#232A45")
IND2 = hexc("#37406A")
IND3 = hexc("#4B5684")
FLOOR_Y = 1250


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
def tear(ctx, x, y, r, c, alpha=1.0):
    """Teardrop, point up, centred on its round end."""
    if alpha <= 0.01:
        return
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.move_to(x, y - 2.1 * r)
    ctx.curve_to(x + 0.35 * r, y - 1.2 * r, x + r, y - 0.6 * r, x + r, y)
    ctx.arc(x, y, r, 0, math.pi)
    ctx.curve_to(x - r, y - 0.6 * r, x - 0.35 * r, y - 1.2 * r, x, y - 2.1 * r)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.45 * alpha)
    ctx.arc(x - 0.35 * r, y - 0.2 * r, 0.22 * r, 0, 2 * math.pi)
    ctx.fill()


def night_room(ctx, t, nights=0.0, warm=0.0, moon_p=None):
    """Indigo bedroom wall with an arched window; nights 0..1 sweeps moons across the window."""
    g = cairo.LinearGradient(0, 0, 0, FLOOR_Y)
    g.add_color_stop_rgba(0, *lerpc(IND, hexc("#5A4A5E"), warm))
    g.add_color_stop_rgba(1, *lerpc(IND2, hexc("#8A6A5A"), warm))
    ctx.set_source(g)
    ctx.paint()
    wx, wy, ww, wh = 600, 260, 330, 470
    ctx.save()
    ctx.move_to(wx, wy + wh)
    ctx.line_to(wx, wy + ww / 2)
    ctx.arc(wx + ww / 2, wy + ww / 2, ww / 2, math.pi, 2 * math.pi)
    ctx.line_to(wx + ww, wy + wh)
    ctx.close_path()
    ctx.clip()
    sg = cairo.LinearGradient(0, wy, 0, wy + wh)
    sg.add_color_stop_rgba(0, *lerpc(hexc("#151A30"), hexc("#E9B98A"), warm))
    sg.add_color_stop_rgba(1, *lerpc(hexc("#2C3560"), hexc("#F3D9B0"), warm))
    ctx.set_source(sg)
    ctx.paint()
    r = random.Random(61)
    for _ in range(26):
        sx, sy = r.uniform(wx, wx + ww), r.uniform(wy, wy + wh * 0.8)
        tw = 0.5 + 0.5 * math.sin(t * r.uniform(1, 3) + r.uniform(0, 6))
        ctx.set_source_rgba(*Q.MOON[:3], (0.3 + 0.5 * tw) * (1 - warm))
        ctx.arc(sx, sy, r.uniform(1.5, 3.5), 0, 2 * math.pi)
        ctx.fill()
    if moon_p is None:
        moon_p = 0.55
    n_moons = 1 + int(nights * 4)
    for k in range(n_moons):
        p = (moon_p + nights * 3.2 + k * 0.0) % 1.0 if nights > 0 else moon_p
        mx = lerp(wx - 60, wx + ww + 60, p)
        my = wy + 210 - 140 * math.sin(math.pi * p)
        if k == 0:
            Q.moon(ctx, mx, my, 46, 1 - warm)
    # rain-like streaks of condensation on the glass
    for i in range(9):
        u = (t * 0.25 + i * 0.13) % 1.0
        x = wx + 25 + i * 34
        ctx.set_source_rgba(0.75, 0.85, 1.0, 0.18 * (1 - warm))
        ctx.set_line_width(3)
        ctx.move_to(x, wy + 120 + u * 260)
        ctx.line_to(x + 2, wy + 160 + u * 260)
        ctx.stroke()
    ctx.restore()
    # frame + cross bars
    ctx.set_source_rgba(*col("brown"))
    ctx.set_line_width(16)
    ctx.move_to(wx, wy + wh)
    ctx.line_to(wx, wy + ww / 2)
    ctx.arc(wx + ww / 2, wy + ww / 2, ww / 2, math.pi, 2 * math.pi)
    ctx.line_to(wx + ww, wy + wh)
    ctx.close_path()
    ctx.stroke()
    ctx.set_line_width(10)
    ctx.move_to(wx + ww / 2, wy)
    ctx.line_to(wx + ww / 2, wy + wh)
    ctx.move_to(wx, wy + 300)
    ctx.line_to(wx + ww, wy + 300)
    ctx.stroke()
    ctx.set_source_rgba(*col("brown2"))
    rounded(ctx, wx - 30, wy + wh, ww + 60, 26, 8)
    ctx.fill()
    # moonlight patch on the wall
    mg = cairo.RadialGradient(wx + ww / 2, wy + wh + 300, 20, wx + ww / 2, wy + wh + 300, 480)
    mg.add_color_stop_rgba(0, *lerpc(hexc("#A9B8E8"), col("gold2"), warm)[:3], 0.18)
    mg.add_color_stop_rgba(1, 0.6, 0.7, 1.0, 0)
    ctx.set_source(mg)
    ctx.paint()
    # floor
    ctx.set_source_rgba(*lerpc(hexc("#1A1F33"), hexc("#5E4636"), warm))
    ctx.rectangle(0, FLOOR_Y, W, H)
    ctx.fill()


def tallies(ctx, n, x0, y0, alpha=1.0):
    """Chalk tally marks on the wall: one per night."""
    if alpha <= 0.01 or n <= 0:
        return
    ctx.set_source_rgba(0.85, 0.88, 1.0, 0.75 * alpha)
    ctx.set_line_width(6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    full = int(n)
    for i in range(full):
        grp, k = divmod(i, 5)
        gx = x0 + grp * 110
        if k < 4:
            ctx.move_to(gx + k * 18, y0)
            ctx.line_to(gx + k * 18 + 3, y0 + 70)
        else:
            ctx.move_to(gx - 10, y0 + 55)
            ctx.line_to(gx + 66, y0 + 12)
        ctx.stroke()


def bed(ctx, cx, base, s, flood=0.0, t=0.0, wet=0.0):
    """Side-view bed; base = floor line."""
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("brown"))
    ctx.rectangle(-330, -230, 30, 230)
    ctx.rectangle(300, -150, 26, 150)
    ctx.fill()
    rounded(ctx, -340, -260, 52, 70, 14)
    ctx.fill()
    ctx.set_source_rgba(*col("brown2"))
    rounded(ctx, -310, -120, 620, 46, 10)
    ctx.fill()
    mc = lerpc(hexc("#C9D2EE"), hexc("#6F8FB4"), wet)
    ctx.set_source_rgba(*mc)
    rounded(ctx, -305, -175, 610, 62, 24)
    ctx.fill()
    ctx.set_source_rgba(*lerpc(hexc("#E6EBF8"), hexc("#8EAAC8"), wet))
    ctx.save()
    ctx.translate(-225, -188)
    ctx.scale(1, 0.45)
    ctx.arc(0, 0, 70, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.restore()


def lying(ctx, cx, y, s, c, curl=1.0, alpha=1.0, sob=0.0, t=0.0):
    """A figure lying on its side on the bed, knees drawn up; y = mattress top."""
    ctx.save()
    ctx.translate(cx, y - 8 * s + sob * 4 * math.sin(t * 9))
    ctx.scale(s, s)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.arc(-200, -38, 34, 0, 2 * math.pi)
    ctx.fill()
    ctx.move_to(-165, -60)
    ctx.curve_to(-60, -82, 40, -74, 90, -52)
    ctx.curve_to(150 - 40 * curl, -90 * curl, 220 - 70 * curl, -70 * curl, 230 - 80 * curl, -8)
    ctx.line_to(-160, -6)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def sitting(ctx, x, base, s, c, slump=1.0, alpha=1.0):
    """Figure sitting on the bed edge, head in hands when slumped."""
    ctx.save()
    ctx.translate(x, base)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.move_to(-40, 0)
    ctx.curve_to(-46, -50, -40, -110, -30 + 20 * slump, -150 + 18 * slump)
    ctx.curve_to(0 + 20 * slump, -160 + 18 * slump, 30 + 20 * slump, -150 + 18 * slump, 40 + 10 * slump, -110)
    ctx.curve_to(46, -60, 44, -20, 40, 0)
    ctx.close_path()
    ctx.fill()
    ctx.arc(10 + 46 * slump, -186 + 50 * slump, 32, 0, 2 * math.pi)
    ctx.fill()
    ctx.move_to(40, 0)
    ctx.line_to(110, 0)
    ctx.curve_to(120, 40, 112, 120, 108, 150)
    ctx.line_to(84, 150)
    ctx.curve_to(86, 110, 88, 50, 70, 26)
    ctx.line_to(30, 26)
    ctx.close_path()
    ctx.fill()
    ctx.set_line_width(20)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(30, -130 + 14 * slump)
    ctx.curve_to(70, -100, 100, -60, 100, -10 - 120 * slump)
    ctx.stroke()
    ctx.restore()


def water(ctx, t, level, alpha=1.0, gold=0.0):
    """Teal flood rising from the bottom to y = level."""
    if level >= H or alpha <= 0.01:
        return
    c1 = lerpc(col("water"), col("gold2"), gold)
    c2 = lerpc(col("teal"), col("gold"), gold)
    g = cairo.LinearGradient(0, level, 0, H)
    g.add_color_stop_rgba(0, *c1[:3], 0.82 * alpha)
    g.add_color_stop_rgba(1, *c2[:3], 0.95 * alpha)
    ctx.set_source(g)
    ctx.move_to(0, H)
    for i in range(0, 41):
        x = i * W / 40
        ctx.line_to(x, level + 10 * math.sin(x / 70 + t * 2.4) + 5 * math.sin(x / 31 - t * 3.1))
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35 * alpha)
    ctx.set_line_width(4)
    for i in range(0, 41):
        x = i * W / 40
        y = level + 10 * math.sin(x / 70 + t * 2.4) + 5 * math.sin(x / 31 - t * 3.1)
        ctx.line_to(x, y) if i else ctx.move_to(x, y)
    ctx.stroke()


def falling_tears(ctx, t, x, y0, y1, n, alpha, rate=1.2, r=10, c=None):
    c = c or hexc("#BFD8F2")
    for k in range(n):
        u = (t * rate + k / n) % 1.0
        tear(ctx, x + 6 * math.sin(k * 2.1), lerp(y0, y1, ein(u)), r, c, alpha * (1 - seg(u, 0.85, 1.0)))


def ripples(ctx, cx, cy, t, t0, alpha, c=(0.85, 0.92, 1.0), n=3, speed=0.8, rmax=420, flat=0.3):
    for k in range(n):
        u = (t - t0) * speed - k * 0.3
        if 0 <= u < 1:
            ctx.set_source_rgba(*c, alpha * (1 - u))
            ctx.set_line_width(5)
            ctx.save()
            ctx.translate(cx, cy)
            ctx.scale(1, flat)
            ctx.arc(0, 0, 60 + rmax * u, 0, 2 * math.pi)
            ctx.restore()
            ctx.stroke()


def shadow_foes(ctx, t, press, alpha=1.0):
    """Dark figures with spears pressing in from both edges."""
    if alpha <= 0.01:
        return
    for i, (side, dx, s) in enumerate([(-1, 0, 1.1), (1, 0, 1.15), (-1, 150, 0.85), (1, 160, 0.9)]):
        x = (W / 2 + side * (lerp(700, 380, press) + dx))
        sway = 6 * math.sin(t * 2 + i)
        Q.person(ctx, x + sway, FLOOR_Y + 40, s, hexc("#0F1220"), 0, 0, 0, 0.2, alpha=alpha * 0.92)
        P.spear(ctx, x - side * 60 * s + sway, FLOOR_Y + 40, 430 * s, hexc("#0F1220")[:3] + (alpha * 0.92,))


def paper_slip(ctx, cx, cy, w, h, rot, alpha, text=None, reveal=1.0):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.set_source_rgba(0, 0, 0, 0.18 * alpha)
    rounded(ctx, -w / 2 + 8, -h / 2 + 10, w, h, 10)
    ctx.fill()
    ctx.set_source_rgba(*col("cream2", alpha))
    # torn right edge
    ctx.move_to(-w / 2, -h / 2)
    ctx.line_to(w / 2 - 10, -h / 2)
    rr = random.Random(5)
    n = 8
    for k in range(n + 1):
        ctx.line_to(w / 2 - 10 + rr.uniform(-14, 14), -h / 2 + h * k / n)
    ctx.line_to(-w / 2, h / 2)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    if text:
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(rot)
        s = text_surf(text, F_SERIF_I, 50, "#3B2A1E")
        sw, sh = s.get_width(), s.get_height()
        ctx.rectangle(-w / 2 + 20, -sh / 2, (sw) * reveal, sh)
        ctx.clip()
        ctx.set_source_surface(s, -w / 2 + 20, -sh / 2)
        ctx.paint_with_alpha(alpha)
        ctx.restore()


def dawn_sky(ctx, k):
    g = cairo.LinearGradient(0, 0, 0, 1300)
    g.add_color_stop_rgba(0, *lerpc(IND, hexc("#F3D9B0"), k))
    g.add_color_stop_rgba(0.6, *lerpc(IND2, hexc("#F2B98A"), k))
    g.add_color_stop_rgba(1, *lerpc(IND3, hexc("#E89466"), k))
    ctx.set_source(g)
    ctx.paint()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: a giant tear lands; pull back to a figure crying in bed at night."""
    t = lt
    night_room(ctx, t, moon_p=0.62)
    tallies(ctx, 0, 0, 0)
    ctx.save()
    pull = ease(seg(lt, 0.35, 1.6))
    cam(ctx, 330, 1060, lerp(2.4, 1.0, pull))
    bed(ctx, 400, FLOOR_Y, 1.0, wet=0.15)
    lying(ctx, 420, FLOOR_Y - 175, 1.0, col("dark"), 1.0, 1.0, sob=1.0, t=t)
    falling_tears(ctx, t, 230, FLOOR_Y - 205, FLOOR_Y - 175, 3, 0.85 * ease(seg(lt, 0.8, 1.2)), 1.4, 7)
    ctx.restore()
    # giant tear drops into frame and splashes at the first frame
    drop = seg(lt, -0.2, 0.12)
    if lt < 0.9:
        ty = lerp(-200, 860, ein(drop))
        tear(ctx, 540, ty, 120 * (1 - 0.6 * seg(lt, 0.12, 0.5)), hexc("#BFD8F2"), 1 - seg(lt, 0.12, 0.45))
        if lt >= 0.12:
            sp = eout(seg(lt, 0.12, 0.8))
            for i in range(12):
                a = math.pi + i * math.pi / 11
                tear(ctx, 540 + math.cos(a) * 330 * sp, 900 + math.sin(a) * 260 * sp + 200 * sp * sp, 16 * (1 - sp),
                     hexc("#BFD8F2"), 1 - sp)
            ripples(ctx, 540, 940, lt, 0.12, 0.8, n=2, speed=1.6, rmax=600)
    kword(ctx, "ANYONE?", t, T_ANYONE - 0.05, 540, 240, 150, "#CFE0F5", B2 - T_ANYONE)
    grade(ctx, cool=0.25)


def scene2(ctx, lt):
    """Title card that rips open on 'raw'."""
    t = lt + B2
    night_room(ctx, t, moon_p=0.66)
    rip = eout(seg(t, T_RAW - 0.05, T_RAW + 0.35))
    for side in (-1, 1):
        ctx.save()
        ctx.translate(side * 360 * rip, 0)
        ctx.rotate(side * 0.05 * rip)
        ctx.save()
        rr = random.Random(9)
        ctx.move_to(540, 180)
        pts = [(540 + rr.uniform(-30, 30), 180 + k * 1000 / 14) for k in range(15)]
        if side < 0:
            ctx.move_to(90, 180)
            for x, y in pts:
                ctx.line_to(x, y)
            ctx.line_to(90, 1180)
        else:
            ctx.move_to(990, 180)
            for x, y in pts:
                ctx.line_to(x, y)
            ctx.line_to(990, 1180)
        ctx.close_path()
        ctx.clip()
        pop = back_out(seg(lt, -0.05, 0.3))
        ctx.translate(540, 680)
        ctx.scale(max(0.01, pop), max(0.01, pop))
        ctx.translate(-540, -680)
        ctx.set_source_rgba(0, 0, 0, 0.25)
        rounded(ctx, 100, 194, 900, 1000, 30)
        ctx.fill()
        ctx.set_source_rgba(*col("cream2"))
        rounded(ctx, 90, 180, 900, 1000, 30)
        ctx.fill()
        ctx.set_source_rgba(*col("gold"))
        ctx.set_line_width(6)
        rounded(ctx, 90, 180, 900, 1000, 30)
        ctx.stroke()
        draw_text(ctx, "PSALM 6", F_SERIF, 150, "#3B2A1E", 540, 440, ease(seg(t, T_PSALM - 0.2, T_PSALM + 0.2)))
        ctx.set_source_rgba(*col("gold"))
        ctx.rectangle(440, 545, 200, 6)
        ctx.fill()
        draw_text(ctx, "A prayer of David", F_SERIF_I, 64, "#6E5039", 540, 640, ease(seg(t, T_PRAYER1 - 0.1, T_PRAYER1 + 0.3)))
        # tear stains on the page
        for i, (x, y, r) in enumerate([(360, 820, 34), (690, 900, 28), (520, 1010, 40)]):
            a = ease(seg(t, T_DAVID1 - 0.2 + i * 0.15, T_DAVID1 + 0.2 + i * 0.15))
            ctx.set_source_rgba(0.55, 0.65, 0.8, 0.28 * a)
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()
        ctx.restore()
        ctx.restore()
    kword(ctx, "RAW", t, T_RAW - 0.03, 540, 690, 230, "#E07A5F", B3 - T_RAW + 0.1)


def scene3(ctx, lt):
    """Worn out from groaning; every night; the bed floods with tears."""
    t = lt + B3
    nights = ease(seg(t, T_EVERY - 0.2, T_FLOODS + 0.4))
    night_room(ctx, t, nights=nights, moon_p=0.66)
    tallies(ctx, lerp(0, 11, nights), 90, 300, ease(seg(t, T_EVERY - 0.3, T_EVERY)))
    flood = ease(seg(t, T_FLOODS - 0.2, T_TEARS1 + 0.4))
    level = lerp(H + 40, FLOOR_Y - 150, flood)
    bed(ctx, 430, FLOOR_Y, 1.0, wet=0.3 + 0.6 * flood)
    slumped = 1 - ease(seg(t, T_NIGHT - 0.3, T_NIGHT + 0.2))
    if slumped > 0.01:
        sitting(ctx, 640, FLOOR_Y - 120, 1.15, col("dark"), 1.0, slumped)
        # groans: wobbly sound lines from the head
        for k in range(3):
            u = ((t - T_WORN) * 0.9 - k * 0.3)
            if 0 <= u < 1:
                ctx.set_source_rgba(0.8, 0.86, 1.0, 0.6 * (1 - u) * slumped)
                ctx.set_line_width(5)
                ctx.arc(700, FLOOR_Y - 370, 60 + 200 * u, math.radians(-150), math.radians(-30))
                ctx.stroke()
    ly = ease(seg(t, T_NIGHT - 0.3, T_NIGHT + 0.2))
    if ly > 0.01:
        lying(ctx, 450, FLOOR_Y - 175, 1.0, col("dark"), 1.0, ly, sob=1.0, t=t)
        falling_tears(ctx, t, 260, FLOOR_Y - 205, FLOOR_Y - 172, 5, ly, 2.0, 8)
        # tears spill over the mattress edge
        for k in range(6):
            u = (t * 1.6 + k / 6) % 1.0
            tear(ctx, 140 + 20 * k, lerp(FLOOR_Y - 150, FLOOR_Y + 20, ein(u)), 7, hexc("#BFD8F2"),
                 ly * ease(seg(t, T_FLOODS - 0.4, T_FLOODS)) * (1 - u))
    water(ctx, t, level, 1.0)
    if flood > 0.2:
        ripples(ctx, 260, level + 10, t, T_TEARS1 - 0.2, 0.6, n=3, speed=0.6, rmax=360, flat=0.18)
    P.tag(ctx, "Psalm 6:6", 230, 200, seg(t, T_EVERY - 0.1, T_EVERY + 0.3), 1.0, 270)
    kword(ctx, "FLOODS", t, T_FLOODS - 0.03, 540, 560, 140, "#9FD3DB", B4 - T_FLOODS)
    grade(ctx, cool=0.3, desat=0.2)


def scene4(ctx, lt):
    """Bones ache, soul shaken, enemies pressing in."""
    t = lt + B4
    R.bg(ctx, hexc("#151A2C"))
    g = cairo.RadialGradient(540, 760, 40, 540, 760, 900)
    g.add_color_stop_rgba(0, *IND2[:3], 1)
    g.add_color_stop_rgba(1, *hexc("#151A2C")[:3], 1)
    ctx.set_source(g)
    ctx.paint()
    sk = ease(seg(t, T_SHAKEN - 0.15, T_SHAKEN + 0.1)) * (1 - 0.6 * ease(seg(t, T_ENEMIES, T_LET + 0.4)))
    jx, jy = 12 * sk * math.sin(t * 57), 8 * sk * math.sin(t * 71)
    cx, base = 540 + jx, 1130 + jy
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(1.9, 1.9)
    ctx.translate(-cx, -base)
    Q.person(ctx, cx, base, 1.0, hexc("#0D1020"), 0.7, 0, 0, 0.1)
    # x-ray bones that glow and ache
    bn = ease(seg(t, T_BONES - 0.25, T_BONES + 0.1))
    ache = 0.5 + 0.5 * math.sin(t * 10) * ease(seg(t, T_ACHE - 0.1, T_ACHE + 0.2))
    if bn > 0:
        bc = lerpc(hexc("#C9D6F2"), hexc("#E0805F"), 0.6 * ease(seg(t, T_ACHE - 0.1, T_ACHE + 0.2)))
        ctx.set_source_rgba(*bc[:3], 0.85 * bn * (0.7 + 0.3 * ache))
        ctx.set_line_width(5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(cx + 4, base - 130)
        ctx.line_to(cx, base - 20)
        ctx.stroke()
        for k in range(5):
            y = base - 118 + k * 15
            for sx in (-1, 1):
                ctx.move_to(cx, y)
                ctx.curve_to(cx + sx * 18, y - 6, cx + sx * 30, y + 2, cx + sx * 32, y + 12)
                ctx.stroke()
        ctx.arc(cx + 10, base - 158, 20, 0, 2 * math.pi)
        ctx.stroke()
    # the soul: a small light inside, trembling
    so = ease(seg(t, T_SOUL - 0.25, T_SOUL + 0.1))
    if so > 0:
        fl = 0.7 + 0.3 * math.sin(t * 23) * sk
        lg = cairo.RadialGradient(cx, base - 95, 2, cx, base - 95, 60)
        lg.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.95 * so * fl)
        lg.add_color_stop_rgba(1, 1, 0.8, 0.5, 0)
        ctx.set_source(lg)
        ctx.arc(cx, base - 95, 60, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()
    press = ease(seg(t, T_ENEMIES - 0.3, T_LET + 0.5))
    shadow_foes(ctx, t, press, ease(seg(t, T_ENEMIES - 0.35, T_ENEMIES)))
    P.tag(ctx, "Psalm 6:2-3", 540, 190, seg(t, T_BONES - 0.1, T_BONES + 0.3), 1 - ease(seg(t, T_ENEMIES - 0.3, T_ENEMIES)), 300)
    P.tag(ctx, "Psalm 6:7", 540, 190, seg(t, T_ENEMIES - 0.1, T_ENEMIES + 0.3), 1.0, 260)
    draw_text(ctx, "bones", F_SERIF_I, 70, "#C9D6F2", 250, 420, ease(seg(t, T_BONES - 0.2, T_BONES + 0.2)) * (1 - ease(seg(t, T_ENEMIES - 0.4, T_ENEMIES))))
    draw_text(ctx, "soul", F_SERIF_I, 70, "#E3B04B", 830, 420, ease(seg(t, T_SOUL - 0.2, T_SOUL + 0.2)) * (1 - ease(seg(t, T_ENEMIES - 0.4, T_ENEMIES))))
    kword(ctx, "SHAKEN", t, T_SHAKEN - 0.03, 540 + jx, 330 + jy, 160, "#CFE0F5", T_ENEMIES - T_SHAKEN - 0.3)
    grade(ctx, desat=0.35, cool=0.2)


def scene5(ctx, lt):
    """'Then, near the end, everything turns': ten verse dots, the turn at verse 8."""
    t = lt + B5
    turn = ease(seg(t, T_TURNS - 0.1, T_TURNS + 0.5))
    ctx.push_group()
    R.bg(ctx, lerpc(hexc("#1B2036"), col("cream"), turn))
    rays(ctx, 540, 760, 0, 2 * math.pi, 16, 1100, 0.9 * turn, t * 0.5)
    ctx.pop_group_to_source()
    ctx.paint()
    draw_text(ctx, "PSALM 6", F_SERIF, 64, "#FBF6EC" if turn < 0.5 else "#3B2A1E", 540, 300, ease(seg(lt, 0.0, 0.3)))
    # path of verses
    y = 760
    x0, x1 = 120, 960
    ctx.set_line_width(8)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    prog = ease(seg(t, T_THEN - 0.2, T_END + 0.1))
    ctx.set_source_rgba(*lerpc(hexc("#5A648F"), col("brown2"), turn))
    ctx.move_to(x0, y)
    ctx.line_to(lerp(x0, x1, prog), y)
    ctx.stroke()
    for v in range(1, 11):
        x = lerp(x0, x1, (v - 1) / 9)
        on = clamp((prog * 9 + 1 - v) * 3)
        if on <= 0:
            continue
        lit = v >= 8
        c = lerpc(hexc("#7C86B4"), col("gold2") if lit else col("brown2"), turn)
        r = 26 if not (v == 8) else 26 + 22 * turn + 6 * turn * math.sin(t * 6)
        if v == 8 and turn > 0:
            gg = cairo.RadialGradient(x, y, 5, x, y, 200 * turn)
            gg.add_color_stop_rgba(0, 1, 0.92, 0.65, 0.8 * turn)
            gg.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
            ctx.set_source(gg)
            ctx.arc(x, y, 200 * turn, 0, 2 * math.pi)
            ctx.fill()
        ctx.set_source_rgba(*c[:3], on)
        ctx.arc(x, y, r * back_out(clamp(on)), 0, 2 * math.pi)
        ctx.fill()
        draw_text(ctx, str(v), F_SERIF, 34, "#FBF6EC" if turn < 0.5 else "#3B2A1E", x, y + 70, on * 0.85)
    # marker that travels along the verses
    mx = lerp(x0, lerp(x0, x1, 7 / 9), prog)
    ctx.set_source_rgba(*lerpc(hexc("#BFD8F2"), col("rust"), turn))
    ctx.move_to(mx, y - 52)
    ctx.line_to(mx - 22, y - 95)
    ctx.line_to(mx + 22, y - 95)
    ctx.close_path()
    ctx.fill()
    draw_text(ctx, "near the end", F_SERIF_I, 62, "#CFE0F5" if turn < 0.5 else "#6E5039", 540, 560,
              ease(seg(t, T_END - 0.3, T_END + 0.1)))
    draw_text(ctx, "verse 8", F_SERIF_I, 58, "#A8741A", lerp(x0, x1, 7 / 9) - 40, 960, turn)
    # a cool-to-warm page wipe on the turn
    wipe = seg(t, T_TURNS - 0.15, T_TURNS + 0.35)
    if 0 < wipe < 1:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        wx = lerp(-200, W + 200, eout(wipe))
        lg = cairo.LinearGradient(wx - 180, 0, wx + 180, 0)
        lg.add_color_stop_rgba(0, 1, 0.85, 0.5, 0)
        lg.add_color_stop_rgba(0.5, 1, 0.9, 0.65, 0.6)
        lg.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(lg)
        ctx.paint()
        ctx.restore()
    kword(ctx, "EVERYTHING TURNS", t, T_TURNS - 0.05, 540, 1150, 84, "#E3B04B", B6 - T_TURNS + 0.1)


def scene6(ctx, lt):
    """Verse card 6:8-9; tears rise as light."""
    t = lt + B6
    R.bg(ctx, col("cream"))
    g = cairo.LinearGradient(0, 0, 0, 1300)
    g.add_color_stop_rgba(0, *col("cream2"))
    g.add_color_stop_rgba(1, *col("gold2")[:3], 0.45)
    ctx.set_source(g)
    ctx.paint()
    rays(ctx, 540, -80, math.radians(55), math.radians(125), 10, 1800, 0.8, t * 0.4)
    vc = ease(seg(lt, 0.0, 0.3))
    P.verse_card(ctx, 540, 470, 940, 520, vc, 0.94 + 0.06 * back_out(seg(lt, 0.0, 0.3)))
    P.tag(ctx, "Psalm 6:8-9", 540, 222, seg(lt, 0.1, 0.4), vc, 300)
    hl = ease(seg(t, T_HEARD1 - 0.1, T_HEARD1 + 0.2))
    draw_text(ctx, "“The LORD has", F_SERIF_I, 64, "#3B2A1E", 540, 330, ease(seg(t, T_LORD1 - 0.2, T_LORD1 + 0.2)))
    draw_text(ctx, "heard", F_SERIF, 96, "#A8741A", 540, 420, hl, 0.9 + 0.1 * back_out(seg(t, T_HEARD1 - 0.1, T_HEARD1 + 0.25)))
    draw_text(ctx, "the sound of my weeping.", F_SERIF_I, 58, "#3B2A1E", 540, 510, ease(seg(t, T_SOUND - 0.2, T_SOUND + 0.2)))
    draw_text(ctx, "The LORD accepts my prayer.”", F_SERIF_I, 56, "#6E5039", 540, 610, ease(seg(t, T_ACCEPTS - 0.3, T_ACCEPTS + 0.1)))
    # kneeling figure below, tears rising as golden motes into the light
    Q.person(ctx, 540, 1330, 1.25, col("brown"), 0.3, 0, 0, 0.75, 0.8)
    for k in range(10):
        u = ((t - T_SOUND) * 0.5 + k / 10) % 1.0
        if t < T_SOUND - 0.3:
            continue
        a = ease(seg(t, T_SOUND - 0.3, T_SOUND + 0.3)) * math.sin(math.pi * u)
        x = 540 + 60 * math.sin(k * 1.7 + t * 1.2) * (1 - u)
        y = lerp(1120, 760, u)
        c = lerpc(hexc("#BFD8F2"), col("gold2"), u)
        tear(ctx, x, y, 12 * (1 - 0.5 * u), c, a)
    ripples(ctx, 540, 1080, t, T_WEEPING - 0.1, 0.5, c=(0.85, 0.65, 0.25), n=3, speed=0.5, rmax=380, flat=0.25)
    if t > T_ACCEPTS - 0.2:
        ac = ease(seg(t, T_ACCEPTS - 0.2, T_ACCEPTS + 0.3))
        g2 = cairo.RadialGradient(540, 1180, 10, 540, 1180, 420 * ac)
        g2.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.7)
        g2.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(g2)
        ctx.arc(540, 1180, 420 * ac, 0, 2 * math.pi)
        ctx.fill()
    dust(ctx, t, 0.6, "gold2", 6, -18)


def scene7(ctx, lt):
    """Nothing around him has changed yet; but his tears were heard."""
    t = lt + B7
    night_room(ctx, t, moon_p=0.7)
    tallies(ctx, 11, 90, 300, 1.0)
    bed(ctx, 430, FLOOR_Y, 1.0, wet=0.9)
    lying(ctx, 450, FLOOR_Y - 175, 1.0, col("dark"), 1.0, 1.0, sob=0.2, t=t)
    water(ctx, t, FLOOR_Y - 150, 1.0, gold=0.3 * ease(seg(t, T_TEARS2 - 0.3, T_HEARD2 + 0.3)))
    shadow_foes(ctx, t, 0.75, 0.9 * (1 - 0.35 * ease(seg(t, T_DAVID2, T_HEARD2))))
    draw_text(ctx, "not changed", F_SERIF_I, 66, "#CFE0F5", 540, 200, ease(seg(t, T_CHANGED - 0.2, T_CHANGED + 0.2)))
    draw_text(ctx, "...yet", F_SERIF_I, 66, "#E3B04B", 540, 280, ease(seg(t, T_YET - 0.2, T_YET + 0.2)))
    # a warm column of light on the bed
    li = ease(seg(t, T_DAVID2 - 0.3, T_KNOWS + 0.3))
    if li > 0:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        lg = cairo.LinearGradient(0, 0, 0, FLOOR_Y)
        lg.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.0)
        lg.add_color_stop_rgba(1, 1, 0.82, 0.45, 0.35 * li)
        ctx.set_source(lg)
        ctx.move_to(330, 0)
        ctx.line_to(560, 0)
        ctx.line_to(760, FLOOR_Y)
        ctx.line_to(120, FLOOR_Y)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
        dust(ctx, t, 0.5 * li, "gold2", 4, -10)
    # tears on the bed glint gold
    gl = ease(seg(t, T_TEARS2 - 0.2, T_TEARS2 + 0.3))
    for i, (x, y) in enumerate([(230, FLOOR_Y - 172), (330, FLOOR_Y - 166), (180, FLOOR_Y - 120), (420, FLOOR_Y - 168)]):
        tear(ctx, x, y, 11, lerpc(hexc("#BFD8F2"), col("gold2"), gl), 0.9)
        if gl > 0:
            V.rays(ctx, x, y, 0, 2 * math.pi, 6, 70, gl * (0.6 + 0.4 * math.sin(t * 5 + i)), t)
    kword(ctx, "HEARD", t, T_HEARD2 - 0.03, 540, 640, 200, "#E3B04B", B8 - T_HEARD2)
    grade(ctx, cool=0.25 * (1 - li), warm=0.15 * li)


HEB = "עַד־מָתָי"


def scene8(ctx, lt):
    """Nugget: verse 3, 'ad-matay, 'until when?'"""
    t = lt + B8
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.6, "gold2", 6, -12)
    P.tag(ctx, "Psalm 6:3", 540, 200, seg(t, T_THREE - 0.2, T_THREE + 0.2), 1.0, 260)
    draw_text(ctx, "verse 3", F_SERIF_I, 70, "#DCC59D", 540, 320, ease(seg(t, T_LOOK - 0.1, T_LOOK + 0.3)) * (1 - ease(seg(t, T_HEBREW - 0.2, T_HEBREW + 0.1))))
    draw_text(ctx, "In Hebrew", F_SERIF_I, 60, "#DCC59D", 540, 320, ease(seg(t, T_HEBREW - 0.1, T_HEBREW + 0.3)))
    draw_text(ctx, "“And you, LORD...", F_SERIF_I, 76, "#FBF6EC", 540, 440, ease(seg(t, T_YOU2 - 0.2, T_LORD3 + 0.2)))
    hb = ease(seg(t, T_ADMATAI - 0.5, T_ADMATAI - 0.2))
    reveal = ease(seg(t, T_ADMATAI - 0.45, T_ADMATAI + 0.25))
    rays(ctx, 540, 700, 0, 2 * math.pi, 18, 1100, hb * (0.4 + 0.6 * seg(t, T_ADMATAI, T_ADMATAI + 0.3)), t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 250, 540, 700, reveal, hb, rtl=True)
    sub = ease(seg(t, T_ADMATAI + 0.05, T_ADMATAI + 0.4))
    draw_text(ctx, "‘ad-matay", F_SERIF_I, 92, "#FBF6EC", 540, 920, sub, 0.9 + 0.1 * back_out(seg(t, T_ADMATAI + 0.05, T_ADMATAI + 0.4)))
    un = ease(seg(t, T_UNTIL - 0.15, T_UNTIL + 0.2))
    draw_text(ctx, "“until when?”", F_SERIF_I, 80, "#E3B04B", 540, 1050, un)
    draw_text(ctx, "how long?", F_SERIF_R, 52, "#DCC59D", 540, 1145, ease(seg(t, T_WHEN + 0.1, T_WHEN + 0.5)))


def scene9(ctx, lt):
    """He doesn't even finish the sentence; God still hears it."""
    t = lt + B9
    P.dark_bg(ctx, lt + 1.0, 1.0)
    # the line is written, then stops dead; the quill lifts
    line = "And you, LORD, how long"
    s = text_surf(line, F_SERIF_I, 72, "#FBF6EC")
    sw, sh = s.get_width(), s.get_height()
    write = ease(seg(lt, 0.0, T_FINISH - B9 + 0.35))
    x0 = 540 - sw / 2
    ctx.save()
    ctx.rectangle(x0, 560 - sh / 2, sw * write, sh)
    ctx.clip()
    ctx.set_source_surface(s, x0, 560 - sh / 2)
    ctx.paint()
    ctx.restore()
    stop = ease(seg(t, T_FINISH + 0.3, T_FINISH + 0.6))
    # broken-off dash and the empty space after it
    if stop > 0:
        ctx.set_source_rgba(*col("gold2", stop))
        ctx.set_line_width(7)
        ctx.move_to(x0 + sw + 6, 570)
        ctx.line_to(x0 + sw + 6 + 70 * stop, 570)
        ctx.stroke()
        ctx.set_source_rgba(0.85, 0.75, 0.6, 0.6 * stop)
        ctx.set_dash([10, 18])
        ctx.set_line_width(4)
        ctx.move_to(x0 + sw + 90, 600)
        ctx.line_to(x0 + sw + 90 + 160 * stop, 600)
        ctx.stroke()
        ctx.set_dash([])
    qx = x0 + sw * write + 30 - 0 * stop
    qy = 500 - 120 * ein(stop)
    ctx.save()
    ctx.translate(qx, qy)
    ctx.rotate(-0.6)
    ctx.set_source_rgba(*col("cream2", 1 - 0.6 * stop))
    ctx.move_to(0, 0)
    ctx.curve_to(40, -80, 30, -180, 0, -230)
    ctx.curve_to(-30, -180, -40, -80, 0, 0)
    ctx.fill()
    ctx.restore()
    # an ink drop falls where the sentence stopped
    if stop > 0:
        u = seg(t, T_FINISH + 0.5, T_FINISH + 1.1)
        tear(ctx, x0 + sw + 10, lerp(600, 760, ein(u)), 12, col("gold2"), 1 - seg(u, 0.85, 1.0))
    draw_text(ctx, "unfinished", F_SERIF_I, 64, "#DCC59D", 540, 300, ease(seg(t, T_SENTENCE1 - 0.3, T_SENTENCE1)) * (1 - 0.5 * ease(seg(t, T_GOD1 - 0.2, T_GOD1))))
    # God still hears: rings of light rising from the gap
    he = ease(seg(t, T_GOD1 - 0.2, T_HEARS + 0.2))
    rays(ctx, 540, -60, math.radians(55), math.radians(125), 10, 1500, 0.9 * he, t * 0.4)
    for k in range(4):
        u = (t - T_GOD1) * 0.7 - k * 0.22
        if 0 <= u < 1 and he > 0:
            ctx.set_source_rgba(1, 0.88, 0.55, 0.6 * (1 - u) * he)
            ctx.set_line_width(6)
            ctx.arc(x0 + sw + 40, 770, 40 + 380 * u, math.radians(180), math.radians(360))
            ctx.stroke()
    kword(ctx, "STILL HEARD", t, T_HEARS - 0.03, 540, 1020, 130, "#E3B04B", B10 - T_HEARS)


def scene10(ctx, lt):
    """Close: dawn; give God the half sentence and the tears. End card."""
    t = lt + B10
    k = ease(seg(t, B10, T_YOUR))
    dawn_sky(ctx, k)
    # hills and a low sun
    sy = lerp(1320, 1060, ease(seg(t, B10, DUR)))
    sg = cairo.RadialGradient(540, sy, 40, 540, sy, 560)
    sg.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.9 * k)
    sg.add_color_stop_rgba(1, 1, 0.7, 0.4, 0)
    ctx.set_source(sg)
    ctx.arc(540, sy, 560, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*col("gold2", k))
    ctx.arc(540, sy, 100, 0, 2 * math.pi)
    ctx.fill()
    V.hills(ctx, 1190, 50, lerpc(hexc("#2A3050"), hexc("#B8604A"), k), 0, 61)
    V.hills(ctx, 1250, 40, lerpc(hexc("#1E2338"), hexc("#8F4E3A"), k), 0, 62, 1.3)
    ctx.set_source_rgba(*lerpc(hexc("#161A2A"), hexc("#7A4A35"), k))
    ctx.rectangle(0, 1300, W, H)
    ctx.fill()
    rays(ctx, 540, sy, math.radians(190), math.radians(350), 12, 1500, 0.7 * k, t * 0.4)
    # kneeling figure on the hill
    Q.person(ctx, 540, 1300, 1.15, col("dark"), 0.25, 0, 0, 0.55 + 0.3 * ease(seg(t, T_GIVE1 - 0.2, T_GIVE1 + 0.3)), 0.8)
    # "if the words won't come": dots that fail to become words
    nw = ease(seg(t, T_WORDS - 0.2, T_WORDS + 0.2)) * (1 - ease(seg(t, T_GIVE1 - 0.2, T_GIVE1)))
    for i in range(3):
        a = nw * (0.5 + 0.5 * math.sin(t * 6 - i))
        ctx.set_source_rgba(*col("cream2", a))
        ctx.arc(500 + i * 40, 1040, 10, 0, 2 * math.pi)
        ctx.fill()
    # the half sentence on a torn slip rises into the light
    up = ein(seg(t, T_GIVE1 - 0.1, T_TEARS3 + 0.4))
    sa = ease(seg(t, T_GIVE1 - 0.2, T_GIVE1 + 0.1)) * (1 - seg(up, 0.85, 1.0))
    paper_slip(ctx, 540, lerp(1060, 640, up), 400, 96, -0.05 + 0.08 * math.sin(t * 2), sa, "And you, LORD...",
               ease(seg(t, T_HALF - 0.2, T_SENTENCE2 + 0.2)))
    # a tear follows it up, turning gold
    tu = ein(seg(t, T_TEARS3 - 0.3, T_YOUR + 0.2))
    ta = ease(seg(t, T_GIVE2 - 0.1, T_GIVE2 + 0.2)) * (1 - seg(tu, 0.85, 1.0))
    tear(ctx, 540, lerp(1120, 700, tu), 22, lerpc(hexc("#BFD8F2"), col("gold2"), tu), ta)
    # end card (doubles as the cover)
    end = ease(seg(t, T_YOUR - 0.35, T_YOUR))
    draw_text(ctx, "PSALM 6", F_SERIF, 54, "#FBF6EC", 540, 340, end, stroke=3, stroke_color="#5E3424")
    ctx.set_source_rgba(*col("cream2", end))
    ctx.rectangle(490, 395, 100, 4)
    ctx.fill()
    draw_text(ctx, "Your tears", F_SERIF, 120, "#FBF6EC", 540, 520, end, 0.92 + 0.08 * back_out(seg(t, T_YOUR - 0.35, T_YOUR)), stroke=4, stroke_color="#5E3424")
    hd = ease(seg(t, T_HEARD3 - 0.3, T_HEARD3 + 0.05))
    draw_text(ctx, "are heard.", F_SERIF, 120, "#FFE3A3", 540, 665, hd, 0.92 + 0.08 * back_out(seg(t, T_HEARD3 - 0.3, T_HEARD3 + 0.1)), stroke=4, stroke_color="#5E3424")
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


SCENES = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5),
          (B6, B7, scene6), (B7, B8, scene7), (B8, B9, scene8), (B9, B10, scene9), (B10, DUR + 1, scene10)]
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
        os.makedirs("/home/claude/psalm6/stills", exist_ok=True)
        for t in map(float, sys.argv[2:]):
            render_frame(t).write_to_png(f"/home/claude/psalm6/stills/t{t:05.2f}.png")
    elif sys.argv[1] == "times":
        for k, v in sorted(((k, v) for k, v in globals().items() if k.startswith(("T_", "B"))
                            and isinstance(v, float)), key=lambda x: x[1]):
            print(f"{k:12s} {v:6.2f}")
    else:
        video(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
