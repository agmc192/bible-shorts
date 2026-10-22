"""Psalm 9 Short. Cool morning stone-and-teal palette. Central image: a high, safe place (misgav)."""
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

E = Episode(9)
wt, DUR = E.wt, E.dur
T_FORGOTTEN1 = wt("forgotten", 1); T_STRUGGLE = wt("struggle"); T_REGISTER = wt("register"); T_ANYONE = wt("anyone")
T_PSALM = wt("psalm", 1); T_DAVID1 = wt("david", 1); T_THANKS = wt("thanks"); T_WANTS = wt("wants"); T_TELL = wt("tell")
T_WONDERFUL = wt("wonderful"); T_DEEDS = wt("deeds"); T_SITS = wt("sits"); T_ENTHRONED = wt("enthroned")
T_FOREVER = wt("forever"); T_JUDGES = wt("judges"); T_WORLD = wt("world"); T_RIGHTEOUSNESS = wt("righteousness")
T_FORGET = wt("forget"); T_CRY = wt("cry"); T_AFFLICTED = wt("afflicted"); T_POINT = wt("point"); T_KNOW = wt("know")
T_NAME = wt("name"); T_TRUST = wt("trust"); T_FORSAKEN = wt("forsaken"); T_SEEK = wt("seek"); T_NEEDY = wt("needy")
T_ALWAYS = wt("always"); T_FORGOTTEN2 = wt("forgotten", 2); T_CALLS = wt("calls"); T_STRONGHOLD = wt("stronghold")
T_OPPRESSED = wt("oppressed"); T_HEBREW = wt("hebrew"); T_MISGAV = wt("misgahv"); T_HIGH = wt("high"); T_SAFE = wt("safe")
T_REACH = wt("reach"); T_TODAY = wt("today"); T_WRITE = wt("write"); T_DONE1 = wt("done", 1); T_THANK = wt("thank")
T_LOUD = wt("loud"); T_REMEMBER = wt("remember"); T_DONE2 = wt("done", 2); T_REMEMBERS = wt("remembers")

B1 = 0.0
B2 = T_PSALM - 0.3
B3 = T_WANTS - 0.3
B4 = T_POINT - 0.6
B5 = T_CALLS - 0.35
B6 = T_TODAY - 0.45

E.zooms = [(0.1, 0.12), (T_FORGOTTEN1, 0.06), (T_THANKS, 0.10), (T_ENTHRONED, 0.08), (T_CRY, 0.06), (T_TRUST, 0.06),
           (T_FORGOTTEN2, 0.08), (T_STRONGHOLD, 0.10), (T_MISGAV, 0.12), (T_REACH, 0.06), (T_REMEMBERS, 0.07)]
E.shakes = [(0.1, 14, 0.6), (T_THANKS, 6, 0.3), (T_STRONGHOLD, 10, 0.5), (T_MISGAV, 10, 0.5), (T_REACH, 6, 0.4)]
E.flashes = [(0.1, (0.9, 0.95, 1), 0.35, 0.3), (T_THANKS, (1, 0.92, 0.7), 0.35, 0.4), (T_ENTHRONED, (1, 0.9, 0.6), 0.3, 0.45),
             (T_FORGOTTEN2, (1, 0.92, 0.75), 0.3, 0.4), (T_MISGAV, (1, 0.85, 0.5), 0.3, 0.4),
             (T_REMEMBERS, (1, 0.95, 0.85), 0.3, 0.4)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6)]

SKY1 = hexc("#CFE0E3")
SKY2 = hexc("#9FC2C7")
TEAL = hexc("#2F6F73")
SLATE = hexc("#5B6B73")
SLATE2 = hexc("#3E4A52")
GROUND_Y = 1240


def morning(ctx, warm=0.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND_Y)
    g.add_color_stop_rgba(0, *lerpc(SKY1, hexc("#F6E7C4"), warm))
    g.add_color_stop_rgba(1, *lerpc(SKY2, hexc("#F2CF95"), warm))
    ctx.set_source(g)
    ctx.paint()


