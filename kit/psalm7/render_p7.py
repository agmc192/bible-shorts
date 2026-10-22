"""Psalm 7 Short. Daylight stone-and-olive palette. Central image: the pit the plotter digs and falls into."""
import sys, math, random
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/psalm4")
import cairo
from engine import Episode
import render as R
import render_v2 as V
import render_p2 as P
import render_p3 as Q
import render_p4 as P4
from render import (W, H, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, text_surf, rounded, cam,
                    F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword

E = Episode(7)
wt, DUR = E.wt, E.dur
T_LIES = wt("lies"); T_PSALM = wt("psalm"); T_SONG = wt("song"); T_WORDS = wt("words"); T_CUSH = wt("cush")
T_BENJ = wt("benjaminite"); T_RUNS = wt("runs"); T_REFUGE = wt("refuge"); T_EVEN = wt("even")
T_WRONG = wt("wrong"); T_ENEMY = wt("enemy"); T_CATCH = wt("catch"); T_LEAVES = wt("leaves"); T_CASE1 = wt("case", 1)
T_RIGHTEOUS = wt("righteous"); T_JUDGE1 = wt("judge", 1); T_TWIST = wt("twist"); T_PLOTS = wt("plots")
T_DIGS = wt("digs"); T_PIT1 = wt("pit", 1); T_FALLS = wt("falls"); T_HOLE = wt("hole"); T_TROUBLE = wt("trouble")
T_HEAD = wt("head"); T_VERSE = wt("verse"); T_NINE = wt("nine"); T_TESTS = wt("tests"); T_HEART1 = wt("heart")
T_MIND = wt("mind"); T_HEBREW = wt("hebrew"); T_HEARTS = wt("hearts"); T_KIDNEYS = wt("kidneys")
T_KLAYOT = wt("klahyote"); T_SEAT = wt("seat"); T_DEEPEST = wt("deepest"); T_SEES = wt("sees"); T_DOWN = wt("down")
T_TODAY = wt("today"); T_DIG2 = wt("dig"); T_BRING = wt("bring"); T_CASE2 = wt("case", 2); T_JUDGE2 = wt("judge", 2)
T_LEAVE = wt("leave"); T_VERDICT = wt("verdict"); T_KEEP = wt("keep"); T_PEACE = wt("peace")

B1 = 0.0
B2 = T_PSALM - 0.3
B3 = T_RUNS - 0.55
B4 = T_LEAVES - 0.45
B5 = T_TWIST - 0.55
B6 = T_VERSE - 0.4
B7 = T_TODAY - 0.5

E.zooms = [(0.1, 0.12), (T_LIES, 0.07), (T_CUSH, 0.05), (T_REFUGE, 0.08), (T_CATCH, 0.06), (T_JUDGE1, 0.10),
           (T_TWIST, 0.10), (T_FALLS, 0.10), (T_HEAD, 0.08), (T_KLAYOT, 0.12), (T_DOWN, 0.07), (T_VERDICT, 0.06),
           (T_PEACE, 0.06)]
E.shakes = [(0.1, 16, 0.6), (T_LIES, 8, 0.4), (T_CATCH, 6, 0.4), (T_JUDGE1, 8, 0.4), (T_FALLS + 0.15, 16, 0.6),
            (T_HEAD + 0.1, 10, 0.4), (T_KLAYOT, 10, 0.5)]
E.flashes = [(0.1, (1, 1, 1), 0.4, 0.3), (T_REFUGE, (1, 0.92, 0.7), 0.25, 0.4), (T_JUDGE1, (1, 0.9, 0.6), 0.35, 0.4),
             (T_FALLS + 0.15, (1, 0.95, 0.9), 0.3, 0.3), (T_KLAYOT, (1, 0.85, 0.5), 0.3, 0.4),
             (T_DOWN, (1, 0.92, 0.7), 0.25, 0.4), (T_PEACE, (1, 0.95, 0.85), 0.3, 0.4)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6, B7)]

STONE = hexc("#CDBB98")
STONE2 = hexc("#B19C77")
OLIVE = hexc("#7D8A4A")
OLIVE2 = hexc("#5E6B35")
EARTH = hexc("#7A5537")
EARTH2 = hexc("#5C3E28")
GROUND_Y = 1150


# ---------------------------------------------------------------- helpers
def day_sky(ctx, k=1.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND_Y)
    g.add_color_stop_rgba(0, *lerpc(hexc("#E9D9B8"), hexc("#F6E7C4"), k))
    g.add_color_stop_rgba(1, *lerpc(hexc("#D8C49C"), hexc("#F2D9A6"), k))
    ctx.set_source(g)
    ctx.paint()


