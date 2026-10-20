"""Synthesized sound-effects bed for the Psalm 1 Short (v2), timed to the visuals."""
import numpy as np
from scipy import signal
from scipy.io import wavfile
import render_v2 as V

SR = 48000
import json as _j
_M = _j.load(open('/home/claude/psalm1/vo/timemap.json'))
DUR = _M['new_dur']
def TM(t):
    return float(np.interp(t, _M['orig'], _M['new']))
def D(t0, d):
    return TM(t0 + d) - TM(t0)
N = int(SR * DUR)
rng = np.random.default_rng(5)
L = np.zeros(N)
Rt = np.zeros(N)


def t_arr(d):
    return np.arange(int(SR * d)) / SR


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def norm(x):
    m = np.max(np.abs(x)) + 1e-9
    return x / m


def place(x, t0, gain=1.0, pan=0.0):
    i0 = int(TM(t0) * SR)
    if i0 >= N:
        return
    x = x[: N - i0]
    gl, gr = gain * np.sqrt((1 - pan) / 2) * 1.414, gain * np.sqrt((1 + pan) / 2) * 1.414
    L[i0:i0 + len(x)] += x * gl
    Rt[i0:i0 + len(x)] += x * gr


def env(n, a, r, shape=2.0):
    """attack fraction a, release to end."""
    e = np.ones(n)
    na = max(1, int(n * a))
    e[:na] = np.linspace(0, 1, na) ** shape
    e[na:] = np.linspace(1, 0, n - na) ** shape
    return e


def sweep_lp(x, f0, f1):
    """one-pole lowpass with cutoff sweeping f0->f1 (exponential)."""
    n = len(x)
    f = f0 * (f1 / f0) ** (np.arange(n) / n)
    a = np.exp(-2 * np.pi * f / SR)
    y = np.empty(n)
    s = 0.0
    for i in range(n):
        s = a[i] * s + (1 - a[i]) * x[i]
        y[i] = s
    return y


def whoosh(d=0.6, f0=300, f1=3000, peak=0.7):
    n = int(SR * d)
    x = rng.standard_normal(n)
    y = sweep_lp(x, f0, f1) + 0.5 * sweep_lp(x, f0 * 0.5, f1 * 0.5)
    e = env(n, peak, 1, 1.6)
    return norm(hp(y, 80) * e)


def hit(f0=70, f1=38, d=0.9):
    t = t_arr(d)
    f = f1 + (f0 - f1) * np.exp(-t * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 4.5)
    click = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 90) * 0.4
    return norm(body + click)


def thump(d=0.35):
    t = t_arr(d)
    f = 50 + 70 * np.exp(-t * 25)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11))


def glass_crack():
    d = 0.5
    t = t_arr(d)
    x = np.zeros(len(t))
    for k in range(9):
        i0 = int(SR * (k * 0.012 + rng.uniform(0, 0.01)))
        burst = hp(rng.standard_normal(2400), 2500) * np.exp(-np.arange(2400) / 300)
        x[i0:i0 + 2400] += burst * (1 - k / 12)
    for f in (3150, 4420, 5800, 7100):
        x += 0.25 * np.sin(2 * np.pi * f * t) * np.exp(-t * 18)
    return norm(x)


def shatter(d=1.6):
    t = t_arr(d)
    x = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 6) * 0.5
    for _ in range(70):
        st = rng.uniform(0, d * 0.8) ** 1.6
        f = rng.uniform(2200, 8000)
        n = int(SR * rng.uniform(0.04, 0.14))
        i0 = int(st * SR)
        tt = np.arange(n) / SR
        ping = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 40) * rng.uniform(0.3, 1.0) * (1 - st / d)
        x[i0:i0 + n] += ping[: len(x) - i0]
    return norm(x)


def wind(d, f=500, mod=0.35):
    t = t_arr(d)
    x = lp(rng.standard_normal(len(t)), f, 2)
    x = x * (0.55 + 0.45 * np.sin(2 * np.pi * mod * t + rng.uniform(0, 6))) * env(len(t), 0.15, 1, 1)
    return norm(x)


