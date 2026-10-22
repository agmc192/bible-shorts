"""Psalm 11 Short. Slate-blue storm turning to clear high sky. Central image: the steady throne above shaking ground, and the eyes that look closely."""
import sys, math, random
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/psalm4")
import cairo
from engine import Episode
import render as R
import render_v2 as V
import render_p2 as P
import render_p3 as Q
from render import (W, H, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, text_surf, rounded, cam,
                    F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword

E = Episode(11)
wt, DUR = E.wt, E.dur
T_SHAKING = wt("shaking"); T_RUN1 = wt("run", 1); T_PSALM = wt("psalm", 1); T_ADVICE = wt("advice"); T_FLEE1 = wt("flee", 1)
T_BIRD = wt("bird"); T_MOUNTAIN = wt("mountain"); T_ARROWS = wt("arrows"); T_STRING = wt("string")
T_FOUNDATIONS = wt("foundations"); T_DESTROYED = wt("destroyed"); T_RIGHTEOUS = wt("righteous"); T_ANSWER = wt("answer")
T_LORD1 = wt("lord", 1); T_REFUGE1 = wt("refuge", 1); T_WHY = wt("why"); T_TEMPLE = wt("temple"); T_THRONE1 = wt("throne", 1)
T_HEAVEN = wt("heaven"); T_GROUND = wt("ground"); T_SHAKE = wt("shake"); T_THRONE2 = wt("throne", 2); T_DOESNT = wt("doesnt")
T_DISTANT = wt("distant"); T_VERSE = wt("verse"); T_EYES1 = wt("eyes", 1); T_SEE = wt("see"); T_EYELIDS1 = wt("eyelids", 1)
T_TEST = wt("test"); T_PERSON = wt("person"); T_HEBREW = wt("hebrew"); T_AFAPPAV = wt("ahfahppahv"); T_EYELIDS2 = wt("eyelids", 2)
T_PICTURE = wt("picture"); T_NARROWING = wt("narrowing"); T_CLOSELY = wt("closely"); T_NOTHING = wt("nothing"); T_PAST = wt("past")
T_FEAR = wt("fear"); T_RUN2 = wt("run", 2); T_STOP = wt("stop"); T_LOOK2 = wt("look", 2); T_UP1 = wt("up", 1); T_LOUD = wt("loud")
T_REFUGE2 = wt("refuge", 2); T_DONT = wt("dont"); T_FLEE2 = wt("flee", 2); T_UP2 = wt("up", 2)

B1 = 0.0
B2 = T_PSALM - 0.3
B3 = T_ARROWS - 0.5
B4 = T_ANSWER - 0.5
B5 = T_DISTANT - 0.45
B6 = T_HEBREW - 0.4
B7 = T_FEAR - 0.7

E.zooms = [(0.1, 0.12), (T_RUN1, 0.08), (T_FLEE1, 0.08), (T_STRING, 0.08), (T_DESTROYED, 0.1), (T_REFUGE1, 0.12),
           (T_DOESNT, 0.07), (T_SEE, 0.08), (T_AFAPPAV, 0.12), (T_NOTHING, 0.06), (T_UP1, 0.08), (T_UP2, 0.08)]
E.shakes = [(0.1, 18, 0.9), (T_SHAKING, 12, 0.7), (T_DESTROYED, 16, 0.8), (T_SHAKE, 14, 0.8), (T_AFAPPAV, 8, 0.4)]
E.flashes = [(0.1, (1, 1, 1), 0.3, 0.3), (T_REFUGE1, (1, 0.95, 0.8), 0.45, 0.5), (T_AFAPPAV, (1, 0.88, 0.55), 0.3, 0.4),
             (T_UP2, (1, 0.95, 0.85), 0.35, 0.45)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6, B7)]

STORM1 = hexc("#25303D")
STORM2 = hexc("#4F6075")
CLEAR1 = hexc("#9CC3DD")
CLEAR2 = hexc("#F3E6C8")
GROUND_Y = 1260

