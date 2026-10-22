"""Psalm 12 Short. Plum-and-charcoal city of empty words; molten silver; a double heart. Central image: words you can trust, refined like silver."""
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

E = Episode(12)
wt, DUR = E.wt, E.dur
T_TRUST1 = wt("trust", 1); T_ANYMORE = wt("anymore"); T_DAVID = wt("david"); T_PSALM = wt("psalm", 1); T_CRIES = wt("cries")
T_SAVE = wt("save"); T_FAITHFUL = wt("faithful"); T_VANISHED = wt("vanished"); T_EVERYONE = wt("everyone"); T_LIES = wt("lies")
T_FLATTER = wt("flatter"); T_LIPS = wt("lips"); T_BOAST = wt("boast"); T_TONGUES = wt("tongues"); T_WIN = wt("win")
T_MASTER = wt("master"); T_THEN = wt("then"); T_SPEAKS = wt("speaks"); T_POOR = wt("poor"); T_PLUNDERED = wt("plundered")
T_NEEDY = wt("needy"); T_GROAN = wt("groan"); T_ARISE = wt("arise"); T_AGAINST = wt("against"); T_NOISE = wt("noise")
T_WORDS1 = wt("words", 1); T_PURE = wt("pure"); T_SILVER = wt("silver"); T_REFINED = wt("refined"); T_FURNACE = wt("furnace")
T_SEVEN = wt("seven"); T_LOOK = wt("look"); T_FLATTERERS = wt("flatterers"); T_DOUBLE = wt("double"); T_HEBREW = wt("hebrew")
T_BELEV = wt("behlev"); T_VALEV = wt("vahlev"); T_HEART2 = wt("heart", 2); T_HEART3 = wt("heart", 3); T_HEART4 = wt("heart", 4)
T_SHOW = wt("show"); T_UNDERNEATH = wt("underneath"); T_TODAY = wt("today"); T_GUARD = wt("guard"); T_MEAN = wt("mean")
T_FILL = wt("fill"); T_TRUST2 = wt("trust", 2); T_HEART5 = wt("heart", 5); T_WORD = wt("word")

B1 = 0.0
B2 = T_DAVID - 0.3
B3 = T_EVERYONE - 0.4
B4 = T_THEN - 0.4
B5 = T_AGAINST - 0.15
B6 = T_LOOK - 0.4
B7 = T_TODAY - 0.4

E.zooms = [(0.1, 0.12), (T_TRUST1, 0.08), (T_SAVE, 0.08), (T_VANISHED, 0.06), (T_MASTER, 0.08), (T_ARISE, 0.14),
           (T_PURE, 0.08), (T_FURNACE, 0.08), (T_BELEV, 0.12), (T_UNDERNEATH, 0.06), (T_HEART5, 0.08), (T_WORD, 0.08)]
E.shakes = [(0.1, 12, 0.6), (T_MASTER, 10, 0.5), (T_ARISE, 16, 0.8), (T_BELEV, 8, 0.4)]
E.flashes = [(0.1, (1, 1, 1), 0.3, 0.3), (T_ARISE, (1, 0.94, 0.75), 0.55, 0.6), (T_PURE, (0.95, 0.97, 1.0), 0.35, 0.4),
             (T_BELEV, (1, 0.88, 0.55), 0.3, 0.4), (T_WORD, (1, 0.95, 0.85), 0.35, 0.45)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6, B7)]

PLUM1 = hexc("#2B2030")
PLUM2 = hexc("#5A4256")
GROUND_Y = 1250
_r = random.Random(12)
BUBBLES = [(_r.uniform(150, 930), _r.uniform(250, 1150), _r.uniform(0.5, 1.1), _r.uniform(0, 1), _r.choice((-1, 1))) for _ in range(16)]
WORDS = ["sure!", "trust me", "promise", "100%", "honestly", "no really", "of course", "believe me"]
PEOPLE = [(_r.uniform(90, 990), _r.uniform(0.75, 1.1), _r.uniform(0, 1)) for _ in range(9)]


