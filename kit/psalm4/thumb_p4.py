import sys, cairo, math
sys.path.insert(0, "/home/claude/psalm1"); sys.path.insert(0, "/home/claude/psalm4")
import render as R
import render_p4 as P
W, H = 1080, 1920
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
R.bg(c, R.col("cream"))
g = cairo.RadialGradient(540, 900, 50, 540, 900, 900)
g.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.28); g.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
c.set_source(g); c.paint()
R.draw_text(c, "PSALM 4", R.F_SERIF, 230, "#3B2A1E", 540, 640)
c.set_source_rgba(*R.col("gold")); c.rectangle(440, 790, 200, 7); c.fill()
R.draw_text(c, "in a minute", R.F_SERIF_I, 120, "#A8741A", 540, 900)
P.kettle(c, 520, 1330, 0.62, 0.0, 0.0, 1.0)
c.save(); c.set_operator(cairo.OPERATOR_MULTIPLY); c.set_source_surface(R.PAPER, 0, 0); c.paint_with_alpha(0.5); c.restore()
R.vignette(c)
s.write_to_png("/home/claude/psalm4/psalm4_thumbnail.png")