_r = random.Random(11)
RAIN = [(_r.uniform(0, W), _r.uniform(0, H), _r.uniform(0.6, 1.4)) for _ in range(140)]


def sky(ctx, t, clear=0.0, rain=0.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND_Y)
    g.add_color_stop_rgba(0, *lerpc(STORM1, CLEAR1, clear))
    g.add_color_stop_rgba(1, *lerpc(STORM2, CLEAR2, clear))
    ctx.set_source(g)
    ctx.paint()
    P.clouds(ctx, 120, t, hexc("#2A3440"), 0.35 * (1 - clear), 30, 3, 1.3)
    P.clouds(ctx, 260, t, hexc("#3E4B5A"), 0.3 * (1 - clear), -22, 4, 1.0)
    if rain > 0.01:
        ctx.set_source_rgba(0.8, 0.86, 0.95, 0.35 * rain)
        ctx.set_line_width(3)
        for x, y, s in RAIN:
            yy = (y + t * 1400 * s) % H
            xx = (x - t * 300 * s) % W
            ctx.move_to(xx, yy)
            ctx.line_to(xx - 12 * s, yy + 50 * s)
        ctx.stroke()


def mountain(ctx, cx, base, s, c, alpha=1.0):
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.move_to(cx - 420 * s, base)
    ctx.line_to(cx - 140 * s, base - 380 * s)
    ctx.line_to(cx - 60 * s, base - 330 * s)
    ctx.line_to(cx + 30 * s, base - 470 * s)
    ctx.line_to(cx + 160 * s, base - 300 * s)
    ctx.line_to(cx + 420 * s, base)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(0.92, 0.94, 0.98, 0.7 * alpha)
    ctx.move_to(cx - 30 * s, base - 380 * s)
    ctx.line_to(cx + 30 * s, base - 470 * s)
    ctx.line_to(cx + 90 * s, base - 390 * s)
    ctx.line_to(cx + 40 * s, base - 410 * s)
    ctx.line_to(cx + 10 * s, base - 370 * s)
    ctx.close_path()
    ctx.fill()


def bird(ctx, x, y, s, flap, alpha=1.0, c=None):
    c = c or hexc("#1A1714")
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c[:3], alpha)
    w = 30 * math.sin(flap)
    ctx.move_to(-60, -w)
    ctx.curve_to(-30, -w * 0.6 - 10, -12, -8, 0, 0)
    ctx.curve_to(12, -8, 30, -w * 0.6 - 10, 60, -w)
    ctx.curve_to(30, -w * 0.2, 10, 6, 0, 10)
    ctx.curve_to(-10, 6, -30, -w * 0.2, -60, -w)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def archer(ctx, x, base, s, draw, flip=1, alpha=1.0, c=None):
    """Faceless archer silhouette; draw 0..1 pulls the string back."""
    c = c or hexc("#14181E")
    ctx.save()
    ctx.translate(x, base)
    ctx.scale(s * flip, s)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.arc(0, -230, 30, 0, 2 * math.pi)
    ctx.fill()
    ctx.move_to(-35, -195); ctx.line_to(35, -195); ctx.line_to(45, -60); ctx.line_to(-45, -60); ctx.close_path(); ctx.fill()
    ctx.rectangle(-38, -62, 28, 62); ctx.rectangle(10, -62, 28, 62); ctx.fill()
    # bow arm forward, bow, string drawn back
    ctx.set_line_width(14)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.move_to(20, -170); ctx.line_to(120, -170); ctx.stroke()
    ctx.set_line_width(8)
    ctx.arc(70, -170, 95, -1.1, 1.1)
    ctx.stroke()
    sx = 70 + 95 * math.cos(1.1) - 70 * draw
    ctx.set_line_width(2)
    ctx.move_to(70 + 95 * math.cos(-1.1), -170 + 95 * math.sin(-1.1))
    ctx.line_to(sx, -170)
    ctx.line_to(70 + 95 * math.cos(1.1), -170 + 95 * math.sin(1.1))
    ctx.stroke()
    ctx.set_line_width(4)
    ctx.move_to(sx, -170); ctx.line_to(sx + 190, -170); ctx.stroke()
    ctx.move_to(sx + 190, -170); ctx.line_to(sx + 172, -180); ctx.line_to(sx + 172, -160); ctx.close_path(); ctx.fill()
    ctx.restore()


