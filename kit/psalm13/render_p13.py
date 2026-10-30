"""Psalm 13 Short. Ink-blue night of waiting, an hourglass, four 'How long?'s; one golden 'but' breaks it into dawn.
Central image: a long night that turns on one small word."""
import sys, math, random
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/psalm4")
sys.path.insert(0, "/home/claude/psalm6")
import cairo
from engine import Episode, end_card, end_thumbnail
import render as R
import render_v2 as V
import render_p2 as P
import render_p3 as Q
import render_p4 as P4
from render import (W, H, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, rounded,
                    F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword

E = Episode(13)
wt, DUR = E.wt, E.dur
T_PRAYED = wt("prayed"); T_SAME = wt("same"); T_TIRED = wt("tired"); T_YOURSELF = wt("yourself")
T_DAVID = wt("david", 1); T_PSALM = wt("psalm", 1); T_HOW1 = wt("how", 1); T_FOUR = wt("four"); T_VERSES = wt("verses")
T_HOW2 = wt("how", 2); T_FORGET = wt("forget"); T_HOW3 = wt("how", 3); T_HIDE1 = wt("hide", 1); T_FACE = wt("face")
T_HOW4 = wt("how", 4); T_ENEMY = wt("enemy"); T_WIN = wt("win")
T_THEN1 = wt("then", 1); T_LOOK = wt("look"); T_ANSWER = wt("answer"); T_LIGHT = wt("light"); T_EYES = wt("eyes")
T_SMALL = wt("small"); T_WORD1 = wt("word", 1); T_TURNS = wt("turns"); T_BUT1 = wt("but", 1); T_BUT2 = wt("but", 2)
T_TRUSTED = wt("trusted"); T_STEADFAST1 = wt("steadfast", 1); T_LOVE1 = wt("love", 1)
T_PHRASE = wt("phrase"); T_HEBREW = wt("hebrew"); T_KHESED = wt("khehsed"); T_LOYAL = wt("loyal"); T_COVENANT = wt("covenant")
T_LOVE4 = wt("love", 4); T_QUIT = wt("quit")
T_DAVID2 = wt("david", 2); T_QUESTION = wt("question"); T_LAST = wt("last"); T_WORD2 = wt("word", 3)
T_TODAY = wt("today"); T_WRITE1 = wt("write", 1); T_HOW5 = wt("how", 5); T_WRITE2 = wt("write", 2); T_BUT3 = wt("but", 3)
T_KEEP = wt("keep"); T_ADD = wt("add"); T_BUT4 = wt("but", 4)

B1 = 0.0
B2 = T_DAVID - 0.3
B3 = T_HOW2 - 0.3
B4 = T_THEN1 - 0.35
B5 = T_SMALL - 0.9
B6 = T_PHRASE - 0.35
B7 = T_DAVID2 - 0.35
B8 = T_TODAY - 0.35

E.zooms = [(0.1, 0.12), (T_HOW1, 0.08), (T_HOW2, 0.07), (T_HOW3, 0.07), (T_HOW4, 0.09), (T_EYES, 0.06),
           (T_BUT1, 0.16), (T_KHESED, 0.12), (T_QUIT, 0.06), (T_LAST, 0.07), (T_KEEP, 0.07), (T_BUT4, 0.1)]
E.shakes = [(0.1, 10, 0.5), (T_HOW4, 10, 0.5), (T_ENEMY, 8, 0.4), (T_BUT1, 18, 0.8), (T_KHESED, 8, 0.4)]
E.flashes = [(0.1, (1, 1, 1), 0.25, 0.3), (T_BUT1, (1, 0.93, 0.7), 0.6, 0.7), (T_KHESED, (1, 0.88, 0.55), 0.3, 0.4),
             (T_BUT4, (1, 0.95, 0.85), 0.35, 0.45)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B6, B7, B8)]

