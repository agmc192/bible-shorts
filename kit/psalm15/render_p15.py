"""Psalm 15 Short. Desert-dusk terracotta and olive; a lit tent on a holy hill; a portrait in a gold frame; ground that shakes.
Central image: God's tent with its door open to a guest."""
import sys, math, random
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/psalm4")
import cairo
from engine import Episode, end_card, end_thumbnail
import render as R
import render_v2 as V
import render_p2 as P
import render_p3 as Q
import render_p4 as P4
from render import (W, H, col, hexc, lerp, lerpc, clamp, seg, ease, eout, ein, draw_text, rounded,
                    F_SERIF, F_SERIF_I, F_SERIF_R, F_HEB, F_CAP)
back_out, rays, dust, grade, kword = V.back_out, V.rays, V.dust, V.grade, V.kword

E = Episode(15)
wt, DUR = E.wt, E.dur
T_KEEP1 = wt("keep", 1); T_WORD1 = wt("word", 1); T_COSTS = wt("costs"); T_PSALM = wt("psalm"); T_QUESTION = wt("question")
T_LORD = wt("lord"); T_STAY1 = wt("stay", 1); T_TENT = wt("tent"); T_LIVE1 = wt("live", 1); T_HILL = wt("hill")
T_WORD2 = wt("word", 2); T_HEBREW = wt("hebrew"); T_GOOR = wt("goor"); T_LIVE2 = wt("live", 2); T_GUEST1 = wt("guest", 1)
T_GETS = wt("gets"); T_GUEST2 = wt("guest", 2); T_ANSWER = wt("answer"); T_PORTRAIT = wt("portrait")
T_WALKS = wt("walks"); T_INTEGRITY = wt("integrity"); T_TRUTH = wt("truth"); T_SLANDER = wt("slander")
T_KEEPS = wt("keeps"); T_HURTS = wt("hurts"); T_BRIBE = wt("bribe"); T_INNOCENT = wt("innocent")
T_ENDS = wt("ends"); T_PROMISE2 = wt("promise", 2); T_NEVER = wt("never"); T_SHAKEN = wt("shaken")
T_TODAY = wt("today"); T_KEEP2 = wt("keep", 2); T_BREAK = wt("break"); T_KEEP3 = wt("keep", 3); T_WORD3 = wt("word", 3)
T_STAND = wt("stand"); T_UNSHAKEN = wt("unshaken")

B1 = 0.0
B2 = T_PSALM - 0.35
B3 = T_WORD2 - 0.35
B4 = T_ANSWER - 0.35
B5 = T_ENDS - 0.35
B6 = T_TODAY - 0.35

E.zooms = [(0.1, 0.12), (T_COSTS, 0.08), (T_TENT, 0.07), (T_HILL, 0.07), (T_GOOR, 0.12), (T_GUEST2, 0.06),
           (T_PORTRAIT, 0.07), (T_HURTS, 0.06), (T_SHAKEN, 0.1), (T_KEEP3, 0.07), (T_UNSHAKEN, 0.1)]
E.shakes = [(0.1, 10, 0.5), (T_NEVER - 0.6, 22, 1.2), (T_COSTS, 8, 0.4)]
E.flashes = [(0.1, (1, 1, 1), 0.25, 0.3), (T_GOOR, (1, 0.88, 0.55), 0.3, 0.4), (T_SHAKEN, (1, 0.94, 0.75), 0.45, 0.6),
             (T_UNSHAKEN, (1, 0.95, 0.85), 0.35, 0.45)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6)]

DUSK1 = hexc("#E9A46A")
DUSK2 = hexc("#7A3E3A")
HILL = hexc("#5E4A2E")
TERRA = hexc("#B5573A")


def dusk(ctx, t, k=1.0):
    g = cairo.LinearGradient(0, 0, 0, 1300)
    g.add_color_stop_rgba(0, *lerpc(hexc("#3E2A3A"), DUSK2, k))
    g.add_color_stop_rgba(0.6, *lerpc(hexc("#7A4A44"), DUSK1, k))
    g.add_color_stop_rgba(1, *lerpc(hexc("#B07A55"), hexc("#F2CF95"), k))
    ctx.set_source(g)
    ctx.paint()