def city(ctx, t, k=1.0, warm=0.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND_Y)
    g.add_color_stop_rgba(0, *lerpc(PLUM1, hexc("#F1E2C4"), warm))
    g.add_color_stop_rgba(1, *lerpc(PLUM2, hexc("#E9C9A0"), warm))
    ctx.set_source(g)
    ctx.paint()
    r = random.Random(3)
    x = -20
    while x < W:
        w = r.uniform(80, 160)
        h = r.uniform(180, 460)
        ctx.set_source_rgba(*lerpc(hexc("#1E1622"), hexc("#B58E74"), warm)[:3], 1)
        ctx.rectangle(x, GROUND_Y - h, w - 8, h)
        ctx.fill()
        for wy in range(int(GROUND_Y - h + 30), GROUND_Y - 40, 60):
            for wx in (x + 18, x + w / 2):
                if r.random() < 0.5:
                    ctx.set_source_rgba(1, 0.85, 0.55, (0.5 + 0.3 * math.sin(t * 2 + wx)) * k * (1 - warm))
                    ctx.rectangle(wx, wy, 18, 26)
                    ctx.fill()
        x += w
    ctx.set_source_rgba(*lerpc(hexc("#17111A"), hexc("#7A6A4E"), warm))
    ctx.rectangle(0, GROUND_Y, W, H)
    ctx.fill()


def word_bubble(ctx, cx, cy, s, txt, alpha, tail=1, c="#E8DCC8", tc="#2B2030"):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    P4.bubble(ctx, 0, 0, 300, 110, hexc(c), alpha, tail)
    ctx.restore()
    draw_text(ctx, txt, F_SERIF_I, 46 * s, tc, cx, cy, alpha)


def heart(ctx, cx, cy, s, c, alpha=1.0, glow=0.0):
    if glow > 0:
        g = cairo.RadialGradient(cx, cy, 10, cx, cy, 2.6 * s)
        g.add_color_stop_rgba(0, 1, 0.88, 0.55, 0.6 * glow * alpha)
        g.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
        ctx.set_source(g)
        ctx.arc(cx, cy, 2.6 * s, 0, 2 * math.pi)
        ctx.fill()
    P4.heart_path(ctx, cx, cy, s)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.fill()