def ground(ctx, c=None):
    V.hills(ctx, GROUND_Y - 140, 50, hexc("#8DA9A8"), 0, 91)
    ctx.set_source_rgba(*(c or hexc("#6E8C79")))
    ctx.rectangle(0, GROUND_Y, W, H)
    ctx.fill()


def cliff_fort(ctx, cx, top, s, glow, t):
    """A tall crag with a small fortress on top: a high, safe place."""
    if glow > 0:
        rays(ctx, cx, top - 60, 0, 2 * math.pi, 14, 900, glow, t * 0.4)
    ctx.save()
    ctx.translate(cx, top)
    ctx.scale(s, s)
    ctx.set_source_rgba(*SLATE2)
    ctx.move_to(-230, 1100)
    ctx.curve_to(-200, 700, -170, 300, -120, 60)
    ctx.line_to(-60, 0)
    ctx.line_to(80, 10)
    ctx.curve_to(140, 300, 200, 700, 250, 1100)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*SLATE)
    ctx.move_to(-120, 60)
    ctx.curve_to(-90, 300, -100, 600, -150, 1100)
    ctx.line_to(-60, 1100)
    ctx.curve_to(-40, 600, -50, 300, -60, 0)
    ctx.close_path()
    ctx.fill()
    # fortress
    ctx.set_source_rgba(*col("sand2"))
    ctx.rectangle(-90, -110, 180, 120)
    ctx.fill()
    for i in range(5):
        ctx.rectangle(-90 + i * 40, -140, 22, 32)
    ctx.fill()
    ctx.rectangle(-130, -170, 60, 180)
    ctx.rectangle(70, -170, 60, 180)
    ctx.fill()
    ctx.set_source_rgba(1, 0.85, 0.5, 0.6 + 0.4 * glow)
    rounded(ctx, -22, -60, 44, 70, 20)
    ctx.fill()
    ctx.restore()


def throne(ctx, cx, cy, s, alpha, t):
    if alpha <= 0.01:
        return
    rays(ctx, cx, cy - 120 * s, 0, 2 * math.pi, 16, 900, alpha, t * 0.4)
    g = cairo.RadialGradient(cx, cy - 120 * s, 10, cx, cy - 120 * s, 380 * s)
    g.add_color_stop_rgba(0, 1, 0.96, 0.8, 0.95 * alpha)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    ctx.set_source(g)
    ctx.arc(cx, cy - 120 * s, 380 * s, 0, 2 * math.pi)
    ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_source_rgba(*col("gold2", alpha))
    ctx.move_to(-110, 0)
    ctx.line_to(-110, -300)
    ctx.curve_to(-110, -360, 110, -360, 110, -300)
    ctx.line_to(110, 0)
    ctx.line_to(80, 0)
    ctx.line_to(80, -110)
    ctx.line_to(-80, -110)
    ctx.line_to(-80, 0)
    ctx.close_path()
    ctx.fill()
    ctx.rectangle(-140, -120, 280, 30)
    ctx.fill()
    ctx.restore()