def land(ctx, t, px=0.0):
    V.hills(ctx, GROUND_Y - 170, 70, hexc("#C7B087"), px * 0.3, 71)
    V.hills(ctx, GROUND_Y - 90, 50, OLIVE, px * 0.6, 72, 1.3)
    ctx.set_source_rgba(*STONE)
    ctx.rectangle(0, GROUND_Y, W, H)
    ctx.fill()


def shovel(ctx, x, y, ang, s=1.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("brown2", alpha))
    ctx.set_line_width(10)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, 0)
    ctx.line_to(0, 170)
    ctx.stroke()
    ctx.set_source_rgba(*hexc("#8C8C8C")[:3], alpha)
    ctx.move_to(-30, 165)
    ctx.line_to(30, 165)
    ctx.line_to(22, 230)
    ctx.curve_to(10, 248, -10, 248, -22, 230)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def rock_refuge(ctx, cx, base, s, glow, t):
    if glow > 0:
        rays(ctx, cx, base - 260 * s, 0, 2 * math.pi, 14, 900, glow, t * 0.4)
        g = cairo.RadialGradient(cx, base - 220 * s, 20, cx, base - 220 * s, 420 * s)
        g.add_color_stop_rgba(0, 1, 0.93, 0.7, 0.6 * glow)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.arc(cx, base - 220 * s, 420 * s, 0, 2 * math.pi)
        ctx.fill()
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(s, s)
    ctx.set_source_rgba(*STONE2)
    ctx.move_to(-260, 0)
    ctx.curve_to(-280, -150, -200, -330, -60, -380)
    ctx.curve_to(60, -420, 200, -330, 240, -190)
    ctx.curve_to(270, -90, 270, -30, 260, 0)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*hexc("#9A8562"))
    ctx.move_to(-120, -300)
    ctx.curve_to(-60, -250, -40, -170, -70, -90)
    ctx.set_line_width(8)
    ctx.stroke()
    ctx.move_to(120, -260)
    ctx.curve_to(90, -200, 110, -140, 150, -100)
    ctx.stroke()
    ctx.restore()


def scales(ctx, cx, top, s, tilt, alpha=1.0, glow=0.0, t=0.0):
    """Balance scales hanging from a ray of light; tilt -1..1."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, top)
    ctx.scale(s, s)
    gold = col("gold2", alpha)
    ctx.set_source_rgba(*gold)
    ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, 0)
    ctx.line_to(0, 120)
    ctx.stroke()
    a = 0.22 * tilt
    lx, ly = -260 * math.cos(a), 120 - 260 * math.sin(a)
    rx, ry = 260 * math.cos(a), 120 + 260 * math.sin(a)
    ctx.set_line_width(12)
    ctx.move_to(lx, ly)
    ctx.line_to(rx, ry)
    ctx.stroke()
    ctx.arc(0, 120, 16, 0, 2 * math.pi)
    ctx.fill()
    for x, y in ((lx, ly), (rx, ry)):
        ctx.set_line_width(4)
        ctx.move_to(x, y)
        ctx.line_to(x - 80, y + 180)
        ctx.move_to(x, y)
        ctx.line_to(x + 80, y + 180)
        ctx.stroke()
        ctx.move_to(x - 100, y + 180)
        ctx.curve_to(x - 80, y + 230, x + 80, y + 230, x + 100, y + 180)
        ctx.close_path()
        ctx.fill()
    ctx.restore()
    return (cx + lx * s, top + (ly + 190) * s), (cx + rx * s, top + (ry + 190) * s)


def scroll(ctx, cx, cy, w, open_, alpha=1.0, rot=0.0, label=None):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ww = 30 + (w - 30) * open_
    ctx.set_source_rgba(*col("cream2", alpha))
    ctx.rectangle(-ww / 2, -40, ww, 80)
    ctx.fill()
    ctx.set_source_rgba(*col("brown2", alpha))
    for sx in (-1, 1):
        rounded(ctx, sx * ww / 2 - 14, -54, 28, 108, 12)
        ctx.fill()
    ctx.restore()
    if label and open_ > 0.85:
        draw_text(ctx, label, F_SERIF_I, 34, "#3B2A1E", cx, cy, alpha * seg(open_, 0.85, 1.0))


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: dark speech bubbles of lies swarm a lone figure."""
    t = lt
    day_sky(ctx, 0.3)
    land(ctx, t)
    R.figure(ctx, 540, GROUND_Y + 20, 1.6, col("brown"), 0.0)
    r = random.Random(7)
    for i in range(9):
        side = -1 if i % 2 == 0 else 1
        delay = 0.05 + i * 0.18
        u = eout(seg(lt, delay, delay + 0.6))
        x0 = 540 + side * 800
        y0 = r.uniform(300, 1000)
        x1 = 540 + side * r.uniform(150, 380)
        y1 = r.uniform(380, 900)
        x, y = lerp(x0, x1, u) + 6 * math.sin(t * 3 + i), lerp(y0, y1, u)
        P4.bubble(ctx, x, y, 210, 100, hexc("#3E3A40"), 0.92 * u, -side)
        P4.scribble(ctx, x, y, 140, 30 + i + int(t * 4), 0.9 * u)
    # first-frame slam: a huge bubble flashes in and settles
    big = ease(seg(lt, 0.0, 0.12)) * (1 - ease(seg(lt, 0.45, 0.8)))
    if big > 0:
        P4.bubble(ctx, 540, 640, 820, 380, hexc("#2E2A30"), big, 1)
        P4.scribble(ctx, 540, 640, 560, 99, big)
    kword(ctx, "LIES", t, T_LIES - 0.04, 540, 240, 210, "#E07A5F", B2 - T_LIES)
    grade(ctx, desat=0.25)