def mask(ctx, cx, cy, s, alpha):
    """A smiling mask held up in front of a face: one heart for show."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_source_rgba(0.96, 0.92, 0.84, alpha)
    ctx.save(); ctx.scale(1, 1.25); ctx.arc(0, 0, 40, 0, 2 * math.pi); ctx.restore()
    ctx.fill()
    ctx.set_source_rgba(0.17, 0.12, 0.19, alpha)
    ctx.set_line_width(5)
    for dx in (-15, 15):
        ctx.move_to(dx - 9, -8); ctx.curve_to(dx - 4, -16, dx + 4, -16, dx + 9, -8)
    ctx.stroke()
    ctx.arc(0, 10, 20, 0.2, math.pi - 0.2)
    ctx.stroke()
    ctx.restore()


def crucible(ctx, cx, cy, s, heat, purity, t):
    """Furnace mouth with a crucible of silver; heat 0..1 glows; purity 0..1 turns dull grey to bright silver."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    # furnace
    ctx.set_source_rgba(*hexc("#3A2C2A"))
    rounded(ctx, -330, -150, 660, 520, 60)
    ctx.fill()
    g = cairo.RadialGradient(0, 200, 20, 0, 200, 340)
    g.add_color_stop_rgba(0, 1, 0.75, 0.3, heat)
    g.add_color_stop_rgba(0.6, 0.95, 0.35, 0.1, 0.8 * heat)
    g.add_color_stop_rgba(1, 0.4, 0.1, 0.05, 0)
    ctx.set_source(g)
    rounded(ctx, -250, 40, 500, 290, 40)
    ctx.fill()
    for k in range(7):
        x = -200 + k * 66
        fh = 80 + 50 * math.sin(t * 9 + k * 1.7)
        ctx.set_source_rgba(1, 0.6 + 0.2 * math.sin(t * 7 + k), 0.2, 0.7 * heat)
        ctx.move_to(x - 30, 320); ctx.curve_to(x - 20, 320 - fh * 0.6, x + 8 * math.sin(t * 5 + k), 320 - fh, x, 320 - fh)
        ctx.curve_to(x + 10, 320 - fh * 0.6, x + 20, 320 - fh * 0.3, x + 30, 320); ctx.close_path(); ctx.fill()
    # crucible bowl
    ctx.set_source_rgba(*hexc("#5E4A3E"))
    ctx.move_to(-190, -60); ctx.line_to(190, -60); ctx.curve_to(170, 120, 90, 170, 0, 170); ctx.curve_to(-90, 170, -170, 120, -190, -60)
    ctx.close_path(); ctx.fill()
    met = lerpc(hexc("#6F6A66"), hexc("#F4F6FA"), purity)
    ctx.save()
    ctx.scale(1, 0.32)
    gm = cairo.RadialGradient(-40, -200, 10, 0, -190, 190)
    gm.add_color_stop_rgba(0, 1, 1, 1, 0.4 + 0.6 * purity)
    gm.add_color_stop_rgba(0.4, *met[:3], 1)
    gm.add_color_stop_rgba(1, *lerpc(met, hexc("#2A2420"), 0.5)[:3], 1)
    ctx.set_source(gm)
    ctx.arc(0, -190, 175, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    # dross skimming off as purity rises
    r = random.Random(9)
    for k in range(10):
        a = r.uniform(0, 2 * math.pi)
        rr = r.uniform(30, 150) * (1 - purity)
        ctx.set_source_rgba(0.25, 0.22, 0.2, 0.9 * (1 - purity))
        ctx.arc(rr * math.cos(a) + 120 * purity * math.copysign(1, math.cos(a)), -61 + rr * 0.3 * math.sin(a), 14, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()
    if purity > 0.5:
        rays(ctx, cx, cy - 61 * s, math.pi, 2 * math.pi, 12, 700, (purity - 0.5) * 1.2, t * 0.3, (0.92, 0.95, 1.0))


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: a city full of speech bubbles that pop as empty."""
    t = lt
    city(ctx, t)
    for k, (x, y, s, ph, tl) in enumerate(BUBBLES):
        a = ease(seg(t, ph * 1.5, ph * 1.5 + 0.25))
        pop = seg(t, 2.2 + ph * 1.6, 2.4 + ph * 1.6)
        word_bubble(ctx, x, y + 6 * math.sin(t * 2 + k), s * (1 + 0.3 * pop), WORDS[k % len(WORDS)], a * (1 - pop), tl)
    for x, s, ph in PEOPLE[:5]:
        Q.person(ctx, x, GROUND_Y + 20, s, hexc("#100B12"), 0, 0, 0, 0.1)
    kword(ctx, "TRUST?", t, T_TRUST1 - 0.04, 540, 700, 190, "#E3B04B", B2 - T_TRUST1 + 0.2)
    grade(ctx, desat=0.15)


def scene2(ctx, lt):
    """Title; 'Save, Lord, for the faithful have vanished': figures fade until one remains."""
    t = lt + B2
    city(ctx, t, 0.6)
    ti = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_SAVE - 0.4, T_SAVE - 0.1)))
    draw_text(ctx, "PSALM 12", F_SERIF, 150, "#FBF6EC", 540, 560, ti, 0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#1E1622")
    van = ease(seg(t, T_FAITHFUL - 0.2, T_VANISHED + 0.6))
    for k, (x, s, ph) in enumerate(PEOPLE):
        if k == 4:
            continue
        a = 1 - clamp(van * 1.6 - ph * 0.6)
        Q.person(ctx, x, GROUND_Y + 20, s, hexc("#100B12"), 0, 0, 0, 0.1, alpha=a)
    cry = ease(seg(t, T_SAVE - 0.3, T_SAVE))
    Q.person(ctx, 540, GROUND_Y + 20, 1.2, hexc("#100B12"), 0, 0, 0, 0.2 + 0.8 * cry)
    P.tag(ctx, "Psalm 12:1", 540, 380, seg(t, T_SAVE - 0.2, T_SAVE + 0.2), 1.0, 250)
    draw_text(ctx, "“Save, LORD,", F_SERIF_I, 96, "#FBF6EC", 540, 540, cry, stroke=3, stroke_color="#1E1622")
    draw_text(ctx, "the faithful have vanished.”", F_SERIF_I, 66, "#E3B04B", 540, 650, ease(seg(t, T_FAITHFUL - 0.3, T_FAITHFUL)), stroke=3, stroke_color="#1E1622")
    grade(ctx, desat=0.15)


def scene3(ctx, lt):
    """Everyone lies: smiling masks, flattering bubbles, the boast."""
    t = lt + B3
    city(ctx, t, 0.6)
    P.tag(ctx, "Psalm 12:2-4", 540, 200, seg(t, T_EVERYONE - 0.2, T_EVERYONE + 0.2), 1.0, 280)
    ma = ease(seg(t, T_LIES - 0.3, T_LIES))
    xs = (200, 420, 660, 880)
    for k, x in enumerate(xs):
        Q.person(ctx, x, GROUND_Y + 20, 1.0, hexc("#100B12"), 0, 0, 0, 0.15)
        mask(ctx, x + 4, GROUND_Y - 158, 0.85, ma * clamp(ma * 4 - k * 0.6))
    fl = ease(seg(t, T_FLATTER - 0.2, T_LIPS + 0.3)) * (1 - ease(seg(t, T_BOAST - 0.2, T_BOAST + 0.2)))
    for k, (txt, x, y) in enumerate((("you're amazing!", 300, 760), ("so wise!", 760, 680), ("the best!", 520, 880))):
        word_bubble(ctx, x, y, 0.9, txt, fl * clamp(fl * 3 - k * 0.5), (-1, 1, -1)[k], "#F3C9CF")
    draw_text(ctx, "everyone lies", F_SERIF, 92, "#FBF6EC", 540, 420, ease(seg(t, T_EVERYONE - 0.2, T_LIES)) * (1 - ease(seg(t, T_FLATTER - 0.3, T_FLATTER))), stroke=4, stroke_color="#1E1622")
    bb = ease(seg(t, T_TONGUES - 0.4, T_TONGUES - 0.1))
    if bb > 0:
        P4.bubble(ctx, 540, 600, 880, 330, hexc("#1E1622"), 0.95 * bb, 1)
        draw_text(ctx, "“With our tongues", F_SERIF_I, 66, "#FBF6EC", 540, 520, ease(seg(t, T_TONGUES - 0.3, T_TONGUES)))
        draw_text(ctx, "we will win.", F_SERIF_I, 66, "#FBF6EC", 540, 600, ease(seg(t, T_WIN - 0.3, T_WIN)))
        draw_text(ctx, "Who is master over us?”", F_SERIF_I, 66, "#E07A5F", 540, 690, ease(seg(t, T_MASTER - 0.3, T_MASTER)))
    grade(ctx, desat=0.15)


def scene4(ctx, lt):
    """God speaks: 'I will now arise.' Light breaks over the city."""
    t = lt + B4
    rise = ease(seg(t, T_ARISE - 0.5, T_ARISE + 0.4))
    city(ctx, t, 0.6, 0.6 * rise)
    sy = lerp(GROUND_Y + 200, 560, rise)
    if rise > 0:
        rays(ctx, 540, sy, 0, 2 * math.pi, 20, 1200, rise, t * 0.3)
        g = cairo.RadialGradient(540, sy, 20, 540, sy, 400)
        g.add_color_stop_rgba(0, 1, 0.97, 0.85, rise)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g)
        ctx.arc(540, sy, 400, 0, 2 * math.pi)
        ctx.fill()
    for k, x in enumerate((360, 720)):
        Q.person(ctx, x, GROUND_Y + 20, (0.8, 0.95)[k], lerpc(hexc("#100B12"), col("brown"), rise), 0.6 * (1 - rise), 0, 0, 0.1 + 0.7 * rise)
    P.tag(ctx, "Psalm 12:5", 540, 200, seg(t, T_THEN - 0.2, T_THEN + 0.2), 1.0, 250)
    draw_text(ctx, "Then God speaks.", F_SERIF, 90, "#FBF6EC", 540, 420, ease(seg(t, T_THEN - 0.2, T_SPEAKS)) * (1 - ease(seg(t, T_POOR - 0.4, T_POOR - 0.1))), stroke=4, stroke_color="#1E1622")
    draw_text(ctx, "“the poor are plundered,", F_SERIF_I, 66, "#FBF6EC", 540, 400, ease(seg(t, T_POOR - 0.3, T_POOR)) * (1 - rise), stroke=3, stroke_color="#1E1622")
    draw_text(ctx, "the needy groan”", F_SERIF_I, 66, "#FBF6EC", 540, 500, ease(seg(t, T_NEEDY - 0.3, T_NEEDY)) * (1 - rise), stroke=3, stroke_color="#1E1622")
    draw_text(ctx, "“I will now arise.”", F_SERIF, 110, "#3B2A1E", 540, 380, ease(seg(t, T_ARISE - 0.3, T_ARISE + 0.1)), 0.92 + 0.08 * back_out(seg(t, T_ARISE - 0.3, T_ARISE + 0.2)))


def scene5(ctx, lt):
    """Against the noise, God's words: pure, like silver refined in a furnace seven times."""
    t = lt + B5
    R.bg(ctx, hexc("#231A1E"))
    dust(ctx, t, 0.4, "gold2", 6, -30)
    heat = ease(seg(t, T_WORDS1 - 0.5, T_PURE))
    n = clamp((t - (T_REFINED - 0.2)) / (T_SEVEN + 0.9 - T_REFINED + 0.2))
    purity = ease(seg(t, T_PURE - 0.3, T_PURE + 0.2)) * 0.25 + 0.75 * n
    crucible(ctx, 540, 1040, 1.15, heat, purity, t)
    # the noise falls away
    na = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_WORDS1 - 0.3, T_WORDS1)))
    for k, (x, y, s, ph, tl) in enumerate(BUBBLES[:8]):
        word_bubble(ctx, x, y * 0.6 + 100 + 120 * (1 - na), s * 0.8, WORDS[k % len(WORDS)], na * 0.7, tl)
    P.tag(ctx, "Psalm 12:6", 540, 200, seg(t, T_WORDS1 - 0.2, T_WORDS1 + 0.2), 1.0, 250)
    draw_text(ctx, "God’s words:", F_SERIF_I, 80, "#E8DCC8", 540, 360, ease(seg(t, T_WORDS1 - 0.3, T_WORDS1)))
    draw_text(ctx, "pure", F_SERIF, 150, "#F4F6FA", 540, 500, ease(seg(t, T_PURE - 0.2, T_PURE + 0.1)), 0.92 + 0.08 * back_out(seg(t, T_PURE - 0.2, T_PURE + 0.2)), stroke=5, stroke_color="#231A1E")
    draw_text(ctx, "like silver refined seven times", F_SERIF_I, 58, "#C9D3E0", 540, 620, ease(seg(t, T_SILVER - 0.3, T_SILVER)))
    # one pulse per refining
    for k in range(7):
        tk = T_REFINED + k * (T_SEVEN + 0.9 - T_REFINED) / 7
        u = t - tk
        if 0 < u < 0.6:
            ctx.set_source_rgba(0.95, 0.97, 1.0, 0.5 * (1 - u / 0.6))
            ctx.set_line_width(6)
            ctx.arc(540, 1040 - 70, 120 + 400 * u, math.pi, 2 * math.pi)
            ctx.stroke()