def pillar(ctx, x, base, h, crack, fall, side, alpha=1.0):
    """Stone pillar; crack 0..1 draws a fracture, fall 0..1 topples the upper half."""
    w = 90
    c = hexc("#C9B79A")
    ctx.save()
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.rectangle(x - w / 2 - 15, base - 30, w + 30, 30)
    ctx.fill()
    ctx.rectangle(x - w / 2, base - h * 0.5, w, h * 0.5 - 30)
    ctx.fill()
    ctx.save()
    ctx.translate(x + side * w / 2, base - h * 0.5)
    ctx.rotate(side * fall * 1.2)
    ctx.translate(0, fall * fall * 260)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.rectangle(-side * w / 2 - w / 2, -h * 0.5, w, h * 0.5)
    ctx.fill()
    ctx.rectangle(-side * w / 2 - w / 2 - 20, -h * 0.5 - 30, w + 40, 30)
    ctx.fill()
    ctx.restore()
    if crack > 0:
        ctx.set_source_rgba(0.2, 0.16, 0.12, alpha)
        ctx.set_line_width(5)
        ctx.move_to(x - w / 2, base - h * 0.5)
        n = 6
        for i in range(1, n + 1):
            u = i / n * crack
            ctx.line_to(x - w / 2 + w * u, base - h * 0.5 + (12 if i % 2 else -12))
        ctx.stroke()
    ctx.restore()


def eye(ctx, cx, cy, s, open_, alpha=1.0, look=0.0, glow=0.0):
    """Stylised eye of light, open_ 1 = wide, ~0.35 = narrowed to look closely."""
    if alpha <= 0.01:
        return
    if glow > 0:
        g = cairo.RadialGradient(cx, cy, 20, cx, cy, 420 * s)
        g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.5 * glow * alpha)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.arc(cx, cy, 420 * s, 0, 2 * math.pi)
        ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    op = max(0.04, open_)
    def lid():
        ctx.move_to(-260, 0)
        ctx.curve_to(-120, -170 * op, 120, -170 * op, 260, 0)
        ctx.curve_to(120, 170 * op, -120, 170 * op, -260, 0)
        ctx.close_path()
    lid()
    ctx.set_source_rgba(1, 0.97, 0.88, alpha)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    ctx.set_source_rgba(*col("gold", alpha))
    ctx.arc(look * 80, 0, 95, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(0.16, 0.11, 0.07, alpha)
    ctx.arc(look * 80, 0, 44, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9 * alpha)
    ctx.arc(look * 80 + 26, -30, 15, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    lid()
    ctx.set_line_width(12)
    ctx.set_source_rgba(0.23, 0.17, 0.12, alpha)
    ctx.stroke()
    # lashes on the upper lid
    for k in range(7):
        u = (k + 1) / 8
        x = -260 + 520 * u
        y = -170 * op * 0.75 * math.sin(math.pi * u)
        ctx.move_to(x, y)
        ctx.line_to(x * 1.08, y - 40 - 10 * math.sin(math.pi * u))
    ctx.stroke()
    ctx.restore()


def throne_heaven(ctx, cx, cy, s, alpha, t):
    if alpha <= 0.01:
        return
    rays(ctx, cx, cy - 140 * s, 0, 2 * math.pi, 18, 1000, alpha * 0.9, t * 0.3)
    g = cairo.RadialGradient(cx, cy - 140 * s, 10, cx, cy - 140 * s, 420 * s)
    g.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.95 * alpha)
    g.add_color_stop_rgba(1, 1, 0.88, 0.55, 0)
    ctx.set_source(g)
    ctx.arc(cx, cy - 140 * s, 420 * s, 0, 2 * math.pi)
    ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("gold2", alpha))
    ctx.move_to(-120, 0); ctx.line_to(-120, -280)
    ctx.curve_to(-120, -380, 0, -400, 0, -400); ctx.curve_to(0, -400, 120, -380, 120, -280)
    ctx.line_to(120, 0); ctx.line_to(90, 0); ctx.line_to(90, -110); ctx.line_to(-90, -110); ctx.line_to(-90, 0)
    ctx.close_path(); ctx.fill()
    ctx.rectangle(-150, -125, 300, 32); ctx.fill()
    ctx.rectangle(-170, 0, 340, 26); ctx.fill()
    ctx.restore()
    # cloud bank under the throne
    ctx.set_source_rgba(1, 1, 1, 0.85 * alpha)
    r = random.Random(5)
    for i in range(9):
        x = cx + (i - 4) * 70 * s + 10 * math.sin(t + i)
        ctx.arc(x, cy + 40 * s + r.uniform(-14, 14), r.uniform(55, 85) * s, 0, 2 * math.pi)
        ctx.fill()