def notebook(ctx, cx, cy, s, alpha, lines_prog, t):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.rotate(-0.04)
    ctx.set_source_rgba(0, 0, 0, 0.2 * alpha)
    rounded(ctx, -290, -360, 600, 740, 20)
    ctx.fill()
    ctx.set_source_rgba(*col("cream2", alpha))
    rounded(ctx, -300, -370, 600, 740, 20)
    ctx.fill()
    ctx.set_source_rgba(0.55, 0.7, 0.85, 0.5 * alpha)
    ctx.set_line_width(3)
    for i in range(9):
        y = -260 + i * 70
        ctx.move_to(-250, y)
        ctx.line_to(250, y)
    ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: a hurrying crowd streams past one still, greyed figure."""
    t = lt
    morning(ctx)
    ground(ctx)
    r = random.Random(9)
    for i in range(14):
        speed = r.uniform(380, 620)
        y = GROUND_Y + r.uniform(-10, 80)
        x = (r.uniform(0, W + 400) + speed * (t + 0.3)) % (W + 400) - 200
        sc = r.uniform(0.8, 1.05)
        Q.person(ctx, x, y + 40, sc, hexc("#4A5A62"), 0, 0, 0, 0.1, alpha=0.75)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.set_line_width(3)
        for k in range(3):
            ctx.move_to(x - 60 - k * 18, y - 60 - k * 30)
            ctx.line_to(x - 120 - k * 18, y - 60 - k * 30)
        ctx.stroke()
    fade = 0.4 + 0.6 * (1 - ease(seg(t, T_FORGOTTEN1 - 0.3, T_FORGOTTEN1 + 0.4)))
    Q.person(ctx, 540, GROUND_Y + 60, 1.45, lerpc(hexc("#9AA6AC"), col("brown"), fade * 0.3), 0.7, 0, 0, 0.0, alpha=0.9)
    kword(ctx, "FORGOTTEN", t, T_FORGOTTEN1 - 0.05, 540, 300, 150, "#CFE0F5", B2 - T_FORGOTTEN1)
    grade(ctx, desat=0.4)


def scene2(ctx, lt):
    """Title; the psalm starts with thanks."""
    t = lt + B2
    morning(ctx, 0.4 * ease(seg(t, T_THANKS - 0.3, T_THANKS + 0.3)))
    ground(ctx)
    pop = back_out(seg(lt, -0.05, 0.3))
    draw_text(ctx, "PSALM 9", F_SERIF, 160, "#3B2A1E", 540, 480, clamp(pop), 0.9 + 0.1 * pop)
    ctx.set_source_rgba(*col("gold", clamp(pop)))
    ctx.rectangle(440, 590, 200, 6)
    ctx.fill()
    draw_text(ctx, "A psalm of David", F_SERIF_I, 66, "#4A3524", 540, 680, ease(seg(t, T_DAVID1 - 0.2, T_DAVID1 + 0.2)))
    th = ease(seg(t, T_THANKS - 0.2, T_THANKS + 0.2))
    if th > 0:
        Q.person(ctx, 540, GROUND_Y + 60, 1.3, col("brown"), 0, 0, 0, 1.0 * th)
        for k in range(10):
            a = k * math.pi / 5 + t
            rr = 160 + 40 * math.sin(t * 3 + k)
            R.star_path(ctx, 540 + rr * math.cos(a), 980 + rr * 0.6 * math.sin(a), 14, 6, 5, t)
            ctx.set_source_rgba(*col("gold2", th))
            ctx.fill()
    P.tag(ctx, "Psalm 9:1-2", 540, 200, seg(t, T_THANKS - 0.2, T_THANKS + 0.2), 1.0, 270)
    kword(ctx, "THANKS", t, T_THANKS - 0.04, 540, 860, 170, "#E3B04B", B3 - T_THANKS)


def scene3(ctx, lt):
    """God's wonderful deeds; enthroned forever; judges the world; does not forget the cry."""
    t = lt + B3
    morning(ctx, 0.5)
    ground(ctx)
    # wonderful deeds: a scroll of sky, sea and hills unrolling
    sc = ease(seg(t, T_TELL - 0.2, T_DEEDS + 0.3)) * (1 - ease(seg(t, T_SITS - 0.4, T_SITS)))
    if sc > 0:
        w = 840 * sc
        ctx.set_source_rgba(*col("cream2", sc))
        ctx.rectangle(540 - w / 2, 380, w, 300)
        ctx.fill()
        ctx.save()
        ctx.rectangle(540 - w / 2, 380, w, 300)
        ctx.clip()
        ctx.set_source_rgba(*col("gold2", sc))
        ctx.arc(330, 470, 50, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(*col("water", sc))
        ctx.move_to(420, 640)
        for i in range(9):
            ctx.curve_to(440 + i * 30, 600, 455 + i * 30, 680, 470 + i * 30, 640)
        ctx.line_to(700, 680)
        ctx.line_to(420, 680)
        ctx.close_path()
        ctx.fill()
        ctx.set_source_rgba(*col("leaf", sc))
        ctx.move_to(680, 680)
        ctx.line_to(770, 480)
        ctx.line_to(860, 680)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
        ctx.set_source_rgba(*col("brown2", sc))
        for sx in (-1, 1):
            rounded(ctx, 540 + sx * w / 2 - 16, 360, 32, 340, 14)
            ctx.fill()
        draw_text(ctx, "all his wonderful deeds", F_SERIF_I, 60, "#3B2A1E", 540, 300, sc)
    th = ease(seg(t, T_SITS - 0.3, T_ENTHRONED + 0.2))
    throne(ctx, 540, 860, 1.0, th, t)
    P.tag(ctx, "Psalm 9:7-8", 540, 200, seg(t, T_ENTHRONED - 0.1, T_ENTHRONED + 0.3), 1 - ease(seg(t, T_FORGET - 0.3, T_FORGET)), 270)
    draw_text(ctx, "forever", F_SERIF_I, 76, "#A8741A", 540, 330, ease(seg(t, T_FOREVER - 0.2, T_FOREVER + 0.2)) * (1 - ease(seg(t, T_JUDGES - 0.2, T_JUDGES))))
    if t > T_WORLD - 0.4:
        P.globe(ctx, 540, 1120, 110, t * 0.6, 0.2, ease(seg(t, T_WORLD - 0.4, T_WORLD)) * (1 - ease(seg(t, T_FORGET - 0.3, T_FORGET))))
    draw_text(ctx, "in righteousness", F_SERIF_I, 64, "#3B2A1E", 540, 330, ease(seg(t, T_RIGHTEOUSNESS - 0.3, T_RIGHTEOUSNESS)) * (1 - ease(seg(t, T_FORGET - 0.3, T_FORGET))))
    # a small cry rises from a kneeling figure to the light
    cr = ease(seg(t, T_FORGET - 0.3, T_FORGET))
    if cr > 0:
        Q.person(ctx, 540, GROUND_Y + 60, 1.1, col("brown"), 0.6, 0, 0, 0.3, 0.8, alpha=cr)
        for k in range(4):
            u = (t - T_CRY) * 0.9 - k * 0.25
            if 0 <= u < 1:
                ctx.set_source_rgba(1, 0.88, 0.55, 0.7 * (1 - u))
                ctx.set_line_width(5)
                ctx.arc(540, GROUND_Y - 140 - 360 * u, 40 + 60 * u, math.radians(200), math.radians(340))
                ctx.stroke()
        P.tag(ctx, "Psalm 9:12", 540, 200, seg(t, T_FORGET - 0.1, T_FORGET + 0.3), 1.0, 250)
        draw_text(ctx, "does not forget", F_SERIF_I, 72, "#3B2A1E", 540, 330, cr)


def scene4(ctx, lt):
    """Those who know his name trust him; the needy will not always be forgotten: the grey figure regains its colour."""
    t = lt + B4
    morning(ctx, 0.7)
    ground(ctx)
    rays(ctx, 540, -80, math.radians(60), math.radians(120), 10, 1800, 0.7, t * 0.4)
    nm = ease(seg(t, T_NAME - 0.3, T_TRUST + 0.2))
    draw_text(ctx, "THE LORD", F_SERIF, 130, "#E3B04B", 540, 420, nm, 0.9 + 0.1 * back_out(seg(t, T_NAME - 0.3, T_NAME + 0.1)), stroke=5, stroke_color="#3B2A1E", glow=10)
    P.tag(ctx, "Psalm 9:10", 540, 200, seg(t, T_KNOW - 0.2, T_KNOW + 0.2), 1 - ease(seg(t, T_NEEDY - 0.3, T_NEEDY)), 250)
    draw_text(ctx, "not forsaken", F_SERIF_I, 70, "#3B2A1E", 540, 560, ease(seg(t, T_FORSAKEN - 0.3, T_FORSAKEN + 0.1)) * (1 - ease(seg(t, T_NEEDY - 0.3, T_NEEDY))))
    colour = ease(seg(t, T_NEEDY - 0.2, T_FORGOTTEN2 + 0.3))
    walk = ease(seg(t, T_SEEK - 0.6, T_NEEDY))
    c = lerpc(hexc("#9AA6AC"), col("brown"), colour)
    Q.person(ctx, lerp(300, 540, walk), GROUND_Y + 60, 1.4, c, 0.7 * (1 - colour), 0, 0, 0.0 + 0.9 * colour)
    if colour > 0:
        g = cairo.RadialGradient(540, GROUND_Y - 150, 10, 540, GROUND_Y - 150, 420 * colour)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.6)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.arc(540, GROUND_Y - 150, 420 * colour, 0, 2 * math.pi)
        ctx.fill()
    P.tag(ctx, "Psalm 9:18", 540, 200, seg(t, T_NEEDY - 0.1, T_NEEDY + 0.3), 1.0, 250)
    draw_text(ctx, "not always forgotten", F_SERIF_I, 70, "#A8741A", 540, 560, ease(seg(t, T_ALWAYS - 0.2, T_FORGOTTEN2 + 0.1)))
    grade(ctx, desat=0.4 * (1 - colour))


