"""Psalm 3 sound effects, built on the Psalm 1/2 synth library and timed to the voiceover."""
import sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm3")
lib = open("/home/claude/psalm1/sfx.py").read().split("# ---------------------------------------------------------------- the cue sheet")[0]
lib = lib.replace("DUR = 50.0", "DUR = __import__('json').load(open('/home/claude/psalm3/vomap.json'))['video_dur']")
lib = lib.replace("import render_v2 as V\n", "")
exec(lib)
p2 = open("/home/claude/psalm2/sfx_p2.py").read()
exec(p2[p2.index("def crowd_roar"):p2.index("pl = place")])
import render_p3 as P


def tick(hi=True):
    t = t_arr(0.05)
    f = 3200 if hi else 2400
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * 0.5)


def clock(d):
    out = np.zeros(int(SR * d))
    for k in range(int(d * 2)):
        tk = tick(k % 2 == 0)
        i0 = int(k * 0.5 * SR)
        out[i0:i0 + len(tk)] += tk[: len(out) - i0]
    return out


def crickets(d):
    t = t_arr(d)
    x = np.zeros(len(t))
    for f0, rate, ph in [(4300, 2.1, 0), (4700, 1.7, 1.3), (3900, 2.5, 2.1)]:
        chirp = (np.sin(2 * np.pi * 60 * t) > 0.2) * (np.sin(2 * np.pi * rate * t + ph) > 0.6)
        x += np.sin(2 * np.pi * f0 * t) * lp(chirp.astype(float), 300)
    return norm(x * env(len(t), 0.1, 1, 1))


def bird():
    t = t_arr(0.25)
    f = 2600 + 1400 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.25) ** 2)


def birds(d, n=8):
    out = np.zeros(int(SR * d))
    for k in range(n):
        b = bird()
        i0 = int(rng.uniform(0, d - 0.3) * SR)
        out[i0:i0 + len(b)] += b * rng.uniform(0.4, 1.0)
    return norm(out)


def crackle(d):
    t = t_arr(d)
    x = (rng.random(len(t)) < 0.0015) * rng.standard_normal(len(t))
    return norm(bp(x, 800, 5000) + 0.3 * lp(rng.standard_normal(len(t)), 300))


def whisper(d=0.9):
    t = t_arr(d)
    x = bp(rng.standard_normal(len(t)), 1500, 6000) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) ** 2
    return norm(x * env(len(t), 0.2, 1, 1.2))


def footsteps(d, rate=4.5):
    out = np.zeros(int(SR * d))
    for k in range(int(d * rate)):
        th = thump() * 0.6
        i0 = int(k / rate * SR)
        out[i0:i0 + len(th)] += th[: len(out) - i0]
    return out


pl = place
# hook: 3 a.m., worries popping
pl(hit(70, 34, 1.0), 0.1, 0.6)
pl(clock(P.B2 + 0.2), 0.0, 0.35)
for k in range(8):
    pl(plip(), 0.1 + k * 0.05, 0.3, (-1) ** k * 0.4)
pl(drone(3.0) * 0.6, 0.0, 0.2)
pl(thump(), P.T_SLEEP - 0.35, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.5)
# heading and the run
pl(page_ticks(0.5, 10), P.T_HEADING - 0.2, 0.35)
pl(chime(587, 1.6), P.T_DAVID1, 0.2)
pl(footsteps(P.B3 - P.T_RUNNING + 0.3), P.T_RUNNING - 0.3, 0.3)
pl(whoosh(0.8, 300, 3000, 0.5), P.T_ABSALOM1 - 0.3, 0.35, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.45)
# Israel turns, David flees
pl(crowd_roar(3.0, 0.9), P.T_TURNED - 0.6, 0.4)
pl(hit(65, 34, 0.9), P.T_TURNED - 0.02, 0.4)
pl(wind(4.0, 450, 0.3), P.T_FLED - 0.5, 0.25)
pl(pad(3.6, (196, 233.1, 293.7, 349.2)), P.T_FLED, 0.2)
pl(chime(523, 1.6), P.T_COVERED1 - 0.1, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.45)
# enemies at night
pl(crickets(P.B6 - P.B4), P.B4, 0.12)
pl(crackle(P.B6 - P.T_ENEMIES), P.T_ENEMIES - 0.3, 0.2)
pl(hit(70, 36, 1.0), P.T_ENEMIES - 0.02, 0.55)
for k in range(5):
    pl(whisper(1.0), P.T_WONT - 0.1 + k * 0.18, 0.25, (-1) ** k * 0.6)
