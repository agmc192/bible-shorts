"""Psalm 14 Short. Newsprint grey and alarm red, a searching beam from above, then a warm mirror.
Central image: the headlines we judge, and the mirror we skip."""
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

E = Episode(14)
wt, DUR = E.wt, E.dur
T_NEWS1 = wt("news", 1); T_WRONG = wt("wrong"); T_PEOPLE1 = wt("people", 1); T_PSALM = wt("psalm"); T_BLUNTLY = wt("bluntly")
T_FOOL1 = wt("fool", 1); T_HEART1 = wt("heart", 1); T_THERE = wt("there"); T_NO = wt("no", 1); T_GOD1 = wt("god", 1)
T_HEBREW = wt("hebrew"); T_FOOL2 = wt("fool", 2); T_NAVAL = wt("nahvahl"); T_NOT1 = wt("not", 1); T_SMART = wt("smart")
T_MORALLY = wt("morally"); T_SENSELESS = wt("senseless"); T_LIVES = wt("lives"); T_MATTER = wt("matter")
T_LORD = wt("lord"); T_LOOKS = wt("looks"); T_HEAVEN = wt("heaven"); T_SEEKS = wt("seeks"); T_ALL = wt("all")
T_TURNED = wt("turned"); T_ASIDE = wt("aside"); T_NOONE = wt("no", 2); T_GOOD = wt("good"); T_EVEN = wt("even")
T_PAUL = wt("paul"); T_ROMANS = wt("romans"); T_POINT = wt("point"); T_OTHER = wt("other"); T_EVERYONE = wt("everyone")
T_GRACE1 = wt("grace", 1); T_GRACE2 = wt("grace", 2); T_GIFT = wt("gift"); T_JESUS = wt("jesus")
T_TODAY = wt("today"); T_JUDGE = wt("judge"); T_HEADLINES = wt("headlines"); T_SEARCH = wt("search"); T_HEART2 = wt("heart", 2)
T_START = wt("start"); T_MIRROR = wt("mirror"); T_NEWS2 = wt("news", 2)

B1 = 0.0
B2 = T_PSALM - 0.3
B3 = T_HEBREW - 0.35
B4 = T_LORD - 0.45
B5 = T_PAUL - 0.35
B6 = T_TODAY - 0.35

E.zooms = [(0.1, 0.12), (T_WRONG, 0.08), (T_GOD1, 0.09), (T_NAVAL, 0.12), (T_LOOKS, 0.06), (T_EVEN, 0.08),
           (T_GRACE1, 0.07), (T_GIFT, 0.1), (T_MIRROR, 0.08), (T_NEWS2, 0.08)]
E.shakes = [(0.1, 10, 0.5), (T_WRONG, 10, 0.5), (T_GOD1, 8, 0.4), (T_EVEN, 10, 0.5)]
E.flashes = [(0.1, (1, 1, 1), 0.25, 0.3), (T_NAVAL, (1, 0.88, 0.55), 0.3, 0.4), (T_GIFT, (1, 0.94, 0.75), 0.5, 0.6),
             (T_NEWS2, (1, 0.95, 0.85), 0.3, 0.45)]
E.blur = [(b - 0.3, b + 0.1) for b in (B2, B3, B4, B5, B6)]

NEWS_BG = hexc("#2B2B2E")
RED = hexc("#C0392B")
_r = random.Random(14)
HEADS = ["CHAOS", "SCANDAL", "OUTRAGE", "CRISIS", "LIES", "FEUD", "CRASH", "FRAUD"]


def screen(ctx, cx, cy, w, h, t, alpha=1.0, k=1.0):
    """A news screen: red BREAKING bar, flashing headline blocks, scrolling ticker."""
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.set_source_rgba(0.08, 0.08, 0.09, alpha)
    rounded(ctx, -w / 2 - 24, -h / 2 - 24, w + 48, h + 48, 30); ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h); ctx.clip()
    ctx.set_source_rgba(*hexc("#3A3F4A")[:3], alpha); ctx.paint()
    i = int(t * 2.2) % len(HEADS)
    for row in range(4):
        y = -h / 2 + 150 + row * (h - 260) / 4
        ww = (0.85 - 0.18 * ((row + i) % 3)) * w
        ctx.set_source_rgba(0.85, 0.85, 0.88, (0.55 - 0.1 * row) * alpha)
        ctx.rectangle(-w / 2 + 40, y, ww - 80, 26); ctx.fill()
    ctx.set_source_rgba(*RED[:3], alpha)
    ctx.rectangle(-w / 2, -h / 2 + 30, w, 90); ctx.fill()
    draw_text(ctx, "BREAKING", F_CAP, 54, "#FFFFFF", -w / 2 + 170, -h / 2 + 75, alpha)
    draw_text(ctx, HEADS[i], F_CAP, int(min(110, w / 6)), "#FFFFFF", 0, -h / 2 + 260, alpha * (0.7 + 0.3 * math.sin(t * 9) ** 2), stroke=3, stroke_color="#1A1A1A")
    ctx.set_source_rgba(0.1, 0.1, 0.12, alpha)
    ctx.rectangle(-w / 2, h / 2 - 80, w, 80); ctx.fill()
    off = (t * 220) % 600
    for k2 in range(5):
        draw_text(ctx, HEADS[(k2 + 3) % len(HEADS)].lower() + " •", F_CAP, 36, "#E8E2D4", -w / 2 + 120 + k2 * 300 - off, h / 2 - 40, alpha)
    ctx.restore()


