"""Psalm 6 sound effects, built on the Psalm 1/2 synth library and timed to the voiceover."""
import sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, "/home/claude/psalm1")
sys.path.insert(0, "/home/claude/psalm6")
lib = open("/home/claude/psalm1/sfx.py").read().split("# ---------------------------------------------------------------- the cue sheet")[0]
lib = lib.replace("DUR = 50.0", "DUR = __import__('json').load(open('/home/claude/psalm6/vomap.json'))['video_dur']")
lib = lib.replace("import render_v2 as V\n", "")
exec(lib)
p2 = open("/home/claude/psalm2/sfx_p2.py").read()
exec(p2[p2.index("def crowd_roar"):p2.index("pl = place")])
import render_p6 as P


def drip():
    t = t_arr(0.18)
    f = 900 + 1600 * np.exp(-t * 40)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28))


def drips(d, rate=2.0, jitter=0.25):
    out = np.zeros(int(SR * d))
    k, tt = 0, 0.0
    while tt < d - 0.2:
        x = drip() * rng.uniform(0.5, 1.0)
        i0 = int(tt * SR)
        out[i0:i0 + len(x)] += x[: len(out) - i0]
        tt += 1 / rate + rng.uniform(-jitter, jitter) / rate
    return out


def rip(d=0.45):
    t = t_arr(d)
    x = bp(rng.standard_normal(len(t)), 900, 6000) * (0.6 + 0.4 * (rng.random(len(t)) < 0.03))
    return norm(x * env(len(t), 0.02, 1, 1.4))


def groan(d=1.6):
    t = t_arr(d)
    f = 110 + 18 * np.sin(2 * np.pi * 1.3 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return norm(lp(x, 600) * env(len(t), 0.3, 1, 1.4))


def heartbeat(d, bpm=62):
    out = np.zeros(int(SR * d))
    k = 0
    while k * 60 / bpm < d - 0.4:
        for off, g in ((0.0, 1.0), (0.22, 0.6)):
            th = thump(0.3) * g
            i0 = int((k * 60 / bpm + off) * SR)
            out[i0:i0 + len(th)] += th[: len(out) - i0]
        k += 1
    return out


def quill(d=0.9):
    t = t_arr(d)
    x = bp(rng.standard_normal(len(t)), 2500, 8000) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) ** 4
    return norm(x * env(len(t), 0.1, 1, 1))


pl = place
# hook: the tear lands, quiet night
pl(hit(60, 30, 1.2), 0.1, 0.55)
pl(drip(), 0.12, 0.6)
pl(water(0.8, 300, 2200, 12), 0.13, 0.3)
pl(rain(P.B2 + 0.4), 0.0, 0.12)
pl(drips(P.B2 - 0.8, 1.4), 0.8, 0.22, -0.3)
pl(chime(523, 1.6), P.T_ANYONE, 0.12)
pl(whoosh(0.5, 400, 5000, 0.85), P.B2 - 0.35, 0.45)
# title, rip on "raw"
pl(page_ticks(0.3, 8), P.B2 + 0.05, 0.25)
pl(chime(587, 1.6), P.T_PSALM, 0.18)
pl(rip(0.45), P.T_RAW - 0.08, 0.6)
pl(hit(70, 34, 0.8), P.T_RAW - 0.02, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B3 - 0.35, 0.45)
# worn out, every night, flood
pl(groan(1.4), P.T_WORN - 0.1, 0.18)
for k in range(5):
    pl(whoosh(0.3, 500, 2500, 0.5), P.T_EVERY - 0.1 + k * 0.17, 0.15, (-1) ** k * 0.5)
pl(drips(P.B4 - P.T_NIGHT, 3.0), P.T_NIGHT, 0.25, 0.3)
pl(water(P.B4 - P.T_FLOODS + 0.4, 200, 1800, 40), P.T_FLOODS - 0.2, 0.4)
pl(hit(55, 30, 1.0), P.T_FLOODS - 0.02, 0.4)
pl(whoosh(0.5, 400, 5000, 0.85), P.B4 - 0.35, 0.45)
# bones, soul, enemies
pl(drone(P.B5 - P.B4), P.B4, 0.18)
pl(heartbeat(P.B5 - P.B4, 70), P.B4 + 0.1, 0.35)
pl(glass_crack(), P.T_ACHE - 0.05, 0.25)
pl(chime(440, 1.4), P.T_SOUL, 0.15)
pl(thunder(1.4) * 0.6, P.T_SHAKEN - 0.05, 0.4)
pl(crowd_roar(P.B5 - P.T_ENEMIES, 0.35), P.T_ENEMIES - 0.2, 0.18)
pl(clank(0.8), P.T_ENEMIES - 0.02, 0.3, -0.5)
pl(clank(0.8), P.T_LET - 0.02, 0.3, 0.5)
pl(whoosh(0.5, 400, 5000, 0.85), P.B5 - 0.35, 0.45)
# the turn at verse 8
for k in range(8):
    pl(ping(), P.T_THEN + k * (P.T_END - P.T_THEN + 0.1) / 8, 0.12, -0.7 + k * 0.2)