# shield and the lifted head
pl(swell(1.8, 62), P.T_PRAYS - 0.2, 0.45)
pl(riser(0.8), P.T_SHIELD - 0.8, 0.3)
pl(hit(60, 32, 1.4), P.T_SHIELD - 0.02, 0.7)
pl(chime(659, 2.5), P.T_SHIELD, 0.3)
pl(sparkle(1.2), P.T_GLORY - 0.1, 0.2)
pl(chime(784, 2.0), P.T_LIFTS1, 0.3)
pl(thump(), P.T_LIFTS1 - 0.02, 0.4)
pl(chime(880, 2.0), P.T_LIFTS2, 0.25)
# sleep through the night, wake at dawn
pl(pad(P.T_WAKES - P.T_LIES + 0.5, (174.6, 220, 261.6, 349.2)), P.T_LIES - 0.2, 0.2)
pl(thump(), P.T_SLEEPS - 0.02, 0.35)
pl(birds(2.8, 9), P.T_WAKES - 0.1, 0.3)
pl(chime(659, 2.0), P.T_WAKES, 0.3)
pl(sparkle(1.0), P.T_HELD, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.45)
# nugget
pl(drone(P.B8 - P.B7), P.B7, 0.2)
pl(chime(440, 2.0), P.T_KEY + 0.15, 0.2)
pl(thump(), P.T_KEY + 0.55, 0.3)
pl(riser(1.4), P.T_YESHUAH - 1.4, 0.35)
pl(hit(70, 34, 1.4), P.T_YESHUAH - 0.02, 0.95)
pl(chime(523, 2.2), P.T_YESHUAH, 0.25)
pl(riser(0.8), P.T_YESHUA - 0.8, 0.25)
pl(hit(80, 38, 1.0), P.T_YESHUA - 0.02, 0.75)
pl(hit(55, 30, 1.8), P.T_JESUS - 0.02, 0.7)
pl(chime(523, 3.0), P.T_JESUS, 0.35)
pl(chime(784, 2.8), P.T_JESUS + 0.02, 0.2)
pl(whoosh(0.5, 400, 4500, 0.8), P.T_SAVES - 0.55, 0.35)
pl(chime(659, 2.0), P.T_SAVES, 0.25)
pl(whoosh(0.5, 400, 5000, 0.85), P.B8 - 0.35, 0.45)
# hand it to God
pl(clock(P.B9 - P.B8), P.B8, 0.15)
pl(whoosh(1.4, 300, 6000, 0.6), P.T_HAND - 0.1, 0.4)
pl(pad(3.4, (261.6, 329.6, 392, 523.3)), P.T_AWAKE - 0.6, 0.22)
# rest
pl(crickets(P.DUR - P.B9), P.B9, 0.1)
pl(chime(523, 3.0), P.T_SALVATION2, 0.25)
pl(hit(50, 30, 1.6), P.T_REST - 0.02, 0.45)
pl(chime(392, 3.0), P.T_REST, 0.3)
pl(chime(587, 2.8), P.T_REST + 0.03, 0.18)

mix = np.stack([L, Rt], axis=1)
fade = int(SR * 0.4)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix[: int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))[:, None]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 2.4) / np.tanh(2.4) * 10 ** (-3 / 20)
wavfile.write("/home/claude/psalm3/sfx.wav", SR, (mix * 32767).astype(np.int16))
print("sfx written", round(len(mix) / SR, 2), "s")
