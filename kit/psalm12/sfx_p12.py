import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm12")
from sfxlib import load
S = load(12)
import render_p12 as P
pl, w = S.place, S
# hook: a city of chatter, bubbles popping
pl(w.hit(55, 28, 1.2), 0.1, 0.4)
pl(w.crowd_roar(P.B2 + 0.3, 0.3), 0.0, 0.12)
for k, (x, y, s, ph, tl) in enumerate(P.BUBBLES):
    pl(w.ping(), ph * 1.5, 0.05, (x - 540) / 540)
    pl(w.plip(), 2.2 + ph * 1.6, 0.12, (x - 540) / 540)
pl(w.thump(0.4), P.T_TRUST1 - 0.03, 0.35)
pl(w.chime(494, 1.8), P.T_PSALM, 0.16)
# the faithful vanish
pl(w.drone(P.B3 - P.B2), P.B2, 0.14)
pl(w.hit(60, 30, 1.0), P.T_SAVE - 0.02, 0.3)
pl(w.whoosh(1.4, 3000, 300, 0.3), P.T_FAITHFUL - 0.1, 0.25)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.4)
# masks, flattery, the boast
pl(w.crowd_roar(P.B4 - P.B3, 0.25), P.B3, 0.1)
for k in range(4):
    pl(w.ping(), P.T_LIES - 0.2 + k * 0.15, 0.08, -0.6 + 0.4 * k)
for k in range(3):
    pl(w.sparkle(0.5), P.T_FLATTER + k * 0.3, 0.1, (-0.4, 0.4, 0)[k])
pl(w.hit(55, 28, 1.2), P.T_MASTER - 0.02, 0.45)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.4)
# God arises
pl(w.drone(P.T_ARISE - P.B4), P.B4, 0.15)
pl(w.groan(1.4), P.T_GROAN - 0.1, 0.2)
pl(w.riser(1.4), P.T_ARISE - 1.4, 0.35)
pl(w.hit(65, 32, 1.8), P.T_ARISE - 0.02, 0.8)
pl(w.swell(2.0, 60), P.T_ARISE - 0.2, 0.4)
pl(w.chime(659, 2.4), P.T_ARISE + 0.1, 0.22)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.4)
# furnace, silver
pl(w.hiss(P.B6 - P.B5), P.B5, 0.15)
pl(w.wind(P.B6 - P.B5, 250, 0.5), P.B5, 0.12)
pl(w.chime(880, 2.2), P.T_PURE, 0.2)
for k in range(7):
    tk = P.T_REFINED + k * (P.T_SEVEN + 0.9 - P.T_REFINED) / 7
    pl(w.clank(0.5), tk, 0.12)
    pl(w.ping(), tk + 0.02, 0.08)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.4)
# be-lev va-lev
pl(w.drone(P.B7 - P.B6), P.B6, 0.18)
pl(w.heartbeat(P.B7 - P.T_DOUBLE, 64), P.T_DOUBLE, 0.25)
pl(w.riser(1.4), P.T_BELEV - 1.4, 0.3)
pl(w.hit(70, 34, 1.4), P.T_BELEV - 0.02, 0.85)
pl(w.chime(440, 2.2), P.T_BELEV, 0.25)
pl(w.rip(0.45), P.T_HEART4, 0.2)
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.4)
# close
pl(w.pad(P.DUR - P.B7, (261.6, 329.6, 392, 523.3)), P.B7, 0.16)
pl(w.sparkle(1.0), P.T_GUARD, 0.18)
pl(w.hit(55, 32, 1.4), P.T_HEART5 - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_HEART5, 0.22)
pl(w.hit(50, 30, 1.6), P.T_WORD - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_WORD, 0.3)
pl(w.chime(587, 2.8), P.T_WORD + 0.03, 0.18)
S.write("/home/claude/psalm12/sfx.wav")