HEB = "בְּלֵב וָלֵב"


def scene6(ctx, lt):
    """Nugget: be-lev va-lev, 'with a heart and a heart': one heart for show, another underneath."""
    t = lt + B6
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.5, "gold2", 6, -12)
    P.tag(ctx, "Psalm 12:2", 540, 200, seg(t, T_LOOK - 0.2, T_LOOK + 0.2), 1.0, 250)
    draw_text(ctx, "Look at verse two.", F_SERIF_I, 70, "#E8DCC8", 540, 340, ease(seg(t, T_LOOK - 0.2, T_LOOK + 0.2)) * (1 - ease(seg(t, T_FLATTERERS - 0.3, T_FLATTERERS))))
    draw_text(ctx, "the flatterers speak", F_SERIF_I, 70, "#E8DCC8", 540, 340, ease(seg(t, T_FLATTERERS - 0.2, T_FLATTERERS + 0.2)) * (1 - ease(seg(t, T_DOUBLE - 0.3, T_DOUBLE))))
    draw_text(ctx, "with a double heart", F_SERIF, 84, "#E3B04B", 540, 340, ease(seg(t, T_DOUBLE - 0.2, T_DOUBLE + 0.2)) * (1 - ease(seg(t, T_BELEV - 0.5, T_BELEV - 0.2))))
    mk = ease(seg(t, T_FLATTERERS - 0.2, T_FLATTERERS + 0.3)) * (1 - ease(seg(t, T_HEART2 - 0.6, T_HEART2 - 0.3)))
    if mk > 0:
        Q.person(ctx, 540, 1300, 1.6, hexc("#120D10"), 0, 0, 0, 0.1, alpha=mk)
        mask(ctx, 546, 1300 - 178 * 1.6, 1.4, mk)
    hb = ease(seg(t, T_BELEV - 0.45, T_BELEV - 0.1))
    reveal = ease(seg(t, T_BELEV - 0.4, T_VALEV + 0.4))
    rays(ctx, 540, 380, 0, 2 * math.pi, 18, 1000, hb * 0.6, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 170, 540, 380, reveal, hb, rtl=True)
    draw_text(ctx, "be-lev va-lev", F_SERIF_I, 80, "#FBF6EC", 540, 540, ease(seg(t, T_VALEV, T_VALEV + 0.3)))
    draw_text(ctx, "“with a heart and a heart”", F_SERIF_I, 62, "#E3B04B", 540, 640, ease(seg(t, T_HEART2 - 0.3, T_HEART2)))
    # two hearts: they separate into the one for show and the one underneath
    ha = ease(seg(t, T_HEART2 - 0.3, T_HEART2)) * (0 if t < T_HEART2 - 0.3 else 1)
    sp = ease(seg(t, T_HEART4 - 0.2, T_UNDERNEATH + 0.3))
    heart(ctx, lerp(540, 380, sp) if ha else 540, lerp(1020, 960, sp), 110, hexc("#E3B04B"), ha, ha * 0.8)
    a2 = ease(seg(t, T_HEART3 - 0.3, T_HEART3))
    heart(ctx, lerp(560, 700, sp), lerp(1040, 1140, sp), 110, lerpc(hexc("#E3B04B"), hexc("#4A3A44"), sp), a2 * (0.7 + 0.3 * sp))
    draw_text(ctx, "for show", F_SERIF_I, 56, "#FFE3A3", 380, 1180, ease(seg(t, T_SHOW - 0.3, T_SHOW)))
    draw_text(ctx, "underneath", F_SERIF_I, 56, "#B8A0B0", 700, 1340, ease(seg(t, T_UNDERNEATH - 0.3, T_UNDERNEATH)))


