"""Loads the shared sound-effects synth library for episode N. Usage: from sfxlib import load; S = load(7)."""
import sys, json
import numpy as np


def load(n):
    sys.path.insert(0, "/home/claude/psalm1")
    g = {"__name__": "sfxlib_ep"}
    lib = open("/home/claude/psalm1/sfx.py").read().split("# ---------------------------------------------------------------- the cue sheet")[0]
    lib = lib.replace("DUR = 50.0", f"DUR = __import__('json').load(open('/home/claude/psalm{n}/vomap.json'))['video_dur']")
    lib = lib.replace("import render_v2 as V\n", "")
    exec(lib, g)
    p2 = open("/home/claude/psalm2/sfx_p2.py").read()
    exec(p2[p2.index("def crowd_roar"):p2.index("pl = place")], g)
    p6 = open("/home/claude/psalm6/sfx_p6.py").read()
    exec(p6[p6.index("def drip"):p6.index("\npl = place")], g)

    def write(path):
        L, Rt, SR = g["L"], g["Rt"], g["SR"]
        mix = np.stack([L, Rt], axis=1)
        fade = int(SR * 0.4)
        mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
        mix[: int(SR * 0.01)] *= np.linspace(0, 1, int(SR * 0.01))[:, None]
        peak = np.max(np.abs(mix))
        mix = np.tanh(mix / peak * 2.4) / np.tanh(2.4) * 10 ** (-3 / 20)
        from scipy.io import wavfile
        wavfile.write(path, SR, (mix * 32767).astype(np.int16))
        print("sfx written", round(len(mix) / SR, 2), "s")

    g["write"] = write
    return type("S", (), g)