def scene2(ctx, lt):
    """Title on a stone tablet; the words of Cush unroll."""
    t = lt + B2
    day_sky(ctx, 0.6)
    land(ctx, t, 40 * lt)
    pop = back_out(seg(lt, -0.05, 0.3))
    ctx.save()
    ctx.translate(540, 620)
    ctx.scale(max(0.01, pop), max(0.01, pop))
    ctx.translate(-540, -620)
    ctx.set_source_rgba(0, 0, 0, 0.2)
    rounded(ctx, 130, 254, 820, 760, 60)
    ctx.fill()
    ctx.set_source_rgba(*STONE2)
    rounded(ctx, 120, 240, 840, 760, 60)
    ctx.fill()
    ctx.set_source_rgba(*hexc("#9A8562"))
    ctx.set_line_width(8)
    rounded(ctx, 150, 270, 780, 700, 48)
    ctx.stroke()
    draw_text(ctx, "PSALM 7", F_SERIF, 150, "#3B2A1E", 540, 430, ease(seg(t, T_PSALM - 0.2, T_PSALM + 0.2)))
    ctx.set_source_rgba(*col("gold"))
    ctx.rectangle(440, 530, 200, 6)
    ctx.fill()
    draw_text(ctx, "A song of David", F_SERIF_I, 64, "#4A3524", 540, 620, ease(seg(t, T_SONG - 0.1, T_SONG + 0.3)))
    sc = ease(seg(t, T_WORDS - 0.2, T_CUSH + 0.3))
    scroll(ctx, 540, 800, 700, sc, ease(seg(t, T_WORDS - 0.3, T_WORDS)), 0, "the words of Cush, a Benjaminite")
    ctx.restore()
    P.tag(ctx, "Psalm 7 heading", 540, 1110, seg(t, T_CUSH - 0.1, T_CUSH + 0.3), 1.0, 360)


def scene3(ctx, lt):
    """David runs to the rock of refuge; 'if I've done this wrong...'"""
    t = lt + B3
    day_sky(ctx, 1.0)
    land(ctx, t, 30 * lt)
    glow = ease(seg(t, T_REFUGE - 0.4, T_REFUGE + 0.2))
    rock_refuge(ctx, 800, GROUND_Y + 10, 1.0, glow, t)
    run = ease(seg(t, B3 + 0.1, T_REFUGE + 0.1))
    x = lerp(120, 600, run)
    bob = 10 * abs(math.sin(t * 12)) * (1 - seg(run, 0.95, 1.0))
    arms = ease(seg(t, T_EVEN - 0.2, T_WRONG))
    Q.person(ctx, x, GROUND_Y + 20 - bob, 1.2, col("brown"), 0.0, 0, 0, 0.3 + 0.7 * arms)
    # a pursuer's shadow at the far left, held back
    en = ease(seg(t, T_ENEMY - 0.4, T_ENEMY)) * (1 - 0.3 * ease(seg(t, T_CATCH, B4)))
    if en > 0:
        Q.person(ctx, lerp(-80, 140, en), GROUND_Y + 20, 1.25, hexc("#2A2420"), 0, 0, 0, 0.75, alpha=0.85 * en)
    draw_text(ctx, "refuge", F_SERIF_I, 80, "#A8741A", 800, 470, glow)
    oath = ease(seg(t, T_WRONG - 0.3, T_WRONG + 0.1))
    draw_text(ctx, "“If I have done this...”", F_SERIF_I, 64, "#3B2A1E", 540, 300, oath)
    P.tag(ctx, "Psalm 7:1", 800, 560, seg(t, T_REFUGE - 0.1, T_REFUGE + 0.3), 1 - oath, 240)
    P.tag(ctx, "Psalm 7:3-5", 540, 190, seg(t, T_WRONG - 0.1, T_WRONG + 0.3), 1.0, 300)


