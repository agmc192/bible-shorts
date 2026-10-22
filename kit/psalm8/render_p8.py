"""Psalm 8 Short. Violet hilltop night, then a golden pastoral day. Central image: a small figure under the stars, crowned."""
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

E = Episode(8)
wt, DUR = E.wt, E.dur
T_LOOKED = wt("looked"); T_SKY = wt("sky"); T_TINY = wt("tiny"); T_DAVID = wt("david"); T_PSALM = wt("psalm")
T_MOON = wt("moon"); T_STARS1 = wt("stars", 1); T_WORK = wt("work"); T_FINGERS = wt("fingers"); T_ASKS = wt("asks")
T_MAN = wt("man"); T_MINDFUL1 = wt("mindful", 1); T_NOTICE = wt("notice"); T_CROWNED1 = wt("crowned", 1)
T_GLORY1 = wt("glory", 1); T_HONOR1 = wt("honor", 1); T_CHARGE = wt("charge"); T_SHEEP = wt("sheep"); T_OXEN = wt("oxen")
T_FISH = wt("fish"); T_SEA = wt("sea"); T_WORD = wt("word"); T_MINDFUL2 = wt("mindful", 2); T_ZAKAR = wt("zahkhar")
T_REMEMBER = wt("remember"); T_SET = wt("set"); T_STARS2 = wt("stars", 2); T_KEEPS = wt("keeps"); T_MIND = wt("mind")
T_HEBREWS = wt("hebrews"); T_JESUS = wt("jesus"); T_LOWER = wt("lower"); T_LITTLE = wt("little"); T_WHILE = wt("while")
T_CROWNED2 = wt("crowned", 2); T_GLORY2 = wt("glory", 2); T_SUFFERED = wt("suffered"); T_DEATH = wt("death")
T_TONIGHT = wt("tonight"); T_OUTSIDE = wt("outside"); T_UP = wt("up", 2); T_SMALL1 = wt("small", 1)
T_GRATEFUL = wt("grateful"); T_SMALL2 = wt("small", 2); T_REMEMBERED = wt("remembered")

B1 = 0.0
B2 = T_DAVID - 0.3
B3 = T_MOON - 0.9
B4 = T_ASKS - 0.3
B5 = T_NOTICE - 0.9
B6 = T_WORD - 0.5
B7 = T_HEBREWS - 0.35
B8 = T_TONIGHT - 0.35

E.zooms = [(0.1, 0.12), (T_TINY, 0.08), (T_FINGERS, 0.06), (T_MAN, 0.08), (T_CROWNED1, 0.10), (T_ZAKAR, 0.12),
           (T_MIND, 0.06), (T_JESUS, 0.08), (T_DEATH, 0.06), (T_GLORY2, 0.08), (T_REMEMBERED, 0.07)]
E.shakes = [(0.1, 14, 0.6), (T_TINY, 6, 0.4), (T_CROWNED1, 8, 0.4), (T_ZAKAR, 10, 0.5), (T_JESUS, 6, 0.4)]
E.flashes = [(0.1, (0.85, 0.85, 1), 0.4, 0.35), (T_CROWNED1, (1, 0.9, 0.6), 0.4, 0.45), (T_ZAKAR, (1, 0.85, 0.5), 0.3, 0.4),
             (T_GLORY2, (1, 0.92, 0.7), 0.35, 0.45), (T_REMEMBERED, (1, 0.95, 0.85), 0.3, 0.4)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6, B7, B8)]

VIO = hexc("#251B3E")
VIO2 = hexc("#46336B")
VIO3 = hexc("#7A5C8E")
HILL_Y = 1240

_sr = random.Random(88)
STARS = [(_sr.uniform(0, W), _sr.uniform(0, 1150), _sr.uniform(1.5, 4.5), _sr.uniform(0, 6.28)) for _ in range(160)]
CONST = [[(200, 320), (290, 260), (380, 300), (450, 230), (560, 270)],
         [(640, 520), (720, 440), (830, 470), (900, 380)],
         [(150, 640), (240, 590), (300, 690), (420, 650)]]