def ground_band(ctx, y, c, shake_t=0.0, t=0.0):
    off = 10 * shake_t * math.sin(t * 40)
    ctx.set_source_rgba(*c[:3])
    ctx.move_to(0, y + off)
    for i in range(13):
        ctx.line_to(i * 90, y + off + (6 * math.sin(i * 1.7 + t * 30) * shake_t))
    ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); ctx.fill()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: storm, shaking ground; a figure caught mid-step, poised to run."""
    t = lt
    sky(ctx, t, 0.0, 1.0)
    mountain(ctx, 780, GROUND_Y - 40, 0.9, hexc("#1F2832"))
    sh = 1 - ease(seg(t, 0.2, 3.2)) * 0.6
    ground_band(ctx, GROUND_Y, hexc("#1A1E24"), sh, t)
    lean = ease(seg(t, T_RUN1 - 0.4, T_RUN1 + 0.2))
    ctx.save()
    ctx.translate(380, GROUND_Y + 20)
    ctx.rotate(0.18 * lean)
    Q.person(ctx, 0, 0, 1.3, hexc("#0F1215"), 0, 0, 0, 0.3)
    ctx.restore()
    for k in range(3):
        x = 380 - 40 - k * 50 - 60 * lean
        ctx.set_source_rgba(0.8, 0.85, 0.95, 0.35 * lean)
        ctx.set_line_width(5)
        ctx.move_to(x, GROUND_Y - 200 + k * 50)
        ctx.line_to(x - 80, GROUND_Y - 200 + k * 50)
        ctx.stroke()
    kword(ctx, "SHAKING", t, T_SHAKING - 0.04, 540, 620, 150, "#CFE0F5", T_RUN1 - T_SHAKING)
    kword(ctx, "RUN?", t, T_RUN1 - 0.04, 540, 620, 210, "#E3B04B", B2 - T_RUN1 + 0.3)
    grade(ctx, cool=0.2)


def scene2(ctx, lt):
    """Title; the advice: flee like a bird to your mountain."""
    t = lt + B2
    sky(ctx, t, 0.08, 0.7)
    fl = ease(seg(t, T_BIRD - 0.4, B3 + 0.2))
    mountain(ctx, 760, GROUND_Y - 40, lerp(0.9, 1.1, fl), hexc("#26313C"))
    ground_band(ctx, GROUND_Y, hexc("#1A1E24"))
    Q.person(ctx, 300, GROUND_Y + 20, 1.2, hexc("#0F1215"), 0.2, 0, 0, 0.2)
    ti = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_FLEE1 - 0.4, T_FLEE1 - 0.1)))
    draw_text(ctx, "PSALM 11", F_SERIF, 150, "#FBF6EC", 540, 520, ti, 0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#1A222C")
    draw_text(ctx, "the advice", F_SERIF_I, 64, "#CFE0F5", 540, 640, ease(seg(t, T_ADVICE - 0.3, T_ADVICE)) * ti)
    # whispers around the figure
    wa = ease(seg(t, T_ADVICE - 0.2, T_ADVICE + 0.3)) * (1 - ease(seg(t, B3 - 0.3, B3)))
    for k, (dx, dy) in enumerate(((-150, -330), (170, -300), (-60, -420))):
        draw_text(ctx, "“flee!”", F_SERIF_I, 46, "#B8C6D6", 300 + dx, GROUND_Y + dy, wa * (0.5 + 0.5 * math.sin(t * 3 + k)))
    P.tag(ctx, "Psalm 11:1", 540, 380, seg(t, T_FLEE1 - 0.2, T_FLEE1 + 0.2), 1.0, 250)
    draw_text(ctx, "“Flee like a bird", F_SERIF_I, 84, "#FBF6EC", 540, 520, ease(seg(t, T_FLEE1 - 0.2, T_FLEE1 + 0.1)), stroke=3, stroke_color="#1A222C")
    draw_text(ctx, "to your mountain!”", F_SERIF_I, 84, "#E3B04B", 540, 630, ease(seg(t, T_MOUNTAIN - 0.3, T_MOUNTAIN)), stroke=3, stroke_color="#1A222C")
    # the bird takes off from the figure toward the peak
    if fl > 0:
        x = lerp(330, 790, fl)
        y = lerp(GROUND_Y - 260, GROUND_Y - 560, fl) - 120 * math.sin(math.pi * fl)
        bird(ctx, x, y, lerp(1.6, 0.8, fl), t * 14, 1.0, hexc("#F3E6C8"))
    grade(ctx, cool=0.2)


def scene3(ctx, lt):
    """Arrows on the string; the foundations crack and fall. What can the righteous do?"""
    t = lt + B3
    sky(ctx, t, 0.0, 0.5)
    ground_band(ctx, GROUND_Y, hexc("#1A1E24"), seg(t, T_DESTROYED - 0.2, T_DESTROYED + 0.8), t)
    dr = ease(seg(t, T_ARROWS - 0.2, T_STRING + 0.3))
    ar_a = 1 - ease(seg(t, T_FOUNDATIONS - 0.5, T_FOUNDATIONS - 0.1)) * 0.75
    archer(ctx, 130, GROUND_Y + 10, 1.05, dr, 1, ar_a)
    archer(ctx, 950, GROUND_Y + 10, 1.05, dr, -1, ar_a)
    P.tag(ctx, "Psalm 11:2-3", 540, 300, seg(t, T_ARROWS - 0.2, T_ARROWS + 0.2), 1.0, 280)
    draw_text(ctx, "arrows on the string", F_SERIF_I, 72, "#FBF6EC", 540, 430, ease(seg(t, T_ARROWS - 0.2, T_STRING)) * (1 - ease(seg(t, T_FOUNDATIONS - 0.4, T_FOUNDATIONS - 0.1))), stroke=3, stroke_color="#1A222C")
    # foundations
    fa = ease(seg(t, T_FOUNDATIONS - 0.5, T_FOUNDATIONS))
    cr = ease(seg(t, T_FOUNDATIONS, T_DESTROYED))
    fall = ein(seg(t, T_DESTROYED - 0.05, T_DESTROYED + 0.9))
    for k, x in enumerate((340, 540, 740)):
        pillar(ctx, x, GROUND_Y + 10, 520, cr, fall * (0.8 + 0.2 * k), (-1, 1, 1)[k], fa)
    if fall > 0:
        ctx.set_source_rgba(0.85, 0.8, 0.7, 0.35 * (1 - fall) * fa)
        for k in range(18):
            a = k * 0.9
            rr = 60 + 300 * fall
            ctx.arc(540 + rr * math.cos(a), GROUND_Y - 40 - 0.3 * rr * abs(math.sin(a)), 30 * (1 - fall) + 8, 0, 2 * math.pi)
            ctx.fill()
    draw_text(ctx, "FOUNDATIONS", F_SERIF, 100, "#CFE0F5", 540, 430, ease(seg(t, T_FOUNDATIONS - 0.15, T_FOUNDATIONS + 0.1)) * (1 - ease(seg(t, T_RIGHTEOUS - 0.6, T_RIGHTEOUS - 0.3))), 0.94 + 0.06 * back_out(seg(t, T_FOUNDATIONS - 0.15, T_FOUNDATIONS + 0.2)), stroke=5, stroke_color="#1A222C")
    draw_text(ctx, "what can the righteous do?", F_SERIF_I, 66, "#E3B04B", 540, 430, ease(seg(t, T_RIGHTEOUS - 0.4, T_RIGHTEOUS)), stroke=3, stroke_color="#1A222C")
    grade(ctx, cool=0.2, desat=0.15)


def scene4(ctx, lt):
    """'In the Lord I take refuge.' The throne in heaven; the ground may shake, the throne doesn't."""
    t = lt + B4
    clear = ease(seg(t, T_LORD1 - 0.3, T_REFUGE1 + 0.4))
    sky(ctx, t, clear, 0.5 * (1 - clear))
    up = ease(seg(t, T_WHY - 0.2, T_TEMPLE))
    draw_text(ctx, "“In the LORD", F_SERIF, 108, "#FBF6EC", 540, lerp(720, 330, up), ease(seg(t, T_LORD1 - 0.3, T_LORD1)) * (1 - ease(seg(t, T_WHY - 0.2, T_WHY + 0.1))), stroke=5, stroke_color="#25303D")
    draw_text(ctx, "I take refuge.”", F_SERIF, 108, "#E3B04B", 540, lerp(850, 460, up), ease(seg(t, T_REFUGE1 - 0.4, T_REFUGE1)) * (1 - ease(seg(t, T_WHY - 0.2, T_WHY + 0.1))), stroke=5, stroke_color="#25303D")
    P.tag(ctx, "Psalm 11:1", 540, 560, seg(t, T_LORD1 - 0.2, T_LORD1 + 0.2), 1 - ease(seg(t, T_WHY - 0.2, T_WHY + 0.1)), 250)
    th = ease(seg(t, T_TEMPLE - 0.4, T_THRONE1 + 0.1))
    throne_heaven(ctx, 540, 640, 0.95, th, t)
    P.tag(ctx, "Psalm 11:4", 540, 180, seg(t, T_TEMPLE - 0.2, T_TEMPLE + 0.2), th, 250)
    draw_text(ctx, "his throne is in heaven", F_SERIF_I, 64, "#3B2A1E", 540, 790, ease(seg(t, T_HEAVEN - 0.4, T_HEAVEN)) * (1 - ease(seg(t, T_GROUND - 0.3, T_GROUND))))
    # below: the ground shakes, the figure holds on
    sh = seg(t, T_SHAKE - 0.1, T_SHAKE + 0.9)
    ground_band(ctx, GROUND_Y, lerpc(hexc("#1A1E24"), hexc("#6E7B5C"), clear), sh * (1 - sh) * 4, t)
    Q.person(ctx, 540, GROUND_Y + 20, 1.1, lerpc(hexc("#0F1215"), col("brown"), clear), 0, 0, 0, 0.3 + 0.6 * ease(seg(t, T_THRONE2 - 0.2, T_DOESNT)))
    draw_text(ctx, "the ground may shake", F_SERIF_I, 64, "#3B2A1E", 540, 790, ease(seg(t, T_GROUND - 0.2, T_SHAKE)) * (1 - ease(seg(t, T_THRONE2 - 0.3, T_THRONE2))))
    draw_text(ctx, "the throne doesn’t", F_SERIF, 80, "#A8741A", 540, 790, ease(seg(t, T_THRONE2 - 0.2, T_DOESNT)))
    grade(ctx, cool=0.2 * (1 - clear))


