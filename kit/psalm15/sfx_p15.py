import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm15")
from sfxlib import load
S = load(15)
import render_p15 as P
pl, w = S.place, S
# hook: a promise, and what it costs
pl(w.hit(55, 28, 1.2), 0.1, 0.35)
pl(w.wind(P.B2, 300, 0.3), 0.0, 0.08)
pl(w.ping(), 0.15, 0.12)
pl(w.thump(0.4), P.T_WORD1 - 0.03, 0.3)
for k in range(9):
    pl(w.clank(0.3), P.T_COSTS - 0.15 + k * 0.09 + 0.35, 0.06, (-0.3, 0.3)[k % 2])
pl(w.hit(60, 30, 1.0), P.T_COSTS - 0.02, 0.3)
# title, tent on the holy hill
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.35)
pl(w.chime(392, 1.8), P.T_PSALM, 0.14)
pl(w.wind(P.B3 - P.B2, 400, 0.4), P.B2, 0.1)
pl(w.swell(1.8, 60), P.T_TENT - 0.3, 0.25)
pl(w.chime(523, 2.0), P.T_HILL, 0.14)
# gur
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.35)
pl(w.drone(P.B4 - P.B3), P.B3, 0.16)
pl(w.riser(1.3), P.T_GOOR - 1.3, 0.3)
pl(w.hit(70, 34, 1.4), P.T_GOOR - 0.02, 0.8)
pl(w.chime(440, 2.2), P.T_GOOR, 0.25)
pl(w.sparkle(1.0), P.T_GUEST2 - 0.2, 0.15)
# the portrait
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.35)
pl(w.pad(P.B5 - P.B4, (220, 277.2, 329.6, 440)), P.B4, 0.1)
pl(w.thump(0.4), P.T_PORTRAIT - 0.03, 0.3)
for k, tk in enumerate((P.T_WALKS, P.T_TRUTH, P.T_SLANDER, P.T_KEEPS, P.T_BRIBE)):
    pl(w.ping(), tk - 0.2, 0.12, (-0.4, 0.4, -0.4, 0.4, 0)[k])
    pl(w.page_ticks(0.25), tk - 0.22, 0.12)
# never shaken
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.35)
pl(w.thunder(2.0), P.T_NEVER - 0.8, 0.35)
pl(w.shatter(1.2), P.T_NEVER - 0.4, 0.2)
pl(w.hit(65, 30, 1.6), P.T_SHAKEN - 0.02, 0.7)
pl(w.chime(659, 2.6), P.T_SHAKEN + 0.05, 0.22)
# close
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.35)
pl(w.pad(P.DUR - P.B6, (261.6, 329.6, 392, 523.3)), P.B6, 0.13)
pl(w.quill(0.6), P.T_BREAK + 0.1, 0.3)
pl(w.hit(55, 32, 1.4), P.T_KEEP3 - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_KEEP3, 0.2)
pl(w.hit(50, 30, 1.6), P.T_STAND - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_UNSHAKEN, 0.3)
pl(w.chime(587, 2.8), P.T_UNSHAKEN + 0.03, 0.18)
S.write("/home/claude/psalm15/sfx.wav")