def water(d, lo=300, hi=2200, bubbles=40):
    t = t_arr(d)
    x = bp(rng.standard_normal(len(t)), lo, hi) * 0.6
    for _ in range(bubbles):
        n = int(SR * 0.05)
        tt = np.arange(n) / SR
        f = rng.uniform(350, 900) * (1 + tt * 12)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 70)
        i0 = int(rng.uniform(0, d - 0.06) * SR)
        x[i0:i0 + n] += b * rng.uniform(0.3, 0.9)
    return norm(x * env(len(t), 0.08, 1, 1))


def plip():
    t = t_arr(0.12)
    f = 650 * (1 + t * 14)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45))


def chime(base=880, d=2.0):
    t = t_arr(d)
    x = sum(a * np.sin(2 * np.pi * base * m * t) * np.exp(-t * dec)
            for m, a, dec in [(1, 1, 2.5), (1.5, 0.5, 3), (2, 0.35, 4), (3, 0.15, 6)])
    return norm(x * env(len(t), 0.005, 1, 1.0))


def sparkle(d=1.2):
    x = np.zeros(int(SR * d))
    for k in range(10):
        c = chime(rng.choice([1320, 1568, 1760, 2093, 2349]), 0.6) * 0.5
        i0 = int(SR * k * d / 12)
        x[i0:i0 + len(c)] += c[: len(x) - i0]
    return norm(x)


def drone(d):
    t = t_arr(d)
    x = 0.6 * np.sin(2 * np.pi * 55 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t) + 0.25 * np.sin(2 * np.pi * 110.3 * t)
    x *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.2 * t)
    x += 0.3 * lp(rng.standard_normal(len(t)), 180)
    return norm(x * env(len(t), 0.1, 1, 1))


def riser(d=1.6):
    t = t_arr(d)
    f = 180 * (6 ** (t / d))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    noise = sweep_lp(rng.standard_normal(len(t)), 300, 6000) * 0.8
    return norm((tone + noise) * (t / d) ** 2)


def growl(d=2.2):
    t = t_arr(d)
    f = 62 + 10 * np.sin(2 * np.pi * 1.7 * t)
    saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    rough = 0.6 + 0.4 * np.sin(2 * np.pi * 27 * t)
    x = lp(saw * rough, 700, 2) + 0.5 * bp(rng.standard_normal(len(t)), 150, 600) * rough
    return norm(x * env(len(t), 0.25, 1, 1.2))


def page_ticks(d=0.6, rate=11):
    x = np.zeros(int(SR * d))
    for k in range(int(d * rate)):
        n = 900
        b = bp(rng.standard_normal(n), 1800, 6000) * np.exp(-np.arange(n) / 160)
        i0 = int(k / rate * SR)
        x[i0:i0 + n] += b
    return norm(x)


def rain(d):
    t = t_arr(d)
    x = hp(rng.standard_normal(len(t)), 2500) * 0.4
    clicks = (rng.random(len(t)) < 0.002) * rng.standard_normal(len(t))
    x += hp(clicks, 1500) * 0.8
    return norm(x * env(len(t), 0.15, 1, 1))


def thunder(d=2.5):
    t = t_arr(d)
    x = lp(rng.standard_normal(len(t)), 160, 3) * (0.7 + 0.3 * np.sin(2 * np.pi * 3 * t)) * np.exp(-t * 1.6)
    crack = hp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 25)
    return norm(x + 0.5 * crack)


def hiss(d=1.0):
    t = t_arr(d)
    return norm(hp(rng.standard_normal(len(t)), 4000) * env(len(t), 0.1, 1, 1.5))


# ---------------------------------------------------------------- the cue sheet
# hook
place(glass_crack(), 0.12, 0.9)
place(hit(80, 36, 1.2), 0.12, 0.9)
place(shatter(), 0.42, 0.55)
place(whoosh(1.6, 200, 2500, 0.5), 0.45, 0.35, -0.3)
place(wind(D(0.5, 3.6), 600, 0.4), 0.5, 0.18)
place(thump(), V.T_STEADY - 0.02, 0.6)
place(riser(0.8), 3.45, 0.35)
place(whoosh(0.5, 400, 5000, 0.85), 3.8, 0.55)
place(hit(60, 35, 0.6), 4.22, 0.4)
# drought
place(wind(D(4.3, 5.2), 380, 0.25), 4.3, 0.16, 0.2)
place(hiss(2.0), 6.6, 0.07)
for k in range(6):
    place(glass_crack() * 0.3, V.T_CRACKED - 0.6 + k * 0.28, 0.25, (-1) ** k * 0.4)