def crowd_row(ctx, t, y, n, s, c, turn=0.0, alpha=1.0, seed=3):
    r = random.Random(seed)
    for k in range(n):
        x = 90 + k * (900 / (n - 1)) + r.uniform(-20, 20)
        tt = clamp(turn * 1.4 - r.uniform(0, 0.4))
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1 - 0.15 * tt, 1)   # turning away: narrower silhouette, head bowed off-axis
        Q.person(ctx, 0, 0, s * r.uniform(0.9, 1.1), c, 0.6 * tt, 0, 0, 0, 0, alpha)
        ctx.restore()


def mirror(ctx, cx, cy, w, h, alpha, glow=0.0, inner=None):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.set_source_rgba(*hexc("#8A6A44")[:3], alpha)
    ctx.save(); ctx.scale(1, h / w); ctx.arc(0, 0, w / 2 + 26, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    ctx.save(); ctx.scale(1, h / w); ctx.arc(0, 0, w / 2, 0, 2 * math.pi); ctx.restore()
    ctx.clip()
    g = cairo.LinearGradient(-w / 2, -h / 2, w / 2, h / 2)
    g.add_color_stop_rgba(0, *lerpc(hexc("#BFD3DE"), hexc("#FFE9B8"), glow)[:3], alpha)
    g.add_color_stop_rgba(1, *lerpc(hexc("#7E97A8"), hexc("#F2C66A"), glow)[:3], alpha)
    ctx.set_source(g); ctx.paint()
    if inner:
        inner(ctx)
    ctx.set_source_rgba(1, 1, 1, 0.35 * alpha)
    ctx.move_to(-w * 0.3, -h * 0.3); ctx.line_to(-w * 0.1, -h * 0.42); ctx.line_to(w * 0.2, h * 0.1); ctx.line_to(0, h * 0.2)
    ctx.close_path(); ctx.fill()
    ctx.restore()


def gift(ctx, cx, cy, s, open_, alpha=1.0):
    if alpha <= 0.01:
        return
    if open_ > 0:
        rays(ctx, cx, cy - 60 * s, math.pi, 2 * math.pi, 16, 900, open_ * alpha, 0)
        g = cairo.RadialGradient(cx, cy - 60 * s, 10, cx, cy - 60 * s, 300)
        g.add_color_stop_rgba(0, 1, 0.95, 0.8, open_ * alpha)
        g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
        ctx.set_source(g); ctx.arc(cx, cy - 60 * s, 300, 0, 2 * math.pi); ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.set_source_rgba(*hexc("#A8741A")[:3], alpha)
    ctx.rectangle(-120, -60, 240, 180); ctx.fill()
    ctx.set_source_rgba(*hexc("#F3E3C3")[:3], alpha)
    ctx.rectangle(-18, -60, 36, 180); ctx.fill()
    ctx.save()
    ctx.translate(-140, -60)
    ctx.rotate(-1.1 * open_)
    ctx.set_source_rgba(*hexc("#C8902E")[:3], alpha)
    ctx.rectangle(0, -50, 280, 50); ctx.fill()
    ctx.set_source_rgba(*hexc("#F3E3C3")[:3], alpha)
    ctx.rectangle(122, -50, 36, 50); ctx.fill()
    ctx.restore()
    ctx.restore()


# ---------------------------------------------------------------- scenes
def scene1(ctx, lt):
    """Hook: a wall of news; 'what is wrong with people?'"""
    t = lt
    R.bg(ctx, NEWS_BG)
    screen(ctx, 540, 760, 900, 1000, t)
    Q.person(ctx, 540, 1420, 1.6, hexc("#0D0D0F"), 0, 0, 0, 0.0)
    kword(ctx, "WHAT IS WRONG", t, T_WRONG - 0.15, 540, 330, 88, "#FBF6EC", B2 - T_WRONG + 0.2)
    kword(ctx, "WITH PEOPLE?", t, T_PEOPLE1 - 0.1, 540, 450, 88, "#E07A5F", B2 - T_PEOPLE1 + 0.1)
    grade(ctx, desat=0.35)


def scene2(ctx, lt):
    """Title; the fool says in his heart, 'There is no God.'"""
    t = lt + B2
    R.bg(ctx, NEWS_BG)
    screen(ctx, 540, 760, 900, 1000, t, 0.12)
    ti = ease(seg(lt, 0.0, 0.3)) * (1 - ease(seg(t, T_FOOL1 - 0.4, T_FOOL1 - 0.1)))
    draw_text(ctx, "PSALM 14", F_SERIF, 150, "#FBF6EC", 540, 520, ti, 0.9 + 0.1 * back_out(seg(lt, 0.0, 0.3)), stroke=3, stroke_color="#1A1A1A")
    draw_text(ctx, "opens bluntly", F_SERIF_I, 70, "#E8DCC8", 540, 660, ti * ease(seg(t, T_BLUNTLY - 0.3, T_BLUNTLY)))
    fa = ease(seg(t, T_FOOL1 - 0.3, T_FOOL1))
    Q.person(ctx, 540, 1400, 2.2, hexc("#141416"), 0, 0, 0, 0, 0, fa)
    hx, hy = 540, 1400 - 2.2 * 100
    ha = ease(seg(t, T_HEART1 - 0.3, T_HEART1))
    if ha > 0:
        P4.heart_path(ctx, hx, hy, 70)
        ctx.set_source_rgba(*RED[:3], 0.9 * ha); ctx.fill()
    P.tag(ctx, "Psalm 14:1", 540, 200, seg(t, T_FOOL1 - 0.2, T_FOOL1 + 0.2), 1.0, 250)
    draw_text(ctx, "the fool says in his heart", F_SERIF_I, 64, "#E8DCC8", 540, 360, fa)
    draw_text(ctx, "“There is no God.”", F_SERIF, 100, "#FBF6EC", 540, 500, ease(seg(t, T_THERE - 0.2, T_THERE + 0.1)), 0.92 + 0.08 * back_out(seg(t, T_GOD1 - 0.2, T_GOD1 + 0.2)), stroke=4, stroke_color="#1A1A1A")
    grade(ctx, desat=0.35)


HEB = "נָבָל"


def scene3(ctx, lt):
    """Nugget: nabal, not 'not smart' but morally senseless, living as if God doesn't matter."""
    t = lt + B3
    P.dark_bg(ctx, lt, eout(seg(lt, 0.0, 0.8)))
    dust(ctx, t, 0.5, "gold2", 6, -12)
    draw_text(ctx, "the Hebrew word for fool", F_SERIF_I, 64, "#E8DCC8", 540, 330, ease(seg(t, T_HEBREW - 0.2, T_HEBREW + 0.2)))
    hb = ease(seg(t, T_NAVAL - 0.45, T_NAVAL - 0.1))
    reveal = ease(seg(t, T_NAVAL - 0.4, T_NAVAL + 0.5))
    rays(ctx, 540, 530, 0, 2 * math.pi, 18, 1000, hb * 0.5, t * 0.4)
    P.burn_word(ctx, HEB, F_HEB, 230, 540, 520, reveal, hb, rtl=True)
    draw_text(ctx, "nah-VAHL", F_SERIF_I, 84, "#FBF6EC", 540, 700, ease(seg(t, T_NAVAL, T_NAVAL + 0.3)))
    na = ease(seg(t, T_NOT1 - 0.2, T_NOT1 + 0.1)) * (1 - ease(seg(t, T_MORALLY - 0.4, T_MORALLY - 0.1)))
    draw_text(ctx, "not smart", F_SERIF, 90, "#9AA0AA", 540, 900, na)
    st = ease(seg(t, T_SMART, T_SMART + 0.3)) * na
    if st > 0:
        ctx.set_source_rgba(*RED[:3], na)
        ctx.set_line_width(12)
        ctx.move_to(300, 905); ctx.line_to(300 + 480 * st, 895); ctx.stroke()
        draw_text(ctx, "✗", F_SERIF, 90, "#C0392B", 830, 900, st)
    draw_text(ctx, "morally senseless", F_SERIF, 92, "#E3B04B", 540, 900, ease(seg(t, T_MORALLY - 0.2, T_SENSELESS)), 0.92 + 0.08 * back_out(seg(t, T_MORALLY - 0.2, T_MORALLY + 0.3)))
    draw_text(ctx, "living as if God doesn’t matter", F_SERIF_I, 60, "#FBF6EC", 540, 1030, ease(seg(t, T_LIVES - 0.2, T_MATTER)))


def scene4(ctx, lt):
    """The Lord looks down from heaven: a beam sweeps the crowd; all have turned aside; not even one."""
    t = lt + B4
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hexc("#3B3A45")); g.add_color_stop_rgba(1, *hexc("#1D1C22"))
    ctx.set_source(g); ctx.paint()
    look = ease(seg(t, T_LOOKS - 0.3, T_LOOKS + 0.3))
    bx = 540 + 330 * math.sin((t - T_LOOKS) * 1.1) * look
    if look > 0:
        ctx.save()
        lg = cairo.LinearGradient(0, 0, 0, 1500)
        lg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.75 * look)
        lg.add_color_stop_rgba(1, 1, 0.9, 0.6, 0.12 * look)
        ctx.set_source(lg)
        ctx.move_to(540 - 60, -20); ctx.line_to(540 + 60, -20); ctx.line_to(bx + 240, 1500); ctx.line_to(bx - 240, 1500); ctx.close_path(); ctx.fill()
        ctx.restore()
        g2 = cairo.RadialGradient(540, -40, 10, 540, -40, 400)
        g2.add_color_stop_rgba(0, 1, 0.97, 0.85, look)
        g2.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.set_source(g2); ctx.arc(540, -40, 400, 0, 2 * math.pi); ctx.fill()
    turn = ease(seg(t, T_TURNED - 0.3, T_ASIDE + 0.4))
    crowd_row(ctx, t, 1280, 7, 1.0, hexc("#0E0D12"), turn, 1.0, 5)
    crowd_row(ctx, t, 1460, 6, 1.3, hexc("#08080B"), turn, 1.0, 9)
    P.tag(ctx, "Psalm 14:2-3", 540, 200, seg(t, T_LORD - 0.2, T_LORD + 0.2), 1.0, 280)
    draw_text(ctx, "seeking anyone who seeks him", F_SERIF_I, 60, "#E8DCC8", 540, 380, ease(seg(t, T_HEAVEN - 0.2, T_SEEKS)) * (1 - ease(seg(t, T_ALL - 0.3, T_ALL))))
    draw_text(ctx, "all have turned aside", F_SERIF, 84, "#FBF6EC", 540, 380, ease(seg(t, T_ALL - 0.2, T_ALL + 0.1)) * (1 - ease(seg(t, T_NOONE - 0.3, T_NOONE))), stroke=3, stroke_color="#1A1A1A")
    draw_text(ctx, "no one does good", F_SERIF, 84, "#FBF6EC", 540, 380, ease(seg(t, T_NOONE - 0.2, T_NOONE + 0.1)), stroke=3, stroke_color="#1A1A1A")
    kword(ctx, "NOT EVEN ONE", t, T_EVEN - 0.1, 540, 520, 120, "#E07A5F", B5 - T_EVEN + 0.1)
    grade(ctx, desat=0.3)


