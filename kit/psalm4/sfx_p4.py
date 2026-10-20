"""Psalm 3 sound effects, built on the Psalm 1/2 synth library and timed to the voiceover."""
import sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm4")
lib = open("/home/claude/psalm1/sfx.py").read().split("# ---------------------------------------------------------------- the cue sheet")[0]
lib = lib.replace("DUR = 50.0", "DUR = __import__('json').load(open('/home/claude/psalm4/vomap.json'))['video_dur']")
lib = lib.replace("import render_v2 as V\n", "")
exec(lib)
p2 = open("/home/claude/psalm2/sfx_p2.py").read()
exec(p2[p2.index("def crowd_roar"):p2.index("pl = place")])
import render_p4 as P


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

def boil(d):
    t = t_arr(d)
    x = bp(rng.standard_normal(len(t)), 400, 3000) * 0.5
    for _ in range(int(40 * d)):
        n = int(SR * 0.04); i0 = int(rng.uniform(0, d - 0.05) * SR)
        tt = np.arange(n) / SR
        x[i0:i0 + n] += np.sin(2 * np.pi * rng.uniform(300, 900) * (1 + tt * 10) * tt) * np.exp(-tt * 80)
    return norm(x * env(len(t), 0.3, 1, 1))

def whistle(d):
    t = t_arr(d)
    f = 1800 + 400 * (t / d)
    return norm((np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * bp(rng.standard_normal(len(t)), 1500, 3000)) * env(len(t), 0.5, 1, 1.2))

# hook: thoughts on repeat
pl(hit(70, 34, 1.0), 0.1, 0.6)
pl(clock(P.B2 + 0.2), 0.0, 0.3)
for k in range(6):
    pl(whoosh(0.35, 400, 3000, 0.6), 0.2 + k * 0.62, 0.15, (-1) ** k * 0.5)
pl(thump(), P.T_ARGUMENT - 0.05, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.5)
# David, honor to shame, lies
pl(chime(587, 1.6), P.T_PSALM, 0.2)
pl(hit(60, 32, 0.9), P.T_SHAME - 0.02, 0.45)
for k in range(4):
    pl(whisper(0.8), P.T_CHASING - 0.2 + k * 0.15, 0.22, (-1) ** k * 0.6)
pl(page_ticks(0.4, 10), P.T_WRITES - 0.2, 0.3)
pl(whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.45)
# the kettle
pl(boil(P.T_STILL - P.T_ANGRY1 + 0.4), P.T_ANGRY1 - 0.4, 0.4)
pl(whistle(P.T_SIN1 - P.T_ANGRY1 + 0.3), P.T_ANGRY1, 0.18)
pl(hit(75, 36, 0.8), P.T_ANGRY1 - 0.02, 0.5)
pl(thump(), P.T_SIN1 - 0.02, 0.35)
pl(chime(698, 1.6), P.T_HEART, 0.2)
pl(chime(523, 2.4), P.T_STILL, 0.3)
pl(whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.45)
# nugget
pl(drone(P.B5 - P.B4), P.B4, 0.2)
pl(riser(1.4), P.T_RIGZU - 1.4, 0.35)
pl(hit(70, 34, 1.4), P.T_RIGZU - 0.02, 0.95)
pl(chime(440, 2.2), P.T_RIGZU, 0.25)
pl(crackle(1.0), P.T_TREMBLE - 0.1, 0.2)
pl(thunder(1.6) * 0.7, P.T_SHAKE - 0.05, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.45)
# Paul and the sunset
pl(page_ticks(0.3, 8), P.B5 + 0.1, 0.25, -0.4)
pl(page_ticks(0.3, 8), P.T_PAUL - 0.3, 0.25, 0.4)
pl(sparkle(0.8), P.T_LINE - 0.1, 0.2)
pl(whoosh(1.0, 300, 3000, 0.5), P.T_SUN1 - 0.7, 0.35)
pl(pad(P.B6 - P.T_SUN1 + 0.5, (196, 246.9, 293.7, 392)), P.T_SUN1 - 0.4, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.45)
# feel vs feed
pl(crackle(1.2), P.T_FEELING2 - 0.2, 0.2, -0.5)
pl(crackle(P.B7 - P.T_FEEDING), P.T_FEEDING - 0.1, 0.45, 0.5)
pl(hit(70, 36, 0.8), P.T_FEEDING - 0.02, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.45)
# trust, joy, peace
pl(swell(1.8, 65), P.T_TRUST - 0.3, 0.4)
pl(wind(2.4, 600, 0.3), P.T_FILLS - 0.2, 0.18)
pl(hit(55, 30, 1.4), P.T_JOY - 0.02, 0.55)
pl(chime(659, 2.5), P.T_JOY, 0.3)
pl(sparkle(1.2), P.T_JOY + 0.1, 0.2)
pl(crickets(P.B8 - P.T_PEACE + 0.4), P.T_PEACE - 0.4, 0.12)
pl(pad(P.B8 - P.T_PEACE + 0.4, (174.6, 220, 261.6, 349.2)), P.T_PEACE - 0.4, 0.2)
pl(chime(523, 2.2), P.T_PEACE, 0.25)
pl(whoosh(0.5, 400, 5000, 0.85), P.B8 - 0.35, 0.45)
# close
pl(pad(P.DUR - P.B8, (261.6, 329.6, 392, 523.3)), P.B8, 0.18)
pl(whoosh(1.4, 300, 6000, 0.6), P.T_HAND - 0.1, 0.4)
pl(chime(784, 2.0), P.T_GOD, 0.25)
pl(hit(55, 32, 1.4), P.T_FEEL - 0.02, 0.4)
pl(chime(523, 3.0), P.T_FEEL, 0.25)
pl(hit(50, 30, 1.6), P.T_FEED - 0.02, 0.5)
pl(chime(392, 3.0), P.T_FEED, 0.3)
pl(chime(587, 2.8), P.T_FEED + 0.03, 0.18)
mix = np.stack([L, Rt], axis=1)
fade = int(SR * 0.4)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix[: int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))[:, None]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 2.4) / np.tanh(2.4) * 10 ** (-3 / 20)
wavfile.write("/home/claude/psalm4/sfx.wav", SR, (mix * 32767).astype(np.int16))
print("sfx written", round(len(mix) / SR, 2), "s")
