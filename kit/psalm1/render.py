"""Psalm 1 Short: renders a 1080x1920 30fps animation with burned-in captions."""
import math, random, subprocess, sys
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
DUR = 50.0
FONTS = "/home/claude/psalm1/fonts/"
F_SERIF = FONTS + "lora/files/lora-latin-700-normal.woff"
F_SERIF_I = FONTS + "lora/files/lora-latin-600-italic.woff"
F_SERIF_R = FONTS + "lora/files/lora-latin-400-normal.woff"
F_HEB = FONTS + "frank-ruhl-libre/files/frank-ruhl-libre-hebrew-700-normal.woff"
F_CAP = FONTS + "nunito/files/nunito-latin-800-normal.woff"


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


C = {
    "cream": "#F3EBDD", "cream2": "#FBF6EC", "brown": "#3B2A1E", "brown2": "#6E5039",
    "sand": "#DCC59D", "sand2": "#C9AE80", "crack": "#9C7B50", "teal": "#2F7F7A",
    "water": "#3D8FA0", "water2": "#8CC7CF", "gold": "#C9962E", "gold2": "#E3B04B",
    "rust": "#A9472F", "leaf": "#5F8F3E", "leaf2": "#7FAA4E", "leafdark": "#466E2E",
    "dry": "#A98657", "dark": "#2A1D14", "dead": "#8C7158",
}


def col(name, a=1.0):
    return hexc(C[name], a)


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(lerp(x, y, t) for x, y in zip(c1, c2))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ein(x):
    x = clamp(x)
    return x ** 3


# ---------------------------------------------------------------- text helpers
_font_cache = {}
_text_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _font_cache[k]


def pil_to_cairo(im):
    arr = np.asarray(im.convert("RGBA")).astype(np.float32)
    a = arr[..., 3:4] / 255.0
    rgb = arr[..., :3] * a
    bgra = np.dstack([rgb[..., 2], rgb[..., 1], rgb[..., 0], arr[..., 3]]).astype(np.uint8)
    bgra = np.ascontiguousarray(bgra)
    h, w = bgra.shape[:2]
    surf = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, w, h, w * 4)
    _KEEP.append(bgra)
    return surf


_KEEP = []


def text_surf(txt, path, size, color, rtl=False, stroke=0, stroke_color=None, glow=0):
    key = (txt, path, size, color, rtl, stroke, stroke_color, glow)
    if key in _text_cache:
        return _text_cache[key]
    f = font(path, size)
    direction = "rtl" if rtl else None
    l, t, r, b = f.getbbox(txt, direction=direction, stroke_width=stroke)
    pad = 20 + glow * 2
    w, h = int(r - l + pad * 2), int(b - t + pad * 2)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill = tuple(int(c * 255) for c in hexc(color))
    sc = tuple(int(c * 255) for c in hexc(stroke_color)) if stroke_color else None
    d.text((pad - l, pad - t), txt, font=f, fill=fill, direction=direction,
           stroke_width=stroke, stroke_fill=sc)
    if glow:
        from PIL import ImageFilter
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((pad - l, pad - t), txt, font=f, fill=fill[:3] + (150,), direction=direction)
        g = g.filter(ImageFilter.GaussianBlur(glow))
        im = Image.alpha_composite(g, im)
    s = pil_to_cairo(im)
    _text_cache[key] = s
    return s


def draw_surf(ctx, s, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.001:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)
    ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def draw_text(ctx, txt, path, size, color, cx, cy, alpha=1.0, scale=1.0, **kw):
    draw_surf(ctx, text_surf(txt, path, size, color, **kw), cx, cy, alpha, scale)


# ---------------------------------------------------------------- captions
LINES = [
    (0.25, 4.0, "Ever notice how some people stay steady when life falls apart?"),
    (4.3, 13.0, "Psalm 1 opens the whole book with the answer. Picture a tree in dry, cracked ground, "
                "planted right beside a stream. The heat comes, but its leaves stay green."),
    (13.3, 19.0, "The psalm says that's the person who delights in God's word. They're like that tree by the stream."),
    (19.3, 33.4, "Here's the key. The word for \"meditate\" is the Hebrew hagah. Isaiah uses that same word "
                 "for a lion growling over its prey. It's not skimming, it's chewing. That's how we're meant "
                 "to come to God's word. Devoted. Hungry. It's the water our roots drink from."),
    (33.7, 39.2, "Then the psalm shows the other path: a life like chaff, dry and weightless, blown away by the wind."),
    (39.5, 44.2, "So what keeps you standing isn't how strong you are. It's where your roots go."),
    (44.5, 47.9, "Start today. One verse, read slowly, chewed on all day. Be rooted in God's word."),
]
HIGHLIGHT = {"steady", "stream", "green", "delights", "hagah", "lion", "chewing", "water",
             "chaff", "roots", "rooted", "devoted", "hungry", "one", "verse"}


def build_chunks():
    out = []
    for a, b, txt in LINES:
        words = txt.split()
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 3 or w[-1] in ".,?!:":
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)

        def weight(g):
            p = g[-1][-1]
            return sum(len(x) + 1 for x in g) + (7 if p in ".?!" else 3 if p in ",:" else 0)

        ws = [weight(g) for g in groups]
        tot, t = sum(ws), a
        for g, wg in zip(groups, ws):
            d = (b - a) * wg / tot
            out.append((t, t + d, g))
            t += d
    return out


CHUNKS = build_chunks()


def clean(w):
    return w.strip('".,:;!')


def caption_surf(words):
    key = ("cap",) + tuple(words)
    if key in _text_cache:
        return _text_cache[key]
    size = 92
    stroke = 8
    while True:
        f = font(F_CAP, size)
        disp = [clean(w) if not w.endswith("?") else w.strip('"') for w in words]
        space = f.getlength(" ")
        widths = [f.getlength(w) for w in disp]
        total = sum(widths) + space * (len(disp) - 1)
        if total < 960 or size < 60:
            break
        size -= 4
    asc, desc = f.getmetrics()
    pad = 24
    w, h = int(total + pad * 2 + stroke * 2), int(asc + desc + pad * 2)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad + stroke
    for word, ww in zip(disp, widths):
        hl = word.lower().strip("?'").replace("'s", "") in HIGHLIGHT
        fill = (227, 176, 75, 255) if hl else (255, 249, 238, 255)
        d.text((x, pad), word, font=f, fill=fill, stroke_width=stroke, stroke_fill=(43, 29, 20, 255))
        x += ww + space
    s = pil_to_cairo(im)
    _text_cache[key] = s
    return s