def scene5(ctx, lt):
    """Paul quotes it in Romans 3: everyone needs grace; grace as a gift, through Jesus."""
    t = lt + B5
    warm = ease(seg(t, T_GRACE2 - 0.5, T_GIFT + 0.5))
    R.bg(ctx, lerpc(hexc("#2E2B30"), hexc("#F1E2C4"), warm))
    so = ease(seg(lt, 0.0, 0.5))
    P7scroll(ctx, 540, 360, 640, so, so * (1 - ease(seg(t, T_GRACE2 - 0.4, T_GRACE2))), "Romans 3:10-12")
    P.tag(ctx, "Romans 3:23-24", 540, 200, seg(t, T_GRACE2 - 0.2, T_GRACE2 + 0.2), 1.0, 300)
    pa = ease(seg(t, T_POINT - 0.2, T_POINT + 0.2)) * (1 - ease(seg(t, T_EVERYONE - 0.4, T_EVERYONE - 0.1)))
    draw_text(ctx, "not to point fingers", F_SERIF_I, 70, "#E8DCC8", 540, 560, pa)
    ea = ease(seg(t, T_EVERYONE - 0.2, T_GRACE1)) * (1 - ease(seg(t, T_GRACE2 - 0.4, T_GRACE2)))
    draw_text(ctx, "everyone needs grace", F_SERIF, 88, "#E3B04B", 540, 560, ea, 0.94 + 0.06 * back_out(seg(t, T_GRACE1 - 0.2, T_GRACE1 + 0.3)), stroke=3, stroke_color="#1A1A1A")
    crowd_row(ctx, t, 1480, 6, 1.2, lerpc(hexc("#0E0D12"), col("dark"), warm), 0.0, 1.0, 9)
    op = ease(seg(t, T_GIFT - 0.3, T_GIFT + 0.4))
    gift(ctx, 540, 1000, 1.3, op, ease(seg(t, T_GRACE2 - 0.4, T_GRACE2)))
    draw_text(ctx, "grace, as a gift", F_SERIF, 88, "#3B2A1E", 540, 450, ease(seg(t, T_GIFT - 0.3, T_GIFT)))
    draw_text(ctx, "through Jesus", F_SERIF_I, 76, "#A8741A", 540, 570, ease(seg(t, T_JESUS - 0.3, T_JESUS)))
    grade(ctx, desat=0.3 * (1 - warm), warm=0.08 * warm)


