"""Shared render engine for Bible Shorts (Psalm 7 onward). Each episode supplies scenes and cue lists."""
import sys, os, math, json, re, subprocess
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm2")
sys.path.insert(0, "/home/claude/psalm3")
import cairo
import render as R
from render import W, H, FPS, col, ease, seg, clamp


class Episode:
    def __init__(self, n):
        self.n = n
        self.dir = f"/home/claude/psalm{n}"
        self.map = json.load(open(os.environ.get("VOMAP", f"{self.dir}/vomap.json")))
        self.callout = self.map.get("callout")
        self.dur = self.map["video_dur"]
        self.zooms, self.shakes, self.flashes, self.blur = [], [], [], []
        self.scenes = []
        self.xf = 0.12
        self.zc = (540, 860)

    def wt(self, word, n=1):
        k = 0
        for a, b, w in self.map["words"]:
            if re.sub(r"[^A-Za-z0-9]", "", w).lower() == word:
                k += 1
                if k == n:
                    return a
        raise KeyError(word)

    def zoom_amt(self, t):
        z = 0.0
        for t0, a in self.zooms:
            u = t - t0
            if 0 <= u < 1.2:
                z += a * (ease(u / 0.07) if u < 0.07 else math.exp(-(u - 0.07) * 5))
        return 1 + z

    def shake_amt(self, t):
        dx = dy = rot = 0.0
        for t0, amp, dur in self.shakes:
            u = t - t0
            if 0 <= u < dur:
                k = amp * (1 - u / dur) ** 2
                dx += k * math.sin(u * 61 + t0)
                dy += k * math.sin(u * 47 + 1.3 * t0)
                rot += k * 0.0009 * math.sin(u * 53)
        return dx, dy, rot

    def content(self, ctx, t):
        active = [(a, b, f) for a, b, f in self.scenes if a - self.xf <= t < b + self.xf]
        for i, (a, b, f) in enumerate(active):
            alpha = 1.0 if i == 0 else ease(seg(t, a - self.xf, a + self.xf))
            ctx.save()
            if alpha < 1:
                ctx.push_group()
                f(ctx, t - a)
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(alpha)
            else:
                f(ctx, t - a)
            ctx.restore()

    def render_frame(self, t):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        R.bg(ctx, col("dark"))
        dx, dy, rot = self.shake_amt(t)
        z = self.zoom_amt(t)
        ctx.save()
        ctx.translate(self.zc[0] + dx, self.zc[1] + dy)
        ctx.rotate(rot)
        ctx.scale(z, z)
        ctx.translate(-self.zc[0], -self.zc[1])
        if any(a <= t < b for a, b in self.blur):
            for k, ts in enumerate([t - 2 / 90, t - 1 / 90, t]):
                ctx.push_group()
                self.content(ctx, ts)
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(1 / (k + 1))
        else:
            self.content(ctx, t)
        ctx.restore()
        for t0, c, a, d in self.flashes:
            u = t - t0
            if 0 <= u < d:
                ctx.set_source_rgba(*c, a * (1 - u / d) ** 2)
                ctx.paint()
        if self.callout:
            callout_chips(ctx, t, self.callout)
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_MULTIPLY)
        ctx.set_source_surface(R.PAPER, 0, 0)
        ctx.paint_with_alpha(0.5)
        ctx.restore()
        R.vignette(ctx)
        surf.flush()
        return surf

    def video(self, path, n0, n1):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", path]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n0, n1):
            p.stdin.write(bytes(self.render_frame(i / FPS).get_data()))
        p.stdin.close()
        p.wait()

    def main(self, argv):
        if argv[1] == "stills":
            os.makedirs(f"{self.dir}/stills", exist_ok=True)
            for f in os.listdir(f"{self.dir}/stills"):
                os.remove(f"{self.dir}/stills/{f}")
            for t in map(float, argv[2:]):
                self.render_frame(t).write_to_png(f"{self.dir}/stills/t{t:05.2f}.png")
        else:
            self.video(argv[2], int(argv[3]), int(argv[4]))


