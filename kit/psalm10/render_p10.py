"""Psalm 10 Short. Storm-dusk palette with an eclipsed sun. Central image: the hidden sun that turns out to see."""
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

E = Episode(10)
wt, DUR = E.wt, E.dur
T_FAR1 = wt("far", 1); T_AWAY1 = wt("away", 1); T_FALLING = wt("falling"); T_APART = wt("apart"); T_PSALM = wt("psalm", 1)
T_QUESTION = wt("question"); T_WHY2 = wt("why", 2); T_STAND = wt("stand"); T_AWAY2 = wt("away", 2); T_HIDE = wt("hide")
T_TROUBLE1 = wt("trouble", 1); T_WATCHES = wt("watches"); T_PROUD = wt("proud"); T_HUNT = wt("hunt"); T_WEAK = wt("weak")
T_LION = wt("lion"); T_AMBUSH = wt("ambush"); T_WICKED1 = wt("wicked", 1); T_FORGOTTEN = wt("forgotten")
T_NEVER1 = wt("never", 1); T_SEE1 = wt("see", 1); T_ANSWERS = wt("answers"); T_DO = wt("do", 2); T_SEE2 = wt("see", 2)
T_NOTE = wt("note"); T_GRIEF = wt("grief"); T_HELPLESS = wt("helpless"); T_COMMIT = wt("commit"); T_HEARS = wt("hears")
T_DESIRE = wt("desire"); T_JUSTICE = wt("justice"); T_FATHERLESS = wt("fatherless"); T_OPPRESSED = wt("oppressed")
T_HEBREW = wt("hebrew"); T_RAITAH = wt("raheetah"); T_SEEN = wt("seen"); T_WICKED2 = wt("wicked", 2)
T_NEVER2 = wt("never", 2); T_SEE3 = wt("see", 3); T_ALREADY = wt("already"); T_TODAY = wt("today"); T_HONEST = wt("honest")
T_HANDLE = wt("handle"); T_ASK = wt("ask"); T_SEES = wt("sees")

B1 = 0.0
B2 = T_PSALM - 0.3
B3 = T_WATCHES - 0.6
B4 = T_ANSWERS - 0.5
B5 = T_HEBREW - 0.45
B6 = T_TODAY - 0.4

E.zooms = [(0.1, 0.12), (T_APART, 0.08), (T_HIDE, 0.08), (T_AMBUSH, 0.10), (T_FORGOTTEN, 0.06), (T_SEE2, 0.14),
           (T_JUSTICE, 0.06), (T_RAITAH, 0.12), (T_ALREADY, 0.07), (T_SEES, 0.08)]
E.shakes = [(0.1, 16, 0.7), (T_APART, 12, 0.6), (T_AMBUSH, 10, 0.5), (T_SEE2, 14, 0.6), (T_RAITAH, 10, 0.5)]
E.flashes = [(0.1, (1, 0.95, 0.9), 0.35, 0.3), (T_SEE2, (1, 0.92, 0.7), 0.6, 0.6), (T_RAITAH, (1, 0.85, 0.5), 0.3, 0.4),
             (T_ALREADY, (1, 0.92, 0.75), 0.3, 0.4), (T_SEES, (1, 0.95, 0.85), 0.35, 0.45)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6)]

DUSK1 = hexc("#3B3F4A")
DUSK2 = hexc("#6B5E5A")
DUSK3 = hexc("#9A7A62")
GRASS = hexc("#4C5A3A")
GROUND_Y = 1240

_dr = random.Random(10)
DEBRIS = [(_dr.uniform(80, W - 80), _dr.uniform(900, 1300), _dr.uniform(20, 60), _dr.uniform(-2, 2)) for _ in range(14)]


def sky(ctx, k_light=0.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND_Y)
    g.add_color_stop_rgba(0, *lerpc(DUSK1, hexc("#F6E2B8"), k_light))
    g.add_color_stop_rgba(0.6, *lerpc(DUSK2, hexc("#F3CC8E"), k_light))
    g.add_color_stop_rgba(1, *lerpc(DUSK3, hexc("#E9A46E"), k_light))
    ctx.set_source(g)
    ctx.paint()


