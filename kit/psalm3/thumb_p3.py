import sys, cairo, math
sys.path.insert(0, "/home/claude/psalm1"); sys.path.insert(0, "/home/claude/psalm3")
import render as R
import render_p3 as P
W, H = 1080, 1920
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
R.bg(c, R.col("cream"))
g = cairo.RadialGradient(540, 900, 50, 540, 900, 900)
g.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.28); g.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
c.set_source(g); c.paint()
R.draw_text(c, "PSALM 3", R.F_SERIF, 230, "#3B2A1E", 540, 640)
c.set_source_rgba(*R.col("gold")); c.rectangle(440, 790, 200, 7); c.fill()
R.draw_text(c, "in a minute", R.F_SERIF_I, 120, "#A8741A", 540, 900)
g2 = cairo.RadialGradient(540, 1240, 40, 540, 1240, 260)
g2.add_color_stop_rgba(0, *R.col("gold2")[:3], 0.45); g2.add_color_stop_rgba(1, *R.col("gold2")[:3], 0)
c.set_source(g2); c.arc(540, 1240, 260, 0, 6.283); c.fill()
c.push_group()
c.set_source_rgba(*R.col("gold2")); c.arc(540, 1240, 95, 0, 6.283); c.fill()
c.set_operator(cairo.OPERATOR_CLEAR); c.arc(585, 1215, 82, 0, 6.283); c.fill()
c.pop_group_to_source(); c.paint()
for (x, y, r) in [(380, 1130, 14), (720, 1110, 11), (420, 1360, 10), (690, 1370, 13), (560, 1050, 9)]:
    c.set_source_rgba(*R.col("gold")); R.star_path(c, x, y, r, r * 0.35, 4); c.fill()
c.save(); c.set_operator(cairo.OPERATOR_MULTIPLY); c.set_source_surface(R.PAPER, 0, 0); c.paint_with_alpha(0.5); c.restore()
R.vignette(c)
s.write_to_png("/home/claude/psalm3/psalm3_thumbnail.png")