INK1 = hexc("#141A2E")
INK2 = hexc("#2C3552")
DAWN1 = hexc("#F4D9A8")
DAWN2 = hexc("#E8A86A")
FLOOR_Y = 1290
_r = random.Random(13)
STARS = [(_r.uniform(0, W), _r.uniform(0, 1150), _r.uniform(1.5, 4), _r.uniform(0, 6)) for _ in range(80)]


def sky(ctx, t, dawn=0.0, stars=1.0):
    g = cairo.LinearGradient(0, 0, 0, FLOOR_Y)
    g.add_color_stop_rgba(0, *lerpc(INK1, hexc("#F7E6C4"), dawn))
    g.add_color_stop_rgba(1, *lerpc(INK2, DAWN2, dawn))
    ctx.set_source(g)
    ctx.paint()
    for x, y, s, ph in STARS:
        tw = 0.5 + 0.5 * math.sin(t * 1.7 + ph)
        ctx.set_source_rgba(0.9, 0.92, 1.0, (0.3 + 0.6 * tw) * stars * (1 - dawn))
        ctx.arc(x, y, s, 0, 2 * math.pi)
        ctx.fill()


def room(ctx, t, dawn=0.0, stars=1.0, hidden=0.0):
    """Wall with a tall arched window onto the night (or dawn) sky; floor below."""
    ctx.set_source_rgba(*lerpc(hexc("#1C2238"), hexc("#D9B58A"), dawn))
    ctx.paint()
    ctx.save()
    ctx.move_to(300, 1080); ctx.line_to(300, 470); ctx.curve_to(300, 250, 780, 250, 780, 470); ctx.line_to(780, 1080)
    ctx.close_path()
    ctx.clip_preserve()
    ctx.new_path()
    sky(ctx, t, dawn, stars)
    # the light (not God pictured; just a glow) that can be hidden behind cloud
    lx, ly = 540, 520
    g = cairo.RadialGradient(lx, ly, 10, lx, ly, 260)
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.85 * (1 - hidden) + 0.3 * dawn)
    g.add_color_stop_rgba(1, 1, 0.85, 0.6, 0)
    ctx.set_source(g)
    ctx.arc(lx, ly, 260, 0, 2 * math.pi)
    ctx.fill()
    if hidden > 0:
        for k, (cx, cy, rr) in enumerate(((430, 520, 120), (560, 500, 140), (660, 540, 110), (520, 580, 120))):
            off = (1 - hidden) * (300 if k % 2 else -300)
            ctx.set_source_rgba(0.24, 0.27, 0.38, 0.95 * hidden)
            ctx.arc(cx + off, cy, rr, 0, 2 * math.pi)
            ctx.fill()
    ctx.restore()
    # window frame and sill
    ctx.set_source_rgba(*lerpc(hexc("#0E1220"), hexc("#7A5A3E"), dawn))
    ctx.set_line_width(22)
    ctx.move_to(300, 1080); ctx.line_to(300, 470); ctx.curve_to(300, 250, 780, 250, 780, 470); ctx.line_to(780, 1080)
    ctx.close_path(); ctx.stroke()
    ctx.set_line_width(12)
    ctx.move_to(540, 300); ctx.line_to(540, 1080); ctx.move_to(300, 700); ctx.line_to(780, 700); ctx.stroke()
    ctx.rectangle(270, 1080, 540, 30); ctx.fill()
    ctx.set_source_rgba(*lerpc(hexc("#0B0E19"), hexc("#8C6A48"), dawn))
    ctx.rectangle(0, FLOOR_Y, W, H)
    ctx.fill()
    # window light on the floor
    ctx.set_source_rgba(1, 0.9, 0.7, 0.10 + 0.25 * dawn)
    ctx.move_to(300, FLOOR_Y); ctx.line_to(780, FLOOR_Y); ctx.line_to(900, H); ctx.line_to(180, H); ctx.close_path(); ctx.fill()


