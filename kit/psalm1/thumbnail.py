"""Series thumbnail: 'PSALM N / in a minute' on cream paper with a small icon.
Usage: python3 thumbnail.py 2 out.png"""
import sys
import cairo
import render as R

n = sys.argv[1] if len(sys.argv) > 1 else "1"
out = sys.argv[2] if len(sys.argv) > 2 else f"/home/claude/psalm1/psalm{n}_thumbnail.png"
W, H = 1080, 1920
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
c = cairo.Context(s)
R.bg(c, R.col("cream"))
g = cairo.RadialGradient(540, 900, 50, 540, 900, 900)
g.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.28)
g.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
c.set_source(g)
c.paint()
R.draw_text(c, f"PSALM {n}", R.F_SERIF, 230 if len(n) < 3 else 200, "#3B2A1E", 540, 640)
c.set_source_rgba(*R.col("gold"))
c.rectangle(440, 790, 200, 7)
c.fill()
R.draw_text(c, "in a minute", R.F_SERIF_I, 120, "#A8741A", 540, 900)
# chapter icon: replace this block with an icon that fits the chapter
c.save()
c.translate(540, 1330)
c.scale(0.55, 0.55)
c.translate(-540, -1000)
c.set_source_rgba(*R.col("water"))
c.set_line_width(40)
c.set_line_cap(cairo.LINE_CAP_ROUND)
c.move_to(300, 1040)
c.curve_to(420, 1010, 660, 1070, 780, 1040)
c.stroke()
R.tree(c, 540, 1004, 1, 1, 0, 1, 0.25)
c.restore()
c.save()
c.set_operator(cairo.OPERATOR_MULTIPLY)
c.set_source_surface(R.PAPER, 0, 0)
c.paint_with_alpha(0.5)
c.restore()
R.vignette(c)
s.write_to_png(out)
print(out)