def night(ctx, t, k=1.0, stars=1.0, warm=0.0):
    g = cairo.LinearGradient(0, 0, 0, HILL_Y)
    g.add_color_stop_rgba(0, *lerpc(VIO, hexc("#F2D7A8"), warm))
    g.add_color_stop_rgba(0.7, *lerpc(VIO2, hexc("#F3C68E"), warm))
    g.add_color_stop_rgba(1, *lerpc(VIO3, hexc("#E9A46E"), warm))
    ctx.set_source(g)
    ctx.paint()
    # milky way band
    ctx.save()
    ctx.translate(540, 520)
    ctx.rotate(-0.5)
    mg = cairo.LinearGradient(0, -170, 0, 170)
    mg.add_color_stop_rgba(0, 1, 1, 1, 0)
    mg.add_color_stop_rgba(0.5, 0.9, 0.85, 1.0, 0.16 * stars * (1 - warm))
    mg.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(mg)
    ctx.rectangle(-1100, -170, 2200, 340)
    ctx.fill()
    ctx.restore()
    for x, y, s, ph in STARS:
        tw = 0.5 + 0.5 * math.sin(t * 1.7 + ph)
        ctx.set_source_rgba(1, 0.96, 0.85, (0.35 + 0.6 * tw) * stars * (1 - warm))
        ctx.arc(x, y, s, 0, 2 * math.pi)
        ctx.fill()


def hill(ctx, k_warm=0.0, y=HILL_Y):
    ctx.set_source_rgba(*lerpc(hexc("#171128"), hexc("#7D8A4A"), k_warm))
    ctx.move_to(0, H)
    ctx.line_to(0, y + 60)
    ctx.curve_to(260, y - 40, 760, y - 60, W, y + 40)
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.fill()


def sheep(ctx, x, y, s, alpha):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("cream2", alpha))
    for dx, dy, r in [(-30, 0, 34), (0, -14, 38), (30, 0, 34), (0, 10, 36)]:
        ctx.arc(dx, dy, r, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgba(*col("dark", alpha))
    ctx.arc(58, -10, 18, 0, 2 * math.pi)
    ctx.fill()
    for lx in (-24, 22):
        ctx.rectangle(lx, 30, 9, 34)
    ctx.fill()
    ctx.restore()


def ox(ctx, x, y, s, alpha):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("brown2", alpha))
    rounded(ctx, -80, -40, 150, 76, 34)
    ctx.fill()
    ctx.arc(86, -24, 28, 0, 2 * math.pi)
    ctx.fill()
    for lx in (-60, -26, 22, 52):
        ctx.rectangle(lx, 26, 14, 50)
    ctx.fill()
    ctx.set_source_rgba(*col("cream2", alpha))
    ctx.set_line_width(7)
    ctx.move_to(80, -44)
    ctx.curve_to(70, -70, 90, -80, 100, -70)
    ctx.move_to(98, -44)
    ctx.curve_to(110, -70, 130, -66, 126, -50)
    ctx.stroke()
    ctx.restore()