def hourglass(ctx, cx, cy, s, sand, alpha=1.0, glow=0.0):
    """Sand runs top to bottom; sand 0..1 is the fraction fallen."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_source_rgba(*hexc("#8A6A44")[:3], alpha)
    ctx.rectangle(-90, -150, 180, 18); ctx.fill()
    ctx.rectangle(-90, 132, 180, 18); ctx.fill()
    ctx.set_line_width(8)
    for sx in (-1, 1):
        ctx.move_to(sx * 76, -132); ctx.line_to(sx * 76, 132); ctx.stroke()
    def bulb():
        ctx.move_to(-62, -132); ctx.curve_to(-62, -50, -8, -20, -8, 0); ctx.curve_to(-8, 20, -62, 50, -62, 132)
        ctx.line_to(62, 132); ctx.curve_to(62, 50, 8, 20, 8, 0); ctx.curve_to(8, -20, 62, -50, 62, -132); ctx.close_path()
    ctx.save()
    bulb(); ctx.clip()
    ctx.set_source_rgba(0.85, 0.9, 1.0, 0.18 * alpha); ctx.paint()
    sc = lerpc(hexc("#D8B577"), hexc("#F2C66A"), glow)
    ctx.set_source_rgba(*sc[:3], alpha)
    top = 120 * (1 - sand)
    ctx.rectangle(-70, -10 - top, 140, top); ctx.fill()
    bot = 125 * sand
    ctx.move_to(-70, 132); ctx.line_to(-70, 132 - bot * 0.6); ctx.line_to(0, 132 - bot); ctx.line_to(70, 132 - bot * 0.6)
    ctx.line_to(70, 132); ctx.close_path(); ctx.fill()
    if 0 < sand < 1:
        ctx.rectangle(-2.5, 0, 5, 132 - bot); ctx.fill()
    ctx.restore()
    bulb()
    ctx.set_source_rgba(0.85, 0.9, 1.0, 0.7 * alpha)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def kneeler(ctx, x, y, s, c, alpha=1.0, arms=0.0, bow=0.6):
    Q.person(ctx, x, y, s, c, bow, 0, 0, arms, 1.0, alpha)


def echo_bubbles(ctx, t, t0, n, alpha):
    """The same prayer again and again: identical bubbles stacking up."""
    for k in range(n):
        tk = t0 + k * 0.42
        a = ease(seg(t, tk, tk + 0.2)) * alpha
        if a <= 0.01:
            continue
        x = 540 + (k % 2 * 2 - 1) * (60 + 18 * k)
        y = 880 - k * 120
        P4.bubble(ctx, x, y, 300, 96, hexc("#E8E2D4"), a * (0.95 - 0.08 * k), 1 if k % 2 else -1)
        draw_text(ctx, "please…", F_SERIF_I, 44, "#2C3552", x, y, a * (0.95 - 0.08 * k))


def count_dots(ctx, n, alpha, y=1500 - 270, lit_col="#E3B04B"):
    if alpha <= 0.01:
        return
    for k in range(4):
        x = 540 + (k - 1.5) * 70
        on = clamp(n - k)
        ctx.set_source_rgba(*lerpc(hexc("#5A6383"), hexc(lit_col), on)[:3], alpha)
        ctx.arc(x, y, 14 + 6 * on, 0, 2 * math.pi)
        ctx.fill()


def hl_count(t):
    return sum(ease(seg(t, tk - 0.05, tk + 0.12)) for tk in (T_HOW1, T_HOW2, T_HOW3, T_HOW4))


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: a kneeling figure at a night window, the same prayer stacking up."""
    t = lt
    room(ctx, t)
    hourglass(ctx, 860, FLOOR_Y - 150, 0.75, 0.15 + 0.05 * t)
    kneeler(ctx, 470, FLOOR_Y + 10, 1.5, hexc("#0A0D18"))
    echo_bubbles(ctx, t, 0.15, 6, 1 - ease(seg(t, B2 - 0.3, B2)))
    kword(ctx, "AGAIN?", t, T_TIRED - 0.05, 540, 300, 180, "#E3B04B", B2 - T_TIRED + 0.1)
    grade(ctx, desat=0.2, cool=0.25)