def scene5(ctx, lt):
    """God isn't distant: his eyes see, his eyelids test every person."""
    t = lt + B5
    sky(ctx, t, 1.0)
    ground_band(ctx, GROUND_Y, hexc("#6E7B5C"))
    # a few people below, each lit as the gaze passes over them
    look = math.sin(t * 1.3) * ease(seg(t, T_PERSON - 0.4, T_PERSON + 0.4))
    for k, x in enumerate((220, 420, 640, 860)):
        lit = clamp(1 - abs((x - 540) / 320 - look) * 1.5)
        Q.person(ctx, x, GROUND_Y + 20, (0.9, 1.05, 0.95, 0.85)[k], lerpc(hexc("#3A3530"), col("brown"), lit), 0, 0, 0, 0.2)
        if lit > 0.05:
            g = cairo.RadialGradient(x, GROUND_Y - 120, 10, x, GROUND_Y - 120, 200)
            g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.45 * lit)
            g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
            ctx.set_source(g)
            ctx.arc(x, GROUND_Y - 120, 200, 0, 2 * math.pi)
            ctx.fill()
    draw_text(ctx, "God isn’t distant", F_SERIF, 96, "#3B2A1E", 540, 300, ease(seg(t, T_DISTANT - 0.4, T_DISTANT)) * (1 - ease(seg(t, T_VERSE - 0.1, T_VERSE + 0.2))))
    ea = ease(seg(t, T_EYES1 - 0.4, T_SEE))
    open_ = lerp(1.0, 0.45, ease(seg(t, T_EYELIDS1 - 0.1, T_TEST + 0.2)))
    eye(ctx, 540, 600, 1.15, open_ * ea, ea, look, ea)
    P.tag(ctx, "Psalm 11:4", 540, 220, seg(t, T_VERSE - 0.2, T_VERSE + 0.2), 1.0, 250)
    draw_text(ctx, "his eyes see", F_SERIF_I, 70, "#3B2A1E", 540, 860, ease(seg(t, T_EYES1 - 0.2, T_SEE)) * (1 - ease(seg(t, T_EYELIDS1 - 0.3, T_EYELIDS1))))
    draw_text(ctx, "his eyelids test", F_SERIF_I, 70, "#A8741A", 540, 860, ease(seg(t, T_EYELIDS1 - 0.2, T_TEST)))
    draw_text(ctx, "every person", F_SERIF, 76, "#3B2A1E", 540, 960, ease(seg(t, T_PERSON - 0.3, T_PERSON)))