pl(riser(1.4), P.T_TURNS - 1.4, 0.4)
pl(hit(60, 30, 1.4), P.T_TURNS - 0.02, 0.7)
pl(swell(1.8, 70), P.T_TURNS - 0.1, 0.4)
pl(chime(659, 2.5), P.T_TURNS, 0.3)
pl(sparkle(1.2), P.T_TURNS + 0.05, 0.25)
pl(whoosh(0.5, 400, 5000, 0.85), P.B6 - 0.35, 0.4)
# heard
pl(pad(P.B7 - P.B6, (196, 246.9, 293.7, 392)), P.B6, 0.2)
pl(chime(784, 2.2), P.T_HEARD1, 0.25)
for k in range(5):
    pl(chime(1046 + 120 * k, 1.0), P.T_SOUND + k * 0.35, 0.07, (-1) ** k * 0.4)
pl(sparkle(1.0), P.T_ACCEPTS, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B7 - 0.35, 0.4)
# nothing changed yet
pl(rain(P.B8 - P.B7), P.B7, 0.1)
pl(drips(P.B8 - P.B7, 1.0), P.B7, 0.15, -0.4)
pl(swell(1.6, 65), P.T_DAVID2 - 0.3, 0.35)
pl(chime(523, 2.0), P.T_TEARS2, 0.2)
pl(hit(55, 30, 1.0), P.T_HEARD2 - 0.02, 0.45)
pl(chime(659, 2.2), P.T_HEARD2, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B8 - 0.35, 0.45)
# nugget
pl(drone(P.B10 - P.B8), P.B8, 0.2)
pl(ping(), P.T_THREE, 0.2)
pl(riser(1.4), P.T_ADMATAI - 1.4, 0.35)
pl(hit(70, 34, 1.4), P.T_ADMATAI - 0.02, 0.9)
pl(chime(440, 2.2), P.T_ADMATAI, 0.25)
pl(chime(392, 1.6), P.T_UNTIL, 0.15)
pl(whoosh(0.4, 400, 4000, 0.6), P.B9 - 0.2, 0.3)
# unfinished sentence; still heard
pl(quill(0.9), P.B9 + 0.05, 0.35)
pl(thump(), P.T_FINISH + 0.35, 0.45)
pl(drip(), P.T_FINISH + 0.95, 0.4)
pl(swell(1.4, 70), P.T_GOD1 - 0.3, 0.35)
pl(hit(55, 30, 1.2), P.T_HEARS - 0.02, 0.5)
pl(chime(659, 2.2), P.T_HEARS, 0.25)
pl(sparkle(1.0), P.T_HEARS + 0.1, 0.2)
pl(whoosh(0.5, 400, 5000, 0.85), P.B10 - 0.35, 0.45)
# close: dawn
pl(wind(P.DUR - P.B10, 500, 0.3), P.B10, 0.12)
pl(pad(P.DUR - P.B10, (261.6, 329.6, 392, 523.3)), P.B10, 0.18)
pl(page_ticks(0.3, 6), P.T_GIVE1 - 0.1, 0.25)
pl(whoosh(1.4, 300, 6000, 0.6), P.T_GIVE1, 0.35)
pl(sparkle(1.0), P.T_TEARS3, 0.2)
pl(hit(55, 32, 1.4), P.T_YOUR - 0.02, 0.4)
pl(chime(523, 3.0), P.T_YOUR, 0.25)
pl(hit(50, 30, 1.6), P.T_HEARD3 - 0.02, 0.45)
pl(chime(392, 3.0), P.T_HEARD3, 0.3)
pl(chime(587, 2.8), P.T_HEARD3 + 0.03, 0.18)
mix = np.stack([L, Rt], axis=1)
fade = int(SR * 0.4)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix[: int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))[:, None]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 2.4) / np.tanh(2.4) * 10 ** (-3 / 20)
wavfile.write("/home/claude/psalm6/sfx.wav", SR, (mix * 32767).astype(np.int16))
print("sfx written", round(len(mix) / SR, 2), "s")