def scene2(ctx, lt):
    """Title; 'How long?' four times in two verses: four dots ready to light."""
    t = lt + B2
    room(ctx, t)
    hourglass(ctx, 860, FLOOR_Y - 150, 0.75, 0.35 + 0.03 * lt)
    kneeler(ctx, 470, FLOOR_Y + 10, 1.5, hexc("#0A0D18"))
    ti = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_HOW1 - 0.4, T_HOW1 - 0.1)))
    draw_text(ctx, "PSALM 13", F_SERIF, 150, "#FBF6EC", 540, 520, ti, 0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#141A2E")
    P.tag(ctx, "Psalm 13:1-2", 540, 200, seg(t, T_HOW1 - 0.2, T_HOW1 + 0.2), 1.0, 290)
    kword(ctx, "HOW LONG?", t, T_HOW1 - 0.04, 540, 500, 135, "#FBF6EC", B3 - T_HOW1 + 0.2)
    draw_text(ctx, "×4", F_SERIF, 130, "#E3B04B", 540, 690, ease(seg(t, T_FOUR - 0.2, T_FOUR + 0.1)), 0.9 + 0.1 * back_out(seg(t, T_FOUR - 0.2, T_FOUR + 0.2)), stroke=4, stroke_color="#141A2E")
    count_dots(ctx, hl_count(t), ease(seg(t, T_HOW1 - 0.3, T_HOW1)))
    grade(ctx, desat=0.2, cool=0.25)


def scene3(ctx, lt):
    """Forget me? Hide your face? Enemy win? The glow goes behind cloud; a shadow looms; sand runs on."""
    t = lt + B3
    hid = ease(seg(t, T_HIDE1 - 0.3, T_FACE + 0.3))
    room(ctx, t, 0, 1 - 0.6 * hid, hid)
    hourglass(ctx, 860, FLOOR_Y - 150, 0.75, 0.5 + 0.05 * lt)
    fg = ease(seg(t, T_FORGET - 0.3, T_FORGET + 0.4))
    kneeler(ctx, 470, FLOOR_Y + 10, lerp(1.5, 1.05, fg), hexc("#0A0D18"), 1.0, 0, 0.9)
    en = ease(seg(t, T_ENEMY - 0.4, T_WIN + 0.2))
    if en > 0:
        ctx.save()
        ctx.push_group()
        Q.person(ctx, 790, FLOOR_Y + 10, lerp(1.6, 3.2, en), hexc("#05070D"), 0, 0, 0, 0.3)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(0.85 * en)
        ctx.restore()
    for k, (tk, txt, y) in enumerate(((T_HOW2, "forget me?", 360), (T_HOW3, "hide your face?", 360), (T_HOW4, "my enemy win?", 360))):
        nxt = (T_HOW3, T_HOW4, B4)[k]
        a = ease(seg(t, tk - 0.15, tk + 0.1)) * (1 - ease(seg(t, nxt - 0.25, nxt - 0.05)))
        draw_text(ctx, "How long…", F_SERIF_I, 66, "#C9D1E8", 540, y - 90, a)
        draw_text(ctx, txt, F_SERIF, 100, "#FBF6EC", 540, y + 20, a, 0.92 + 0.08 * back_out(seg(t, tk, tk + 0.35)), stroke=4, stroke_color="#141A2E")
    count_dots(ctx, hl_count(t), 1.0)
    grade(ctx, desat=0.3, cool=0.3)


def scene4(ctx, lt):
    """Look at me, answer me, light up my eyes: the figure lifts its head, two small lights."""
    t = lt + B4
    room(ctx, t, 0.08 * ease(seg(t, T_LIGHT - 0.2, T_EYES + 0.5)), 0.6, 1.0 - 0.3 * ease(seg(t, T_LOOK - 0.2, T_EYES)))
    hourglass(ctx, 860, FLOOR_Y - 150, 0.75, 0.75 + 0.04 * lt)
    up = ease(seg(t, T_LOOK - 0.3, T_LOOK + 0.3))
    kneeler(ctx, 470, FLOOR_Y + 10, 1.5, hexc("#0A0D18"), 1.0, 0.4 * ease(seg(t, T_ANSWER - 0.2, T_ANSWER + 0.3)), 0.9 - 0.9 * up)
    el = ease(seg(t, T_LIGHT - 0.1, T_EYES + 0.2))
    if el > 0:
        hy = FLOOR_Y + 10 - 1.5 * (92 + 40)
        for dx in (-13, 13):
            g = cairo.RadialGradient(470 + dx, hy - 4, 1, 470 + dx, hy - 4, 60)
            g.add_color_stop_rgba(0, 1, 0.93, 0.7, el)
            g.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
            ctx.set_source(g)
            ctx.arc(470 + dx, hy - 4, 60, 0, 2 * math.pi)
            ctx.fill()
    P.tag(ctx, "Psalm 13:3", 540, 200, seg(t, T_THEN1 - 0.1, T_THEN1 + 0.3), 1.0, 250)
    for k, (tk, txt) in enumerate(((T_LOOK, "look at me"), (T_ANSWER, "answer me"), (T_LIGHT, "light up my eyes"))):
        draw_text(ctx, txt, F_SERIF_I, 74, ("#C9D1E8", "#E8DCC8", "#F2C66A")[k], 540, 360 + k * 105, ease(seg(t, tk - 0.2, tk + 0.1)))
    count_dots(ctx, 4, 1 - ease(seg(t, T_LOOK - 0.3, T_LOOK)))
    grade(ctx, desat=0.25, cool=0.25)


def scene5(ctx, lt):
    """One small word turns the whole psalm: BUT. Night snaps to dawn; the verse card."""
    t = lt + B5
    dawn = ease(seg(t, T_BUT1 - 0.05, T_BUT1 + 0.9))
    room(ctx, t, dawn, 0.6 * (1 - dawn), 1.0 - dawn)
    hourglass(ctx, 860, FLOOR_Y - 150, 0.75, 0.82, 1.0, dawn)
    kneeler(ctx, 470, FLOOR_Y + 10, 1.5, lerpc(hexc("#0A0D18"), col("dark"), dawn), 1.0, 0.7 * dawn, 0.3 * (1 - dawn))
    if dawn > 0:
        rays(ctx, 540, 520, 0, 2 * math.pi, 22, 1300, 0.8 * dawn, t * 0.3)
    pre = ease(seg(t, T_SMALL - 0.3, T_SMALL)) * (1 - ease(seg(t, T_BUT1 - 0.2, T_BUT1)))
    draw_text(ctx, "one small word", F_SERIF_I, 76, "#E8DCC8", 540, 360, pre)
    draw_text(ctx, "turns the whole psalm", F_SERIF_I, 64, "#C9D1E8", 540, 460, pre * ease(seg(t, T_TURNS - 0.2, T_TURNS)))
    bw = ease(seg(t, T_BUT1 - 0.04, T_BUT1 + 0.08))
    bout = ease(seg(t, T_TRUSTED - 0.5, T_TRUSTED - 0.15))
    draw_text(ctx, "BUT", F_SERIF, 330, "#E3B04B", 540, 600, bw * (1 - bout), lerp(1.8, 1.0, ein(seg(t, T_BUT1 - 0.04, T_BUT1 + 0.1))), stroke=8, stroke_color="#2A1D14")
    ca = ease(seg(t, T_BUT2 - 0.3, T_BUT2))
    if ca > 0:
        P.verse_card(ctx, 540, 520, 900, 420, ca, 0.95 + 0.05 * back_out(seg(t, T_BUT2 - 0.3, T_BUT2 + 0.2)))
        draw_text(ctx, "“But I have trusted", F_SERIF_I, 64, "#3B2A1E", 540, 450, ca)
        draw_text(ctx, "in your", F_SERIF_I, 64, "#3B2A1E", 540, 535, ca * ease(seg(t, T_TRUSTED, T_TRUSTED + 0.3)))
        draw_text(ctx, "steadfast love.”", F_SERIF, 76, "#A8741A", 540, 625, ca * ease(seg(t, T_STEADFAST1 - 0.2, T_STEADFAST1 + 0.1)))
        P.tag(ctx, "Psalm 13:5", 540, 790, seg(t, T_BUT2 - 0.1, T_BUT2 + 0.3), ca, 250)
    grade(ctx, desat=0.25 * (1 - dawn), cool=0.25 * (1 - dawn), warm=0.12 * dawn)


HEB = "חֶסֶד"


def scene6(ctx, lt):
    """Nugget: chesed, loyal covenant love, love that doesn't quit: a golden cord that never breaks."""
    t = lt + B6
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.5, "gold2", 6, -12)
    draw_text(ctx, "steadfast love", F_SERIF_I, 80, "#E8DCC8", 540, 360, ease(seg(t, T_PHRASE - 0.2, T_PHRASE + 0.3)) * (1 - ease(seg(t, T_KHESED - 0.5, T_KHESED - 0.2))))
    draw_text(ctx, "in Hebrew…", F_SERIF_I, 60, "#C9B48A", 540, 470, ease(seg(t, T_HEBREW - 0.2, T_HEBREW + 0.2)) * (1 - ease(seg(t, T_KHESED - 0.5, T_KHESED - 0.2))))
    hb = ease(seg(t, T_KHESED - 0.45, T_KHESED - 0.1))
    reveal = ease(seg(t, T_KHESED - 0.4, T_KHESED + 0.5))
    rays(ctx, 540, 480, 0, 2 * math.pi, 18, 1000, hb * 0.6, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 240, 540, 470, reveal, hb, rtl=True)
    draw_text(ctx, "KHEH-sed", F_SERIF_I, 84, "#FBF6EC", 540, 650, ease(seg(t, T_KHESED, T_KHESED + 0.3)))
    draw_text(ctx, "loyal, covenant love", F_SERIF, 70, "#E3B04B", 540, 780, ease(seg(t, T_LOYAL - 0.3, T_COVENANT + 0.1)))
    # the cord: one unbroken golden line, looping on and on
    cp = ease(seg(t, T_LOVE4 - 0.4, T_QUIT + 0.6))
    if cp > 0:
        ctx.save()
        ctx.set_source_rgba(0.89, 0.69, 0.29, 0.95)
        ctx.set_line_width(10)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        n = int(200 * cp)
        for i in range(n + 1):
            u = i / 200
            x = 120 + 840 * u
            y = 1100 + 60 * math.sin(u * 4 * 2 * math.pi + t * 2) * math.cos(u * math.pi * 0.5)
            (ctx.move_to if i == 0 else ctx.line_to)(x, y)
        ctx.stroke()
        ctx.restore()
    draw_text(ctx, "love that doesn’t quit", F_SERIF_I, 70, "#FBF6EC", 540, 1260, ease(seg(t, T_LOVE4 - 0.2, T_QUIT)))


