"""Psalm 2 Short. Scenes are timed directly to the ElevenLabs voiceover (vomap.json).
Reuses the art library (render.py) and effects (render_v2.py) from the Psalm 1 build."""
import sys, os, math, random, json, re, subprocess
sys.path.insert(0, "/home/claude/psalm1")
import numpy as np
import cairo
import render as R
import render_v2 as V
from render import (W, H, FPS, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, draw_surf,
                    text_surf, rounded, cam, F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword
F_GREEK = "/home/claude/psalm1/fonts/noto-serif/files/noto-serif-greek-700-normal.woff"

MAP = json.load(open("/home/claude/psalm2/vomap.json"))
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


T_OUT = wt("out"); T_CONTROL = wt("control")
T_RAGING = wt("raging"); T_RULERS = wt("rulers"); T_BREAK = wt("break"); T_KING1 = wt("king", 1)
T_DAVID = wt("david"); T_HEAVEN = wt("heaven"); T_WORRIED = wt("worried"); T_LAUGHS = wt("laughs")
T_SPEAKS = wt("speaks"); T_KING2 = wt("king", 2); T_HILL = wt("hill")
T_KEY = wt("key"); T_ANOINTED = wt("anointed"); T_MASHIACH = wt("mashiach"); T_MESSIAH = wt("messiah")
T_CHRISTOS = wt("christos"); T_CHRIST = wt("christ"); T_SON = wt("son"); T_JESUS = wt("jesus", 1)
T_CHAOS = wt("chaos"); T_CHARGE = wt("charge"); T_BEGAN = wt("began"); T_BLESSED = wt("blessed", 1)
T_REFUGE = wt("refuge"); T_NEWS = wt("news"); T_LOUD = wt("loud"); T_TAKE = wt("take", 2); T_KING4 = wt("king", 4)
T_RAGES = wt("rages"); T_REIGNS = wt("reigns")

# scene boundaries (absolute seconds)
B1, B2, B3, B4, B5, B6, B7, B8 = 0.0, 3.75, 11.75, 14.35, 22.1, 37.25, 48.15, 51.75

# ---------------------------------------------------------------- global camera events
ZOOMS = [(0.1, 0.10), (T_RAGING, 0.10), (T_BREAK, 0.09), (T_KING2, 0.08), (T_MASHIACH, 0.12),
         (T_CHRISTOS, 0.10), (T_CHRIST, 0.06), (T_JESUS, 0.08), (T_BLESSED, 0.10), (T_REFUGE, 0.04),
         (T_REIGNS, 0.07)]
SHAKES = [(0.1, 16, 0.6), (1.0, 4, 2.6), (T_RAGING, 12, 0.6), (7.0, 4, 4.0), (T_BREAK, 14, 0.5),
          (T_KING2, 8, 0.4), (T_MASHIACH, 12, 0.5), (T_CHRISTOS, 9, 0.4), (T_CHAOS, 8, 1.2),
          (T_BLESSED, 8, 0.4), (T_LOUD - 0.6, 7, 1.6), (T_REIGNS, 5, 0.4)]
FLASHES = [(0.1, (1, 1, 1), 0.45, 0.3), (T_BREAK, (1, 0.95, 0.85), 0.5, 0.3), (T_KING2, (1, 0.88, 0.55), 0.45, 0.45),
           (T_MASHIACH, (1, 0.85, 0.5), 0.3, 0.4), (T_JESUS, (1, 1, 1), 0.4, 0.45), (T_BLESSED, (1, 0.9, 0.6), 0.35, 0.35),
           (T_REIGNS, (1, 1, 1), 0.55, 0.4)]
BLUR = [(B2 - 0.35, B2 + 0.15), (B3 - 0.3, B3 + 0.1), (B4 - 0.1, B4 + 0.5), (B5 - 0.3, B5 + 0.1),
        (B6 - 0.3, B6 + 0.1), (T_BEGAN - 2.7, T_BEGAN - 2.25), (B7 - 0.3, B7 + 0.1), (T_TAKE - 0.05, T_TAKE + 0.6),
        (B8 - 0.3, B8 + 0.1)]
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


# ---------------------------------------------------------------- art helpers
def crown(ctx, cx, cy, s, alpha=1.0, glow=0.0, colr="gold"):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    if glow > 0:
        g = cairo.RadialGradient(0, -20, 10, 0, -20, 260)
        g.add_color_stop_rgba(0, *col("gold2")[:3], 0.55 * glow * alpha)
        g.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(g)
        ctx.arc(0, -20, 260, 0, 2 * math.pi)
        ctx.fill()
    pts = [(-90, 30), (-90, -34), (-62, -2), (-44, -66), (-22, -6), (0, -84), (22, -6), (44, -66), (62, -2), (90, -34), (90, 30)]
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgba(*col(colr, alpha))
    ctx.fill_preserve()
    ctx.set_source_rgba(*col("brown", 0.85 * alpha))
    ctx.set_line_width(5)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    ctx.set_source_rgba(*col("gold2", alpha))
    ctx.rectangle(-90, 8, 180, 22)
    ctx.fill()
    for x, y in [(-90, -34), (-44, -66), (0, -84), (44, -66), (90, -34)]:
        ctx.set_source_rgba(*col("cream2", alpha))
        ctx.arc(x, y, 9, 0, 2 * math.pi)
        ctx.fill()
    for x in (-50, 0, 50):
        ctx.set_source_rgba(*col("rust", alpha))
        ctx.arc(x, 19, 8, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()


def hill_path(ctx, cx, base, peak, hw):
    ctx.move_to(cx - hw, base)
    ctx.curve_to(cx - hw * 0.55, base, cx - hw * 0.32, peak, cx, peak)
    ctx.curve_to(cx + hw * 0.32, peak, cx + hw * 0.55, base, cx + hw, base)
    ctx.close_path()


def globe(ctx, cx, cy, r, rot, tilt=0.0, alpha=1.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(tilt)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgba(*col("water", alpha))
    ctx.paint()
    lands = [(0.0, 0.5, 0.55, 0.32), (0.9, 0.1, 0.4, 0.45), (2.0, -0.35, 0.5, 0.3), (2.9, 0.4, 0.35, 0.25),
             (3.9, -0.1, 0.45, 0.5), (5.0, 0.25, 0.5, 0.35), (5.6, -0.55, 0.3, 0.2)]
    for lon, lat, w, h in lands:
        a = lon + rot
        c = math.cos(a)
        if c < -0.15:
            continue
        x = r * math.cos(lat) * math.sin(a)
        y = -r * math.sin(lat)
        sx = max(0.05, c)
        for k, (ox, oy, rr) in enumerate([(0, 0, 1.0), (0.5, 0.3, 0.7), (-0.45, -0.25, 0.65), (0.2, -0.5, 0.5)]):
            ctx.save()
            ctx.translate(x + ox * w * r * 0.5 * sx, y + oy * h * r * 0.5)
            ctx.scale(sx, 1)
            ctx.set_source_rgba(*col("sand" if k % 2 == 0 else "leaf2", alpha))
            ctx.arc(0, 0, rr * w * r * 0.45, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
    g = cairo.RadialGradient(-r * 0.35, -r * 0.35, r * 0.1, 0, 0, r * 1.05)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.18 * alpha)
    g.add_color_stop_rgba(0.6, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.1, 0.06, 0.04, 0.45 * alpha)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()
    ctx.save()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.set_source_rgba(*col("brown", alpha))
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()


def clouds(ctx, y, t, color, alpha, speed=20, seed=1, scale=1.0):
    if alpha <= 0.01:
        return
    r = random.Random(seed)
    ctx.set_source_rgba(*color[:3], alpha)
    for i in range(14):
        x = (r.uniform(-200, W + 200) + t * speed * r.uniform(0.6, 1.4)) % (W + 400) - 200
        yy = y + r.uniform(-60, 60) * scale
        rr = r.uniform(70, 150) * scale
        ctx.arc(x, yy, rr, 0, 2 * math.pi)
        ctx.fill()


def storm_sky(ctx, t, k=1.0):
    g = cairo.LinearGradient(0, 0, 0, 1100)
    g.add_color_stop_rgba(0, *lerpc(col("cream"), hexc("#3A2A22"), k))
    g.add_color_stop_rgba(1, *lerpc(col("cream"), hexc("#8A5238"), k))
    ctx.set_source(g)
    ctx.paint()
    clouds(ctx, 120, t, hexc("#2A1D14"), 0.55 * k, 26, 3)
    clouds(ctx, 260, t, hexc("#4E3328"), 0.5 * k, -18, 4, 0.8)


def spear(ctx, x, y, h, c):
    ctx.set_source_rgba(*c)
    ctx.set_line_width(7)
    ctx.move_to(x, y)
    ctx.line_to(x, y - h)
    ctx.stroke()
    ctx.move_to(x - 14, y - h + 6)
    ctx.line_to(x, y - h - 38)
    ctx.line_to(x + 14, y - h + 6)
    ctx.close_path()
    ctx.fill()


def banner(ctx, x, y, h, c, t, ph, fc):
    ctx.set_source_rgba(*c)
    ctx.set_line_width(6)
    ctx.move_to(x, y)
    ctx.line_to(x, y - h)
    ctx.stroke()
    ctx.set_source_rgba(*fc)
    ctx.move_to(x, y - h)
    for i in range(9):
        xx = x + i * 12
        ctx.line_to(xx, y - h + 8 * math.sin(t * 7 + ph + i * 0.7))
    for i in range(8, -1, -1):
        xx = x + i * 12
        ctx.line_to(xx, y - h + 60 + 8 * math.sin(t * 7 + ph + i * 0.7))
    ctx.close_path()
    ctx.fill()


CROWD_ROWS = [(1150, 0.7, 13, 11, 0.55), (1260, 0.85, 11, 12, 0.75), (1390, 1.0, 9, 13, 1.0)]


def crowd(ctx, t, agit=1.0, rise=1.0, alpha=1.0, rows=CROWD_ROWS, tone=1.0):
    if alpha <= 0.01 or rise <= 0:
        return
    ctx.push_group()
    for base, s, n, seed, shade in rows:
        r = random.Random(seed)
        c = lerpc(hexc("#6E4433"), hexc("#2A1D14"), shade * tone)
        for i in range(n):
            x = (i + 0.5) * W / n + r.uniform(-25, 25)
            ph = r.uniform(0, 6.28)
            kind = r.choice(["fist", "fist", "spear", "banner"])
            up = (1 - rise) * 400
            bob = agit * 10 * math.sin(t * 9 + ph)
            y = base + up - abs(bob)
            arms = clamp(0.4 + 0.6 * agit * (0.5 + 0.5 * math.sin(t * 6 + ph)))
            R.figure(ctx, x, y, s, c, arms)
            if kind == "spear":
                spear(ctx, x + 70 * s, y - 120 * s, 260 * s, c)
            elif kind == "banner":
                banner(ctx, x - 60 * s, y - 110 * s, 300 * s, c, t, ph, col("rust", 0.9))
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


def ruler(ctx, x, y, s, c, lean=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(lean)
    R.figure(ctx, 0, 0, s, c, 0.25)
    crown(ctx, 0, -235 * s, 0.33 * s, 1.0, 0, "dry")
    ctx.restore()


def chain(ctx, x0, x1, y, brk, t, alpha=1.0):
    n = int((x1 - x0) / 46)
    mid = n // 2
    ctx.save()
    ctx.set_line_width(9)
    for i in range(n):
        x = x0 + i * 46 + 23
        dx = dy = rot = 0
        if brk > 0:
            side = -1 if i < mid else 1
            dist = abs(i - mid + 0.5)
            u = brk
            dx = side * (60 + 30 * dist) * u
            dy = (120 * u * u) * (1 + dist * 0.05) - 40 * u
            rot = side * u * (1 + dist * 0.2)
        ctx.save()
        ctx.translate(x + dx, y + dy)
        ctx.rotate(rot)
        ctx.set_source_rgba(*col("dry" if i % 2 else "sand2", alpha))
        ctx.save()
        if i % 2:
            ctx.scale(1, 0.28)
            ctx.arc(0, 0, 30, 0, 2 * math.pi)
        else:
            ctx.scale(1, 0.62)
            ctx.arc(0, 0, 30, 0, 2 * math.pi)
        ctx.restore()
        ctx.stroke()
        ctx.restore()
    ctx.restore()


def lyre(ctx, cx, cy, s, pluck_u, alpha=1.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*col("brown2", alpha))
    ctx.set_line_width(26)
    for sx in (-1, 1):
        ctx.move_to(sx * 40, 180)
        ctx.curve_to(sx * 170, 150, sx * 190, -40, sx * 120, -200)
        ctx.stroke()
    ctx.set_source_rgba(*col("dry", alpha))
    ctx.set_line_width(22)
    ctx.move_to(-150, -170)
    ctx.line_to(150, -170)
    ctx.stroke()
    rounded(ctx, -80, 150, 160, 70, 20)
    ctx.set_source_rgba(*col("brown2", alpha))
    ctx.fill()
    ctx.set_source_rgba(*col("gold2", alpha))
    ctx.set_line_width(3.5)
    for i in range(7):
        x = -60 + i * 20
        amp = 0
        if pluck_u >= 0:
            amp = 9 * math.exp(-pluck_u * 3) * math.sin(pluck_u * 60 + i)
        ctx.move_to(x * 1.4, -160)
        ctx.curve_to(x * 1.4 + amp, -60, x + amp, 60, x, 150)
        ctx.stroke()
    ctx.restore()


def horn(ctx, x, y, s, rot, alpha=1.0):
    pts = R.bez_pts([(0, 0), (90, -40), (170, 10), (190, 110)], 22)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    for i, (px, py) in enumerate(pts):
        rr = 46 - i * 1.7
        ctx.set_source_rgba(*lerpc(col("cream2"), col("sand2"), i / len(pts))[:3], alpha)
        ctx.arc(px, py, rr, 0, 2 * math.pi)
        ctx.fill()
        if i % 3 == 0:
            ctx.set_source_rgba(*col("dry", 0.7 * alpha))
            ctx.set_line_width(3)
            ctx.arc(px, py, rr, 0, 2 * math.pi)
            ctx.stroke()
    ctx.restore()


def vortex(ctx, cx, cy, r, t, alpha=1.0, k=1.0):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for arm in range(4):
        pts = []
        for i in range(60):
            th = i / 59 * 2.6 * math.pi
            rr = r * (0.08 + 0.92 * i / 59)
            a = th + arm * math.pi / 2 - t * 3.0 * k
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.55))
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.set_source_rgba(*lerpc(hexc("#4E3328"), col("rust"), arm % 2 * 0.6)[:3], alpha * 0.85)
        ctx.set_line_width(max(3, r * 0.07))
        ctx.stroke()
    ctx.restore()


def verse_card(ctx, cx, cy, w, h, alpha=1.0, scale=1.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)
    ctx.set_source_rgba(0, 0, 0, 0.12 * alpha)
    rounded(ctx, -w / 2 + 10, -h / 2 + 14, w, h, 26)
    ctx.fill()
    ctx.set_source_rgba(*col("cream2", alpha))
    rounded(ctx, -w / 2, -h / 2, w, h, 26)
    ctx.fill()
    ctx.set_source_rgba(*col("gold", alpha))
    ctx.set_line_width(5)
    rounded(ctx, -w / 2, -h / 2, w, h, 26)
    ctx.stroke()
    ctx.restore()


def tag(ctx, txt, cx, cy, u, alpha=1.0, w=300):
    p = back_out(u)
    if p <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(max(0.01, p), max(0.01, p))
    ctx.set_source_rgba(*col("gold", alpha))
    rounded(ctx, -w / 2, -37, w, 74, 37)
    ctx.fill()
    ctx.restore()
    draw_text(ctx, txt, F_SERIF, 44, "#2A1D14", cx, cy, alpha * clamp(p))


def burn_word(ctx, txt, path, size, cx, cy, reveal, alpha, rtl=False, scale=1.0, glow=16):
    if alpha <= 0.01 or reveal <= 0:
        return
    s = text_surf(txt, path, size, "#E3B04B", rtl=rtl, glow=glow)
    ww, hh = s.get_width(), s.get_height()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)
    if rtl:
        ctx.rectangle(ww / 2 - ww * reveal, -hh / 2, ww * reveal, hh)
    else:
        ctx.rectangle(-ww / 2, -hh / 2, ww * reveal, hh)
    ctx.clip()
    ctx.set_source_surface(s, -ww / 2, -hh / 2)
    ctx.paint_with_alpha(alpha)
    ctx.restore()
    if reveal < 1:
        fx = cx + ((ww / 2 - ww * reveal) if rtl else (-ww / 2 + ww * reveal)) * scale
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        lg = cairo.LinearGradient(fx - 40, 0, fx + 40, 0)
        lg.add_color_stop_rgba(0, 1, 0.8, 0.4, 0)
        lg.add_color_stop_rgba(0.5, 1, 0.92, 0.65, 0.9 * alpha)
        lg.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
        ctx.set_source(lg)
        ctx.rectangle(fx - 40, cy - hh * scale / 2, 80, hh * scale)
        ctx.fill()
        ctx.restore()


def dark_bg(ctx, lt, iris=1.0):
    R.bg(ctx, col("dark"))
    g = cairo.RadialGradient(540, 680, 20, 540, 680, 120 + 800 * iris)
    g.add_color_stop_rgba(0, *col("brown2")[:3], 0.7)
    g.add_color_stop_rgba(1, *col("dark")[:3], 0)
    ctx.set_source(g)
    ctx.paint()


def zion(ctx, t, crown_drop=1.0, crown_glow=0.0, hill_glow=0.0, storm=0.0, light=1.0):
    """Calm golden landscape, a holy hill, the crown settling on its peak; optional storm at its foot."""
    R.bg(ctx, col("cream"))
    g = cairo.LinearGradient(0, 0, 0, 1100)
    g.add_color_stop_rgba(0, *col("cream2"))
    g.add_color_stop_rgba(1, *col("gold2")[:3], 0.55)
    ctx.set_source(g)
    ctx.paint()
    rays(ctx, 540, -60, math.radians(55), math.radians(125), 9, 1700, 0.9 * light, t * 0.4)
    V.hills(ctx, 1030, 60, hexc("#E7D6B6"), t * 6, 5)
    V.hills(ctx, 1080, 40, hexc("#D9C497"), -t * 8, 6, 1.3)
    if hill_glow > 0:
        hg = cairo.RadialGradient(540, 760, 20, 540, 760, 420)
        hg.add_color_stop_rgba(0, *col("gold2")[:3], 0.5 * hill_glow)
        hg.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(hg)
        ctx.arc(540, 760, 420, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgba(*col("sand2"))
    hill_path(ctx, 540, 1240, 760, 520)
    ctx.fill()
    ctx.set_source_rgba(*col("leaf2", 0.55))
    hill_path(ctx, 540, 1240, 790, 420)
    ctx.fill()
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(0, 1220, W, H)
    ctx.fill()
    if storm > 0:
        crowd(ctx, t, 0.9, 1.0, storm, rows=[(1330, 0.55, 7, 21, 0.9), (1430, 0.7, 6, 22, 1.0)])
        vortex(ctx, 540, 1460, 520, t, 0.6 * storm)
    cy = lerp(-200, 690, eout(crown_drop))
    crown(ctx, 540, cy, 0.95, 1.0 if crown_drop > 0 else 0, crown_glow)


# ---------------------------------------------------------------- scene 1: the world spinning out of control
_sr = random.Random(31)
ORBIT = [(_sr.uniform(0, 6.28), _sr.uniform(300, 520), _sr.uniform(0.6, 1.4), _sr.choice(["paper", "leaf", "leaf"]),
          _sr.choice(["rust", "leaf", "gold"])) for _ in range(34)]


def scene1(ctx, lt):
    R.bg(ctx, col("dark"))
    gl = cairo.RadialGradient(540, 820, 100, 540, 820, 900)
    gl.add_color_stop_rgba(0, *col("brown2")[:3], 0.7)
    gl.add_color_stop_rgba(1, *col("dark")[:3], 0)
    ctx.set_source(gl)
    ctx.paint()
    dust(ctx, lt, 0.6, "cream2", 0, 0)
    spin = seg(lt, 0.1, 3.4)
    rot = 0.4 + 1.2 * lt + 5.5 * spin * spin * lt
    wob = 0.04 + 0.22 * ease(spin)
    tilt = wob * math.sin(lt * 7)
    ctx.save()
    dive = 1 + 5 * ein(seg(lt, 3.35, 3.85))
    cam(ctx, 540, 820, dive)
    ctx.translate(540, 820)
    ctx.scale(1 + 0.08 * ease(lt / 3.4), 1 + 0.08 * ease(lt / 3.4))
    ctx.translate(-540, -820)
    # swirl trails
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(9):
        rr = 330 + k * 30
        a0 = -rot * (1.2 + k * 0.08) + k
        ctx.set_source_rgba(*col("gold2", (0.12 + 0.35 * spin) * (1 - k / 12)))
        ctx.set_line_width(5)
        ctx.save()
        ctx.translate(540, 820)
        ctx.scale(1, 0.42)
        ctx.arc(0, 0, rr, a0, a0 + 0.9 + spin)
        ctx.restore()
        ctx.stroke()
    gp = 0.55 + 0.45 * back_out(seg(lt, 0.08, 0.4), 2.2)
    globe(ctx, 540, 820, 270 * gp, rot, tilt)
    for a0, rr, sp, kind, c in ORBIT:
        a = a0 + lt * sp * (1 + 3 * spin)
        r2 = rr + 220 * spin * spin
        x, y = 540 + math.cos(a) * r2, 820 + math.sin(a) * r2 * 0.5
        al = clamp(spin * 3) * clamp(1.6 - r2 / 700)
        if al <= 0:
            continue
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(a * 2)
        if kind == "paper":
            ctx.set_source_rgba(*col("cream2", al))
            ctx.rectangle(-18, -24, 36, 48)
            ctx.fill()
        else:
            ctx.scale(1.2, 0.5)
            ctx.set_source_rgba(*col(c, al))
            ctx.arc(0, 0, 18, 0, 2 * math.pi)
            ctx.fill()
        ctx.restore()
    ctx.restore()
    kword(ctx, "OUT OF", lt, T_OUT - 0.04, 540, 250, 100, "#FBF6EC", 3.6 - T_OUT)
    kword(ctx, "CONTROL", lt, T_CONTROL - 0.04, 540, 380, 118, "#E3B04B", 3.6 - T_CONTROL)


# ---------------------------------------------------------------- scene 2: the nations rage, the rulers plot
def scene2(ctx, lt):
    t = lt + B2
    pull = 1 + 2.2 * (1 - eout(seg(lt, 0.0, 0.9)))
    ctx.save()
    cam(ctx, 540, 900, pull)
    storm = 0.7 + 0.3 * ease(seg(lt, 0.2, 2.2))
    storm_sky(ctx, t, storm)
    ctx.set_source_rgba(*lerpc(col("sand"), hexc("#4A3227"), storm))
    ctx.rectangle(0, 1180, W, H)
    ctx.fill()
    rage = seg(t, T_RAGING - 0.1, T_RAGING + 0.3)
    plot = ease(seg(t, T_RULERS - 0.2, T_RULERS + 0.5))
    rise = eout(seg(lt, 1.0, 2.4))
    crowd(ctx, t, 0.2 + 0.8 * rage, rise, 1 - 0.55 * plot, tone=1.0)
    # rulers plotting around a glowing brazier
    if plot > 0:
        ctx.push_group()
        bx, by = 540, 1170
        fl = 0.8 + 0.2 * math.sin(t * 13)
        g = cairo.RadialGradient(bx, by - 60, 10, bx, by - 60, 420)
        g.add_color_stop_rgba(0, 1, 0.65, 0.3, 0.55 * fl)
        g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
        ctx.set_source(g)
        ctx.arc(bx, by - 60, 420, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(*col("brown"))
        ctx.rectangle(bx - 70, by - 40, 140, 60)
        ctx.fill()
        ctx.set_source_rgba(*col("gold2"))
        for k in range(3):
            ctx.move_to(bx - 40 + k * 40, by - 40)
            ctx.curve_to(bx - 60 + k * 40, by - 90, bx - 20 + k * 40, by - 110 - 20 * math.sin(t * 9 + k), bx - 40 + k * 40, by - 150)
            ctx.curve_to(bx - 20 + k * 40, by - 100, bx + k * 40, by - 80, bx - 40 + k * 40, by - 40)
            ctx.fill()
        lean = 0.12 * ease(seg(t, T_RULERS, T_RULERS + 0.8))
        c = col("dark")
        ruler(ctx, bx - 230, by + 80, 1.05, c, lean)
        ruler(ctx, bx + 230, by + 80, 1.05, c, -lean)
        ruler(ctx, bx, by + 170, 1.2, c, 0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(plot)
    # the bonds they want to break
    ch = ease(seg(t, T_RULERS + 0.3, T_RULERS + 0.9))
    brk = seg(t, T_BREAK, T_BREAK + 1.4)
    if ch > 0:
        chain(ctx, 40, 1040, 640, eout(brk), t, ch * (1 - seg(brk, 0.6, 1.0)))
        if 0 < brk < 0.35:
            r = random.Random(int(t * 40))
            for _ in range(16):
                a = r.uniform(0, 6.28)
                d = brk * r.uniform(80, 260)
                ctx.set_source_rgba(1, 0.85, 0.5, 1 - brk / 0.35)
                ctx.arc(540 + math.cos(a) * d, 640 + math.sin(a) * d, r.uniform(3, 7), 0, 2 * math.pi)
                ctx.fill()
    # "his chosen King": a far crown lights up above the storm
    kg = ease(seg(t, T_KING1 - 0.15, T_KING1 + 0.4))
    if kg > 0:
        rays(ctx, 540, 360, 0, 2 * math.pi, 12, 420, kg * 0.8, t * 0.6)
        crown(ctx, 540, 380, 0.55 * (0.85 + 0.15 * back_out(seg(t, T_KING1 - 0.15, T_KING1 + 0.3))), kg, 0.9)
    ctx.restore()
    grade(ctx, desat=0.25 * storm, warm=0.32 * storm)
    a = ease(seg(lt, 0.4, 0.9)) * (1 - ease(seg(t, T_RAGING - 0.6, T_RAGING - 0.1)))
    draw_text(ctx, "PSALM 2", F_SERIF, 118, "#FBF6EC", 540, 250, a, 0.94 + 0.06 * back_out(seg(lt, 0.4, 0.8)), stroke=5, stroke_color="#2A1D14")
    draw_text(ctx, "The King's song", F_SERIF_I, 54, "#FBF6EC", 540, 355, a * ease(seg(lt, 0.7, 1.2)), stroke=3, stroke_color="#2A1D14")
    kword(ctx, "RAGING", t, T_RAGING - 0.04, 540, 330, 180, "#E3B04B", T_RULERS - T_RAGING - 0.1)


# ---------------------------------------------------------------- scene 3: David wrote it
NOTES = [(random.Random(i).uniform(-260, 260), random.Random(i + 50).uniform(0, 1)) for i in range(9)]


def scene3(ctx, lt):
    t = lt + B3
    ctx.save()
    sl = 1300 * (1 - eout(seg(lt, -0.1, 0.3)))
    ctx.translate(sl, 0)
    R.bg(ctx, col("cream"))
    rays(ctx, 540, 720, 0, 2 * math.pi, 14, 900, 0.45, t * 0.4)
    pop = back_out(seg(lt, 0.0, 0.45), 1.4)
    lyre(ctx, 540, 760, 1.2 * max(0.01, pop), t - (T_DAVID - 0.25))
    for i, (x, ph) in enumerate(NOTES):
        u = (lt * 0.5 + ph) % 1.0
        if lt < 0.4:
            continue
        a = math.sin(math.pi * u)
        xx, yy = 540 + x + 20 * math.sin(u * 6 + i), 560 - u * 380
        ctx.set_source_rgba(*col("brown2", 0.8 * a))
        ctx.arc(xx, yy, 13, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_line_width(4)
        ctx.move_to(xx + 12, yy)
        ctx.line_to(xx + 12, yy - 46)
        ctx.line_to(xx + 28, yy - 36)
        ctx.stroke()
    draw_text(ctx, "David", F_SERIF_I, 120, "#3B2A1E", 540, 1130, ease(seg(t, T_DAVID - 0.1, T_DAVID + 0.3)),
              0.9 + 0.1 * back_out(seg(t, T_DAVID - 0.1, T_DAVID + 0.25)))
    tag(ctx, "Acts 4:25", 540, 1260, seg(t, T_DAVID + 0.15, T_DAVID + 0.5))
    ctx.restore()


# ---------------------------------------------------------------- scene 4: heaven isn't worried; the King on Zion
def scene4(ctx, lt):
    t = lt + B4
    zon = ease(seg(t, T_KING2 - 1.1, T_KING2 - 0.5))
    if zon < 1:
        ctx.push_group()
        R.bg(ctx, col("cream"))
        tilt = eout(seg(t, T_HEAVEN - 0.2, T_WORRIED))
        ctx.save()
        ctx.translate(0, 1500 * tilt)
        # the storm we leave behind (below)
        ctx.save()
        ctx.translate(0, -1500)
        storm_sky(ctx, t, 1.0)
        ctx.set_source_rgba(*hexc("#4A3227"))
        ctx.rectangle(0, 1180, W, H)
        ctx.fill()
        crowd(ctx, t, 1.0, 1.0, 1.0)
        ctx.restore()
        # cloud layer between
        clouds(ctx, -60, t, col("cream2"), 1.0, 30, 9, 1.4)
        ctx.restore()
        # heaven's calm light
        la = ease(seg(t, T_HEAVEN, T_WORRIED + 0.2))
        if la > 0:
            ctx.push_group()
            R.bg(ctx, col("cream"))
            g = cairo.LinearGradient(0, 0, 0, H)
            g.add_color_stop_rgba(0, *col("cream2"))
            g.add_color_stop_rgba(1, *col("gold2")[:3], 0.5)
            ctx.set_source(g)
            ctx.paint()
            clouds(ctx, 1500, t, col("cream2"), 0.9, 12, 14, 1.2)
            laugh = sum(math.exp(-((t - (T_LAUGHS + k * 0.22)) ** 2) * 60) for k in range(3))
            core = 0.75 + 0.25 * laugh
            orb = cairo.RadialGradient(540, 620, 20, 540, 620, 520)
            orb.add_color_stop_rgba(0, 1, 0.98, 0.9, core)
            orb.add_color_stop_rgba(0.35, *col("gold2")[:3], 0.55 * core)
            orb.add_color_stop_rgba(1, *col("gold2")[:3], 0)
            ctx.set_source(orb)
            ctx.arc(540, 620, 520, 0, 2 * math.pi)
            ctx.fill()
            rays(ctx, 540, 620, 0, 2 * math.pi, 16, 1200, 0.8, t * 0.3)
            # laughter: soft ripples of light
            for k in range(3):
                u = t - (T_LAUGHS + k * 0.22)
                if 0 <= u < 1.0:
                    ctx.set_source_rgba(*col("gold", 0.8 * (1 - u)))
                    ctx.set_line_width(8 * (1 - u) + 2)
                    ctx.arc(540, 620, 120 + u * 420, 0, 2 * math.pi)
                    ctx.stroke()
            # he speaks: arcs of light travel down
            for k in range(4):
                u = (t - T_SPEAKS) * 0.9 - k * 0.22
                if 0 <= u < 1.0:
                    ctx.set_source_rgba(*col("gold", 0.85 * (1 - u)))
                    ctx.set_line_width(10 * (1 - u) + 3)
                    yy = 700 + u * 900
                    ctx.save()
                    ctx.translate(540, yy)
                    ctx.scale(1, 0.35)
                    ctx.arc(0, 0, 200 + u * 300, math.radians(20), math.radians(160))
                    ctx.restore()
                    ctx.stroke()
            # the raging, seen from heaven: a tiny whirl far below
            vortex(ctx, 540, 1360, 110, t, 0.8 * ease(seg(t, T_WORRIED, T_LAUGHS)))
            dust(ctx, t, 0.5, "gold2", 6, -14)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(la)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - zon)
    if zon > 0:
        ctx.push_group()
        ctx.save()
        cam(ctx, 540, 800, 1.12 - 0.12 * ease(seg(t, T_KING2 - 1.1, T_HILL + 0.6)))
        zion(ctx, t, crown_drop=seg(t, T_KING2 - 0.75, T_KING2), crown_glow=ease(seg(t, T_KING2, T_KING2 + 0.4)),
             hill_glow=ease(seg(t, T_HILL - 0.3, T_HILL + 0.3)))
        ctx.restore()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(zon)
        kword(ctx, "MY KING", t, T_KING2 - 0.03, 540, 300, 170, "#E3B04B", B5 - T_KING2 - 0.2)


# ---------------------------------------------------------------- scene 5: mashiach, Messiah, Christos, Christ
def scene5(ctx, lt):
    t = lt + B5
    dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.7, "gold2", 6, -12)
    # Beat A: the anointing
    aa = ease(seg(t, T_KEY - 0.2, T_KEY + 0.4)) * (1 - ease(seg(t, T_MASHIACH - 0.9, T_MASHIACH - 0.5)))
    if aa > 0:
        tip = ease(seg(t, T_ANOINTED - 0.9, T_ANOINTED - 0.3))
        horn(ctx, 300, 430, 1.25, lerp(-0.2, 0.75, tip), aa)
        drop = seg(t, T_ANOINTED - 0.35, T_ANOINTED + 0.05)
        if 0 < drop < 1:
            dy = lerp(560, 860, ein(drop))
            ctx.set_source_rgba(*col("gold2", aa))
            ctx.save()
            ctx.translate(540, dy)
            ctx.scale(1, 1.3)
            ctx.arc(0, 0, 16, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
        anoint = ease(seg(t, T_ANOINTED, T_ANOINTED + 0.4))
        crown(ctx, 540, 960, 1.1, aa, anoint)
        draw_text(ctx, "anointed", F_SERIF_I, 80, "#DCC59D", 540, 1180, aa * anoint)
    # Beat B: the ladder of words
    fade = 1 - ease(seg(t, T_SON - 2.6, T_SON - 2.1))
    hb = ease(seg(t, T_MASHIACH - 0.6, T_MASHIACH - 0.3)) * fade
    reveal = ease(seg(t, T_MASHIACH - 0.55, T_MASHIACH + 0.05))
    up = ease(seg(t, T_MESSIAH - 0.5, T_MESSIAH - 0.1))
    hy, hs = lerp(660, 300, up), lerp(1.0, 0.62, up)
    rays(ctx, 540, hy, 0, 2 * math.pi, 18, 900 * hs + 200, hb * (0.4 + 0.6 * seg(t, T_MASHIACH, T_MASHIACH + 0.3)) * (1 - 0.6 * up), t * 0.4)
    burn_word(ctx, "מָשִׁיחַ", F_HEB, 300, 540, hy, reveal, hb, rtl=True, scale=hs)
    sub = ease(seg(t, T_MASHIACH + 0.1, T_MASHIACH + 0.5)) * (1 - ease(seg(t, T_MESSIAH - 0.5, T_MESSIAH - 0.2)))
    draw_text(ctx, "mashiach", F_SERIF_I, 96, "#FBF6EC", 540, 900, sub, 0.9 + 0.1 * back_out(seg(t, T_MASHIACH + 0.1, T_MASHIACH + 0.45)))
    draw_text(ctx, "anointed one", F_SERIF_R, 56, "#DCC59D", 540, 1000, sub)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    def link(y0, y1, u):
        if u <= 0:
            return
        ctx.set_source_rgba(*col("gold", fade))
        ctx.set_line_width(5)
        ctx.move_to(540, y0)
        ctx.line_to(540, lerp(y0, y1, u))
        ctx.stroke()
        if u >= 1:
            ctx.move_to(526, y1 - 16)
            ctx.line_to(540, y1)
            ctx.line_to(554, y1 - 16)
            ctx.stroke()

    link(390, 450, eout(seg(t, T_MESSIAH - 0.3, T_MESSIAH)))
    m = seg(t, T_MESSIAH - 0.05, T_MESSIAH + 0.3)
    draw_text(ctx, "Messiah", F_SERIF, 104, "#FBF6EC", 540, 530, ease(m) * fade, 0.9 + 0.1 * back_out(m))
    link(610, 670, eout(seg(t, T_CHRISTOS - 0.6, T_CHRISTOS - 0.3)))
    draw_text(ctx, "Greek", F_SERIF_I, 44, "#DCC59D", 690, 640, ease(seg(t, T_CHRISTOS - 0.9, T_CHRISTOS - 0.5)) * fade)
    burn_word(ctx, "Χριστός", F_GREEK, 120, 540, 770, ease(seg(t, T_CHRISTOS - 0.35, T_CHRISTOS + 0.15)), fade)
    link(860, 920, eout(seg(t, T_CHRIST - 0.4, T_CHRIST - 0.1)))
    kword(ctx, "CHRIST", t, T_CHRIST - 0.03, 540, 1020, 170, "#E3B04B", T_SON - 2.2 - T_CHRIST)
    # Beat C: "You are my Son" (Psalm 2:7)
    ca = ease(seg(t, T_SON - 2.3, T_SON - 1.9)) * (1 - ease(seg(t, T_JESUS - 0.9, T_JESUS - 0.5)))
    if ca > 0:
        pop = back_out(seg(t, T_SON - 2.3, T_SON - 1.95), 1.4)
        verse_card(ctx, 540, 760, 760, 520, ca, max(0.01, 1.2 - 0.2 * pop))
        crown(ctx, 540, 590, 0.55, ca, 0.3)
        draw_text(ctx, "Psalm 2:7", F_SERIF, 64, "#3B2A1E", 540, 700, ca)
        sp = math.exp(-((t - T_SON) ** 2) * 10)
        draw_text(ctx, "“You are my Son”", F_SERIF_I, 86, "#A8741A", 540, 830, ca, 1 + 0.08 * sp)
        draw_text(ctx, "God speaks to his King", F_SERIF_R, 44, "#6E5039", 540, 930, ca * ease(seg(t, T_SON - 1.6, T_SON - 1.2)))
    # Beat D: the New Testament applies it to Jesus
    ja = ease(seg(t, T_JESUS - 2.4, T_JESUS - 2.0))
    if ja > 0:
        tag(ctx, "Acts 13:33", 340, 1160, seg(t, T_JESUS - 2.3, T_JESUS - 1.9), ja, 320)
        tag(ctx, "Hebrews 1:5", 740, 1160, seg(t, T_JESUS - 2.0, T_JESUS - 1.6), ja, 340)
        jr = ease(seg(t, T_JESUS - 0.1, T_JESUS + 0.4))
        rays(ctx, 540, 720, 0, 2 * math.pi, 18, 1000, jr * 0.9, t * 0.5)
        kword(ctx, "JESUS", t, T_JESUS - 0.03, 540, 720, 220, "#E3B04B", B6 - T_JESUS)


# ---------------------------------------------------------------- scene 6: the chaos isn't in charge; blessed; refuge
_rr = random.Random(44)
RAIN = [(_rr.uniform(-100, W + 100), _rr.uniform(0, H), _rr.uniform(0.7, 1.3)) for _ in range(160)]


def scene6(ctx, lt):
    t = lt + B6
    pages = ease(seg(t, T_BEGAN - 2.6, T_BEGAN - 2.25))
    ref = ease(seg(t, T_BLESSED + 0.55, T_BLESSED + 0.9))
    # Beat A + B: storm close up, then pull back to the King on his hill
    if pages < 1:
        ctx.push_group()
        pb = eout(seg(t, T_CHARGE - 0.9, T_CHARGE + 0.3))
        s = lerp(2.6, 1.0, pb)
        ctx.save()
        cam(ctx, 540, lerp(1380, 900, pb), s)
        zion(ctx, t, 1.0, 0.6 * pb, 0.6 * pb, storm=1.0)
        ctx.restore()
        storm = 1 - pb
        grade(ctx, desat=0.3 * storm, warm=0.3 * storm)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - pages)
    # Beat C: Psalm 1 opens with blessed, Psalm 2 closes with it
    if pages > 0 and ref < 1:
        ctx.push_group()
        ctx.save()
        ctx.translate(-1300 * (1 - eout(seg(t, T_BEGAN - 2.6, T_BEGAN - 2.25))), 0)
        R.bg(ctx, col("cream"))
        rays(ctx, 540, 520, 0, 2 * math.pi, 14, 900, 0.4, t * 0.4)
        bl = math.exp(-((t - T_BLESSED) ** 2) * 6)
        for i, (cx, label) in enumerate([(290, "Psalm 1:1"), (790, "Psalm 2:12")]):
            u = back_out(seg(t, T_BEGAN - 2.4 + i * 0.5, T_BEGAN - 2.0 + i * 0.5), 1.3)
            if u <= 0.01:
                continue
            verse_card(ctx, cx, 860, 420, 560, 1.0, max(0.01, u))
            draw_text(ctx, label, F_SERIF, 54, "#3B2A1E", cx, 650, clamp(u))
            hl = ease(seg(t, T_BLESSED - 0.9, T_BLESSED - 0.5))
            yline = 760 if i == 0 else 960
            for j in range(5):
                y = 740 + j * 55
                w = [300, 320, 280, 310, 260][j]
                is_b = (y + 20 == yline)
                ctx.set_source_rgba(*(col("gold2", 0.45 + 0.4 * bl) if (is_b and hl > 0) else col("brown2", 0.35)))
                rounded(ctx, cx - w / 2, y - 9, w * (1 if not is_b else 1), 18, 9)
                ctx.fill()
            if i == 0:
                ctx.save()
                ctx.translate(cx, 1090)
                ctx.scale(0.22, 0.22)
                ctx.translate(-540, -1000)
                R.tree(ctx, 540, 1000, 1, 1, 0, 1, 0)
                ctx.restore()
            else:
                crown(ctx, cx, 1080, 0.45, 1.0, 0)
        br = eout(seg(t, T_BEGAN - 0.6, T_BEGAN))
        if br > 0:
            ctx.set_source_rgba(*col("gold"))
            ctx.set_line_width(6)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            pts = R.bez_pts([(290, 560), (360, 470), (720, 470), (790, 560)], 40)
            R.polyline(ctx, pts, br)
            ctx.stroke()
        ctx.restore()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - ref)
        kword(ctx, "BLESSED", t, T_BLESSED - 0.03, 540, 420, 170, "#E3B04B", 0.8)
    # Beat D: refuge in him
    if ref > 0:
        ctx.push_group()
        R.bg(ctx, hexc("#7C8590"))
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgba(0, *hexc("#5E6670"))
        g.add_color_stop_rgba(1, *hexc("#9AA0A6"))
        ctx.set_source(g)
        ctx.paint()
        clouds(ctx, 80, t, hexc("#4A5058"), 0.9, 20, 17)
        ctx.set_source_rgba(*hexc("#6B6E6E"))
        ctx.rectangle(0, 1240, W, H)
        ctx.fill()
        dome = ease(seg(t, T_BLESSED + 0.6, T_REFUGE))
        # rain everywhere except under the dome of light
        ctx.save()
        ctx.set_source_rgba(*hexc("#C9D2DA", 0.7))
        ctx.set_line_width(4)
        for x0, y0, sp in RAIN:
            y = (y0 + t * 1400 * sp) % H
            x = x0 - (y / H) * 60
            if (x - 540) ** 2 / (430 ** 2) + (y - 1240) ** 2 / (520 ** 2) < dome ** 2:
                continue
            ctx.move_to(x, y)
            ctx.line_to(x - 10, y + 44)
        ctx.stroke()
        ctx.restore()
        if dome > 0:
            dg = cairo.RadialGradient(540, 1100, 30, 540, 1100, 560)
            dg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.95 * dome)
            dg.add_color_stop_rgba(0.6, *col("gold2")[:3], 0.55 * dome)
            dg.add_color_stop_rgba(1, *col("gold2")[:3], 0)
            ctx.set_source(dg)
            ctx.save()
            ctx.translate(540, 1240)
            ctx.scale(1, 520 / 430)
            ctx.arc(0, 0, 430 * dome, math.pi, 2 * math.pi)
            ctx.restore()
            ctx.fill()
            crown(ctx, 540, 660, 0.6, dome, 0.8)
        # people come in from the rain
        for i, (sx, d) in enumerate([(-1, 0.0), (1, 0.15), (-1, 0.3), (1, 0.45), (-1, 0.6)]):
            u = ease(seg(t, T_BLESSED + 0.7 + d, T_REFUGE + 0.4 + d))
            x = lerp(540 + sx * 720, 540 + sx * (60 + i * 55), u)
            R.figure(ctx, x, 1250, 0.75, col("brown"), 0.2 + 0.5 * u)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(ref)
        draw_text(ctx, "refuge", F_SERIF_I, 96, "#FBF6EC", 540, 380, ease(seg(t, T_REFUGE - 0.1, T_REFUGE + 0.3)) * ref,
                  stroke=4, stroke_color="#2A1D14")


# ---------------------------------------------------------------- scene 7: the news feels loud; take it to the King
_nr = random.Random(57)
NOTIFS = [(_nr.uniform(-330, 330), _nr.uniform(-520, 380), _nr.uniform(-0.2, 0.2), _nr.uniform(0, 1)) for _ in range(14)]


def scene7(ctx, lt):
    t = lt + B7
    R.bg(ctx, col("cream"))
    calm = ease(seg(t, T_TAKE, T_TAKE + 0.9))
    loud = ease(seg(t, T_NEWS - 0.6, T_LOUD + 0.2)) * (1 - calm)
    rays(ctx, 540, -40, math.radians(60), math.radians(120), 8, 1500, calm, t * 0.4)
    crown(ctx, 540, lerp(-150, 230, eout(seg(t, T_TAKE - 0.2, T_TAKE + 0.5))), 0.6, calm, 1.0)
    vib = 6 * loud * math.sin(t * 70)
    ctx.save()
    ctx.translate(540 + vib, 900)
    ctx.set_source_rgba(0, 0, 0, 0.15)
    rounded(ctx, -230 + 12, -440 + 16, 460, 880, 56)
    ctx.fill()
    ctx.set_source_rgba(*col("brown"))
    rounded(ctx, -230, -440, 460, 880, 56)
    ctx.fill()
    ctx.set_source_rgba(*lerpc(hexc("#F1D9CC"), col("cream2"), calm))
    rounded(ctx, -205, -410, 410, 820, 40)
    ctx.fill()
    if calm > 0:
        g = cairo.RadialGradient(0, -100, 10, 0, -100, 380)
        g.add_color_stop_rgba(0, *col("gold2")[:3], 0.5 * calm)
        g.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(g)
        ctx.paint()
    ctx.restore()
    # notifications pile up, then rise into the light
    for i, (x, y, rot, d) in enumerate(NOTIFS):
        u = back_out(seg(t, B7 + 0.1 + i * 0.11, B7 + 0.35 + i * 0.11))
        if u <= 0.01:
            continue
        lift = ein(seg(t, T_TAKE - 0.1 + d * 0.3, T_TAKE + 0.8 + d * 0.3))
        xx = 540 + x * (1 - 0.6 * lift) + vib
        yy = 900 + y - lift * (900 + y + 700)
        al = 1 - seg(lift, 0.6, 1.0)
        if al <= 0:
            continue
        ctx.save()
        ctx.translate(xx, yy)
        ctx.rotate(rot * (1 - lift))
        ctx.scale(max(0.01, u) * (1 - 0.5 * lift), max(0.01, u) * (1 - 0.5 * lift))
        ctx.set_source_rgba(0, 0, 0, 0.12 * al)
        rounded(ctx, -150 + 6, -46 + 8, 300, 92, 20)
        ctx.fill()
        ctx.set_source_rgba(*col("cream2", al))
        rounded(ctx, -150, -46, 300, 92, 20)
        ctx.fill()
        ctx.set_source_rgba(*col("rust", al))
        ctx.arc(-108, 0, 24, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(*col("cream2", al))
        ctx.rectangle(-111, -14, 6, 18)
        ctx.fill()
        ctx.arc(-108, 10, 3.5, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(*col("brown2", 0.7 * al))
        rounded(ctx, -70, -20, 190, 14, 7)
        ctx.fill()
        rounded(ctx, -70, 6, 140, 12, 6)
        ctx.fill()
        ctx.restore()
    grade(ctx, desat=0.0, warm=0.18 * loud)
    if loud > 0:
        for k in range(3):
            u = (t * 1.4 + k / 3) % 1.0
            ctx.set_source_rgba(*col("rust", 0.5 * loud * (1 - u)))
            ctx.set_line_width(6)
            for sx in (-1, 1):
                ctx.arc(540 + sx * 290, 520, 40 + u * 120, math.radians(-50 if sx > 0 else 130), math.radians(50 if sx > 0 else 230))
                ctx.stroke()


# ---------------------------------------------------------------- scene 8: the world rages, Jesus reigns, loop
def scene8(ctx, lt):
    t = lt + B8
    R.bg(ctx, col("cream"))
    rg = ease(seg(t, T_REIGNS - 0.1, T_REIGNS + 0.4))
    rays(ctx, 540, 500, 0, 2 * math.pi, 16, 1000, 0.25 + 0.55 * rg, t * 0.4)
    wr = ease(seg(t, T_RAGES - 0.6, T_RAGES - 0.2))
    vortex(ctx, 540, 1250, lerp(260, 120, rg), t, wr * (1 - 0.6 * rg), 1 - 0.7 * rg)
    draw_text(ctx, "PSALM 2", F_SERIF, 50, "#6E5039", 540, 690, wr)
    ctx.set_source_rgba(*col("gold", wr))
    ctx.rectangle(490, 740, 100, 4)
    ctx.fill()
    draw_text(ctx, "The world rages.", F_SERIF_I, 76, "#6E5039", 540, 830, wr, 0.95 + 0.05 * back_out(seg(t, T_RAGES - 0.6, T_RAGES - 0.2)))
    sc = 0.9 + 0.1 * back_out(seg(t, T_REIGNS - 0.05, T_REIGNS + 0.35))
    draw_text(ctx, "Jesus reigns.", F_SERIF, 112, "#3B2A1E", 540, 970, rg, sc)
    crown(ctx, 540, lerp(300, 470, eout(seg(t, T_REIGNS - 0.2, T_REIGNS + 0.3))), 0.85, rg, 0.9)
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
        os.makedirs("/home/claude/psalm2/stills", exist_ok=True)
        for t in map(float, sys.argv[2:]):
            render_frame(t).write_to_png(f"/home/claude/psalm2/stills/t{t:05.2f}.png")
    elif sys.argv[1] == "times":
        for k, v in sorted(((k, v) for k, v in globals().items() if k.startswith("T_")), key=lambda x: x[1]):
            print(f"{k:12s} {v:6.2f}")
    else:
        video(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