def draw_captions(ctx, t):
    for a, b, g in CHUNKS:
        if a <= t < b:
            pop = 0.9 + 0.1 * eout(seg(t, a, a + 0.14))
            al = seg(t, a, a + 0.08)
            draw_surf(ctx, caption_surf(g), W / 2, 1560, al, pop)
            break


# ---------------------------------------------------------------- shared art
rng = random.Random(7)


def bg(ctx, c):
    ctx.set_source_rgba(*c)
    ctx.paint()


def figure(ctx, x, y, s, c, arms=0.0):
    """Faceless person; y = feet. arms: 0 down, 1 raised like branches."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_source_rgba(*c)
    ctx.arc(0, -178, 32, 0, 2 * math.pi)
    ctx.fill()
    ctx.move_to(-38, -138)
    ctx.curve_to(-50, -90, -48, -40, -44, 0)
    ctx.line_to(44, 0)
    ctx.curve_to(48, -40, 50, -90, 38, -138)
    ctx.curve_to(20, -146, -20, -146, -38, -138)
    ctx.close_path()
    ctx.fill()
    ctx.set_line_width(20)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sx in (-1, 1):
        ang = lerp(math.radians(100), math.radians(-40), arms)
        ex = sx * (40 + 80 * math.cos(ang) * 0.9)
        ey = -128 + 80 * math.sin(ang)
        ctx.move_to(sx * 36, -128)
        ctx.curve_to(sx * 50, -110, ex - sx * 10, ey + 10, ex, ey)
        ctx.stroke()
    ctx.restore()


CANOPY = [(0, -70, 118), (-112, -18, 96), (112, -18, 96), (-62, -150, 92), (66, -150, 92),
          (0, 26, 92), (-176, 52, 70), (176, 52, 70), (0, -200, 78)]


def tree(ctx, cx, by, grow=1.0, green=1.0, sway=0.0, alpha=1.0, glow=0.0, h=330):
    if grow <= 0.001 or alpha <= 0.001:
        return
    ctx.push_group()
    ctx.save()
    ctx.translate(cx, by)
    ctx.rotate(sway)
    g = eout(grow)
    th = h * g
    # trunk
    ctx.set_source_rgba(*col("brown2"))
    ctx.move_to(-38, 0)
    ctx.curve_to(-26, -th * 0.4, -22, -th * 0.7, -16, -th)
    ctx.line_to(16, -th)
    ctx.curve_to(22, -th * 0.7, 26, -th * 0.4, 38, 0)
    ctx.close_path()
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(14 * g)
    for sx in (-1, 1):
        ctx.move_to(0, -th * 0.62)
        ctx.curve_to(sx * 40, -th * 0.75, sx * 90, -th * 0.82, sx * 120 * g, -th * 0.9)
        ctx.stroke()
    # canopy
    cg = ease(seg(grow, 0.35, 1.0))
    if cg > 0:
        base = lerpc(col("dry"), col("leaf"), green)
        dark = lerpc(col("dead"), col("leafdark"), green)
        light = lerpc(col("sand2"), col("leaf2"), green)
        ctx.translate(0, -th)
        for i, (x, y, r) in enumerate(CANOPY):
            ctx.set_source_rgba(*dark)
            ctx.arc(x * cg + 8, y * cg + 10, r * cg, 0, 2 * math.pi)
            ctx.fill()
        for i, (x, y, r) in enumerate(CANOPY):
            ctx.set_source_rgba(*base)
            ctx.arc(x * cg, y * cg, r * cg * 0.96, 0, 2 * math.pi)
            ctx.fill()
        for i, (x, y, r) in enumerate(CANOPY):
            ctx.set_source_rgba(*light[:3], 0.55)
            ctx.arc(x * cg - r * 0.3 * cg, y * cg - r * 0.32 * cg, r * cg * 0.32, 0, 2 * math.pi)
            ctx.fill()
        if glow > 0:
            ctx.set_operator(cairo.OPERATOR_ADD)
            rg = cairo.RadialGradient(0, -40, 10, 0, -40, 320)
            rg.add_color_stop_rgba(0, 1, 0.9, 0.55, 0.22 * glow)
            rg.add_color_stop_rgba(1, 1, 0.9, 0.55, 0)
            ctx.set_source(rg)
            ctx.arc(0, -40, 320, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


GROUND_Y = 1000


def stream_pts(n=160):
    pts = []
    for i in range(n + 1):
        x = -60 + (W + 120) * i / n
        y = 1140 + 20 * math.sin(x / 140.0) + 8 * math.sin(x / 47.0)
        pts.append((x, y))
    return pts


STREAM = stream_pts()


def polyline(ctx, pts, frac=1.0):
    if frac <= 0:
        return False
    n = max(2, int(len(pts) * frac))
    ctx.move_to(*pts[0])
    for p in pts[1:n]:
        ctx.line_to(*p)
    return True


def stream(ctx, t, prog=1.0, alpha=1.0):
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if polyline(ctx, STREAM, prog):
        ctx.set_source_rgba(*col("water", alpha))
        ctx.set_line_width(58)
        ctx.stroke()
    # flowing highlights
    if prog > 0.05:
        ctx.set_line_width(6)
        ctx.set_source_rgba(*col("water2", 0.85 * alpha))
        n = int(len(STREAM) * prog)
        for k in range(10):
            off = (t * 22 + k * 16) % 160
            i0 = int(off)
            for dy in (-12, 10):
                if i0 + 6 < n:
                    ctx.move_to(STREAM[i0][0], STREAM[i0][1] + dy)
                    for j in range(i0 + 1, min(i0 + 6, n)):
                        ctx.line_to(STREAM[j][0], STREAM[j][1] + dy)
                    ctx.stroke()
    ctx.restore()


def ground(ctx, c="sand"):
    ctx.set_source_rgba(*col(c))
    ctx.move_to(0, GROUND_Y + 10)
    ctx.curve_to(300, GROUND_Y - 6, 700, GROUND_Y + 14, W, GROUND_Y)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(*col("brown2", 0.5))
    ctx.set_line_width(3)
    ctx.move_to(0, GROUND_Y + 10)
    ctx.curve_to(300, GROUND_Y - 6, 700, GROUND_Y + 14, W, GROUND_Y)
    ctx.stroke()


def make_cracks():
    r = random.Random(11)
    cracks = []
    for _ in range(22):
        x = r.uniform(20, W - 20)
        y = r.uniform(GROUND_Y + 40, 1380)
        if abs(y - 1140) < 45:
            continue
        pts = [(x, y)]
        ang = r.uniform(0, math.pi)
        for _ in range(r.randint(4, 7)):
            ang += r.uniform(-0.9, 0.9)
            x += math.cos(ang) * r.uniform(22, 48)
            y += math.sin(ang) * r.uniform(8, 22)
            pts.append((x, y))
        cracks.append(pts)
    return cracks


CRACKS = make_cracks()


def cracks(ctx, prog):
    ctx.save()
    ctx.set_source_rgba(*col("crack", 0.9))
    ctx.set_line_width(3.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for i, c in enumerate(CRACKS):
        p = seg(prog, i / len(CRACKS) * 0.6, i / len(CRACKS) * 0.6 + 0.4)
        if polyline(ctx, c, p):
            ctx.stroke()
    ctx.restore()


SHRUBS = [(150, 1004, 1.0), (930, 1000, 1.1), (790, 1004, 0.7), (300, 1000, 0.6)]


def shrub(ctx, x, y, s, dead=1.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    c = lerpc(col("leaf"), col("dead"), dead)
    ctx.set_source_rgba(*c[:3], alpha)
    ctx.set_line_width(6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    droop = 20 * dead
    for a in (-60, -30, 0, 30, 60):
        rad = math.radians(a - 90)
        ex, ey = math.cos(rad) * 70, math.sin(rad) * 70 + droop * abs(a) / 60
        ctx.move_to(0, 0)
        ctx.curve_to(ex * 0.3, ey * 0.5, ex * 0.8, ey * 0.8 - 10 * (1 - dead), ex, ey)
        ctx.stroke()
        ctx.arc(ex, ey, 8, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()


def sun(ctx, t, alpha):
    if alpha <= 0:
        return
    cx, cy = 860, 300
    ctx.save()
    rg = cairo.RadialGradient(cx, cy, 40, cx, cy, 260)
    rg.add_color_stop_rgba(0, *col("gold2", 0.45 * alpha)[:3], 0.45 * alpha)
    rg.add_color_stop_rgba(1, *col("gold2")[:3], 0)
    ctx.set_source(rg)
    ctx.arc(cx, cy, 260, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(*col("gold2", alpha))
    ctx.arc(cx, cy, 88, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_width(8)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(12):
        a = k * math.pi / 6 + t * 0.15
        ctx.move_to(cx + math.cos(a) * 112, cy + math.sin(a) * 112)
        ctx.line_to(cx + math.cos(a) * 146, cy + math.sin(a) * 146)
    ctx.stroke()
    ctx.restore()


def shimmer(ctx, t, alpha):
    if alpha <= 0:
        return
    ctx.save()
    ctx.set_line_width(4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(9):
        y0 = 960 - ((t * 70 + k * 70) % 600)
        a = alpha * 0.5 * math.sin(math.pi * clamp((960 - y0) / 600))
        x0 = 80 + (k * 211) % 860
        ctx.set_source_rgba(*col("gold", a))
        ctx.move_to(x0, y0)
        for i in range(1, 13):
            x = x0 + i * 12
            ctx.line_to(x, y0 + 7 * math.sin(i * 0.9 + t * 4 + k))
        ctx.stroke()
    ctx.restore()


ROOTS_SIMPLE = [
    [(540, 1000), (520, 1040), (470, 1080), (420, 1118)],
    [(540, 1000), (548, 1050), (560, 1090), (575, 1122)],
    [(540, 1000), (590, 1030), (650, 1070), (690, 1120)],
    [(540, 1000), (500, 1020), (430, 1040), (360, 1080)],
    [(540, 1000), (600, 1018), (690, 1036), (760, 1070)],
]


def roots_simple(ctx, prog=1.0, alpha=1.0):
    ctx.save()
    ctx.set_source_rgba(*col("brown2", alpha))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i, r in enumerate(ROOTS_SIMPLE):
        p = seg(prog, i * 0.08, i * 0.08 + 0.6)
        if p <= 0:
            continue
        pts = bez_pts(r, 24)
        ctx.set_line_width(9 if i < 3 else 6)
        if polyline(ctx, pts, p):
            ctx.stroke()
    ctx.restore()


def bez_pts(c, n):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = c
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, cc, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * x0 + b * x1 + cc * x2 + d * x3, a * y0 + b * y1 + cc * y2 + d * y3))
    return out


def world(ctx, t, *, crack=1.0, shrubs_dead=1.0, shrub_alpha=1.0, tree_grow=1.0, tree_green=1.0,
          stream_prog=1.0, sun_a=0.0, shimmer_a=0.0, roots=0.0, tree_alpha=1.0, glow=0.0, sway=0.0):
    bg(ctx, col("cream"))
    sun(ctx, t, sun_a)
    shimmer(ctx, t, shimmer_a)
    ground(ctx)
    cracks(ctx, crack)
    stream(ctx, t, stream_prog)
    if roots > 0:
        roots_simple(ctx, roots)
    for x, y, s in SHRUBS:
        shrub(ctx, x, y, s, shrubs_dead, shrub_alpha)
    tree(ctx, 540, GROUND_Y + 4, tree_grow, tree_green, sway, tree_alpha, glow)


def cam(ctx, cx, cy, s):
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ctx.translate(-cx, -cy)


# ---------------------------------------------------------------- scene 1: hook
def make_debris():
    r = random.Random(3)
    out = []
    for i in range(46):
        out.append(dict(
            kind=r.choice(["paper", "paper", "leaf", "leaf", "tile"]),
            ang=r.uniform(0, 2 * math.pi), r0=r.uniform(170, 420), spin=r.uniform(-3, 3),
            speed=r.uniform(0.6, 1.3), start=r.uniform(0.0, 1.6), size=r.uniform(0.7, 1.3),
            col=r.choice(["rust", "leaf", "gold", "dry"]),
        ))
    return out


DEBRIS = make_debris()
TILES = [(x, y) for y in (1050, 1100, 1150) for x in range(30, 1080, 100)]


def scene1(ctx, lt):
    bg(ctx, col("cream"))
    ctx.save()
    cam(ctx, 540, 900, 1.0 + 0.07 * ease(lt / 4.5))
    fx, fy = 540, 1040
    # ground tiles break away except under the figure
    for i, (x, y) in enumerate(TILES):
        d = abs(x + 45 - fx)
        if d < 80 and y == 1050:
            lift = 0
        else:
            st = 0.5 + (420 - min(d, 420)) / 420 * -0.0 + (i % 7) * 0.18
            lift = ein(seg(lt, st, st + 2.2))
        ox = (x + 45 - fx) * 0.9 * lift
        oy = -260 * lift - 40 * math.sin(i) * lift
        ctx.save()
        ctx.translate(x + 45 + ox, y + 22 + oy)
        ctx.rotate(lift * (i % 5 - 2) * 0.9)
        ctx.set_source_rgba(*col("sand", 1 - 0.85 * lift))
        ctx.rectangle(-46, -22, 92, 44)
        ctx.fill()
        ctx.set_source_rgba(*col("sand2", 1 - 0.85 * lift))
        ctx.set_line_width(3)
        ctx.rectangle(-46, -22, 92, 44)
        ctx.stroke()
        ctx.restore()
    # wind streaks
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(10):
        ph = (lt * 0.7 + k * 0.137) % 1.0
        a = math.sin(math.pi * ph) * 0.35 * seg(lt, 0.3, 1.0)
        rr = 220 + k * 34
        a0 = k * 0.9 + lt * 1.2
        ctx.set_source_rgba(*col("brown2", a))
        ctx.set_line_width(4)
        ctx.arc(fx, 860, rr, a0, a0 + 0.7)
        ctx.stroke()
    # debris spiralling out
    for d in DEBRIS:
        u = lt - d["start"]
        if u <= 0:
            continue
        rr = d["r0"] + 140 * u * d["speed"] + 40 * u * u
        ang = d["ang"] + u * 0.9 * d["speed"]
        x, y = fx + math.cos(ang) * rr, 860 + math.sin(ang) * rr * 0.8
        a = clamp(u / 0.4) * clamp(1.6 - rr / 700)
        if a <= 0:
            continue
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(d["spin"] * u)
        ctx.scale(d["size"], d["size"])
        if d["kind"] == "paper":
            ctx.set_source_rgba(*col("cream2", a))
            ctx.rectangle(-26, -34, 52, 68)
            ctx.fill()
            ctx.set_source_rgba(*col("brown2", a * 0.8))
            ctx.set_line_width(2.5)
            ctx.rectangle(-26, -34, 52, 68)
            ctx.stroke()
            for j in range(4):
                ctx.move_to(-16, -20 + j * 12)
                ctx.line_to(16, -20 + j * 12)
            ctx.stroke()
        elif d["kind"] == "leaf":
            ctx.set_source_rgba(*col(d["col"], a))
            ctx.save()
            ctx.scale(1, 0.5)
            ctx.arc(0, 0, 22, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
        else:
            ctx.set_source_rgba(*col("sand2", a))
            ctx.rectangle(-20, -12, 40, 24)
            ctx.fill()
        ctx.restore()
    # the steady figure + the patch they stand on
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(fx - 90, 1040, 180, 40)
    ctx.fill()
    figure(ctx, fx, fy, 1.6, col("brown"))
    ctx.restore()


# ---------------------------------------------------------------- scene 2: the picture
def scene2(ctx, lt):
    s = 1.0 + 0.05 * ease(lt / 9)
    ctx.save()
    cam(ctx, 540, 900, s)
    world(ctx, lt + 4.2,
          crack=ease(seg(lt, 2.6, 5.0)),
          shrubs_dead=ease(seg(lt, 3.0, 7.5)),
          shrub_alpha=ease(seg(lt, 2.4, 3.2)),
          tree_grow=seg(lt, 3.2, 5.8),
          tree_green=1.0,
          stream_prog=ease(seg(lt, 4.8, 6.6)),
          sun_a=ease(seg(lt, 0.4, 1.6)),
          shimmer_a=ease(seg(lt, 6.2, 7.0)),
          glow=math.sin(math.pi * seg(lt, 7.6, 9.2)),
          sway=0.015 * math.sin(lt * 1.3))
    ctx.restore()
    a = ease(seg(lt, 0.2, 1.0)) * (1 - ease(seg(lt, 5.0, 6.0)))
    draw_text(ctx, "PSALM 1", F_SERIF, 108, "#3B2A1E", 540, 220, a, 0.96 + 0.04 * eout(seg(lt, 0.2, 1.0)))
    draw_text(ctx, "The opening song", F_SERIF_I, 52, "#6E5039", 540, 320, a * ease(seg(lt, 0.6, 1.4)))


# ---------------------------------------------------------------- scene 3: the meaning
def scene3(ctx, lt):
    k = ease(seg(lt, 0.2, 1.6)) * (1 - ease(seg(lt, 3.5, 5.0)))
    ctx.save()
    cam(ctx, 540, 900, 1.05 + 0.03 * ease(lt / 6))
    world(ctx, lt + 13.2, crack=1, shrubs_dead=1, tree_grow=1, stream_prog=1, sun_a=1,
          shimmer_a=0.6, roots=ease(seg(lt, 0.0, 1.4)), tree_alpha=1 - 0.8 * k,
          sway=0.015 * math.sin((lt + 9) * 1.3))
    # the person in the trunk, arms lifted like branches
    if k > 0:
        ctx.push_group()
        glowc = cairo.RadialGradient(540, 820, 20, 540, 820, 300)
        glowc.add_color_stop_rgba(0, *col("gold2")[:3], 0.35)
        glowc.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(glowc)
        ctx.arc(540, 820, 300, 0, 2 * math.pi)
        ctx.fill()
        figure(ctx, 540, GROUND_Y + 4, 2.0, col("brown"), arms=ease(seg(lt, 0.6, 1.8)))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)
    # glowing scroll on the bank
    sa = ease(seg(lt, 1.4, 2.2))
    if sa > 0:
        ctx.save()
        ctx.translate(820, 1062)
        pulse = 0.6 + 0.4 * math.sin(lt * 3)
        rg = cairo.RadialGradient(0, 0, 10, 0, 0, 170)
        rg.add_color_stop_rgba(0, *col("gold2")[:3], 0.55 * sa * pulse)
        rg.add_color_stop_rgba(1, *col("gold2")[:3], 0)
        ctx.set_source(rg)
        ctx.arc(0, 0, 170, 0, 2 * math.pi)
        ctx.fill()
        ctx.scale(eout(seg(lt, 1.4, 2.2)), 1)
        ctx.set_source_rgba(*col("cream2", sa))
        ctx.rectangle(-70, -38, 140, 76)
        ctx.fill()
        ctx.set_source_rgba(*col("brown2", sa))
        ctx.set_line_width(3)
        ctx.rectangle(-70, -38, 140, 76)
        ctx.stroke()
        for sx in (-1, 1):
            ctx.set_source_rgba(*col("dry", sa))
            ctx.rectangle(sx * 70 - 9, -46, 18, 92)
            ctx.fill()
        ctx.set_source_rgba(*col("brown2", 0.6 * sa))
        for j in range(4):
            ctx.move_to(-48, -20 + j * 13)
            ctx.line_to(48, -20 + j * 13)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.restore()
    ctx.restore()


# ---------------------------------------------------------------- scene 4: the nugget
def star_path(ctx, cx, cy, ro, ri, n, rot=0):
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = rot + i * math.pi / n
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    ctx.close_path()


def lion(ctx, x, y, s, alpha, breath=0.0):
    ctx.push_group()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    gold, deep = col("gold"), col("rust")
    # tail
    ctx.set_source_rgba(*gold)
    ctx.set_line_width(16)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(220, -30)
    ctx.curve_to(300, -40, 320, -120, 300, -160)
    ctx.stroke()
    ctx.set_source_rgba(*deep)
    ctx.arc(300, -170, 22, 0, 2 * math.pi)
    ctx.fill()
    # legs (crouched)
    ctx.set_source_rgba(*gold)
    for lx in (-150, -80, 120, 185):
        ctx.rectangle(lx, 20, 46, 92)
        ctx.fill()
        ctx.save()
        ctx.scale(1, 0.55)
        ctx.arc(lx + 18, 112 / 0.55, 32, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    # body + haunch
    ctx.save()
    ctx.scale(1, 0.42)
    ctx.arc(10, 0, 235, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.arc(160, -10, 108, 0, 2 * math.pi)
    ctx.fill()
    # mane
    ctx.set_source_rgba(*deep)
    star_path(ctx, -215, -60, 150 + 6 * breath, 112, 16, 0.1)
    ctx.fill()
    # head
    ctx.set_source_rgba(*gold)
    ctx.arc(-250, -48, 86, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(-200, -128, 22, 0, 2 * math.pi)
    ctx.fill()
    ctx.save()
    ctx.scale(1, 0.75)
    ctx.arc(-322, -20 / 0.75, 52, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    # open mouth + eye
    ctx.set_source_rgba(*col("dark"))
    ctx.move_to(-372, -12)
    ctx.line_to(-310, 2 - 4 * breath)
    ctx.line_to(-372, 18 + 10 * breath)
    ctx.close_path()
    ctx.fill()
    ctx.arc(-270, -80, 9, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


def page_card(ctx, cx, cy, lt_skim, chew, pulse, alpha):
    w, h = 700, 520
    ctx.save()
    ctx.translate(cx, cy)
    ctx.set_source_rgba(*col("cream2", alpha))
    rounded(ctx, -w / 2, -h / 2, w, h, 18)
    ctx.fill()
    nlines = 9
    ctx.save()
    rounded(ctx, -w / 2, -h / 2, w, h, 18)
    ctx.clip()
    skim = 1 - chew
    offs = (lt_skim * 900) % 52 if skim > 0 else 0
    for i in range(-1, nlines + 1):
        y = -h / 2 + 70 + i * 52 - offs * skim
        lw = [560, 600, 520, 590, 480, 600, 540, 580, 420, 560, 500][(i + 1) % 11]
        hl = (i == 4) and chew > 0.5
        if hl:
            g = 0.5 + 0.5 * pulse
            ctx.set_source_rgba(*col("gold2", 0.35 * g * alpha))
            rounded(ctx, -w / 2 + 40, y - 22, lw + 30, 44, 22)
            ctx.fill()
            ctx.set_source_rgba(*col("gold", alpha))
        else:
            ctx.set_source_rgba(*col("brown2", (0.35 + 0.25 * chew) * alpha * (1 - 0.4 * skim)))
        rounded(ctx, -w / 2 + 55, y - 9 - 10 * skim, lw, 18 + 20 * skim, 9)
        ctx.fill()
    # rapidly turning top page while skimming
    if skim > 0.02:
        ph = (lt_skim * 5.5) % 1.0
        fw = math.cos(ph * math.pi)
        ctx.set_source_rgba(*col("cream", 0.95 * alpha * skim))
        ctx.save()
        ctx.translate(-w / 2, 0)
        ctx.scale(max(0.001, (fw + 1) / 2), 1)
        ctx.rectangle(0, -h / 2, w, h)
        ctx.restore()
        ctx.fill()
    ctx.restore()
    ctx.set_source_rgba(*col("gold", alpha))
    ctx.set_line_width(4)
    rounded(ctx, -w / 2, -h / 2, w, h, 18)
    ctx.stroke()
    ctx.restore()


def rounded(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def droplets(ctx, lt, alpha):
    ctx.save()
    for i, r in enumerate(ROOTS_SIMPLE):
        pts = bez_pts(r, 40)[::-1]
        for k in range(3):
            u = ((lt * 0.9 + k / 3 + i * 0.13) % 1.0)
            idx = int(u * (len(pts) - 1))
            x, y = pts[idx]
            ctx.set_source_rgba(*col("water2", alpha * math.sin(math.pi * u)))
            ctx.arc(x, y, 9, 0, 2 * math.pi)
            ctx.fill()
    # up the trunk
    for k in range(4):
        u = (lt * 0.8 + k / 4) % 1.0
        y = GROUND_Y - u * 300
        ctx.set_source_rgba(*col("water2", alpha * math.sin(math.pi * u)))
        ctx.arc(540, y, 8, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()


def scene4(ctx, lt):
    bg(ctx, col("dark"))
    # soft centre light
    rg = cairo.RadialGradient(540, 700, 50, 540, 700, 800)
    rg.add_color_stop_rgba(0, *col("brown2")[:3], 0.55)
    rg.add_color_stop_rgba(1, *col("dark")[:3], 0)
    ctx.set_source(rg)
    ctx.paint()

    # Beat A: the Hebrew word
    hdr = ease(seg(lt, 3.2, 3.9))
    ha = ease(seg(lt, 0.3, 0.6)) * (1 - ease(seg(lt, 11.8, 12.3)))
    reveal = ease(seg(lt, 0.4, 2.0))
    hy, hs = lerp(620, 230, hdr), lerp(1.0, 0.5, hdr)
    if ha > 0:
        s = text_surf("הָגָה", F_HEB, 300, "#E3B04B", rtl=True, glow=14)
        ww, hh = s.get_width(), s.get_height()
        ctx.save()
        ctx.translate(540, hy)
        ctx.scale(hs, hs)
        ctx.rectangle(ww / 2 - ww * reveal, -hh / 2, ww * reveal, hh)  # right to left
        ctx.clip()
        ctx.set_source_surface(s, -ww / 2, -hh / 2)
        ctx.paint_with_alpha(ha)
        ctx.restore()
    sub = ease(seg(lt, 1.6, 2.4)) * (1 - ease(seg(lt, 3.0, 3.5)))
    draw_text(ctx, "hagah", F_SERIF_I, 96, "#FBF6EC", 540, 860, sub)
    draw_text(ctx, "to meditate · to murmur", F_SERIF_R, 56, "#DCC59D", 540, 960, sub)
    draw_text(ctx, "hagah · to meditate", F_SERIF_I, 48, "#DCC59D", 540, 340,
              hdr * (1 - ease(seg(lt, 11.8, 12.3))))

    # Beat B: the lion growling (no prey shown)
    la = ease(seg(lt, 3.8, 4.6)) * (1 - ease(seg(lt, 7.0, 7.6)))
    if la > 0:
        growl = seg(lt, 5.2, 7.2)
        breath = math.sin(lt * 9) * 0.5 + 0.5 if growl > 0 else 0
        lion(ctx, 690 + 40 * (1 - eout(seg(lt, 3.8, 4.8))), 820, 1.0, la, breath * growl)
        if growl > 0:
            ctx.save()
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            mx, my = 690 - 372, 820
            for k in range(4):
                u = ((lt - 5.2) * 0.9 + k * 0.25) % 1.0
                rr = 40 + u * 260
                ctx.set_source_rgba(*col("gold2", la * (1 - u) * 0.9))
                ctx.set_line_width(10 * (1 - u) + 3)
                ctx.arc(mx, my, rr, math.pi - 0.55, math.pi + 0.55)
                ctx.stroke()
            ctx.restore()
        tag = ease(seg(lt, 4.2, 4.8))
        ctx.save()
        ctx.set_source_rgba(*col("gold", la * tag))
        rounded(ctx, 700, 1180, 300, 74, 37)
        ctx.fill()
        ctx.restore()
        draw_text(ctx, "Isaiah 31:4", F_SERIF, 44, "#2A1D14", 850, 1217, la * tag)

    # Beat C: skimming vs chewing
    pa = ease(seg(lt, 7.3, 7.9)) * (1 - ease(seg(lt, 12.0, 12.5)))
    if pa > 0:
        chew = ease(seg(lt, 8.2, 8.8))
        pulse = max(0, math.sin(lt * 5)) * 0.4 + 0.6 * math.exp(-((lt - 11.1) ** 2) * 6) \
            + 0.6 * math.exp(-((lt - 11.6) ** 2) * 6)
        page_card(ctx, 540, 800, lt, chew, clamp(pulse), pa)
        lab = (1 - chew)
        draw_text(ctx, "skimming", F_SERIF_I, 64, "#DCC59D", 540, 470, pa * lab)
        draw_text(ctx, "chewing", F_SERIF_I, 64, "#E3B04B", 540, 470, pa * chew)

    # Beat D: back to the stream, roots drinking
    wa = ease(seg(lt, 12.0, 12.6))
    if wa > 0:
        ctx.push_group()
        ctx.save()
        cam(ctx, 540, 1000, 1.18)
        world(ctx, lt, crack=0.5, shrubs_dead=1, tree_grow=1, stream_prog=1, sun_a=0.6,
              roots=1, sway=0.012 * math.sin(lt * 1.3))
        droplets(ctx, lt, 1.0)
        ctx.restore()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(wa)


# ---------------------------------------------------------------- scene 5: the other path
def make_wheat():
    r = random.Random(5)
    out = []
    for i in range(34):
        x = r.uniform(580, 1060)
        out.append(dict(x=x, h=r.uniform(170, 300), lean=r.uniform(-0.08, 0.12),
                        t=r.uniform(1.2, 4.2), vx=r.uniform(380, 640), vy=r.uniform(-160, -40),
                        spin=r.uniform(-6, 6), ph=r.uniform(0, 6)))
    return sorted(out, key=lambda d: d["x"])


WHEAT = make_wheat()


def scene5(ctx, lt):
    bg(ctx, col("cream"))
    ground(ctx)
    # left: the rooted tree, kept green
    ctx.save()
    ctx.rectangle(0, 0, 540, H)
    ctx.clip()
    ctx.save()
    ctx.translate(270, GROUND_Y)
    ctx.scale(0.62, 0.62)
    ctx.translate(-540, -GROUND_Y)
    stream(ctx, lt + 33.6, 1.0)
    roots_simple(ctx, 1.0)
    tree(ctx, 540, GROUND_Y + 4, 1, 1, 0.01 * math.sin(lt), 1, 0.3)
    ctx.restore()
    ctx.restore()
    # right: wheat turning to chaff
    wind = seg(lt, 1.0, 1.4)
    ctx.save()
    ctx.rectangle(540, 0, 540, H)
    ctx.clip()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(7):
        ph = (lt * 0.8 + k * 0.17) % 1.0
        a = math.sin(math.pi * ph) * 0.4 * wind
        y = 560 + k * 70
        x0 = 520 + ph * 700
        ctx.set_source_rgba(*col("brown2", a))
        ctx.set_line_width(4)
        ctx.move_to(x0, y)
        ctx.curve_to(x0 + 60, y - 14, x0 + 120, y + 14, x0 + 200, y)
        ctx.stroke()
    for d in WHEAT:
        bx, by = d["x"], GROUND_Y + 6
        bend = d["lean"] + 0.12 * wind * math.sin(lt * 3 + d["ph"])
        u = lt - d["t"]
        stalk_a = 1 - ease(seg(u, 0.3, 1.2))
        tx = bx + math.sin(bend) * d["h"]
        ty = by - math.cos(bend) * d["h"]
        if stalk_a > 0:
            ctx.set_source_rgba(*col("dry", stalk_a))
            ctx.set_line_width(5)
            ctx.move_to(bx, by)
            ctx.curve_to(bx, by - d["h"] * 0.5, tx, ty + 30, tx, ty)
            ctx.stroke()
        # head / husk
        if u < 0:
            hx, hy, rot, ha = tx, ty, bend, 1.0
        else:
            hx = tx + d["vx"] * u + 40 * u * u
            hy = ty + d["vy"] * u + 30 * math.sin(u * 5 + d["ph"])
            rot = bend + d["spin"] * u
            ha = 1 - seg(u, 0.6, 1.6)
        if ha > 0:
            ctx.save()
            ctx.translate(hx, hy)
            ctx.rotate(rot)
            ctx.set_source_rgba(*col("gold" if u < 0 else "sand2", ha))
            for j in range(5):
                ctx.save()
                ctx.translate(0, -j * 13)
                ctx.scale(0.55, 1)
                ctx.arc(0, 0, 12, 0, 2 * math.pi)
                ctx.restore()
                ctx.fill()
            ctx.restore()
    ctx.restore()
    # divider
    dv = eout(seg(lt, 0.1, 0.7))
    ctx.set_source_rgba(*col("gold"))
    ctx.set_line_width(5)
    ctx.move_to(540, 380)
    ctx.line_to(540, 380 + 1000 * dv)
    ctx.stroke()
    draw_text(ctx, "rooted", F_SERIF_I, 62, "#466E2E", 270, 300, ease(seg(lt, 0.4, 1.0)))
    draw_text(ctx, "chaff", F_SERIF_I, 62, "#A9472F", 810, 300, ease(seg(lt, 0.8, 1.4)))


# ---------------------------------------------------------------- scene 6: deep roots + storm
def make_deep_roots():
    r = random.Random(9)
    segs = []

    def grow(x, y, ang, length, width, depth, t0):
        if depth > 5 or length < 30:
            return
        x2 = x + math.cos(ang) * length
        y2 = y + math.sin(ang) * length
        segs.append((x, y, x2, y2, width, t0, depth))
        n = 2 if depth < 4 else 1
        for i in range(n):
            na = ang + r.uniform(-0.7, 0.7) + (0.35 if i else -0.35) * (1 if depth < 3 else 0.5)
            na = clamp(na, math.radians(25), math.radians(155))
            grow(x2, y2, na, length * r.uniform(0.68, 0.85), width * 0.68, depth + 1, t0 + 0.16)

    for a in (60, 80, 100, 120):
        grow(540, 700, math.radians(a), 238, 26, 0, 0.0)
    return segs


DEEP = make_deep_roots()


def scene6(ctx, lt):
    bg(ctx, col("cream"))
    # camera: start at the surface, drop below, then pull back to see storm + roots together
    drop = ease(seg(lt, 0.0, 1.8))
    pull = ease(seg(lt, 2.1, 3.4))
    cy = lerp(lerp(560, 1060, drop), 950, pull)
    sc = lerp(lerp(1.15, 1.0, drop), 0.72, pull)
    ctx.save()
    ctx.translate(540, 700)
    ctx.scale(sc, sc)
    ctx.translate(-540, -cy)
    storm = ease(seg(lt, 2.4, 3.2))
    # sky darkens with storm
    ctx.set_source_rgba(*lerpc(col("cream"), hexc("#B9AE9C"), storm))
    ctx.rectangle(-900, -900, 2900, 1600)
    ctx.fill()
    # soil cross-section
    ctx.set_source_rgba(*col("sand"))
    ctx.rectangle(-900, 700, 2900, 2600)
    ctx.fill()
    ctx.set_source_rgba(*col("sand2"))
    for k in range(5):
        ctx.rectangle(-900, 900 + k * 230, 2900, 6)
        ctx.fill()
    ctx.set_source_rgba(*col("brown2", 0.6))
    ctx.set_line_width(4)
    ctx.move_to(-900, 700)
    ctx.line_to(2000, 700)
    ctx.stroke()
    # underground water
    ctx.set_source_rgba(*col("water", 0.9))
    ctx.rectangle(-900, 1470, 2900, 90)
    ctx.fill()
    ctx.set_source_rgba(*col("water2", 0.9))
    ctx.set_line_width(6)
    for k in range(14):
        x = ((lt * 120 + k * 210) % 2900) - 900
        ctx.move_to(x, 1500 + (k % 2) * 30)
        ctx.line_to(x + 90, 1500 + (k % 2) * 30)
        ctx.stroke()
    # roots
    g = seg(lt, 0.2, 2.6) * 1.6
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*col("brown2"))
    for x, y, x2, y2, w, t0, dep in DEEP:
        p = clamp((g - t0) / 0.3)
        if p <= 0:
            continue
        ctx.set_line_width(w)
        ctx.move_to(x, y)
        ctx.line_to(lerp(x, x2, p), lerp(y, y2, p))
        ctx.stroke()
    # tree above, swaying in the storm but holding
    sway = storm * 0.05 * math.sin(lt * 4.2)
    tree(ctx, 540, 704, 1, 1, sway, 1, 0, 300)
    # storm: cloud + rain
    if storm > 0:
        ctx.set_source_rgba(*hexc("#5E544A", 0.85 * storm))
        for x, y, r in [(220, 20, 110), (390, -10, 140), (580, 0, 130), (770, 20, 110), (480, 60, 110),
                        (300, 70, 90), (680, 70, 90), (900, 40, 90), (100, 50, 80)]:
            ctx.arc(x + 30 * math.sin(lt), y, r, 0, 2 * math.pi)
            ctx.fill()
        ctx.set_source_rgba(*hexc("#7A8C95", 0.75 * storm))
        ctx.set_line_width(5)
        rr = random.Random(int(lt * 15))
        for _ in range(70):
            x = rr.uniform(0, 1080)
            y = rr.uniform(140, 680)
            ctx.move_to(x, y)
            ctx.line_to(x - 22, y + 60)
        ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- scene 7: next step + end card
def scene7(ctx, lt):
    bg(ctx, col("cream"))
    end = ease(seg(lt, 3.5, 4.1))
    body = 1 - end
    if body > 0:
        ctx.push_group()
        pop = eout(seg(lt, 0.0, 0.7))
        ctx.save()
        ctx.translate(540, 600)
        ctx.scale(0.9 + 0.1 * pop, 0.9 + 0.1 * pop)
        ctx.set_source_rgba(*hexc("#000000", 0.08))
        rounded(ctx, -300 + 10, -330 + 14, 600, 660, 26)
        ctx.fill()
        ctx.set_source_rgba(*col("cream2"))
        rounded(ctx, -300, -330, 600, 660, 26)
        ctx.fill()
        ctx.set_source_rgba(*col("gold"))
        ctx.set_line_width(5)
        rounded(ctx, -300, -330, 600, 660, 26)
        ctx.stroke()
        ctx.restore()
        draw_text(ctx, "Psalm 1:2", F_SERIF, 76, "#3B2A1E", 540, 360, pop)
        ctx.set_source_rgba(*col("gold", pop))
        ctx.rectangle(470, 418, 140, 4)
        ctx.fill()
        for i, line in enumerate(["Their joy is", "God's word.", "They chew on it", "day and night."]):
            draw_text(ctx, line, F_SERIF_I, 58, "#6E5039", 540, 510 + i * 84, ease(seg(lt, 0.4 + i * 0.15, 0.9 + i * 0.15)))
        # soil + seedling
        ctx.set_source_rgba(*col("sand"))
        rounded(ctx, 240, 1060, 600, 120, 30)
        ctx.fill()
        sg = eout(seg(lt, 1.0, 2.4))
        rg = eout(seg(lt, 1.8, 3.3))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(*col("leaf"))
        ctx.set_line_width(10)
        ctx.move_to(540, 1064)
        ctx.curve_to(540, 1064 - 50 * sg, 548, 1064 - 90 * sg, 540, 1064 - 120 * sg)
        ctx.stroke()
        if sg > 0.5:
            la = ease(seg(sg, 0.5, 1.0))
            for sx in (-1, 1):
                ctx.save()
                ctx.translate(540, 1064 - 110 * sg)
                ctx.rotate(sx * 0.6)
                ctx.scale(la, la)
                ctx.save()
                ctx.scale(1.6, 0.7)
                ctx.arc(sx * 22, 0, 22, 0, 2 * math.pi)
                ctx.restore()
                ctx.fill()
                ctx.restore()
        if rg > 0:
            ctx.set_source_rgba(*col("brown2"))
            ctx.set_line_width(6)
            pts = bez_pts([(540, 1066), (536, 1100), (548, 1130), (532, 1170)], 20)
            polyline(ctx, pts, rg)
            ctx.stroke()
            pts = bez_pts([(540, 1100), (520, 1112), (505, 1130), (494, 1150)], 12)
            if polyline(ctx, pts, seg(rg, 0.5, 1)):
                ctx.set_line_width(4)
                ctx.stroke()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(body)
    if end > 0:
        draw_text(ctx, "PSALM 1", F_SERIF, 50, "#6E5039", 540, 700, end)
        ctx.set_source_rgba(*col("gold", end))
        ctx.rectangle(490, 750, 100, 4)
        ctx.fill()
        draw_text(ctx, "Be rooted in", F_SERIF, 96, "#3B2A1E", 540, 850, end, 0.95 + 0.05 * eout(seg(lt, 3.5, 4.3)))
        draw_text(ctx, "God's word.", F_SERIF, 96, "#3B2A1E", 540, 970, end, 0.95 + 0.05 * eout(seg(lt, 3.5, 4.3)))
        ctx.save()
        ctx.translate(540, 1340)
        ctx.scale(0.4, 0.4)
        ctx.translate(-540, -1000)
        tree(ctx, 540, 1000, eout(seg(lt, 3.7, 4.8)), 1, 0, end, 0.4)
        ctx.restore()


SCENES = [
    (0.0, 4.2, scene1),
    (4.2, 13.2, scene2),
    (13.2, 19.2, scene3),
    (19.2, 33.6, scene4),
    (33.6, 39.4, scene5),
    (39.4, 44.4, scene6),
    (44.4, 50.0, scene7),
]
XF = 0.35  # crossfade half-width


# ---------------------------------------------------------------- texture + frame
def make_paper():
    r = np.random.default_rng(1)
    n = r.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    n = (n - n.min()) / (n.max() - n.min())
    v = (226 + n * 29).astype(np.uint8)
    v = np.kron(v, np.ones((2, 2), dtype=np.uint8))
    im = Image.fromarray(v, "L").convert("RGBA")
    return pil_to_cairo(im)


PAPER = make_paper()


def vignette(ctx):
    rg = cairo.RadialGradient(W / 2, H * 0.42, 500, W / 2, H * 0.42, 1300)
    rg.add_color_stop_rgba(0, 0.16, 0.11, 0.08, 0)
    rg.add_color_stop_rgba(1, 0.16, 0.11, 0.08, 0.22)
    ctx.set_source(rg)
    ctx.paint()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
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
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_surface(PAPER, 0, 0)
    ctx.paint_with_alpha(0.55)
    ctx.restore()
    vignette(ctx)
    draw_captions(ctx, t)
    surf.flush()
    return surf


def still(t, path):
    render_frame(t).write_to_png(path)


def video(path, start=0.0, end=DUR):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n0, n1 = int(start * FPS), int(end * FPS)
    for i in range(n0, n1):
        s = render_frame(i / FPS)
        p.stdin.write(bytes(s.get_data()))
        if i % 150 == 0:
            print(f"frame {i}/{n1}", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        import os
        os.makedirs("/home/claude/psalm1/stills", exist_ok=True)
        for t in map(float, sys.argv[2:]):
            still(t, f"/home/claude/psalm1/stills/t{t:05.1f}.png")
    else:
        video(sys.argv[2])
