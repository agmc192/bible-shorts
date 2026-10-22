import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm9")
from sfxlib import load
S = load(9)
import render_p9 as P
pl, w = S.place, S
# hook: a hurrying crowd streams past one still figure
pl(w.hit(55, 28, 1.4), 0.1, 0.5)
pl(w.whoosh(1.2, 2500, 300, 0.4), 0.1, 0.3)
pl(w.crowd_roar(P.B2 + 0.3, 0.35), 0.0, 0.12)
pl(w.wind(P.B2, 500, 0.3), 0.0, 0.12)
pl(w.thump(0.4), P.T_ANYONE - 0.03, 0.35)
pl(w.chime(587, 1.8), P.T_PSALM, 0.18)
# title, thanks
pl(w.pad(P.B3 - P.B2, (196, 246.9, 293.7, 392)), P.B2, 0.16)
pl(w.lyre_strum(), P.T_THANKS, 0.3)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.4)
# deeds, throne, judgment
pl(w.sparkle(1.2), P.T_WONDERFUL, 0.22)
pl(w.riser(1.0), P.T_ENTHRONED - 1.0, 0.25)
pl(w.hit(60, 30, 1.4), P.T_ENTHRONED - 0.02, 0.55)
pl(w.chime(659, 2.2), P.T_FOREVER, 0.18)
pl(w.thump(0.45), P.T_JUDGES, 0.35)
pl(w.drone(P.B4 - P.T_FORGET), P.T_FORGET, 0.12)
pl(w.chime(523, 2.2), P.T_CRY, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.4)
# trust; the forgotten figure regains colour
pl(w.pad(P.B5 - P.B4, (220, 277.2, 329.6, 440)), P.B4, 0.16)
pl(w.ping(), P.T_NAME, 0.12)
pl(w.ping(), P.T_TRUST, 0.12, 0.3)
pl(w.swell(1.6, 60), P.T_ALWAYS - 0.3, 0.35)
pl(w.sparkle(1.4), P.T_FORGOTTEN2, 0.25)
pl(w.chime(784, 2.4), P.T_FORGOTTEN2 + 0.2, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.4)
# stronghold / misgav: arrows fall short
pl(w.wind(P.B6 - P.B5, 700, 0.4), P.B5, 0.18)
pl(w.hit(60, 30, 1.2), P.T_STRONGHOLD - 0.02, 0.5)
pl(w.riser(1.4), P.T_MISGAV - 1.4, 0.3)
pl(w.hit(70, 34, 1.4), P.T_MISGAV - 0.02, 0.85)
pl(w.chime(440, 2.2), P.T_MISGAV, 0.25)
for k, dt in enumerate((0.0, 0.25, 0.5)):
    pl(w.whoosh(0.35, 3000, 900, 0.3), P.T_REACH - 0.6 + dt, 0.2, -0.4 + 0.4 * k)
    pl(w.thump(0.2), P.T_REACH - 0.25 + dt, 0.15, -0.4 + 0.4 * k)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.4)
# close
pl(w.pad(P.DUR - P.B6, (261.6, 329.6, 392, 523.3)), P.B6, 0.16)
pl(w.page_ticks(0.9, 14), P.T_WRITE, 0.3)
pl(w.sparkle(1.0), P.T_THANK, 0.2)
pl(w.hit(55, 32, 1.4), P.T_REMEMBER - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_REMEMBER, 0.22)
pl(w.hit(50, 30, 1.6), P.T_REMEMBERS - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_REMEMBERS, 0.3)
pl(w.chime(587, 2.8), P.T_REMEMBERS + 0.03, 0.18)
S.write("/home/claude/psalm9/sfx.wav")