HEB = "מִשְׂגָּב"


def scene5(ctx, lt):
    """Stronghold: misgav, a high safe place; arrows fall short."""
    t = lt + B5
    dark = ease(seg(t, T_HEBREW - 0.3, T_HEBREW + 0.2)) * (1 - ease(seg(t, T_HIGH - 0.3, T_HIGH)))
    morning(ctx, 0.3)
    V.hills(ctx, GROUND_Y + 60, 40, hexc("#8DA9A8"), 0, 92)
    rise = ease(seg(lt, 0.0, 1.2))
    cliff_fort(ctx, 540, lerp(900, 360, rise), 1.0, ease(seg(t, T_STRONGHOLD - 0.3, T_STRONGHOLD + 0.2)), t)
    P.tag(ctx, "Psalm 9:9", 540, 200, seg(t, T_STRONGHOLD - 0.2, T_STRONGHOLD + 0.2), 1.0, 240)
    kword(ctx, "STRONGHOLD", t, T_STRONGHOLD - 0.04, 540, 1050, 130, "#E3B04B", T_HEBREW - T_STRONGHOLD - 0.1)
    if dark > 0:
        ctx.set_source_rgba(0.08, 0.06, 0.05, 0.75 * dark)
        ctx.paint()
    hb = ease(seg(t, T_MISGAV - 0.5, T_MISGAV - 0.2)) * (1 - ease(seg(t, T_REACH, T_REACH + 0.5)))
    reveal = ease(seg(t, T_MISGAV - 0.45, T_MISGAV + 0.3))
    P.burn_word(ctx, HEB, F_HEB, 220, 540, 620, reveal, hb, rtl=True)
    draw_text(ctx, "misgav", F_SERIF_I, 90, "#FBF6EC", 540, 800, ease(seg(t, T_MISGAV + 0.1, T_MISGAV + 0.5)) * (1 - ease(seg(t, T_REACH, T_REACH + 0.5))), stroke=3, stroke_color="#2A1D14")
    draw_text(ctx, "a high, safe place", F_SERIF_I, 70, "#FFE3A3", 540, 900, ease(seg(t, T_HIGH - 0.2, T_SAFE + 0.2)), stroke=3, stroke_color="#2A1D14")
    # arrows from below fall short of the fortress
    ar = seg(t, T_REACH - 0.6, T_REACH + 0.6)
    if 0 < ar < 1:
        for k in range(5):
            u = clamp(ar * 1.4 - k * 0.08)
            x = 140 + k * 190
            y = lerp(1500, 1150, math.sin(math.pi * u * 0.9))
            ang = -math.pi / 2 + (u - 0.5) * 1.6
            ctx.save()
            ctx.translate(x + 60 * u, y)
            ctx.rotate(ang)
            ctx.set_source_rgba(*SLATE2)
            ctx.set_line_width(5)
            ctx.move_to(-40, 0)
            ctx.line_to(40, 0)
            ctx.stroke()
            ctx.move_to(40, 0)
            ctx.line_to(28, -8)
            ctx.line_to(28, 8)
            ctx.close_path()
            ctx.fill()
            ctx.restore()
    draw_text(ctx, "out of reach", F_SERIF_I, 66, "#3B2A1E", 540, 1380, ease(seg(t, T_REACH - 0.3, T_REACH + 0.1)))