HEB = "עַפְעַפָּיו"


def scene6(ctx, lt):
    """Nugget: af'appav, 'his eyelids'; the eye narrows to look closely. Nothing gets past him."""
    t = lt + B6
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.5, "gold2", 8, -10)
    draw_text(ctx, "In Hebrew,", F_SERIF_I, 76, "#E8DCC8", 540, 330, ease(seg(t, T_HEBREW - 0.2, T_HEBREW + 0.1)) * (1 - ease(seg(t, T_AFAPPAV - 0.4, T_AFAPPAV - 0.1))))
    hb = ease(seg(t, T_AFAPPAV - 0.45, T_AFAPPAV - 0.1))
    reveal = ease(seg(t, T_AFAPPAV - 0.4, T_AFAPPAV + 0.5))
    rays(ctx, 540, 400, 0, 2 * math.pi, 18, 1000, hb * 0.6, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 210, 540, 400, reveal, hb, rtl=True)
    draw_text(ctx, "af'appav", F_SERIF_I, 86, "#FBF6EC", 540, 580, ease(seg(t, T_AFAPPAV + 0.2, T_AFAPPAV + 0.5)))
    draw_text(ctx, "“his eyelids”", F_SERIF_I, 70, "#E3B04B", 540, 680, ease(seg(t, T_EYELIDS2 - 0.3, T_EYELIDS2)))
    P.tag(ctx, "Psalm 11:4", 540, 200, seg(t, T_AFAPPAV - 0.2, T_AFAPPAV + 0.2), 1.0, 250)
    ea = ease(seg(t, T_PICTURE - 0.4, T_PICTURE))
    nar = ease(seg(t, T_NARROWING - 0.1, T_CLOSELY + 0.2))
    eye(ctx, 540, 1000, 0.95, lerp(1.0, 0.32, nar) * ea, ea, 0.5 * math.sin(t * 0.9) * (1 - nar), ea * 0.8)
    draw_text(ctx, "Nothing gets past him.", F_SERIF, 78, "#FFE3A3", 540, 1260, ease(seg(t, T_NOTHING - 0.3, T_PAST)), stroke=4, stroke_color="#2A1D14")