def scene4(ctx, lt):
    """He leaves his case with God, the righteous judge: a scroll on golden scales of light."""
    t = lt + B4
    R.bg(ctx, col("cream"))
    g = cairo.LinearGradient(0, 0, 0, 1400)
    g.add_color_stop_rgba(0, *col("cream2"))
    g.add_color_stop_rgba(1, *col("gold2")[:3], 0.4)
    ctx.set_source(g)
    ctx.paint()
    rays(ctx, 540, -80, math.radians(60), math.radians(120), 10, 1800, 0.9, t * 0.4)
    land_y = 1300
    ctx.set_source_rgba(*STONE)
    ctx.rectangle(0, land_y, W, H)
    ctx.fill()
    tilt = 0.6 * math.sin(t * 2.2) * (1 - ease(seg(t, T_RIGHTEOUS - 0.3, T_JUDGE1)))
    pans = scales(ctx, 540, 260, 1.0, tilt, ease(seg(lt, 0.0, 0.3)), 1.0, t)
    # the scroll is lifted from David's hands and laid on the scale
    lift = ease(seg(t, T_CASE1 - 0.3, T_CASE1 + 0.5))
    if pans:
        (lx, ly), _ = pans
        sx, sy = lerp(540, lx, lift), lerp(land_y - 260, ly - 30, lift)
        scroll(ctx, sx, sy, 160, 0.0, 1.0, -0.2 * (1 - lift))
    Q.person(ctx, 540, land_y + 20, 1.15, col("brown"), 0.25, 0, 0, 0.55 + 0.4 * (1 - lift), 0.8)
    P.tag(ctx, "Psalm 7:11", 540, 200, seg(t, T_RIGHTEOUS - 0.2, T_RIGHTEOUS + 0.2), 1.0, 250)
    kword(ctx, "JUDGE", t, T_JUDGE1 - 0.04, 540, 1050, 190, "#E3B04B", B5 - T_JUDGE1)


