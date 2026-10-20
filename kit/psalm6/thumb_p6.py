import sys, cairo, math
sys.path.insert(0, "/home/claude/psalm1"); sys.path.insert(0, "/home/claude/psalm6")
import render as R
import render_p6 as P
W, H = 1080, 1920
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
R.bg(c, R.col("cream"))
g = cairo.RadialGradient(540, 900, 50, 540, 900, 900)
g.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.28); g.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
c.set_source(g); c.paint()
R.draw_text(c, "PSALM 6", R.F_SERIF, 230, "#3B2A1E", 540, 640)
c.set_source_rgba(*R.col("gold")); c.rectangle(440, 790, 200, 7); c.fill()
R.draw_text(c, "in a minute", R.F_SERIF_I, 120, "#A8741A", 540, 900)
# a single tear turning to gold, with a soft glow
gl = cairo.RadialGradient(540, 1330, 10, 540, 1330, 260)
gl.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.55); gl.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
c.set_source(gl); c.arc(540, 1330, 260, 0, 2 * math.pi); c.fill()
P.tear(c, 540, 1360, 95, R.col("gold2"))
c.save(); c.set_operator(cairo.OPERATOR_MULTIPLY); c.set_source_surface(R.PAPER, 0, 0); c.paint_with_alpha(0.5); c.restore()
R.vignette(c)
s.write_to_png("/home/claude/psalm6/psalm6_thumbnail.png")