def scene7(ctx, lt):
    """He doesn't hide the question; he doesn't let it have the last word: '?' then 'but' after it."""
    t = lt + B7
    R.bg(ctx, hexc("#F1E2C4"))
    rays(ctx, 540, 700, 0, 2 * math.pi, 16, 1100, 0.35, t * 0.2)
    qa = ease(seg(lt, 0.0, 0.35))
    shrink = ease(seg(t, T_LAST - 0.4, T_WORD2 + 0.3))
    draw_text(ctx, "?", F_SERIF, lerp(520, 300, shrink), "#5A6383", lerp(540, 330, shrink), 760, qa)
    draw_text(ctx, "the question stays", F_SERIF_I, 64, "#3B2A1E", 540, 350, ease(seg(t, T_QUESTION - 0.3, T_QUESTION)) * (1 - ease(seg(t, T_LAST - 0.6, T_LAST - 0.3))))
    draw_text(ctx, "but not the last word", F_SERIF_I, 64, "#3B2A1E", 540, 350, ease(seg(t, T_LAST - 0.3, T_LAST)))
    ba = ease(seg(t, T_WORD2 - 0.2, T_WORD2 + 0.15))
    draw_text(ctx, "but…", F_SERIF, 230, "#A8741A", 700, 780, ba, 0.9 + 0.1 * back_out(seg(t, T_WORD2 - 0.2, T_WORD2 + 0.3)))
    grade(ctx, warm=0.08)