def P7scroll(ctx, cx, cy, w, open_, alpha, label):
    if alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ww = 30 + (w - 30) * open_
    ctx.set_source_rgba(*col("cream2", alpha))
    ctx.rectangle(-ww / 2, -50, ww, 100); ctx.fill()
    ctx.set_source_rgba(*col("brown2", alpha))
    for sx in (-1, 1):
        rounded(ctx, sx * ww / 2 - 14, -64, 28, 128, 12); ctx.fill()
    ctx.restore()
    if open_ > 0.85:
        draw_text(ctx, label, F_SERIF, 50, "#3B2A1E", cx, cy, alpha * seg(open_, 0.85, 1.0))
    draw_text(ctx, "Paul quotes Psalm 14", F_SERIF_I, 56, "#E8DCC8", cx, cy - 130, alpha * open_)


def scene6(ctx, lt):
    """Close: turn from the headlines to the mirror; ask God to search your heart. End card; loop."""
    t = lt + B6
    R.bg(ctx, hexc("#E9D3AC"))
    rays(ctx, 760, 760, 0, 2 * math.pi, 16, 1100, 0.4 * ease(seg(t, T_SEARCH - 0.3, T_HEART2)), t * 0.2)
    sa = 1 - ease(seg(t, T_SEARCH - 0.4, T_SEARCH))
    end = ease(seg(t, T_START - 0.4, T_START))
    screen(ctx, 290, 820, 400, 560, t, sa * (1 - end))
    glow = ease(seg(t, T_SEARCH - 0.3, T_HEART2 + 0.2))
    def inner(c):
        Q.person(c, 0, 240, 1.3, hexc("#3B2A1E"), 0, 0, 0, 0, 0, 0.55)
        if glow > 0:
            P4.heart_path(c, 0, 60, 34)
            c.set_source_rgba(0.95, 0.75, 0.3, glow); c.fill()
    mirror(ctx, lerp(790, 540, ease(seg(t, T_SEARCH - 0.4, T_HEART2))), 820, 380, 560, (1 - end), glow, inner)
    turn = ease(seg(t, T_SEARCH - 0.5, T_SEARCH))
    Q.person(ctx, 540, 1430, 1.5, col("dark"), 0.5 * (1 - turn), 0, 0, 0, 0, 1 - end)
    draw_text(ctx, "before you judge the headlines…", F_SERIF_I, 56, "#3B2A1E", 540, 330, ease(seg(t, T_JUDGE - 0.3, T_JUDGE)) * (1 - ease(seg(t, T_SEARCH - 0.4, T_SEARCH - 0.1))))
    draw_text(ctx, "ask God to search your heart", F_SERIF_I, 60, "#A8741A", 540, 330, ease(seg(t, T_SEARCH - 0.2, T_SEARCH + 0.2)) * (1 - end))
    end_card(ctx, t, "PSALM 14", ICON, "Start with the mirror,", "not the news.", T_START, T_NEWS2)
    lp = ease(seg(t, DUR - 0.55, DUR))
    if lp > 0:
        ctx.push_group()
        scene1(ctx, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(lp)


ICON = lambda c, x, y: mirror(c, x, y + 10, 210, 300, 1.0, 0.8)

E.scenes = [(B1, B2, scene1), (B2, B3, scene2), (B3, B4, scene3), (B4, B5, scene4), (B5, B6, scene5), (B6, DUR + 1, scene6)]

if __name__ == "__main__":
    if sys.argv[1] == "thumb":
        end_thumbnail("PSALM 14", ICON, "Start with the mirror,", "not the news.", f"{E.dir}/psalm14_thumbnail.png")
    else:
        E.main(sys.argv)
