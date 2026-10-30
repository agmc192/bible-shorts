"""Voiceover map from forced alignment (pocketsphinx): real word timings for every script word.
Usage: python3 vomap_align.py <episode_dir>
Reads <dir>/phrases.json (script split into caption phrases) and optional <dir>/subs.json
({"KHEH-sed.": "kissed"} : how to spell a non-English word with dictionary words for the aligner).
Writes <dir>/vomap.json in the same format as before."""
import json, os, re, subprocess, sys
from pocketsphinx import Decoder
D = sys.argv[1]
VOICE = sys.argv[2] if len(sys.argv) > 2 else f"{D}/voice.mp3"
OUT = sys.argv[3] if len(sys.argv) > 3 else f"{D}/vomap.json"
OFFSET = 0.25
PH = json.load(open(f"{D}/phrases.json")) if os.path.exists(f"{D}/phrases.json") and len(sys.argv) <= 2 else json.loads(sys.argv[4]) if len(sys.argv) > 4 else json.load(open(f"{D}/phrases.json"))
SUBS = json.load(open(f"{D}/subs.json")) if os.path.exists(f"{D}/subs.json") else {}
NUM = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "7": "seven", "12": "twelve", "13": "thirteen", "14": "fourteen",
       "15": "fifteen", "16": "sixteen", "17": "seventeen", "18": "eighteen", "19": "nineteen", "20": "twenty", "2,": "two",
       "100th": "hundredth"}


def toks(w):
    if w in SUBS:
        return SUBS[w].split()
    c = re.sub(r"[^A-Za-z0-9'\-]", "", w).lower()
    if c in NUM:
        return NUM[c].split()
    c = c.replace("-", " ").replace("'s", "'s")
    return [x for x in re.sub(r"[^a-z' ]", " ", c).split() if x] or ["uh"]


words = []   # (script word, n tokens)
for ph in PH:
    for w in ph.split():
        words.append((w, toks(w)))
text = " ".join(t for _, ts in words for t in ts)
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", VOICE, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
dec = Decoder(samprate=16000, bestpath=False, loglevel="FATAL")
dec.set_align_text(text)
dec.start_utt(); dec.process_raw(raw, full_utt=True); dec.end_utt()
dec.set_alignment()
dec.start_utt(); dec.process_raw(raw, full_utt=True); dec.end_utt()
al = [(w.start / 100, (w.start + w.duration) / 100, re.sub(r"\(\d+\)$", "", w.name)) for w in dec.get_alignment()]
al = [a for a in al if a[2] not in ("<sil>", "<s>", "</s>", "[NOISE]")]
ntok = sum(len(ts) for _, ts in words)
assert len(al) == ntok, (len(al), ntok)
out, k = [], 0
for w, ts in words:
    seg = al[k:k + len(ts)]
    k += len(ts)
    out.append([round(seg[0][0] + OFFSET, 3), round(seg[-1][1] + OFFSET, 3), w])
phrases, i = [], 0
for ph in PH:
    n = len(ph.split())
    phrases.append([out[i][0], out[i + n - 1][1], ph])
    i += n
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOICE],
                           capture_output=True, text=True).stdout)
json.dump({"words": out, "phrases": phrases, "voice_dur": dur, "offset": OFFSET,
           "video_dur": round(out[-1][1] + 1.5, 2), "aligned": True}, open(OUT, "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(out[-1][1] + 1.5, 2))
