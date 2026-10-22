import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm7")
from sfxlib import load
S = load(7)
import render_p7 as P
pl, w = S.place, S
# hook: whispers of lies
pl(w.hit(65, 32, 1.0), 0.1, 0.6)
for k in range(6):
    pl(w.whoosh(0.35, 500, 3500, 0.5), 0.1 + k * 0.18, 0.18, (-1) ** k * 0.6)
pl(w.crowd_roar(P.B2, 0.3), 0.2, 0.12)
pl(w.thump(), P.T_LIES - 0.03, 0.5)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.45)
# title: stone and scroll
pl(w.thump(0.4), P.B2 + 0.05, 0.4)
pl(w.chime(587, 1.6), P.T_PSALM, 0.18)
pl(w.page_ticks(0.5, 10), P.T_WORDS - 0.2, 0.3)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.45)
# running to refuge
for k in range(int((P.T_REFUGE - P.B3) * 4)):
    pl(w.thump(0.2) * 0.5, P.B3 + 0.1 + k * 0.25, 0.25, -0.3 + k * 0.05)
pl(w.swell(1.6, 70), P.T_REFUGE - 0.4, 0.4)
pl(w.chime(659, 2.0), P.T_REFUGE, 0.22)
pl(w.drone(P.B4 - P.T_EVEN), P.T_EVEN, 0.15)
pl(w.growl(1.4) * 0.5, P.T_ENEMY - 0.2, 0.18, -0.6)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.45)
# the judge
pl(w.pad(P.B5 - P.B4, (196, 246.9, 293.7, 392)), P.B4, 0.2)
pl(w.whoosh(0.8, 300, 3000, 0.5), P.T_CASE1 - 0.3, 0.3)
pl(w.clank(0.8), P.T_RIGHTEOUS, 0.25)
pl(w.hit(60, 30, 1.2), P.T_JUDGE1 - 0.02, 0.6)
pl(w.chime(784, 2.0), P.T_JUDGE1, 0.22)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.45)
# the pit
pl(w.riser(0.8), P.T_TWIST - 0.8, 0.3)
pl(w.hit(70, 34, 0.9), P.T_TWIST - 0.02, 0.5)
for k in range(int((P.T_FALLS - P.T_DIGS) / 0.45) + 1):
    pl(w.thump(0.25), P.T_DIGS + k * 0.45, 0.35)
    pl(w.hiss(0.3) * 0.5, P.T_DIGS + k * 0.45 + 0.05, 0.2, 0.4)
pl(w.whoosh(0.4, 2000, 300, 0.4), P.T_FALLS - 0.05, 0.4)
pl(w.hit(55, 28, 1.0), P.T_FALLS + 0.25, 0.7)
pl(w.whoosh(0.7, 400, 2500, 0.5), P.T_TROUBLE - 0.1, 0.3, 0.5)
pl(w.thump(0.3), P.T_HEAD + 0.05, 0.6)
pl(w.ping(), P.T_HEAD + 0.1, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.45)
# nugget
pl(w.drone(P.B7 - P.B6), P.B6, 0.2)
pl(w.ping(), P.T_NINE, 0.2)
pl(w.riser(1.4), P.T_KLAYOT - 1.4, 0.35)
pl(w.hit(70, 34, 1.4), P.T_KLAYOT - 0.02, 0.9)
pl(w.chime(440, 2.2), P.T_KLAYOT, 0.25)
pl(w.swell(1.4, 60), P.T_SEES - 0.2, 0.35)
for k in range(4):
    pl(w.thump(0.2) * 0.6, P.T_SEES + k * 0.25, 0.25)
pl(w.chime(523, 2.4), P.T_DOWN, 0.25)
pl(w.sparkle(1.0), P.T_DOWN + 0.05, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.45)
# close
pl(w.wind(P.DUR - P.B7, 500, 0.3), P.B7, 0.12)
pl(w.pad(P.DUR - P.B7, (261.6, 329.6, 392, 523.3)), P.B7, 0.18)
pl(w.clank(0.6), P.T_DIG2 + 0.25, 0.3, -0.5)
pl(w.whoosh(1.0, 300, 4000, 0.5), P.T_CASE2 - 0.1, 0.3)
pl(w.hit(55, 32, 1.4), P.T_LEAVE - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_LEAVE, 0.25)
pl(w.hit(50, 30, 1.6), P.T_PEACE - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_PEACE, 0.3)
pl(w.chime(587, 2.8), P.T_PEACE + 0.03, 0.18)
S.write("/home/claude/psalm7/sfx.wav")