def eclipse(ctx, cx, cy, r, cover, t, alpha=1.0):
    """Sun at (cx, cy); a dark disc covers it by 'cover' (1 = full eclipse, 0 = clear)."""
    corona = 0.5 + 0.5 * cover
    rays(ctx, cx, cy, 0, 2 * math.pi, 18, 900 * (1.2 - 0.6 * cover), alpha * (1 - 0.6 * cover), t * 0.4)
    g = cairo.RadialGradient(cx, cy, r * 0.8, cx, cy, r * 2.6)
    g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.8 * alpha * corona)
    g.add_color_stop_rgba(1, 1, 0.8, 0.5, 0)
    ctx.set_source(g)
    ctx.arc(cx, cy, r * 2.6, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(1, 0.92, 0.65, alpha)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.fill()
    if cover > 0.01:
        ox = lerp(r * 2.4, 0, cover)
        ctx.set_source_rgba(*hexc("#1E2028")[:3], alpha)
        ctx.arc(cx + ox, cy - ox * 0.2, r * 1.02, 0, 2 * math.pi)
        ctx.fill()


def grass(ctx, t, y=GROUND_Y, c=GRASS, alpha=1.0, n=60, seed=3, hmax=180):
    r = random.Random(seed)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.rectangle(0, y, W, H)
    ctx.fill()
    for i in range(n):
        x = r.uniform(-20, W + 20)
        hh = r.uniform(80, hmax)
        sw = 0.08 * math.sin(t * 1.7 + x * 0.02)
        ctx.move_to(x - 8, y + 4)
        ctx.curve_to(x - 4, y - hh * 0.5, x + sw * hh, y - hh * 0.8, x + sw * hh * 1.3, y - hh)
        ctx.curve_to(x + 4, y - hh * 0.6, x + 6, y - hh * 0.3, x + 8, y + 4)
        ctx.close_path()
        ctx.fill()


def lion_eyes(ctx, x, y, a, t):
    if a <= 0.01:
        return
    blink = 1 - max(0, math.sin(t * 2.2)) ** 30
    for dx in (-36, 36):
        g = cairo.RadialGradient(x + dx, y, 2, x + dx, y, 34)
        g.add_color_stop_rgba(0, 1, 0.85, 0.3, a)
        g.add_color_stop_rgba(1, 1, 0.7, 0.2, 0)
        ctx.set_source(g)
        ctx.arc(x + dx, y, 34, 0, 2 * math.pi)
        ctx.fill()
        ctx.save()
        ctx.translate(x + dx, y)
        ctx.scale(1, 0.55 * blink + 0.02)
        ctx.set_source_rgba(1, 0.86, 0.35, a)
        ctx.arc(0, 0, 16, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()


def eye(ctx, cx, cy, s, open_, alpha=1.0):
    """A stylised open eye made of light (never a face)."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s * max(0.04, open_))
    ctx.move_to(-120, 0)
    ctx.curve_to(-60, -80, 60, -80, 120, 0)
    ctx.curve_to(60, 80, -60, 80, -120, 0)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.8, alpha)
    ctx.fill()
    ctx.restore()
    if open_ > 0.3:
        ctx.set_source_rgba(*col("gold", alpha * seg(open_, 0.3, 1.0)))
        ctx.arc(cx, cy, 40 * s, 0, 2 * math.pi)
        ctx.fill()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: everything falling apart under an eclipsed sun."""
    t = lt
    sky(ctx)
    eclipse(ctx, 540, 420, 110, 1.0, t)
    V.hills(ctx, GROUND_Y - 120, 50, hexc("#2C2F36"), 0, 101)
    ctx.set_source_rgba(*hexc("#2A2723"))
    ctx.rectangle(0, GROUND_Y, W, H)
    ctx.fill()
    ap = ease(seg(t, T_FALLING - 0.3, T_APART + 0.6))
    for x, y, s, sp in DEBRIS:
        yy = y - 300 * ap * (0.5 + 0.5 * abs(sp))
        ctx.save()
        ctx.translate(x + sp * 60 * ap, yy)
        ctx.rotate(sp * ap * 2)
        ctx.set_source_rgba(*hexc("#5A5048"))
        ctx.rectangle(-s / 2, -s / 3, s, s * 0.66)
        ctx.fill()
        ctx.restore()
    # crack splitting the ground on the first frame
    ck = eout(seg(lt, 0.0, 0.4))
    ctx.set_source_rgba(0.05, 0.04, 0.03, 0.95)
    pts = [(820, GROUND_Y), (760, GROUND_Y + 140), (840, GROUND_Y + 260), (700, GROUND_Y + 420), (780, GROUND_Y + 560), (640, H)]
    ctx.move_to(*pts[0])
    for i, (x, y) in enumerate(pts[1:]):
        ctx.line_to(x - 4 - 10 * i * ck, GROUND_Y + (y - GROUND_Y) * ck)
    for i, (x, y) in reversed(list(enumerate(pts[1:]))):
        ctx.line_to(x + 4 + 10 * i * ck, GROUND_Y + (y - GROUND_Y) * ck)
    ctx.close_path()
    ctx.fill()
    Q.person(ctx, 540, GROUND_Y + 30, 1.3, hexc("#141210"), 0.5, 0, 0, 0.1)
    kword(ctx, "FAR AWAY", t, T_FAR1 - 0.04, 540, 760, 150, "#CFE0F5", T_APART - T_FAR1 + 0.4)
    grade(ctx, desat=0.3)


def scene2(ctx, lt):
    """Title and the psalm's opening question."""
    t = lt + B2
    sky(ctx)
    eclipse(ctx, 540, 1080, 90, 1.0, t, 0.8)
    V.hills(ctx, GROUND_Y - 120, 50, hexc("#2C2F36"), 0, 101)
    ctx.set_source_rgba(*hexc("#2A2723"))
    ctx.rectangle(0, GROUND_Y, W, H)
    ctx.fill()
    ti = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_WHY2 - 0.4, T_WHY2 - 0.1)))
    draw_text(ctx, "PSALM 10", F_SERIF, 150, "#FBF6EC", 540, 760, ti, 0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#1E2028")
    draw_text(ctx, "opens with a question", F_SERIF_I, 62, "#E8DCC8", 540, 880, ease(seg(t, T_QUESTION - 0.3, T_QUESTION)) * (1 - ease(seg(t, T_WHY2 - 0.4, T_WHY2 - 0.1))))
    q = ease(seg(t, T_WHY2 - 0.2, T_WHY2 + 0.1))
    P.tag(ctx, "Psalm 10:1", 540, 480, seg(t, T_WHY2 - 0.2, T_WHY2 + 0.2), 1.0, 250)
    draw_text(ctx, "“Why, LORD,", F_SERIF_I, 90, "#FBF6EC", 540, 640, q, stroke=3, stroke_color="#1E2028")
    draw_text(ctx, "do you stand far away?", F_SERIF_I, 70, "#FBF6EC", 540, 750, ease(seg(t, T_STAND - 0.2, T_STAND + 0.1)), stroke=3, stroke_color="#1E2028")
    draw_text(ctx, "Why do you hide yourself", F_SERIF_I, 70, "#E3B04B", 540, 880, ease(seg(t, T_HIDE - 0.3, T_HIDE)), stroke=3, stroke_color="#1E2028")
    draw_text(ctx, "in times of trouble?”", F_SERIF_I, 70, "#E3B04B", 540, 980, ease(seg(t, T_TROUBLE1 - 0.3, T_TROUBLE1)), stroke=3, stroke_color="#1E2028")


def scene3(ctx, lt):
    """The proud hunt the weak; a lion in ambush; 'God has forgotten. He will never see it.'"""
    t = lt + B3
    sky(ctx)
    eclipse(ctx, 820, 300, 70, 1.0, t, 0.7)
    V.hills(ctx, GROUND_Y - 120, 50, hexc("#2C2F36"), 0, 102)
    grass(ctx, t, GROUND_Y, GRASS, 1.0, 50, 5)
    hunt = ease(seg(t, T_HUNT - 0.3, T_AMBUSH + 0.5))
    Q.person(ctx, lerp(160, 360, hunt), GROUND_Y + 30, 1.45, hexc("#1A1714"), 0, 0, 0, 0.6)
    Q.person(ctx, lerp(560, 760, hunt), GROUND_Y + 30, 0.8, hexc("#7A6E66"), 0.6, 0, 0, 0.1)
    grass(ctx, t, GROUND_Y + 120, hexc("#3A4630"), 1.0, 40, 9, 260)
    lion_eyes(ctx, 880, GROUND_Y + 30, ease(seg(t, T_LION - 0.3, T_LION)), t)
    P.tag(ctx, "Psalm 10:2, 8-9", 540, 200, seg(t, T_PROUD - 0.2, T_PROUD + 0.2), 1 - ease(seg(t, T_WICKED1 - 0.3, T_WICKED1)), 320)
    kword(ctx, "AMBUSH", t, T_AMBUSH - 0.04, 540, 460, 170, "#E07A5F", T_WICKED1 - T_AMBUSH)
    # the wicked man's boast
    bb = ease(seg(t, T_FORGOTTEN - 0.4, T_FORGOTTEN - 0.1))
    if bb > 0:
        P4.bubble(ctx, 540, 560, 820, 300, hexc("#2E2A30"), 0.95 * bb, -1)
        draw_text(ctx, "“God has forgotten.", F_SERIF_I, 64, "#FBF6EC", 540, 520, ease(seg(t, T_FORGOTTEN - 0.3, T_FORGOTTEN)))
        draw_text(ctx, "He will never see it.”", F_SERIF_I, 64, "#E07A5F", 540, 610, ease(seg(t, T_NEVER1 - 0.2, T_SEE1)))
        P.tag(ctx, "Psalm 10:11", 540, 200, seg(t, T_FORGOTTEN - 0.2, T_FORGOTTEN + 0.2), 1.0, 250)
    grade(ctx, desat=0.3)


def scene4(ctx, lt):
    """'You do see.' The eclipse clears; the afflicted are heard, the fatherless and oppressed given justice."""
    t = lt + B4
    clear = ease(seg(t, T_DO - 0.1, T_SEE2 + 0.3))
    sky(ctx, clear)
    eclipse(ctx, 540, 380, 120, 1 - clear, t)
    V.hills(ctx, GROUND_Y - 120, 50, lerpc(hexc("#2C2F36"), hexc("#B8604A"), clear), 0, 101)
    grass(ctx, t, GROUND_Y, lerpc(GRASS, hexc("#7D8A4A"), clear), 1.0, 50, 5)
    draw_text(ctx, "“You do see.”", F_SERIF, 130, "#FBF6EC", 540, 680, ease(seg(t, T_DO - 0.2, T_SEE2)) * (1 - ease(seg(t, T_NOTE - 0.3, T_NOTE))),
              0.92 + 0.08 * back_out(seg(t, T_DO - 0.2, T_SEE2 + 0.1)), stroke=5, stroke_color="#3B2A1E")
    P.tag(ctx, "Psalm 10:14", 540, 200, seg(t, T_DO - 0.2, T_DO + 0.2), 1 - ease(seg(t, T_HEARS - 0.3, T_HEARS)), 250)
    # trouble and grief are noted: small marks gather into the light
    nt = ease(seg(t, T_NOTE - 0.2, T_GRIEF + 0.4)) * (1 - ease(seg(t, T_HEARS - 0.3, T_HEARS)))
    if nt > 0:
        for k in range(8):
            a = k * math.pi / 4 + t * 0.6
            rr = lerp(440, 200, nt)
            x, y = 540 + rr * math.cos(a), 380 + rr * 0.7 * math.sin(a)
            P.burn_word(ctx, "·", F_SERIF, 90, x, y, 1.0, nt)
        draw_text(ctx, "trouble and grief: noted", F_SERIF_I, 60, "#3B2A1E", 540, 740, nt)
    kn = ease(seg(t, T_HELPLESS - 0.3, T_COMMIT))
    Q.person(ctx, 540, GROUND_Y + 30, 1.15, col("brown"), 0.4 * (1 - kn), 0, 0, 0.6 + 0.4 * kn, kn, alpha=ease(seg(t, T_HELPLESS - 0.4, T_HELPLESS)))
    # justice for the fatherless and the oppressed: a child lifted into the light
    js = ease(seg(t, T_FATHERLESS - 0.4, T_FATHERLESS + 0.2))
    if js > 0:
        Q.person(ctx, 300, GROUND_Y + 30, 0.7, col("brown"), 0, 0, 0, 0.9 * js, alpha=js)
        Q.person(ctx, 800, GROUND_Y + 30, 0.95, col("brown"), 0.4 * (1 - js), 0, 0, 0.9 * js, alpha=js)
        for x in (300, 800):
            g = cairo.RadialGradient(x, GROUND_Y - 120, 10, x, GROUND_Y - 120, 220 * js)
            g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.6)
            g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
            ctx.set_source(g)
            ctx.arc(x, GROUND_Y - 120, 220 * js, 0, 2 * math.pi)
            ctx.fill()
    P.tag(ctx, "Psalm 10:17-18", 540, 200, seg(t, T_HEARS - 0.2, T_HEARS + 0.2), 1.0, 320)
    draw_text(ctx, "he hears", F_SERIF_I, 70, "#3B2A1E", 540, 740, ease(seg(t, T_HEARS - 0.2, T_HEARS + 0.2)) * (1 - ease(seg(t, T_JUSTICE - 0.3, T_JUSTICE))))
    draw_text(ctx, "justice", F_SERIF, 110, "#A8741A", 540, 740, ease(seg(t, T_JUSTICE - 0.2, T_JUSTICE + 0.2)))
    grade(ctx, desat=0.3 * (1 - clear))


