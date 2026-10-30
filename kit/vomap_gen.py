"""Generic voiceover map: phrases from pauses, words placed by length within each phrase.
Usage: python3 vomap_gen.py <episode_dir>   (reads <dir>/phrases.json, writes <dir>/vomap.json)
Spans shorter than MIN_SPAN (breaths, clicks) are merged into the previous span."""
import re, subprocess, json, sys
D = sys.argv[1]
TH = sys.argv[2] if len(sys.argv) > 2 else "-38dB"
DUR_MIN = sys.argv[3] if len(sys.argv) > 3 else "0.18"
VOICE = f"{D}/voice.mp3"
OFFSET = 0.25
MIN_SPAN = 0.15
PHRASES = json.load(open(f"{D}/phrases.json"))
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", VOICE, "-af", f"silencedetect=noise={TH}:d={DUR_MIN}", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOICE],
                           capture_output=True, text=True).stdout)
spans, cur = [], 0.0
for s, e in zip(st, en):
    if s - cur > 0.05: spans.append([cur, s])
    cur = e
if dur - cur > 0.05: spans.append([cur, dur])
merged = []
for a, b in spans:
    if merged and b - a < MIN_SPAN:
        merged[-1][1] = b if b - a > 0.0 and a - merged[-1][1] < 0.6 else merged[-1][1]
        continue
    merged.append([a, b])
spans = merged
assert len(spans) == len(PHRASES), (len(spans), len(PHRASES))
clean = lambda w: re.sub(r"[^A-Za-z0-9'-]", "", w).lower()
words, phrases = [], []
for (a, b), ph in zip(spans, PHRASES):
    ws = ph.split(); wts = [len(clean(w)) + 2 for w in ws]; tot, t = sum(wts), a
    for w, k in zip(ws, wts):
        words.append([round(t + OFFSET, 3), round(t + OFFSET + (b - a) * k / tot, 3), w]); t += (b - a) * k / tot
    phrases.append([round(a + OFFSET, 3), round(b + OFFSET, 3), ph])
last_speech = spans[-1][1]
json.dump({"words": words, "phrases": phrases, "voice_dur": dur, "offset": OFFSET,
           "video_dur": round(last_speech + OFFSET + 1.5, 2)}, open(f"{D}/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(last_speech + OFFSET + 1.5, 2))