def fish(ctx, x, y, s, alpha, flip=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * flip, s)
    ctx.set_source_rgba(*col("water2", alpha))
    ctx.save()
    ctx.scale(1, 0.5)
    ctx.arc(0, 0, 50, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.move_to(-40, 0)
    ctx.line_to(-80, -24)
    ctx.line_to(-80, 24)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def bird(ctx, x, y, s, alpha):
    ctx.set_source_rgba(*col("dark", alpha))
    ctx.set_line_width(5 * s)
    ctx.move_to(x - 30 * s, y)
    ctx.curve_to(x - 15 * s, y - 16 * s, x - 5 * s, y - 10 * s, x, y)
    ctx.curve_to(x + 5 * s, y - 10 * s, x + 15 * s, y - 16 * s, x + 30 * s, y)
    ctx.stroke()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: stars burst on; we pull back until the figure on the hill is tiny."""
    t = lt
    on = ease(seg(lt, 0.0, 0.25))
    night(ctx, t, 1, on)
    ctx.save()
    pull = ease(seg(lt, 0.1, 2.6))
    cam(ctx, 540, HILL_Y - 120, lerp(3.2, 1.0, pull))
    hill(ctx)
    R.figure(ctx, 540, HILL_Y - 50, 0.55, hexc("#0E0A18"), 0.15)
    ctx.restore()
    kword(ctx, "TINY", t, T_TINY - 0.05, 540, 300, 220, "#E3B04B", B2 - T_TINY + 0.2)


def scene2(ctx, lt):
    t = lt + B2
    night(ctx, t)
    hill(ctx)
    R.figure(ctx, 540, HILL_Y - 50, 0.55, hexc("#0E0A18"), 0.15)
    a = ease(seg(t, T_PSALM - 0.3, T_PSALM))
    draw_text(ctx, "PSALM 8", F_SERIF, 160, "#FBF6EC", 540, 520, ease(seg(lt, 0.0, 0.3)),
              0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#251B3E")
    ctx.set_source_rgba(*col("gold2", a))
    ctx.rectangle(440, 630, 200, 6)
    ctx.fill()
    draw_text(ctx, "A psalm of David", F_SERIF_I, 66, "#E3D6F0", 540, 720, ease(seg(lt, 0.15, 0.5)))


def scene3(ctx, lt):
    """The moon and the stars, drawn by trails of light: the work of God's fingers."""
    t = lt + B3
    night(ctx, t)
    Q.moon(ctx, 820, 260, 70)
    hill(ctx)
    R.figure(ctx, 540, HILL_Y - 50, 0.7, hexc("#0E0A18"), 0.6 * ease(seg(t, T_MOON - 0.3, T_MOON)))
    draw = ease(seg(t, T_STARS1 - 0.2, T_FINGERS + 0.5))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for ci, pts in enumerate(CONST):
        local = clamp(draw * 3 - ci)
        if local <= 0:
            continue
        n = len(pts) - 1
        ctx.set_source_rgba(1, 0.86, 0.55, 0.85)
        ctx.set_line_width(5)
        ctx.move_to(*pts[0])
        for i in range(1, n + 1):
            f = clamp(local * n - (i - 1))
            if f <= 0:
                break
            x = lerp(pts[i - 1][0], pts[i][0], f)
            y = lerp(pts[i - 1][1], pts[i][1], f)
            ctx.line_to(x, y)
        ctx.stroke()
        for i, (x, y) in enumerate(pts):
            if local * n >= i:
                g = cairo.RadialGradient(x, y, 1, x, y, 30)
                g.add_color_stop_rgba(0, 1, 0.95, 0.8, 1)
                g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
                ctx.set_source(g)
                ctx.arc(x, y, 30, 0, 2 * math.pi)
                ctx.fill()
    P.tag(ctx, "Psalm 8:3", 540, 820, seg(t, T_WORK - 0.2, T_WORK + 0.2), 1.0, 240)
    draw_text(ctx, "the work of your fingers", F_SERIF_I, 62, "#FBF6EC", 540, 930, ease(seg(t, T_WORK - 0.2, T_FINGERS + 0.1)))


def scene4(ctx, lt):
    """'What is man, that you are mindful of him?'"""
    t = lt + B4
    night(ctx, t)
    hill(ctx)
    z = lerp(1.0, 1.3, ease(seg(lt, 0, B5 - B4)))
    ctx.save()
    cam(ctx, 540, HILL_Y - 60, z)
    R.figure(ctx, 540, HILL_Y - 50, 0.7, hexc("#0E0A18"), 0.6)
    ctx.restore()
    P.tag(ctx, "Psalm 8:4", 540, 220, seg(t, T_MAN - 0.3, T_MAN), 1.0, 240)
    draw_text(ctx, "“What is man,", F_SERIF_I, 96, "#FBF6EC", 540, 420, ease(seg(t, T_MAN - 0.3, T_MAN + 0.1)), stroke=3, stroke_color="#251B3E")
    draw_text(ctx, "that you are", F_SERIF_I, 76, "#E3D6F0", 540, 540, ease(seg(t, T_MINDFUL1 - 0.6, T_MINDFUL1 - 0.2)))
    draw_text(ctx, "mindful of him?”", F_SERIF_I, 96, "#E3B04B", 540, 650, ease(seg(t, T_MINDFUL1 - 0.2, T_MINDFUL1 + 0.2)), stroke=3, stroke_color="#251B3E")


def scene5(ctx, lt):
    """Crowned with glory and honor; dawn over a world of sheep, oxen, birds and fish."""
    t = lt + B5
    warm = ease(seg(t, T_NOTICE - 0.4, T_CROWNED1 + 0.4))
    night(ctx, t, 1, 1, warm)
    rays(ctx, 540, HILL_Y - 40, math.radians(190), math.radians(350), 14, 1500, 0.7 * warm, t * 0.4)
    hill(ctx, warm)
    cr = ease(seg(t, T_CROWNED1 - 0.3, T_CROWNED1 + 0.3))
    Q.person(ctx, 540, HILL_Y - 40, 1.25, col("brown"), 0.0, 0, 0, 0.35 + 0.4 * cr)
    if cr > 0:
        cy = lerp(500, HILL_Y - 40 - 1.25 * 178 - 70, cr)
        P.crown(ctx, 540, cy, 0.5, 1.0, 0.8 * cr)
    draw_text(ctx, "glory", F_SERIF_I, 70, "#A8741A", 300, 520, ease(seg(t, T_GLORY1 - 0.2, T_GLORY1 + 0.2)) * (1 - ease(seg(t, T_CHARGE - 0.3, T_CHARGE))))
    draw_text(ctx, "& honor", F_SERIF_I, 70, "#A8741A", 780, 520, ease(seg(t, T_HONOR1 - 0.2, T_HONOR1 + 0.2)) * (1 - ease(seg(t, T_CHARGE - 0.3, T_CHARGE))))
    # the world placed in their care
    sh = ease(seg(t, T_SHEEP - 0.2, T_SHEEP + 0.2))
    for i, (x, y) in enumerate([(170, HILL_Y + 60), (300, HILL_Y + 110), (130, HILL_Y + 170)]):
        sheep(ctx, x, y, 0.9, sh * clamp(back_out(seg(t, T_SHEEP - 0.2 + i * 0.1, T_SHEEP + 0.2 + i * 0.1))))
    ox(ctx, 860, HILL_Y + 90, 1.0, ease(seg(t, T_OXEN - 0.2, T_OXEN + 0.2)))
    bd = ease(seg(t, T_CHARGE - 0.2, T_CHARGE + 0.3))
    for i in range(4):
        bird(ctx, 200 + i * 180 + 30 * math.sin(t + i), 300 + 40 * math.sin(t * 1.5 + i * 2), 1.2, bd)
    fs = ease(seg(t, T_FISH - 0.2, T_SEA + 0.1))
    if fs > 0:
        ctx.set_source_rgba(*col("water", 0.85 * fs))
        ctx.rectangle(0, 1620, W, H)
        ctx.fill()
        for i in range(3):
            fish(ctx, 200 + i * 300 + 40 * math.sin(t * 2 + i), 1720 + 30 * i, 0.9, fs, (-1) ** i)
    P.tag(ctx, "Psalm 8:5-8", 540, 200, seg(t, T_CROWNED1 - 0.1, T_CROWNED1 + 0.3), 1.0, 290)
    kword(ctx, "CROWNED", t, T_CROWNED1 - 0.04, 540, 360, 170, "#E3B04B", T_GLORY1 - T_CROWNED1 + 0.2)


HEB = "זָכַר"


def scene6(ctx, lt):
    """Nugget: zakar, to remember. The God who set the stars keeps you in mind."""
    t = lt + B6
    night(ctx, t, 1, 0.6)
    ctx.set_source_rgba(0.05, 0.03, 0.1, 0.55)
    ctx.paint()
    dust(ctx, t, 0.5, "gold2", 6, -12)
    draw_text(ctx, "“mindful”", F_SERIF_I, 80, "#E3D6F0", 540, 330, ease(seg(t, T_MINDFUL2 - 0.3, T_MINDFUL2 + 0.1)) * (1 - ease(seg(t, T_SET - 0.4, T_SET))))
    hb = ease(seg(t, T_ZAKAR - 0.5, T_ZAKAR - 0.2)) * (1 - ease(seg(t, T_SET - 0.4, T_SET)))
    reveal = ease(seg(t, T_ZAKAR - 0.45, T_ZAKAR + 0.3))
    rays(ctx, 540, 600, 0, 2 * math.pi, 18, 1000, hb * 0.8, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 300, 540, 600, reveal, hb, rtl=True)
    sub = ease(seg(t, T_ZAKAR + 0.1, T_ZAKAR + 0.5)) * (1 - ease(seg(t, T_SET - 0.4, T_SET)))
    draw_text(ctx, "zakar", F_SERIF_I, 96, "#FBF6EC", 540, 820, sub)
    draw_text(ctx, "to remember", F_SERIF_R, 64, "#E3B04B", 540, 930, ease(seg(t, T_REMEMBER - 0.2, T_REMEMBER + 0.2)) * (1 - ease(seg(t, T_SET - 0.4, T_SET))))
    # stars placed, then one star settles over a small figure
    pl = ease(seg(t, T_SET - 0.3, T_STARS2 + 0.3))
    if pl > 0:
        for i, (x, y, s, ph) in enumerate(STARS[:60]):
            u = clamp(pl * 2 - i / 60)
            ctx.set_source_rgba(1, 0.95, 0.8, 0.9 * u)
            ctx.arc(x, y * 0.8, s * 1.3, 0, 2 * math.pi)
            ctx.fill()
        hill(ctx)
        R.figure(ctx, 540, HILL_Y - 50, 0.7, hexc("#0E0A18"), 0.2)
        km = ease(seg(t, T_KEEPS - 0.2, T_MIND + 0.3))
        sx, sy = lerp(860, 540, km), lerp(260, HILL_Y - 330, km)
        g = cairo.RadialGradient(sx, sy, 2, sx, sy, 120)
        g.add_color_stop_rgba(0, 1, 0.97, 0.85, 1)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.arc(sx, sy, 120, 0, 2 * math.pi)
        ctx.fill()
        R.star_path(ctx, sx, sy, 26, 11, 5, t)
        ctx.set_source_rgba(1, 0.95, 0.75, 1)
        ctx.fill()
        draw_text(ctx, "keeps you in mind", F_SERIF_I, 72, "#E3B04B", 540, 330, km)


def scene7(ctx, lt):
    """Hebrews 2 applies the psalm to Jesus: made lower for a little while, crowned because he suffered death."""
    t = lt + B7
    warm = ease(seg(t, T_CROWNED2 - 0.4, T_GLORY2 + 0.4))
    night(ctx, t, 1, 0.8, 0.7 * warm)
    P.tag(ctx, "Hebrews 2:6-9", 540, 200, seg(lt, 0.0, 0.3), 1.0, 320)
    draw_text(ctx, "applied to Jesus", F_SERIF_I, 70, "#FBF6EC", 540, 320, ease(seg(t, T_JESUS - 0.2, T_JESUS + 0.2)), stroke=3, stroke_color="#251B3E")
    hill(ctx, 0.5 * warm)
    # made lower: a figure descends from the light to the hill
    down = ease(seg(t, T_LOWER - 0.3, T_WHILE))
    rays(ctx, 540, -80, math.radians(60), math.radians(120), 10, 1700, 0.8 * (1 - 0.5 * down), t * 0.4)
    fy = lerp(560, HILL_Y - 50, down)
    cross_a = ease(seg(t, T_SUFFERED - 0.2, T_DEATH + 0.1))
    R.figure(ctx, 540, fy, 0.9, col("brown"), 0.3 * (1 - cross_a), )
    draw_text(ctx, "made lower", F_SERIF_I, 64, "#E3D6F0", 300, 760, ease(seg(t, T_LOWER - 0.2, T_LOWER + 0.2)) * (1 - ease(seg(t, T_CROWNED2 - 0.3, T_CROWNED2))))
    draw_text(ctx, "for a little while", F_SERIF_I, 56, "#E3D6F0", 780, 860, ease(seg(t, T_LITTLE - 0.2, T_LITTLE + 0.2)) * (1 - ease(seg(t, T_CROWNED2 - 0.3, T_CROWNED2))))
    # a simple cross on the hill, and a crown of light above it
    if cross_a > 0:
        ctx.set_source_rgba(*hexc("#1A1226")[:3], cross_a)
        ctx.rectangle(770, HILL_Y - 420, 26, 400)
        ctx.rectangle(700, HILL_Y - 340, 166, 24)
        ctx.fill()
    cr = ease(seg(t, T_CROWNED2 - 0.2, T_GLORY2 + 0.2))
    if cr > 0:
        P.crown(ctx, 540, lerp(420, fy - 230, cr), 0.55, cr, cr)
    draw_text(ctx, "crowned with glory and honor", F_SERIF_I, 60, "#FFE3A3", 540, 440, cr * (1 - ease(seg(t, B8 - 0.4, B8))), stroke=4, stroke_color="#3B2A1E")
    draw_text(ctx, "because he suffered death", F_SERIF_I, 60, "#FBF6EC", 540, 1000, cross_a, stroke=4, stroke_color="#3B2A1E")


def scene8(ctx, lt):
    """Close: step outside and look up. Small, but remembered."""
    t = lt + B8
    night(ctx, t)
    Q.moon(ctx, 820, 260, 60)
    hill(ctx)
    # a doorway glowing at the foot of the hill
    da = ease(seg(t, T_OUTSIDE - 0.4, T_OUTSIDE))
    ctx.set_source_rgba(1, 0.85, 0.55, 0.85 * da)
    rounded(ctx, 160, HILL_Y - 150, 110, 190, 10)
    ctx.fill()
    walk = ease(seg(t, T_OUTSIDE - 0.2, T_UP + 0.2))
    look = ease(seg(t, T_UP - 0.2, T_UP + 0.3))
    R.figure(ctx, lerp(215, 540, walk), HILL_Y - 40 - 10 * walk, 0.8, hexc("#0E0A18"), 0.15 + 0.5 * look)
    g = ease(seg(t, T_GRATEFUL - 0.3, T_GRATEFUL + 0.3))
    if g > 0:
        rays(ctx, 540, 180, 0, 2 * math.pi, 16, 900, 0.5 * g, t * 0.3)
    end = ease(seg(t, T_SMALL2 - 0.35, T_SMALL2))
    draw_text(ctx, "PSALM 8", F_SERIF, 54, "#FBF6EC", 540, 380, end, stroke=3, stroke_color="#251B3E")
    ctx.set_source_rgba(*col("cream2", end))
    ctx.rectangle(490, 435, 100, 4)
    ctx.fill()
    draw_text(ctx, "Small,", F_SERIF, 140, "#FBF6EC", 540, 570, end, 0.92 + 0.08 * back_out(seg(t, T_SMALL2 - 0.35, T_SMALL2)), stroke=4, stroke_color="#251B3E")
    rm = ease(seg(t, T_REMEMBERED - 0.3, T_REMEMBERED + 0.05))
    draw_text(ctx, "but remembered.", F_SERIF, 110, "#FFE3A3", 540, 730, rm, 0.92 + 0.08 * back_out(seg(t, T_REMEMBERED - 0.3, T_REMEMBERED + 0.1)), stroke=4, stroke_color="#251B3E")
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5),
            (B6, B7, scene6), (B7, B8, scene7), (B8, DUR + 1, scene8)]

if __name__ == "__main__":
    E.main(sys.argv)