def scene7(ctx, lt):
    """Close: when fear says run, look up first. End card."""
    t = lt + B7
    sky(ctx, t, 1.0)
    mountain(ctx, 800, GROUND_Y - 40, 0.8, hexc("#7D8FA3"), 0.7)
    throne_heaven(ctx, 540, 520, 0.6, 0.5 * ease(seg(t, T_LOOK2 - 0.3, T_UP1 + 0.3)), t)
    ground_band(ctx, GROUND_Y, hexc("#6E7B5C"))
    run = 1 - ease(seg(t, T_STOP - 0.2, T_STOP + 0.2))
    up = ease(seg(t, T_LOOK2 - 0.2, T_UP1 + 0.3))
    ctx.save()
    ctx.translate(540, GROUND_Y + 20)
    ctx.rotate(0.16 * run * ease(seg(t, T_RUN2 - 0.4, T_RUN2)))
    Q.person(ctx, 0, 0, 1.2, col("dark"), 0, 0, 0, 0.3 + 0.7 * up)
    ctx.restore()
    draw_text(ctx, "fear says run", F_SERIF_I, 70, "#3B2A1E", 540, 760, ease(seg(t, T_FEAR - 0.3, T_FEAR)) * (1 - ease(seg(t, T_STOP - 0.3, T_STOP))))
    draw_text(ctx, "stop. look up.", F_SERIF, 90, "#A8741A", 540, 760, ease(seg(t, T_STOP - 0.2, T_UP1)) * (1 - ease(seg(t, T_LOUD - 0.3, T_LOUD))))
    end = ease(seg(t, T_DONT - 0.35, T_DONT))
    draw_text(ctx, "PSALM 11", F_SERIF, 54, "#3B2A1E", 540, 300, end)
    ctx.set_source_rgba(*col("gold", end))
    ctx.rectangle(490, 355, 100, 4)
    ctx.fill()
    draw_text(ctx, "“In the LORD I take refuge.”", F_SERIF_I, 62, "#3B2A1E", 540, 760, ease(seg(t, T_LOUD, T_REFUGE2)) * (1 - end))
    draw_text(ctx, "Don’t flee.", F_SERIF, 140, "#3B2A1E", 540, 490, end, 0.92 + 0.08 * back_out(seg(t, T_DONT - 0.35, T_DONT)))
    ls = ease(seg(t, T_UP2 - 0.4, T_UP2 + 0.05))
    draw_text(ctx, "Look up.", F_SERIF, 140, "#A8741A", 540, 650, ls, 0.92 + 0.08 * back_out(seg(t, T_UP2 - 0.4, T_UP2 + 0.1)))
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5), (B6, B7, scene6),
            (B7, DUR + 1, scene7)]

if __name__ == "__main__":
    E.main(sys.argv)