HEB = "רָאִתָה"


def scene5(ctx, lt):
    """Nugget: ra'itah, 'you have seen', against the wicked man's 'he will never see'."""
    t = lt + B5
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.5, "gold2", 6, -12)
    ih = ease(seg(t, T_HEBREW - 0.2, T_HEBREW + 0.2)) * (1 - ease(seg(t, T_RAITAH - 0.6, T_RAITAH - 0.3)))
    draw_text(ctx, "In Hebrew,", F_SERIF_I, 80, "#E8DCC8", 540, 520, ih)
    draw_text(ctx, "one word", F_SERIF, 120, "#E3B04B", 540, 650, ih * ease(seg(t, T_HEBREW + 0.6, T_HEBREW + 0.9)))
    hb = ease(seg(t, T_RAITAH - 0.5, T_RAITAH - 0.2))
    reveal = ease(seg(t, T_RAITAH - 0.45, T_RAITAH + 0.25))
    up = ease(seg(t, T_WICKED2 - 0.4, T_WICKED2))
    y0 = lerp(560, 420, up)
    rays(ctx, 540, y0, 0, 2 * math.pi, 18, 1000, hb * 0.8, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, lerp(260, 200, up), 540, y0, reveal, hb, rtl=True)
    draw_text(ctx, "ra'itah", F_SERIF_I, 88, "#FBF6EC", 540, y0 + 190, ease(seg(t, T_RAITAH + 0.05, T_RAITAH + 0.4)))
    draw_text(ctx, "“You have seen.”", F_SERIF_I, 76, "#E3B04B", 540, y0 + 300, ease(seg(t, T_SEEN - 0.3, T_SEEN)))
    P.tag(ctx, "Psalm 10:14", 540, 200, seg(t, T_RAITAH - 0.2, T_RAITAH + 0.2), 1.0, 250)
    # the boast, struck through
    bs = ease(seg(t, T_WICKED2 - 0.2, T_NEVER2 + 0.2))
    if bs > 0:
        draw_text(ctx, "“He will never see it.”  10:11", F_SERIF_I, 56, "#B8A898", 540, 1020, bs)
        st = ease(seg(t, T_ALREADY - 0.3, T_ALREADY + 0.1))
        if st > 0:
            ctx.set_source_rgba(*col("rust"))
            ctx.set_line_width(7)
            ctx.move_to(200, 1020)
            ctx.line_to(200 + 680 * st, 1020)
            ctx.stroke()
    eye(ctx, 540, 1200, 0.9, ease(seg(t, T_ALREADY - 0.2, T_ALREADY + 0.3)), ease(seg(t, T_ALREADY - 0.3, T_ALREADY)))
    draw_text(ctx, "already", F_SERIF, 100, "#FFE3A3", 540, 1340, ease(seg(t, T_ALREADY - 0.1, T_ALREADY + 0.3)), stroke=4, stroke_color="#2A1D14")


