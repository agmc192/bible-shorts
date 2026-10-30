import sys
sys.path.insert(0, "/home/claude"); sys.path.insert(0, "/home/claude/psalm13")
from sfxlib import load
S = load(13)
import render_p13 as P
pl, w = S.place, S
# hook: night room, the same prayer again and again
pl(w.hit(55, 28, 1.2), 0.1, 0.35)
pl(w.wind(P.B3, 300, 0.3), 0.0, 0.08)
pl(w.lp(w.hiss(P.B5), 2500), 0.0, 0.05)          # sand running
for k in range(6):
    pl(w.plip(), 0.15 + k * 0.42, 0.1, (-0.3, 0.3)[k % 2])
pl(w.thump(0.4), P.T_TIRED - 0.03, 0.35)
# title and the four "how long"s
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.35)
pl(w.chime(392, 1.8), P.T_PSALM, 0.14)
for k, tk in enumerate((P.T_HOW1, P.T_HOW2, P.T_HOW3, P.T_HOW4)):
    pl(w.hit(60 - 3 * k, 30, 1.0), tk - 0.02, 0.28 + 0.05 * k)
    pl(w.ping(), tk + 0.05, 0.1)
pl(w.drone(P.B5 - P.B3), P.B3, 0.14)
pl(w.whoosh(1.2, 2500, 300, 0.4), P.T_HIDE1 - 0.2, 0.2)
pl(w.growl(1.6), P.T_ENEMY - 0.2, 0.18)
# look at me, answer, light up my eyes
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.35)
pl(w.sparkle(1.0), P.T_LIGHT, 0.2)
pl(w.chime(659, 1.6), P.T_EYES, 0.14)
# BUT: the turn
pl(w.riser(1.6), P.T_BUT1 - 1.6, 0.4)
pl(w.hit(70, 32, 1.8), P.T_BUT1 - 0.02, 0.9)
pl(w.swell(2.2, 60), P.T_BUT1 - 0.1, 0.4)
pl(w.chime(523, 2.6), P.T_BUT1 + 0.05, 0.25)
pl(w.pad(P.B6 - P.T_BUT1, (261.6, 329.6, 392, 523.3)), P.T_BUT1, 0.12)
pl(w.page_ticks(0.5), P.T_BUT2 - 0.3, 0.15)
# chesed
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.35)
pl(w.drone(P.B7 - P.B6), P.B6, 0.16)
pl(w.riser(1.3), P.T_KHESED - 1.3, 0.3)
pl(w.hit(70, 34, 1.4), P.T_KHESED - 0.02, 0.8)
pl(w.chime(440, 2.4), P.T_KHESED, 0.25)
pl(w.sparkle(1.2), P.T_LOVE4 - 0.3, 0.15)
# the question and the last word
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.35)
pl(w.thump(0.4), P.T_QUESTION - 0.02, 0.3)
pl(w.chime(587, 2.0), P.T_WORD2, 0.2)
# close: writing, end card
pl(w.whoosh(0.5, 400, 5000, 0.85), P.B8 - 0.35, 0.35)
pl(w.pad(P.DUR - P.B8, (261.6, 329.6, 392, 523.3)), P.B8, 0.13)
pl(w.quill(1.1), P.T_WRITE1, 0.3)
pl(w.quill(1.2), P.T_BUT3 - 0.5, 0.3)
pl(w.hit(55, 32, 1.4), P.T_KEEP - 0.02, 0.4)
pl(w.chime(523, 3.0), P.T_KEEP, 0.2)
pl(w.hit(50, 30, 1.6), P.T_BUT4 - 0.02, 0.45)
pl(w.chime(392, 3.0), P.T_BUT4, 0.3)
pl(w.chime(587, 2.8), P.T_BUT4 + 0.03, 0.18)
S.write("/home/claude/psalm13/sfx.wav")
