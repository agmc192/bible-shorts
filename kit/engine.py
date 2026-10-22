"""Shared render engine for Bible Shorts (Psalm 7 onward). Each episode supplies scenes and cue lists."""
import sys, os, math, json, re, subprocess
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm2")
sys.path.insert(0, "/home/claude/psalm3")
import cairo
import render as R
from render import W, H, FPS, col, ease, seg


class Episode:
    def __init__(self, n):
        self.n = n
        self.dir = f"/home/claude/psalm{n}"
        self.map = json.load(open(f"{self.dir}/vomap.json"))
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