def scene6(ctx, lt):
    """Close: bring God your honest 'why'. End card."""
    t = lt + B6
    sky(ctx, 1.0)
    eclipse(ctx, 540, 820, 110, 0.0, t)
    V.hills(ctx, GROUND_Y - 120, 50, hexc("#B8604A"), 0, 101)
    grass(ctx, t, GROUND_Y, hexc("#7D8A4A"), 1.0, 50, 5)
    Q.person(ctx, 540, GROUND_Y + 30, 1.2, col("dark"), 0, 0, 0, 0.6 + 0.4 * ease(seg(t, T_HONEST - 0.2, T_HONEST + 0.3)))
    qa = seg(t, T_HONEST - 0.4, T_HANDLE + 0.4)
    if 0 < qa < 1:
        qy = lerp(GROUND_Y - 300, 860, ein(qa))
        draw_text(ctx, "?", F_SERIF, lerp(120, 60, qa), "#FBF6EC", 540, qy, 1 - seg(qa, 0.85, 1.0), stroke=4, stroke_color="#3B2A1E")
    end = ease(seg(t, T_ASK - 0.35, T_ASK))
    draw_text(ctx, "PSALM 10", F_SERIF, 54, "#3B2A1E", 540, 300, end)
    ctx.set_source_rgba(*col("gold", end))
    ctx.rectangle(490, 355, 100, 4)
    ctx.fill()
    draw_text(ctx, "Ask why.", F_SERIF, 140, "#3B2A1E", 540, 490, end, 0.92 + 0.08 * back_out(seg(t, T_ASK - 0.35, T_ASK)))
    hs = ease(seg(t, T_SEES - 0.3, T_SEES + 0.05))
    draw_text(ctx, "He sees.", F_SERIF, 140, "#A8741A", 540, 650, hs, 0.92 + 0.08 * back_out(seg(t, T_SEES - 0.3, T_SEES + 0.1)))
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