def scene5(ctx, lt):
    """The twist: the plotter digs a pit and falls in; his trouble lands on his own head."""
    t = lt + B5
    day_sky(ctx, 0.8)
    V.hills(ctx, GROUND_Y - 150, 60, hexc("#C7B087"), 0, 73)
    # ground cross-section
    ctx.set_source_rgba(*OLIVE)
    ctx.rectangle(0, 1000, W, 24)
    ctx.fill()
    g = cairo.LinearGradient(0, 1020, 0, H)
    g.add_color_stop_rgba(0, *EARTH)
    g.add_color_stop_rgba(1, *EARTH2)
    ctx.set_source(g)
    ctx.rectangle(0, 1020, W, H)
    ctx.fill()
    depth = lerp(0, 430, ease(seg(t, T_DIGS - 0.2, T_PIT1 + 0.6)))
    px0, px1 = 380, 700
    ctx.set_source_rgba(*hexc("#4E3523"))
    ctx.move_to(px0, 1000)
    ctx.line_to(px1, 1000)
    ctx.line_to(px1 - 30, 1000 + depth)
    ctx.line_to(px0 + 30, 1000 + depth)
    ctx.close_path()
    ctx.fill()
    # dirt pile growing at the side
    pile = depth / 430
    ctx.set_source_rgba(*EARTH)
    ctx.move_to(720, 1002)
    ctx.curve_to(780, 1002 - 150 * pile, 900, 1002 - 150 * pile, 980, 1002)
    ctx.close_path()
    ctx.fill()
    fall = ein(seg(t, T_FALLS - 0.05, T_FALLS + 0.3))
    fy = lerp(1000, 1000 + depth - 10, fall)
    digging = 1 - seg(t, T_FALLS - 0.2, T_FALLS)
    ph = math.sin(t * 7)
    Q.person(ctx, 540, fy, 1.05, hexc("#1A1410"), 0.3 * digging, 0, 0, 0.5 + 0.2 * ph * digging)
    if digging > 0.01:
        shovel(ctx, 580, fy - 120, 0.5 + 0.3 * ph, 0.9, digging)
        for k in range(4):
            u = ((t - T_DIGS) * 1.5 + k / 4) % 1.0
            if t > T_DIGS - 0.2:
                dx, dy = lerp(560, 860, u), fy - 120 - 260 * math.sin(math.pi * u)
                ctx.set_source_rgba(*EARTH[:3], digging)
                ctx.arc(dx, dy, 16, 0, 2 * math.pi)
                ctx.fill()
    else:
        shovel(ctx, 760, 990, 1.2, 0.9, 1.0)
    # the trouble he made comes back down on his own head
    bk = seg(t, T_TROUBLE - 0.1, T_HEAD + 0.05)
    if 0 < bk < 1:
        bx, by = lerp(860, 540, bk), lerp(860, fy - 230, bk) - 400 * math.sin(math.pi * bk)
        ctx.set_source_rgba(*EARTH2)
        ctx.arc(bx, by, 34, 0, 2 * math.pi)
        ctx.fill()
    if t >= T_HEAD + 0.05:
        st = 1 - seg(t, T_HEAD + 0.05, T_HEAD + 1.3)
        for k in range(4):
            a = t * 5 + k * math.pi / 2
            R.star_path(ctx, 540 + 70 * math.cos(a), fy - 260 + 20 * math.sin(a), 18, 8, 5)
            ctx.set_source_rgba(*col("gold2", st))
            ctx.fill()
    P.tag(ctx, "Psalm 7:15-16", 540, 190, seg(t, T_PLOTS - 0.1, T_PLOTS + 0.3), 1.0, 320)
    draw_text(ctx, "the pit he dug", F_SERIF_I, 64, "#3B2A1E", 540, 320, ease(seg(t, T_PIT1 - 0.3, T_PIT1 + 0.1)) * (1 - ease(seg(t, T_TROUBLE - 0.2, T_TROUBLE))))
    draw_text(ctx, "on his own head", F_SERIF_I, 64, "#A9472F", 540, 320, ease(seg(t, T_HEAD - 0.3, T_HEAD)))
    kword(ctx, "TWIST", t, T_TWIST - 0.04, 540, 560, 200, "#E3B04B", T_PLOTS - T_TWIST + 0.3)


HEB = "כְּלָיוֹת"
LAYERS = [("words", "#C7B087"), ("actions", "#A98657"), ("thoughts", "#7A5537"), ("heart", "#5C3E28")]


