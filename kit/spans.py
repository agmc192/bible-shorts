import re, subprocess, sys
V = sys.argv[1]; th = sys.argv[2] if len(sys.argv) > 2 else "-38dB"; d = sys.argv[3] if len(sys.argv) > 3 else "0.18"
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", V, "-af", f"silencedetect=noise={th}:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V], capture_output=True, text=True).stdout)
cur = 0; sp = []
for s, e in zip(st, en):
    if s - cur > 0.05: sp.append((cur, s))
    cur = e
if dur - cur > 0.05: sp.append((cur, dur))
for i, (a, b) in enumerate(sp): print(i, round(a, 2), round(b, 2), round(b - a, 2))