def scene6(ctx, lt):
    """Close: write down one thing God has done; thank him out loud. End card."""
    t = lt + B6
    morning(ctx, 0.9)
    ground(ctx, hexc("#7D8A4A"))
    rays(ctx, 540, -80, math.radians(60), math.radians(120), 10, 1700, 0.6, t * 0.4)
    nb = ease(seg(t, T_WRITE - 0.3, T_WRITE)) * (1 - ease(seg(t, T_THANK - 0.3, T_THANK)))
    notebook(ctx, 540, 820, 1.0, nb, 0, t)
    s = text_surf("Thank you, God, for...", F_SERIF_I, 52, "#3B2A1E")
    wr = ease(seg(t, T_WRITE, T_DONE1 + 0.3))
    if nb > 0:
        ctx.save()
        ctx.rectangle(270, 560, s.get_width() * wr, 120)
        ctx.clip()
        ctx.set_source_surface(s, 270, 600 - s.get_height() / 2)
        ctx.paint_with_alpha(nb)
        ctx.restore()
        px = 270 + s.get_width() * wr
        ctx.save()
        ctx.translate(px, 590)
        ctx.rotate(0.6)
        ctx.set_source_rgba(*col("gold", nb))
        ctx.rectangle(-8, -150, 16, 140)
        ctx.fill()
        ctx.set_source_rgba(*col("dark", nb))
        ctx.move_to(-8, -10)
        ctx.line_to(8, -10)
        ctx.line_to(0, 12)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    sp = ease(seg(t, T_THANK - 0.3, T_THANK))
    if sp > 0:
        Q.person(ctx, 540, GROUND_Y + 60, 1.3, col("brown"), 0, 0, 0, 1.0 * sp, alpha=sp)
        for k in range(3):
            u = (t - T_THANK) * 0.8 - k * 0.3
            if 0 <= u < 1:
                ctx.set_source_rgba(1, 0.85, 0.5, 0.7 * (1 - u))
                ctx.set_line_width(6)
                ctx.arc(540, GROUND_Y - 200, 60 + 260 * u, math.radians(200), math.radians(340))
                ctx.stroke()
    end = ease(seg(t, T_REMEMBER - 0.35, T_REMEMBER))
    draw_text(ctx, "PSALM 9", F_SERIF, 54, "#3B2A1E", 540, 300, end)
    ctx.set_source_rgba(*col("gold", end))
    ctx.rectangle(490, 355, 100, 4)
    ctx.fill()
    draw_text(ctx, "Remember what he's done.", F_SERIF, 80, "#3B2A1E", 540, 470, end, 0.92 + 0.08 * back_out(seg(t, T_REMEMBER - 0.35, T_REMEMBER)))
    rm = ease(seg(t, T_REMEMBERS - 0.3, T_REMEMBERS + 0.05))
    draw_text(ctx, "He remembers you.", F_SERIF, 100, "#A8741A", 540, 600, rm, 0.92 + 0.08 * back_out(seg(t, T_REMEMBERS - 0.3, T_REMEMBERS + 0.1)))
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5),
            (B6, DUR + 1, scene6)]

if __name__ == "__main__":
    E.main(sys.argv)