def scene6(ctx, lt):
    """Nugget: hearts and kidneys, kelayot; light reaches all the way down."""
    t = lt + B6
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.5, "gold2", 6, -12)
    P.tag(ctx, "Psalm 7:9", 540, 190, seg(t, T_NINE - 0.2, T_NINE + 0.2), 1.0, 240)
    hm = ease(seg(t, T_TESTS - 0.2, T_MIND + 0.2)) * (1 - ease(seg(t, T_KLAYOT - 0.6, T_KLAYOT - 0.3)))
    draw_text(ctx, "“tests the heart and mind”", F_SERIF_I, 64, "#DCC59D", 540, 330, hm)
    lit = ease(seg(t, T_HEARTS - 0.2, T_KIDNEYS + 0.3)) * (1 - ease(seg(t, T_KLAYOT - 0.6, T_KLAYOT - 0.3)))
    draw_text(ctx, "literally:", F_SERIF_R, 52, "#DCC59D", 540, 450, lit)
    draw_text(ctx, "hearts and kidneys", F_SERIF_I, 80, "#FBF6EC", 540, 540, lit)
    hb = ease(seg(t, T_KLAYOT - 0.5, T_KLAYOT - 0.2)) * (1 - ease(seg(t, T_SEAT + 0.6, T_SEES - 0.2)))
    reveal = ease(seg(t, T_KLAYOT - 0.45, T_KLAYOT + 0.3))
    rays(ctx, 540, 520, 0, 2 * math.pi, 18, 1000, hb * 0.8, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 230, 540, 520, reveal, hb, rtl=True)
    draw_text(ctx, "kelayot", F_SERIF_I, 88, "#FBF6EC", 540, 720, ease(seg(t, T_KLAYOT + 0.1, T_KLAYOT + 0.5)) * (1 - ease(seg(t, T_SEES - 0.4, T_SEES - 0.1))))
    draw_text(ctx, "the seat of your deepest feelings", F_SERIF_I, 50, "#DCC59D", 540, 820, ease(seg(t, T_SEAT - 0.2, T_DEEPEST + 0.2)) * (1 - ease(seg(t, T_SEES - 0.4, T_SEES - 0.1))))
    # layers, then a beam of light that goes all the way down
    ly = ease(seg(t, T_SEES - 0.5, T_SEES))
    if ly > 0:
        top = 420
        for i, (name, c) in enumerate(LAYERS):
            y = top + i * 200
            ctx.set_source_rgba(*hexc(c)[:3], ly)
            rounded(ctx, 140, y, 800, 180, 20)
            ctx.fill()
            draw_text(ctx, name, F_SERIF_I, 56, "#FBF6EC" if i > 1 else "#3B2A1E", 300, y + 90, ly)
        beam = ease(seg(t, T_SEES, T_DOWN + 0.4))
        if beam > 0:
            ctx.save()
            ctx.set_operator(cairo.OPERATOR_ADD)
            bg_ = cairo.LinearGradient(0, 0, 0, top + 800 * beam)
            bg_.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.0)
            bg_.add_color_stop_rgba(1, 1, 0.9, 0.6, 0.65)
            ctx.set_source(bg_)
            ctx.move_to(620, 0)
            ctx.line_to(760, 0)
            ctx.line_to(800, top + 800 * beam)
            ctx.line_to(580, top + 800 * beam)
            ctx.close_path()
            ctx.fill()
            ctx.restore()
        if t > T_DOWN:
            g = cairo.RadialGradient(690, top + 690, 10, 690, top + 690, 220)
            g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.9 * ease(seg(t, T_DOWN, T_DOWN + 0.4)))
            g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
            ctx.set_source(g)
            ctx.arc(690, top + 690, 220, 0, 2 * math.pi)
            ctx.fill()
            P4.heart_path(ctx, 690, top + 690, 38)
            ctx.set_source_rgba(*col("rust"))
            ctx.fill()
        kword(ctx, "ALL THE WAY DOWN", t, T_DOWN - 0.05, 540, 300, 90, "#E3B04B", B7 - T_DOWN)


def scene7(ctx, lt):
    """Close: drop the shovel, bring the case to God; end card."""
    t = lt + B7
    day_sky(ctx, 1.0)
    land(ctx, t)
    glow = ease(seg(t, T_BRING - 0.3, T_JUDGE2))
    rock_refuge(ctx, 800, GROUND_Y + 10, 0.9, 0.4 + 0.6 * glow, t)
    # the shovel is dropped
    drop = ease(seg(t, T_DIG2 - 0.3, T_DIG2 + 0.3))
    shovel(ctx, lerp(300, 200, drop), lerp(GROUND_Y - 160, GROUND_Y - 30, drop), lerp(0.3, 1.45, drop), 0.9)
    walk = ease(seg(t, T_BRING - 0.2, T_JUDGE2 + 0.3))
    x = lerp(330, 600, walk)
    Q.person(ctx, x, GROUND_Y + 20 - 6 * abs(math.sin(t * 10)) * (0 < walk < 1), 1.15, col("brown"), 0, 0, 0, 0.55)
    put = ease(seg(t, T_CASE2 - 0.1, T_JUDGE2 + 0.2))
    scroll(ctx, lerp(x + 60, 720, put), lerp(GROUND_Y - 150, GROUND_Y - 330, put), 150, 0.0, 1 - 0.3 * put)
    end = ease(seg(t, T_LEAVE - 0.35, T_LEAVE))
    draw_text(ctx, "PSALM 7", F_SERIF, 54, "#3B2A1E", 540, 300, end)
    ctx.set_source_rgba(*col("gold", end))
    ctx.rectangle(490, 355, 100, 4)
    ctx.fill()
    draw_text(ctx, "Leave the verdict.", F_SERIF, 100, "#3B2A1E", 540, 470, end, 0.92 + 0.08 * back_out(seg(t, T_LEAVE - 0.35, T_LEAVE)))
    kp = ease(seg(t, T_KEEP - 0.3, T_KEEP))
    draw_text(ctx, "Keep your peace.", F_SERIF, 100, "#A8741A", 540, 610, kp, 0.92 + 0.08 * back_out(seg(t, T_KEEP - 0.3, T_KEEP + 0.1)))
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5),
            (B6, B7, scene6), (B7, DUR + 1, scene7)]

if __name__ == "__main__":
    E.main(sys.argv)