def paper(ctx, cx, cy, w, h, alpha, rot=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.set_source_rgba(0.2, 0.13, 0.08, 0.25 * alpha)
    ctx.rectangle(-w / 2 + 12, -h / 2 + 16, w, h); ctx.fill()
    ctx.set_source_rgba(*hexc("#FFF9EE")[:3], alpha)
    ctx.rectangle(-w / 2, -h / 2, w, h); ctx.fill()
    ctx.set_source_rgba(0.55, 0.68, 0.85, 0.5 * alpha)
    ctx.set_line_width(2)
    for y in range(int(-h / 2 + 90), int(h / 2), 70):
        ctx.move_to(-w / 2 + 30, y); ctx.line_to(w / 2 - 30, y)
    ctx.stroke()
    ctx.set_source_rgba(0.85, 0.4, 0.4, 0.5 * alpha)
    ctx.move_to(-w / 2 + 90, -h / 2); ctx.line_to(-w / 2 + 90, h / 2); ctx.stroke()
    ctx.restore()


def ink(ctx, txt, size, color, x, y, reveal, alpha=1.0):
    """Handwritten-style reveal left to right."""
    if reveal <= 0 or alpha <= 0.01:
        return
    s = R.text_surf(txt, F_SERIF_I, size, color)
    ww, hh = s.get_width(), s.get_height()
    ctx.save()
    ctx.rectangle(x - 20, y - hh / 2, ww * reveal, hh)
    ctx.clip()
    ctx.set_source_surface(s, x - 20, y - hh / 2)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def scene8(ctx, lt):
    """Close: write your 'how long', then a line that starts with 'but'. End card; loop."""
    t = lt + B8
    R.bg(ctx, hexc("#E9CFA3"))
    rays(ctx, 540, 300, 0, 2 * math.pi, 16, 1200, 0.45, t * 0.2)
    pa = ease(seg(lt, 0.0, 0.4))
    end = ease(seg(t, T_KEEP - 0.4, T_KEEP))
    paper(ctx, 540, lerp(860, 900, pa), 860, 760, pa * (1 - 0.85 * end), -0.02)
    al = 1 - end
    ink(ctx, "How long, Lord…", 72, "#2C3552", 210, 700, ease(seg(t, T_WRITE1 - 0.1, T_HOW5 + 0.6)), al)
    ink(ctx, "____________ ?", 64, "#5A6383", 210, 780, ease(seg(t, T_HOW5, T_HOW5 + 0.5)), al)
    ink(ctx, "But I trust", 72, "#A8741A", 210, 920, ease(seg(t, T_BUT3 - 0.6, T_BUT3 + 0.4)), al)
    ink(ctx, "your steadfast love.", 64, "#A8741A", 210, 1000, ease(seg(t, T_BUT3, T_BUT3 + 0.8)), al)
    draw_text(ctx, "so today…", F_SERIF_I, 70, "#3B2A1E", 540, 330, ease(seg(t, T_TODAY - 0.2, T_TODAY + 0.2)) * al)
    end_card(ctx, t, "PSALM 13", ICON, "Keep your how long.", "Add a but.", T_KEEP, T_ADD)
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


ICON = lambda c, x, y: hourglass(c, x, y, 0.95, 0.55, 1.0, 0.6)

E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5), (B6, B7, scene6),
            (B7, B8, scene7), (B8, DUR + 1, scene8)]

if __name__ == "__main__":
    if sys.argv[1] == "thumb":
        end_thumbnail("PSALM 13", ICON, "Keep your how long.", "Add a but.", f"{E.dir}/psalm13_thumbnail.png")
    else:
        E.main(sys.argv)
