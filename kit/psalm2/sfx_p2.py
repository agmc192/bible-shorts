"""Psalm 2 sound effects, built on the Psalm 1 synth library and timed to the voiceover."""
import sys, json
import numpy as np
from scipy import signal
from scipy.io import wavfile
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm2")
lib = open("/home/claude/psalm1/sfx.py").read().split("# ---------------------------------------------------------------- the cue sheet")[0]
lib = lib.replace("DUR = 50.0", "DUR = __import__('json').load(open('/home/claude/psalm2/vomap.json'))['video_dur']")
exec(lib)
import render_p2 as P


def crowd_roar(d, intensity=1.0):
    t = t_arr(d)
    x = bp(rng.standard_normal(len(t)), 220, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 2.3 * t))
    for _ in range(int(14 * d)):
        n = int(SR * rng.uniform(0.25, 0.6))
        i0 = int(rng.uniform(0, d - 0.6) * SR)
        f = rng.uniform(380, 900)
        burst = bp(rng.standard_normal(n), f * 0.7, f * 1.6) * np.hanning(n)
        x[i0:i0 + n] += burst * rng.uniform(0.4, 1.0)
    x += 0.5 * lp(rng.standard_normal(len(t)), 140)
    return norm(x * env(len(t), 0.12, 1, 1.0) * intensity)


def clank(d=0.9):
    t = t_arr(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dec) for f, a, dec in
            [(1180, 1, 9), (2630, 0.7, 12), (3970, 0.5, 15), (5520, 0.35, 20), (760, 0.6, 7)])
    x += hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 60) * 0.8
    return norm(x)


def pluck(f, d=1.6):
    n = int(SR * d)
    p = int(SR / f)
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return norm(out)


def lyre_strum(notes=(293.7, 370.0, 440.0, 587.3), gap=0.07):
    out = np.zeros(int(SR * 2.2))
    for k, f in enumerate(notes):
        p = pluck(f)
        i0 = int(k * gap * SR)
        out[i0:i0 + len(p)] += p[: len(out) - i0]
    return norm(out)


def ping():
    t = t_arr(0.35)
    x = (np.sin(2 * np.pi * 1318 * t) + 0.6 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 14)
    return norm(x)


def pad(d, freqs=(220, 277.2, 329.6, 440)):
    t = t_arr(d)
    x = sum(np.sin(2 * np.pi * f * t + i) * (1 + 0.3 * np.sin(2 * np.pi * 0.3 * t + i)) for i, f in enumerate(freqs))
    return norm(lp(x, 2000) * env(len(t), 0.25, 1, 1.2))


def swell(d=1.6, f0=70):
    t = t_arr(d)
    x = np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 1.5 * t) + 0.3 * np.sin(2 * np.pi * f0 * 2 * t)
    return norm(x * env(len(t), 0.45, 1, 1.4))


pl = place
# hook: the world lurches into a spin
pl(hit(85, 36, 1.3), 0.1, 0.9)
pl(whoosh(3.2, 150, 2600, 0.85), 0.15, 0.5)
pl(riser(3.0), 0.5, 0.3)
pl(wind(3.4, 700, 1.2), 0.3, 0.2, 0.3)
pl(thump(), P.T_OUT - 0.02, 0.45)
pl(thump(), P.T_CONTROL - 0.02, 0.6)
pl(whoosh(0.5, 500, 5000, 0.85), P.B2 - 0.4, 0.55)
# the nations rage
pl(wind(8.0, 420, 0.3), P.B2, 0.18)
pl(crowd_roar(4.6, 1.0), P.T_RAGING - 0.6, 0.5)
pl(hit(70, 36, 0.9), P.T_RAGING - 0.02, 0.6)
pl(crowd_roar(3.6, 0.6), P.T_RULERS + 0.6, 0.18)
pl(clank(0.5), P.T_RULERS + 0.4, 0.25, 0.3)
pl(clank(1.0), P.T_BREAK - 0.01, 0.75)
pl(hit(90, 40, 0.8), P.T_BREAK - 0.01, 0.55)
pl(chime(523, 2.0), P.T_KING1 - 0.1, 0.25)
pl(whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.5, -0.4)
# David
pl(lyre_strum(), P.T_DAVID - 0.3, 0.55)
pl(thump(), P.T_DAVID + 0.2, 0.25)
# heaven
pl(whoosh(1.4, 300, 5000, 0.5), P.T_HEAVEN - 0.3, 0.45)
pl(pad(7.6), P.T_HEAVEN, 0.22)
pl(sparkle(1.2), P.T_WORRIED - 0.2, 0.15)
for k in range(3):
    pl(chime(880 * (1 + 0.12 * k), 1.0), P.T_LAUGHS + k * 0.22, 0.16)