def holy_hill(ctx, t, glow=0.0, top_y=760, alpha=1.0):
    """A broad hill with God's tent at the top; the door glows."""
    ctx.set_source_rgba(*hexc("#7A5B38")[:3], alpha)
    ctx.move_to(-50, 1450); ctx.curve_to(200, 1100, 380, top_y + 40, 540, top_y + 30)
    ctx.curve_to(700, top_y + 40, 880, 1100, 1130, 1450); ctx.line_to(1130, H); ctx.line_to(-50, H); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(*HILL[:3], alpha)
    ctx.move_to(-50, 1600); ctx.curve_to(300, 1380, 700, 1420, 1130, 1560); ctx.line_to(1130, H); ctx.line_to(-50, H); ctx.close_path(); ctx.fill()
    tent(ctx, 540, top_y + 34, 1.0, glow, alpha)


def tent(ctx, cx, base, s, glow, alpha=1.0):
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(s, s)
    if glow > 0:
        g = cairo.RadialGradient(0, -60, 10, 0, -60, 340)
        g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.7 * glow * alpha)
        g.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
        ctx.set_source(g); ctx.arc(0, -60, 340, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(*hexc("#E8D2A6")[:3], alpha)
    ctx.move_to(-190, 0); ctx.line_to(-40, -170); ctx.line_to(40, -170); ctx.line_to(190, 0); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(*hexc("#B89A6A")[:3], alpha)
    for x in (-110, 0, 110):
        ctx.rectangle(x - 4, -150 + abs(x) * 0.9, 8, 150 - abs(x) * 0.9); ctx.fill()
    ctx.set_source_rgba(*lerpc(hexc("#4A3424"), hexc("#FFD98A"), glow)[:3], alpha)
    ctx.move_to(-45, 0); ctx.line_to(0, -120); ctx.line_to(45, 0); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(*hexc("#5A4028")[:3], alpha)
    ctx.set_line_width(5)
    ctx.move_to(-40, -170); ctx.line_to(-60, -205); ctx.move_to(40, -170); ctx.line_to(60, -205); ctx.stroke()
    ctx.restore()


def frame(ctx, cx, cy, w, h, alpha, inner=None):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.set_source_rgba(0.2, 0.12, 0.06, 0.3 * alpha)
    ctx.rectangle(-w / 2 + 14, -h / 2 + 18, w, h); ctx.fill()
    ctx.set_source_rgba(*hexc("#C8902E")[:3], alpha)
    ctx.rectangle(-w / 2, -h / 2, w, h); ctx.fill()
    ctx.set_source_rgba(*hexc("#8A5E1E")[:3], alpha)
    ctx.rectangle(-w / 2 + 20, -h / 2 + 20, w - 40, h - 40); ctx.fill()
    ctx.rectangle(-w / 2 + 34, -h / 2 + 34, w - 68, h - 68); ctx.clip()
    ctx.set_source_rgba(*hexc("#F1E2C4")[:3], alpha); ctx.paint()
    if inner:
        inner(ctx)
    ctx.restore()


def coins(ctx, t, t0, alpha):
    r = random.Random(4)
    for k in range(9):
        u = t - t0 - k * 0.09
        if u < 0:
            continue
        x = 600 + r.uniform(-70, 70)
        y = 980 + 900 * u * u
        if y > 1500:
            continue
        ctx.set_source_rgba(0.89, 0.69, 0.29, alpha)
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.35 + 0.65 * abs(math.sin(u * 9 + k))); ctx.arc(0, 0, 22, 0, 2 * math.pi); ctx.restore()
        ctx.fill()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: a figure gives their word; the cost falls away like coins."""
    t = lt
    dusk(ctx, t, 0.4)
    ctx.set_source_rgba(*HILL[:3], 1); ctx.rectangle(0, 1440, W, H); ctx.fill()
    Q.person(ctx, 380, 1450, 1.7, hexc("#2A1C14"), 0, 0, 0, 0.35)
    Q.person(ctx, 720, 1450, 1.5, hexc("#3A2A1E"), 0, 0, 0, 0.2, 0, 0.9)
    ba = ease(seg(t, 0.1, 0.4))
    P4.bubble(ctx, 420, 860, 360, 120, hexc("#FFF4DE"), ba, 1)
    draw_text(ctx, "I promise.", F_SERIF_I, 60, "#3B2A1E", 420, 860, ba)
    coins(ctx, t, T_COSTS - 0.15, 1.0)
    kword(ctx, "YOUR WORD?", t, T_WORD1 - 0.05, 540, 380, 130, "#FBF6EC", T_COSTS - T_WORD1)
    kword(ctx, "EVEN IF IT COSTS?", t, T_COSTS - 0.1, 540, 380, 80, "#E3B04B", B2 - T_COSTS + 0.2)
    grade(ctx, desat=0.15)


def scene2(ctx, lt):
    """Title; Lord, who can stay in your tent? Who can live on your holy hill?"""
    t = lt + B2
    dusk(ctx, t, 0.8)
    rise = ease(seg(lt, 0.0, 0.8))
    glow = ease(seg(t, T_TENT - 0.3, T_TENT + 0.4))
    ctx.save(); ctx.translate(0, 200 * (1 - rise))
    holy_hill(ctx, t, glow)
    ctx.restore()
    ti = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_LORD - 0.4, T_LORD - 0.1)))
    draw_text(ctx, "PSALM 15", F_SERIF, 150, "#FBF6EC", 540, 420, ti, 0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#3E2A3A")
    draw_text(ctx, "asks God a question", F_SERIF_I, 66, "#FFF4DE", 540, 550, ti * ease(seg(t, T_QUESTION - 0.4, T_QUESTION)))
    P.tag(ctx, "Psalm 15:1", 540, 200, seg(t, T_LORD - 0.2, T_LORD + 0.2), 1.0, 250)
    draw_text(ctx, "Who can stay in your tent?", F_SERIF, 76, "#FBF6EC", 540, 380, ease(seg(t, T_LORD - 0.2, T_STAY1)), stroke=3, stroke_color="#3E2A3A")
    draw_text(ctx, "Who can live on your holy hill?", F_SERIF_I, 64, "#FFE3A3", 540, 490, ease(seg(t, T_LIVE1 - 0.3, T_LIVE1)), stroke=3, stroke_color="#3E2A3A")
    grade(ctx, warm=0.06)


HEB = "גּוּר"


def scene3(ctx, lt):
    """Nugget: gur, to live somewhere as a guest. A small figure walks up to the lit door."""
    t = lt + B3
    dusk(ctx, t, 0.3)
    holy_hill(ctx, t, 0.9 + 0.1 * math.sin(t * 2), 760, 0.35)
    ctx.set_source_rgba(0.12, 0.07, 0.06, 0.55); ctx.paint()
    dust(ctx, t, 0.5, "gold2", 6, -12)
    draw_text(ctx, "the word for stay", F_SERIF_I, 64, "#E8DCC8", 540, 330, ease(seg(t, T_WORD2 - 0.2, T_HEBREW)) * (1 - ease(seg(t, T_GUEST2 - 0.4, T_GUEST2 - 0.1))))
    hb = ease(seg(t, T_GOOR - 0.45, T_GOOR - 0.1))
    reveal = ease(seg(t, T_GOOR - 0.4, T_GOOR + 0.5))
    rays(ctx, 540, 520, 0, 2 * math.pi, 18, 1000, hb * 0.5, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 240, 540, 520, reveal, hb, rtl=True)
    draw_text(ctx, "GOOR", F_SERIF_I, 84, "#FBF6EC", 540, 700, ease(seg(t, T_GOOR, T_GOOR + 0.3)))
    draw_text(ctx, "to live somewhere as a guest", F_SERIF, 62, "#E3B04B", 540, 820, ease(seg(t, T_LIVE2 - 0.3, T_GUEST1)))
    wk = ease(seg(t, T_GUEST1 - 0.5, B4))
    tent(ctx, 540, 1350, 1.4, 1.0, ease(seg(t, T_LIVE2 - 0.4, T_LIVE2)))
    Q.person(ctx, lerp(120, 420, wk), 1430, 1.0, hexc("#1E140E"), 0, 0, 0, 0.1, 0, ease(seg(t, T_LIVE2 - 0.4, T_LIVE2)))
    draw_text(ctx, "Who gets to be God’s guest?", F_SERIF_I, 64, "#FBF6EC", 540, 970, ease(seg(t, T_GETS - 0.3, T_GETS)))


TRAITS = [("walks with integrity", "T_WALKS", 300, 500), ("speaks truth from the heart", "T_TRUTH", 760, 610),
          ("doesn’t slander", "T_SLANDER", 280, 1240), ("keeps a promise that hurts", "T_KEEPS", 760, 1345),
          ("won’t take a bribe", "T_BRIBE", 400, 1450)]


def scene4(ctx, lt):
    """The answer reads like a portrait: a gold frame, and its traits pinned around it."""
    t = lt + B4
    R.bg(ctx, hexc("#EAD7B4"))
    rays(ctx, 540, 900, 0, 2 * math.pi, 16, 1100, 0.3, t * 0.2)
    fa = ease(seg(t, T_PORTRAIT - 0.4, T_PORTRAIT))
    fill = clamp((t - T_WALKS) / (T_INNOCENT - T_WALKS + 0.3))

    def inner(c):
        g = cairo.LinearGradient(0, -300, 0, 300)
        g.add_color_stop_rgba(0, 0.95, 0.85, 0.6, 0.5 * fill)
        g.add_color_stop_rgba(1, 0.95, 0.85, 0.6, 0)
        c.set_source(g); c.paint()
        Q.person(c, 0, 230, 1.6, lerpc(hexc("#9A8A74"), col("dark"), fill), 0, 0, 0, 0.1, 0, 0.3 + 0.7 * fill)
    frame(ctx, 540, 930, 480, 620, fa, inner)
    P.tag(ctx, "Psalm 15:2-5", 540, 200, seg(t, T_WALKS - 0.2, T_WALKS + 0.2), 1.0, 280)
    draw_text(ctx, "it reads like a portrait", F_SERIF_I, 66, "#3B2A1E", 540, 340, ease(seg(t, T_ANSWER - 0.2, T_PORTRAIT)))
    for txt, key, x, y in TRAITS:
        tk = globals()[key]
        a = ease(seg(t, tk - 0.25, tk + 0.05))
        if a <= 0.01:
            continue
        s = R.text_surf(txt, F_SERIF_I, 54, "#2A1D14")
        w = min(s.get_width() + 20, 640)
        x = clamp(x, w / 2 + 20, W - w / 2 - 20)
        sc = 0.9 + 0.1 * back_out(seg(t, tk - 0.25, tk + 0.15))
        ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
        ctx.set_source_rgba(0.2, 0.12, 0.06, 0.25 * a); rounded(ctx, -w / 2 + 6, -46, w, 96, 24); ctx.fill()
        ctx.set_source_rgba(*hexc("#FFF9EE")[:3], a); rounded(ctx, -w / 2, -50, w, 96, 24); ctx.fill()
        ctx.set_source_rgba(*col("gold", a)); ctx.set_line_width(4); rounded(ctx, -w / 2, -50, w, 96, 24); ctx.stroke()
        ctx.restore()
        R.draw_surf(ctx, s, x, y - 2, a, sc * min(1.0, 610 / s.get_width()))


def scene5(ctx, lt):
    """It ends with a promise: the ground shakes, everything else topples; the figure stands. Never shaken."""
    t = lt + B5
    dusk(ctx, t, 1.0)
    quake = ease(seg(t, T_NEVER - 0.8, T_NEVER - 0.4)) * (1 - ease(seg(t, T_SHAKEN, T_SHAKEN + 0.5)))
    ctx.set_source_rgba(*HILL[:3], 1)
    ctx.move_to(0, 1300)
    for i in range(41):
        x = i * W / 40
        ctx.line_to(x, 1300 + 18 * quake * math.sin(t * 40 + i * 1.7))
    ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path(); ctx.fill()
    fall = ease(seg(t, T_NEVER - 0.6, T_SHAKEN + 0.2))
    for k, (x, h) in enumerate(((150, 260), (300, 180), (800, 220), (950, 300))):
        ctx.save()
        ctx.translate(x, 1300)
        ctx.rotate((1 if k % 2 else -1) * 1.45 * clamp(fall * 1.3 - 0.15 * k))
        ctx.set_source_rgba(*TERRA[:3], 1)
        ctx.rectangle(-40, -h, 80, h); ctx.fill()
        ctx.restore()
    st = ease(seg(t, T_SHAKEN - 0.2, T_SHAKEN + 0.4))
    if st > 0:
        rays(ctx, 540, 1000, 0, 2 * math.pi, 20, 1200, 0.8 * st, t * 0.3)
    Q.person(ctx, 540, 1310, 1.9, hexc("#2A1C14"), 0, 0, 0, 0.1 + 0.5 * st)
    P.tag(ctx, "Psalm 15:5", 540, 200, seg(t, T_ENDS - 0.2, T_ENDS + 0.2), 1.0, 250)
    draw_text(ctx, "it ends with a promise", F_SERIF_I, 66, "#FFF4DE", 540, 360, ease(seg(t, T_ENDS - 0.2, T_PROMISE2)) * (1 - ease(seg(t, T_NEVER - 0.3, T_NEVER))))
    draw_text(ctx, "never be shaken", F_SERIF, 110, "#FBF6EC", 540, 380, ease(seg(t, T_NEVER - 0.2, T_SHAKEN)), 0.92 + 0.08 * back_out(seg(t, T_SHAKEN - 0.2, T_SHAKEN + 0.3)), stroke=4, stroke_color="#3E2A3A")
    grade(ctx, warm=0.06 * st)


def scene6(ctx, lt):
    """Close: keep one promise you'd rather break; a promise card gets its check. End card; loop."""
    t = lt + B6
    R.bg(ctx, hexc("#EBD2A6"))
    rays(ctx, 540, 300, 0, 2 * math.pi, 16, 1200, 0.45, t * 0.2)
    end = ease(seg(t, T_KEEP3 - 0.4, T_KEEP3))
    ca = ease(seg(lt, 0.0, 0.4)) * (1 - end)
    P.verse_card(ctx, 540, 900, 760, 360, ca, 0.95 + 0.05 * back_out(seg(lt, 0.0, 0.4)))
    draw_text(ctx, "one promise", F_SERIF_I, 70, "#3B2A1E", 540, 850, ca * ease(seg(t, T_KEEP2 - 0.2, T_KEEP2 + 0.2)))
    draw_text(ctx, "I’d rather break", F_SERIF_I, 58, "#8A6A44", 540, 950, ca * ease(seg(t, T_BREAK - 0.3, T_BREAK)))
    ck = ease(seg(t, T_BREAK + 0.1, T_BREAK + 0.5))
    if ck > 0 and ca > 0:
        ctx.set_source_rgba(0.66, 0.45, 0.1, ca)
        ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(840, 900)
        if ck < 0.4:
            ctx.line_to(840 + 40 * ck / 0.4, 900 + 40 * ck / 0.4)
        else:
            ctx.line_to(880, 940); ctx.line_to(880 + 90 * (ck - 0.4) / 0.6, 940 - 120 * (ck - 0.4) / 0.6)
        ctx.stroke()
    draw_text(ctx, "so today…", F_SERIF_I, 70, "#3B2A1E", 540, 330, ease(seg(t, T_TODAY - 0.2, T_TODAY + 0.2)) * (1 - end))
    end_card(ctx, t, "PSALM 15", ICON, "Keep your word.", "Stand unshaken.", T_KEEP3, T_STAND)
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


def ICON(c, x, y):
    c.set_source_rgba(*hexc("#7A5B38"))
    c.move_to(x - 260, y + 150); c.curve_to(x - 150, y + 70, x - 60, y + 60, x, y + 60)
    c.curve_to(x + 60, y + 60, x + 150, y + 70, x + 260, y + 150); c.close_path(); c.fill()
    tent(c, x, y + 68, 0.95, 1.0)

E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5), (B6, DUR + 1, scene6)]

if __name__ == "__main__":
    if sys.argv[1] == "thumb":
        end_thumbnail("PSALM 15", ICON, "Keep your word.", "Stand unshaken.", f"{E.dir}/psalm15_thumbnail.png")
    else:
        E.main(sys.argv)
