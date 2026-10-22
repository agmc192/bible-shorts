import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm10")
from sfxlib import load
S = load(10)
import render_p10 as P
pl, w = S.place, S
# hook: the ground cracks under an eclipsed sun
pl(w.hit(50, 26, 1.6), 0.1, 0.55)
pl(w.glass_crack(), 0.1, 0.25)
pl(w.wind(P.B2 + 0.3, 350, 0.45), 0.0, 0.2)
pl(w.groan(1.6), P.T_FALLING - 0.2, 0.25)
pl(w.thump(0.4), P.T_APART, 0.35)
pl(w.chime(494, 1.8), P.T_PSALM, 0.16)
# the question
pl(w.drone(P.B3 - P.B2), P.B2, 0.15)
pl(w.hit(60, 30, 1.0), P.T_WHY2 - 0.02, 0.3)
pl(w.chime(440, 2.0), P.T_HIDE, 0.16)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.4)
# the hunt, the lion, the boast
pl(w.wind(P.B4 - P.B3, 500, 0.35), P.B3, 0.15)
pl(w.heartbeat(P.B4 - P.T_HUNT, 70), P.T_HUNT, 0.25)
pl(w.growl(2.2), P.T_LION - 0.1, 0.35)
pl(w.hit(55, 28, 1.2), P.T_AMBUSH - 0.02, 0.45)
pl(w.hiss(1.0), P.T_FORGOTTEN - 0.2, 0.12)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.4)
# you do see: eclipse clears
pl(w.riser(1.2), P.T_DO - 1.2, 0.3)
pl(w.hit(65, 32, 1.6), P.T_SEE2 - 0.02, 0.7)
pl(w.swell(2.0, 60), P.T_DO - 0.1, 0.4)
pl(w.chime(659, 2.4), P.T_SEE2, 0.22)
pl(w.pad(P.B5 - P.T_SEE2, (220, 277.2, 329.6, 440)), P.T_SEE2, 0.15)
pl(w.sparkle(1.2), P.T_NOTE, 0.2)
pl(w.ping(), P.T_HEARS, 0.12)
pl(w.lyre_strum(), P.T_JUSTICE, 0.28)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.4)
# ra'itah
pl(w.drone(P.B6 - P.B5), P.B5, 0.18)
pl(w.riser(1.4), P.T_RAITAH - 1.4, 0.3)
pl(w.hit(70, 34, 1.4), P.T_RAITAH - 0.02, 0.85)
pl(w.chime(440, 2.2), P.T_RAITAH, 0.25)
pl(w.rip(0.45), P.T_ALREADY - 0.3, 0.25)
pl(w.chime(659, 2.4), P.T_ALREADY, 0.22)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.4)
# close
pl(w.pad(P.DUR - P.B6, (261.6, 329.6, 392, 523.3)), P.B6, 0.16)
pl(w.wind(P.DUR - P.B6, 400, 0.2), P.B6, 0.1)
pl(w.whoosh(0.9, 300, 2500, 0.4), P.T_HONEST - 0.2, 0.25)
pl(w.hit(55, 32, 1.4), P.T_ASK - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_ASK, 0.22)
pl(w.hit(50, 30, 1.6), P.T_SEES - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_SEES, 0.3)
pl(w.chime(587, 2.8), P.T_SEES + 0.03, 0.18)
S.write("/home/claude/psalm10/sfx.wav")