pl(swell(1.8, 65), P.T_SPEAKS - 0.2, 0.45)
pl(whoosh(0.9, 3000, 300, 0.3), P.T_KING2 - 0.9, 0.35)
pl(hit(60, 32, 1.4), P.T_KING2 - 0.02, 0.75)
pl(chime(659, 2.5), P.T_KING2, 0.3)
pl(sparkle(1.2), P.T_HILL - 0.1, 0.2)
# nugget
pl(drone(15.0), P.B5, 0.2)
pl(plip(), P.T_ANOINTED + 0.02, 0.55)
pl(chime(784, 1.6), P.T_ANOINTED + 0.05, 0.25)
pl(riser(1.4), P.T_MASHIACH - 1.4, 0.35)
pl(hit(70, 34, 1.4), P.T_MASHIACH - 0.02, 0.95)
pl(chime(440, 2.5), P.T_MASHIACH, 0.25)
pl(thump(), P.T_MESSIAH - 0.02, 0.5)
pl(riser(0.9), P.T_CHRISTOS - 0.9, 0.25)
pl(hit(80, 38, 1.0), P.T_CHRISTOS - 0.02, 0.75)
pl(thump(), P.T_CHRIST - 0.02, 0.6)
pl(chime(988, 1.5), P.T_CHRIST, 0.25)
pl(whoosh(0.5, 400, 4500, 0.8), P.T_SON - 2.5, 0.35)
pl(swell(2.2, 82), P.T_SON - 1.2, 0.35)
pl(chime(587, 2.0), P.T_SON, 0.25)
pl(thump(), P.T_JESUS - 2.25, 0.3)
pl(thump(), P.T_JESUS - 1.95, 0.3)
pl(hit(55, 30, 1.8), P.T_JESUS - 0.02, 0.7)
pl(chime(523, 3.0), P.T_JESUS, 0.35)
pl(chime(784, 2.8), P.T_JESUS + 0.02, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.5)
# chaos is real, but not in charge
pl(crowd_roar(2.6, 1.0), P.B6 + 0.1, 0.35)
pl(thunder(2.6), P.T_CHAOS - 0.1, 0.55)
pl(whoosh(1.4, 2500, 250, 0.4), P.T_CHARGE - 1.0, 0.45)
pl(hit(60, 32, 1.0), P.T_CHARGE + 0.1, 0.45)
pl(chime(659, 2.0), P.T_CHARGE + 0.15, 0.2)
# Psalm 1 and Psalm 2 bookend
pl(whoosh(0.5, 400, 5000, 0.85), P.T_BEGAN - 2.75, 0.5, -0.5)
pl(page_ticks(0.3, 8), P.T_BEGAN - 2.3, 0.3, -0.4)
pl(page_ticks(0.3, 8), P.T_BEGAN - 1.8, 0.3, 0.4)
pl(sparkle(0.8), P.T_BEGAN - 0.5, 0.18)
pl(thump(), P.T_BLESSED - 0.02, 0.6)
pl(hit(65, 34, 1.2), P.T_BLESSED - 0.02, 0.5)
pl(chime(698, 2.0), P.T_BLESSED, 0.25)
# refuge
pl(rain(3.6), P.T_BLESSED + 0.5, 0.3)
pl(pad(3.4, (196, 246.9, 293.7, 392)), P.T_BLESSED + 0.8, 0.25)
pl(chime(587, 2.2), P.T_REFUGE, 0.25)
# the news feels loud
for k in range(14):
    pl(ping(), P.B7 + 0.1 + k * 0.11, 0.22, (-1) ** k * 0.5)
pl(hiss(1.6), P.T_NEWS - 0.6, 0.1)
pl(whoosh(1.0, 300, 6000, 0.6), P.T_TAKE - 0.1, 0.5)
pl(pad(2.0, (261.6, 329.6, 392, 523.3)), P.T_TAKE + 0.2, 0.22)
pl(chime(784, 2.0), P.T_KING4, 0.25)
# the world rages, Jesus reigns
pl(whoosh(0.5, 400, 5000, 0.85), P.B8 - 0.35, 0.45)
pl(thunder(1.6) * 0.6, P.T_RAGES - 0.4, 0.35)
pl(hit(55, 32, 1.6), P.T_REIGNS - 0.02, 0.6)
pl(chime(523, 3.0), P.T_REIGNS, 0.35)
pl(chime(784, 2.8), P.T_REIGNS + 0.03, 0.2)

mix = np.stack([L, Rt], axis=1)
fade = int(SR * 0.4)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix[: int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))[:, None]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 2.4) / np.tanh(2.4) * 10 ** (-3 / 20)
wavfile.write("/home/claude/psalm2/sfx.wav", SR, (mix * 32767).astype(np.int16))
print("sfx written", round(len(mix) / SR, 2), "s")
