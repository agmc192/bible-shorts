import sys, cairo, math
sys.path.insert(0, "/home/claude/psalm1"); sys.path.insert(0, "/home/claude/psalm2")
import render as R
import render_p2 as P
W, H = 1080, 1920
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
R.bg(c, R.col("cream"))
g = cairo.RadialGradient(540, 900, 50, 540, 900, 900)
g.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.28); g.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
c.set_source(g); c.paint()
R.draw_text(c, "PSALM 2", R.F_SERIF, 230, "#3B2A1E", 540, 640)
c.set_source_rgba(*R.col("gold")); c.rectangle(440, 790, 200, 7); c.fill()
R.draw_text(c, "in a minute", R.F_SERIF_I, 120, "#A8741A", 540, 900)
P.crown(c, 540, 1250, 0.95, 1.0, 0.7)
c.save(); c.set_operator(cairo.OPERATOR_MULTIPLY); c.set_source_surface(R.PAPER, 0, 0); c.paint_with_alpha(0.5); c.restore()
R.vignette(c)
s.write_to_png("/home/claude/psalm2/psalm2_thumbnail.png")