CHIPS = {"youtube": [("like", "Like"), ("plus", "Subscribe"), ("share", "Share")],
         "instagram": [("like", "Like"), ("plus", "Follow"), ("send", "Send")],
         "tiktok": [("like", "Like"), ("plus", "Follow"), ("send", "Send")]}


def _icon(ctx, kind, x, y, c):
    ctx.set_source_rgba(*c)
    if kind == "like":
        s = 15
        ctx.move_to(x, y + s)
        ctx.curve_to(x - 2.2 * s, y - 0.2 * s, x - 1.1 * s, y - 1.6 * s, x, y - 0.6 * s)
        ctx.curve_to(x + 1.1 * s, y - 1.6 * s, x + 2.2 * s, y - 0.2 * s, x, y + s)
        ctx.fill()
    elif kind == "plus":
        ctx.rectangle(x - 16, y - 4.5, 32, 9); ctx.fill()
        ctx.rectangle(x - 4.5, y - 16, 9, 32); ctx.fill()
    elif kind == "send":
        ctx.move_to(x - 18, y - 2); ctx.line_to(x + 18, y - 16); ctx.line_to(x + 6, y + 18); ctx.line_to(x - 1, y + 3)
        ctx.close_path(); ctx.fill()
    elif kind == "share":
        ctx.move_to(x - 16, y + 14); ctx.curve_to(x - 14, y - 4, x - 2, y - 8, x + 4, y - 8)
        ctx.line_to(x + 4, y - 17); ctx.line_to(x + 19, y - 2); ctx.line_to(x + 4, y + 13); ctx.line_to(x + 4, y + 3)
        ctx.curve_to(x - 4, y + 3, x - 12, y + 6, x - 16, y + 14); ctx.close_path(); ctx.fill()


def callout_chips(ctx, t, co):
    """Like / Follow-or-Subscribe / Send-or-Share buttons that rise above the captions while the callout is spoken."""
    a0, a1 = co["start"], co["end"]
    if not (a0 - 0.4 <= t <= a1 + 0.5):
        return
    vis = ease(seg(t, a0 - 0.35, a0)) * (1 - ease(seg(t, a1 + 0.1, a1 + 0.45)))
    if vis <= 0.01:
        return
    chips = CHIPS[co["plat"]]
    lights = co["lights"]
    widths = [R.font(R.F_CAP, 46).getlength(lbl) + 104 for _, lbl in chips]
    gap = 26
    x = 540 - (sum(widths) + gap * (len(chips) - 1)) / 2
    y = 1395
    for k, ((kind, lbl), w) in enumerate(zip(chips, widths)):
        appear = ease(seg(t, a0 - 0.35 + 0.08 * k, a0 + 0.08 * k))
        lit = ease(seg(t, lights[k] - 0.05, lights[k] + 0.12))
        pop = math.exp(-max(0.0, t - lights[k]) * 9) if t >= lights[k] else 0.0
        sc = (0.85 + 0.15 * appear) * (1 + 0.12 * pop)
        dy = 40 * (1 - appear)
        ctx.save()
        ctx.translate(x + w / 2, y + dy)
        ctx.scale(sc, sc)
        al = vis * appear
        ctx.set_source_rgba(0.17, 0.11, 0.08, 0.35 * al)
        R.rounded(ctx, -w / 2 + 4, -42 + 8, w, 84, 42); ctx.fill()
        fill = R.lerpc(R.hexc("#FFF9EE"), R.hexc("#E3B04B"), lit)
        ctx.set_source_rgba(*fill[:3], al)
        R.rounded(ctx, -w / 2, -42, w, 84, 42); ctx.fill()
        ctx.set_source_rgba(0.17, 0.11, 0.08, al)
        ctx.set_line_width(5)
        R.rounded(ctx, -w / 2, -42, w, 84, 42); ctx.stroke()
        ic = (0.75, 0.2, 0.18, al) if (kind == "like" and lit > 0.5) else (0.17, 0.11, 0.08, al)
        _icon(ctx, kind, -w / 2 + 48, 0, ic)
        R.draw_text(ctx, lbl, R.F_CAP, 46, "#2B1D14", 32, 2, al)
        ctx.restore()
        x += w + gap


