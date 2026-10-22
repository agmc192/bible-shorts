import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm8")
from sfxlib import load
S = load(8)
import render_p8 as P
pl, w = S.place, S
# hook: stars burst on, wide night
pl(w.hit(55, 28, 1.6), 0.1, 0.55)
pl(w.sparkle(1.6), 0.1, 0.35)
pl(w.wind(P.B3, 400, 0.25), 0.0, 0.15)
pl(w.whoosh(2.4, 2000, 300, 0.4), 0.2, 0.3)
pl(w.thump(), P.T_TINY - 0.03, 0.4)
pl(w.chime(659, 1.8), P.T_PSALM, 0.18)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.4)
# moon and stars drawn
pl(w.pad(P.B5 - P.B3, (174.6, 220, 261.6, 349.2)), P.B3, 0.18)
for k in range(12):
    pl(w.ping(), P.T_STARS1 + k * (P.T_FINGERS + 0.5 - P.T_STARS1) / 12, 0.08, -0.6 + k * 0.1)
pl(w.chime(784, 2.0), P.T_FINGERS, 0.18)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.4)
# what is man
pl(w.drone(P.B5 - P.B4), P.B4, 0.15)
pl(w.hit(60, 30, 1.0), P.T_MAN - 0.02, 0.35)
pl(w.chime(523, 2.2), P.T_MINDFUL1, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.4)
# crowned; the world in their care
pl(w.riser(1.2), P.T_CROWNED1 - 1.2, 0.3)
pl(w.hit(60, 30, 1.4), P.T_CROWNED1 - 0.02, 0.6)
pl(w.lyre_strum(), P.T_CROWNED1, 0.3)
pl(w.sparkle(1.0), P.T_GLORY1, 0.2)
pl(w.wind(P.B6 - P.T_CHARGE, 600, 0.3), P.T_CHARGE, 0.1)
pl(w.thump(0.3), P.T_SHEEP, 0.25)
pl(w.thump(0.4), P.T_OXEN, 0.3)
pl(w.water(P.B6 - P.T_FISH + 0.2, 300, 2000, 20), P.T_FISH - 0.2, 0.25)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.4)
# zakar
pl(w.drone(P.B7 - P.B6), P.B6, 0.2)
pl(w.riser(1.4), P.T_ZAKAR - 1.4, 0.35)
pl(w.hit(70, 34, 1.4), P.T_ZAKAR - 0.02, 0.9)
pl(w.chime(440, 2.2), P.T_ZAKAR, 0.25)
pl(w.sparkle(1.4), P.T_SET, 0.25)
pl(w.chime(659, 2.4), P.T_MIND, 0.22)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.4)
# Hebrews 2
pl(w.pad(P.B8 - P.B7, (196, 246.9, 293.7, 392)), P.B7, 0.18)
pl(w.whoosh(1.4, 3000, 400, 0.5), P.T_LOWER - 0.3, 0.3)
pl(w.thump(0.4), P.T_SUFFERED, 0.35)
pl(w.swell(1.6, 60), P.T_CROWNED2 - 0.3, 0.4)
pl(w.chime(784, 2.4), P.T_GLORY2, 0.25)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B8 - 0.35, 0.4)
# close
pl(w.wind(P.DUR - P.B8, 400, 0.25), P.B8, 0.12)
pl(w.pad(P.DUR - P.B8, (261.6, 329.6, 392, 523.3)), P.B8, 0.18)
pl(w.whoosh(0.8, 300, 2500, 0.4), P.T_OUTSIDE - 0.2, 0.25)
pl(w.sparkle(1.2), P.T_GRATEFUL - 0.2, 0.2)
pl(w.hit(55, 32, 1.4), P.T_SMALL2 - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_SMALL2, 0.25)
pl(w.hit(50, 30, 1.6), P.T_REMEMBERED - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_REMEMBERED, 0.3)
pl(w.chime(587, 2.8), P.T_REMEMBERED + 0.03, 0.18)
S.write("/home/claude/psalm8/sfx.wav")
