import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm11")
from sfxlib import load
S = load(11)
import render_p11 as P
pl, w = S.place, S
# hook: storm, ground shaking
pl(w.thunder(2.5), 0.05, 0.6)
pl(w.rain(P.B4 + 1.0), 0.0, 0.22)
pl(w.wind(P.B4, 450, 0.45), 0.0, 0.18)
pl(w.groan(1.8), P.T_SHAKING - 0.2, 0.3)
pl(w.whoosh(0.6, 400, 3000, 0.6), P.T_RUN1 - 0.1, 0.35)
pl(w.chime(494, 1.8), P.T_PSALM, 0.16)
# flee like a bird
pl(w.drone(P.B3 - P.B2), P.B2, 0.12)
for k in range(5):
    pl(w.whoosh(0.25, 1500, 4000, 0.4), P.T_BIRD - 0.2 + k * 0.28, 0.12, -0.3 + 0.15 * k)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.4)
# bows drawn; foundations fall
pl(w.groan(1.2), P.T_ARROWS - 0.1, 0.25, -0.5)
pl(w.groan(1.2), P.T_ARROWS - 0.05, 0.25, 0.5)
pl(w.hiss(0.6), P.T_STRING, 0.12)
pl(w.glass_crack(), P.T_FOUNDATIONS, 0.3)
pl(w.hit(50, 26, 1.6), P.T_DESTROYED - 0.02, 0.6)
pl(w.shatter(1.6), P.T_DESTROYED + 0.15, 0.25)
pl(w.thunder(2.0), P.T_DESTROYED + 0.1, 0.35)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.4)
# refuge; throne in heaven
pl(w.riser(1.2), P.T_LORD1 - 1.2, 0.3)
pl(w.hit(65, 32, 1.6), P.T_REFUGE1 - 0.02, 0.7)
pl(w.swell(2.0, 60), P.T_LORD1 - 0.2, 0.35)
pl(w.chime(659, 2.4), P.T_REFUGE1, 0.22)
pl(w.pad(P.B5 - P.T_TEMPLE, (220, 277.2, 329.6, 440)), P.T_TEMPLE - 0.3, 0.16)
pl(w.lyre_strum(), P.T_THRONE1, 0.28)
pl(w.groan(1.2), P.T_SHAKE - 0.1, 0.3)
pl(w.thump(0.45), P.T_THRONE2, 0.3)
pl(w.chime(784, 2.2), P.T_DOESNT, 0.18)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.4)
# eyes see
pl(w.pad(P.B6 - P.B5, (196, 246.9, 293.7, 392)), P.B5, 0.14)
pl(w.sparkle(1.2), P.T_EYES1, 0.2)
pl(w.ping(), P.T_SEE, 0.12)
pl(w.ping(), P.T_TEST, 0.12, 0.3)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.4)
# af'appav
pl(w.drone(P.B7 - P.B6), P.B6, 0.18)
pl(w.riser(1.4), P.T_AFAPPAV - 1.4, 0.3)
pl(w.hit(70, 34, 1.4), P.T_AFAPPAV - 0.02, 0.85)
pl(w.chime(440, 2.2), P.T_AFAPPAV, 0.25)
pl(w.whoosh(0.7, 2500, 600, 0.4), P.T_NARROWING, 0.2)
pl(w.chime(659, 2.4), P.T_NOTHING, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.4)
# close
pl(w.pad(P.DUR - P.B7, (261.6, 329.6, 392, 523.3)), P.B7, 0.16)
pl(w.wind(P.DUR - P.B7, 400, 0.2), P.B7, 0.1)
pl(w.thump(0.4), P.T_STOP, 0.3)
pl(w.whoosh(0.9, 300, 2500, 0.4), P.T_LOOK2 - 0.2, 0.25)
pl(w.sparkle(1.0), P.T_UP1, 0.18)
pl(w.hit(55, 32, 1.4), P.T_DONT - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_DONT, 0.22)
pl(w.hit(50, 30, 1.6), P.T_UP2 - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_UP2, 0.3)
pl(w.chime(587, 2.8), P.T_UP2 + 0.03, 0.18)
S.write("/home/claude/psalm11/sfx.wav")