def fit_text(ctx, txt, path, size, color, cx, cy, alpha=1.0, scale=1.0, maxw=980, **kw):
    """draw_text that shrinks the font until the line fits maxw."""
    while size > 40 and R.font(path, size).getlength(txt) > maxw:
        size -= 4
    R.draw_text(ctx, txt, path, size, color, cx, cy, alpha, scale, **kw)


def end_card(ctx, t, label, icon, line1, line2, t1, t2, sub="in a minute"):
    """Standard end card (Psalm 13 on). It doubles as the thumbnail and the Instagram/TikTok cover:
    PSALM N, gold rule, 'in a minute', the episode icon, then the closing line in two parts.
    t1 / t2: times the two parts of the closing line are spoken. Fades in over 0.4 s before t1."""
    end = ease(seg(t, t1 - 0.4, t1))
    if end <= 0.001:
        return
    ctx.save()
    ctx.push_group()
    R.bg(ctx, R.col("cream"))
    g = cairo.RadialGradient(540, 700, 50, 540, 700, 900)
    g.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.28)
    g.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
    ctx.set_source(g)
    ctx.paint()
    fit_text(ctx, label, R.F_SERIF, 210, "#3B2A1E", 540, 330, 1.0, 0.94 + 0.06 * V_back_out(seg(t, t1 - 0.4, t1 + 0.1)))
    ctx.set_source_rgba(*R.col("gold"))
    ctx.rectangle(440, 465, 200, 7)
    ctx.fill()
    R.draw_text(ctx, sub, R.F_SERIF_I, 110, "#A8741A", 540, 570)
    gl = cairo.RadialGradient(540, 860, 10, 540, 860, 240)
    gl.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.45)
    gl.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    ctx.set_source(gl)
    ctx.arc(540, 860, 240, 0, 2 * math.pi)
    ctx.fill()
    ctx.save()
    icon(ctx, 540, 860)
    ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(end)
    ctx.restore()
    fit_text(ctx, line1, R.F_SERIF, 92, "#3B2A1E", 540, 1110, end, 0.94 + 0.06 * V_back_out(seg(t, t1 - 0.3, t1 + 0.1)))
    a2 = ease(seg(t, t2 - 0.25, t2 + 0.05))
    fit_text(ctx, line2, R.F_SERIF, 118, "#A8741A", 540, 1250, a2, 0.92 + 0.08 * V_back_out(seg(t, t2 - 0.25, t2 + 0.2)))


def V_back_out(x, s=1.9):
    x = clamp(x)
    x -= 1
    return 1 + x * x * ((s + 1) * x + s)


def end_thumbnail(label, icon, line1, line2, path, sub="in a minute"):
    """The thumbnail PNG is the finished end-card frame (same art, so cover and thumbnail always match)."""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    end_card(c, 100.0, label, icon, line1, line2, 0.0, 0.0, sub)
    c.save()
    c.set_operator(cairo.OPERATOR_MULTIPLY)
    c.set_source_surface(R.PAPER, 0, 0)
    c.paint_with_alpha(0.5)
    c.restore()
    R.vignette(c)
    s.write_to_png(path)


def contact(n, cols=10):
    from PIL import Image, ImageDraw
    import glob
    fs = sorted(glob.glob(f"/home/claude/psalm{n}/stills/t*.png"))
    th = [Image.open(f).resize((216, 384)) for f in fs]
    rows = (len(th) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 216, rows * 404), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, (f, im) in enumerate(zip(fs, th)):
        x, y = (i % cols) * 216, (i // cols) * 404
        sheet.paste(im, (x, y))
        d.text((x + 6, y + 386), f.split("/")[-1][1:-4], fill=(255, 255, 255))
    sheet.save(f"/home/claude/psalm{n}/contact.png")
