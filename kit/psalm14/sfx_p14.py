import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm14")
from sfxlib import load
S = load(14)
import render_p14 as P
pl, w = S.place, S
# hook: newsroom noise
pl(w.hit(55, 28, 1.2), 0.1, 0.35)
pl(w.crowd_roar(P.B2, 0.35), 0.0, 0.08)
for k in range(int(P.B2 * 2.2)):
    pl(w.ping(), k / 2.2, 0.06, (-0.4, 0.4)[k % 2])
pl(w.thump(0.4), P.T_WRONG - 0.03, 0.35)
pl(w.hit(60, 30, 1.0), P.T_PEOPLE1 - 0.02, 0.3)
# title, the fool
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.35)
pl(w.chime(392, 1.8), P.T_PSALM, 0.14)
pl(w.drone(P.B3 - P.B2), P.B2, 0.12)
pl(w.heartbeat(1.4, 70), P.T_HEART1 - 0.2, 0.25)
pl(w.hit(55, 28, 1.2), P.T_GOD1 - 0.02, 0.4)
# nabal
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.35)
pl(w.drone(P.B4 - P.B3), P.B3, 0.16)
pl(w.riser(1.3), P.T_NAVAL - 1.3, 0.3)
pl(w.hit(70, 34, 1.4), P.T_NAVAL - 0.02, 0.8)
pl(w.chime(440, 2.2), P.T_NAVAL, 0.25)
pl(w.rip(0.45), P.T_SMART, 0.2)
pl(w.thump(0.4), P.T_MORALLY - 0.03, 0.3)
# the beam from heaven; all turned aside
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.35)
pl(w.swell(2.0, 60), P.T_LOOKS - 0.4, 0.3)
pl(w.wind(P.B5 - P.B4, 350, 0.4), P.B4, 0.1)
pl(w.whoosh(1.2, 2500, 300, 0.4), P.T_TURNED - 0.2, 0.25)
pl(w.hit(60, 30, 1.2), P.T_EVEN - 0.02, 0.5)
# Romans 3, grace as a gift
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.35)
pl(w.page_ticks(0.5), P.B5 + 0.1, 0.2)
pl(w.chime(523, 2.2), P.T_GRACE1, 0.18)
pl(w.riser(1.2), P.T_GIFT - 1.2, 0.3)
pl(w.hit(65, 32, 1.6), P.T_GIFT - 0.02, 0.6)
pl(w.sparkle(1.2), P.T_GIFT, 0.25)
pl(w.chime(659, 2.6), P.T_JESUS, 0.22)
pl(w.pad(P.B6 - P.T_GIFT + 0.5, (261.6, 329.6, 392, 523.3)), P.T_GIFT, 0.12)
# close
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.35)
pl(w.pad(P.DUR - P.B6, (261.6, 329.6, 392, 523.3)), P.B6, 0.13)
pl(w.sparkle(1.0), P.T_SEARCH, 0.18)
pl(w.hit(55, 32, 1.4), P.T_START - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_MIRROR, 0.2)
pl(w.hit(50, 30, 1.6), P.T_NEWS2 - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_NEWS2, 0.3)
pl(w.chime(587, 2.8), P.T_NEWS2 + 0.03, 0.18)
S.write("/home/claude/psalm14/sfx.wav")