def scene7(ctx, lt):
    """Close: guard your words; one heart, one word. End card."""
    t = lt + B7
    city(ctx, t, 0.0, 1.0)
    rays(ctx, 540, 820, 0, 2 * math.pi, 16, 1100, 0.6, t * 0.25)
    Q.person(ctx, 540, GROUND_Y + 20, 1.2, col("dark"), 0, 0, 0, 0.2 + 0.4 * ease(seg(t, T_FILL - 0.3, T_TRUST2)))
    hg = ease(seg(t, T_GUARD - 0.3, T_GUARD))
    heart(ctx, 540, GROUND_Y - 80, 26, hexc("#E3B04B"), hg, hg)
    draw_text(ctx, "guard your words", F_SERIF_I, 70, "#3B2A1E", 540, 800, hg * (1 - ease(seg(t, T_MEAN - 0.3, T_MEAN))))
    draw_text(ctx, "mean what you say", F_SERIF_I, 70, "#3B2A1E", 540, 800, ease(seg(t, T_MEAN - 0.2, T_MEAN + 0.2)) * (1 - ease(seg(t, T_FILL - 0.2, T_FILL + 0.1))))
    draw_text(ctx, "words you can trust", F_SERIF_I, 70, "#A8741A", 540, 800, ease(seg(t, T_FILL, T_TRUST2)) * (1 - ease(seg(t, T_HEART5 - 0.4, T_HEART5 - 0.1))))
    end = ease(seg(t, T_HEART5 - 0.35, T_HEART5))
    draw_text(ctx, "PSALM 12", F_SERIF, 54, "#3B2A1E", 540, 300, end)
    ctx.set_source_rgba(*col("gold", end))
    ctx.rectangle(490, 355, 100, 4)
    ctx.fill()
    draw_text(ctx, "One heart.", F_SERIF, 140, "#3B2A1E", 540, 490, end, 0.92 + 0.08 * back_out(seg(t, T_HEART5 - 0.35, T_HEART5)))
    ws = ease(seg(t, T_WORD - 0.3, T_WORD + 0.05))
    draw_text(ctx, "One word.", F_SERIF, 140, "#A8741A", 540, 650, ws, 0.92 + 0.08 * back_out(seg(t, T_WORD - 0.3, T_WORD + 0.1)))
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