place(thump(), V.T_CRACKED - 0.02, 0.45)
# the stream bursts in
place(whoosh(0.5, 300, 3500, 0.9), 9.25, 0.4, -0.5)
place(water(1.2, 250, 3000, 60), 9.65, 0.55)
place(water(D(10.4, 10.0), 400, 1800, 50), 10.4, 0.12)
place(sparkle(1.4), V.T_GREEN - 0.05, 0.3)
# the person who delights
place(chime(660, 2.5), 14.5, 0.25)
place(sparkle(1.0), 14.6, 0.15, 0.5)
place(riser(0.7), 18.5, 0.25)
place(whoosh(0.6, 300, 4500, 0.85), 18.7, 0.5)
# hagah
place(drone(D(19.2, 12.4)), 19.2, 0.22)
place(riser(1.7), 20.45, 0.35)
place(hit(70, 34, 1.4), 22.2, 0.95)
place(chime(440, 2.5), 22.2, 0.25)
place(whoosh(0.4, 500, 4000, 0.8), 23.3, 0.3)
place(growl(2.3), 24.15, 0.55, -0.4)
place(page_ticks(0.65), 26.4, 0.45)
place(thump(), 27.06, 0.6)
place(chime(988, 1.5), 27.06, 0.25)
place(thump(), V.T_DEVOTED, 0.35)
place(thump(), V.T_HUNGRY, 0.35)
place(whoosh(0.6, 300, 4000, 0.8), 30.95, 0.4)
for k in range(5):
    place(plip(), 31.6 + k * 0.38, 0.35, (-1) ** k * 0.3)
place(water(D(31.4, 2.0), 400, 1800, 20), 31.4, 0.12)
place(whoosh(0.7, 500, 6000, 0.6), 33.2, 0.5, 0.6)
# chaff
place(wind(D(33.7, 5.8), 700, 0.5), 33.7, 0.2, 0.5)
place(whoosh(1.2, 250, 2500, 0.6), V.T_CHAFF - 0.5, 0.4, 0.6)
place(thump(), V.T_CHAFF - 0.02, 0.55)
place(hiss(1.4), V.T_CHAFF + 0.9, 0.3, 0.7)
place(whoosh(0.4, 400, 5000, 0.85), 39.05, 0.45)
# dive + storm
place(whoosh(1.6, 2500, 200, 0.4), 39.7, 0.5)
place(drone(D(39.6, 4.6)) * 0.6, 39.6, 0.15)
place(plip(), 41.1, 0.5)
place(plip(), 41.45, 0.4)
place(whoosh(0.8, 300, 3000, 0.5), 41.75, 0.4)
place(rain(D(41.9, 2.6)), 41.9, 0.28)
place(wind(D(41.9, 2.6), 900, 0.9), 41.9, 0.2, -0.3)
place(thunder(2.8), 42.9, 0.75)
place(thump(), V.T_ROOTS2 - 0.02, 0.55)
place(hit(90, 40, 0.8), 44.38, 0.6)
# next step + end
place(thump(), 44.42, 0.35)
place(chime(784, 2.0), 45.5, 0.2)
place(sparkle(1.0), 46.0, 0.12)
place(hit(55, 32, 1.6), V.T_ROOTED + 0.28, 0.55)
place(chime(523, 3.0), V.T_ROOTED + 0.3, 0.35)
place(chime(784, 2.8), V.T_ROOTED + 0.32, 0.2)

mix = np.stack([L, Rt], axis=1)
# gentle fade at the very end so the loop is clean
fade = int(SR * 0.4)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix[: int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))[:, None]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 2.4) / np.tanh(2.4)
mix = mix * 10 ** (-3 / 20)
wavfile.write("/home/claude/psalm1/vo/sfx_retimed.wav", SR, (mix * 32767).astype(np.int16))
print("peak normalised; rms dBFS:", round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 1))
