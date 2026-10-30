"""Splice a platform callout clip into an episode's voiceover just before the memorable closing line.
Usage: python3 callout.py <episode_dir> <plat> <clip.mp3> "<first words of the closing line phrase>"
Writes <dir>/voice_<plat>.wav and <dir>/vomap_<plat>.json (all times after the cut shifted)."""
import json, re, subprocess, sys
D, PLAT, CLIP, SPLIT = sys.argv[1:5]
LINES = {"youtube": "Subscribe for a psalm a day, and share this with someone who needs it.",
         "instagram": "Follow for a psalm a day, and send this to someone who needs it.",
         "tiktok": "Follow for a psalm a day, and send this to a friend who needs it."}
KEY2 = {"youtube": "subscribe", "instagram": "follow", "tiktok": "follow"}
KEY3 = {"youtube": "share", "instagram": "send", "tiktok": "send"}
PRE, POST, SR = 0.30, 0.45, 44100
M = json.load(open(f"{D}/vomap.json"))
OFF = M["offset"]
idx = next(i for i, p in enumerate(M["phrases"]) if p[2].startswith(SPLIT))
gap_a = M["phrases"][idx - 1][1] - OFF
gap_b = M["phrases"][idx][0] - OFF
cut = gap_a + 0.55 * (gap_b - gap_a)   # in the pause, closer to the closing line

def run(*a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *a], check=True)

# trim the clip's own leading/trailing silence
run("-i", CLIP, "-af", "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,"
    "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse",
    "-ar", str(SR), "-ac", "1", f"{D}/clip_{PLAT}.wav")
Lc = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{D}/clip_{PLAT}.wav"],
                          capture_output=True, text=True).stdout)
shift = PRE + Lc + POST
run("-i", f"{D}/voice.mp3", "-i", f"{D}/clip_{PLAT}.wav", "-filter_complex",
    f"[0:a]aresample={SR},aformat=channel_layouts=mono,asplit=2[a][b];"
    f"[a]atrim=0:{cut:.4f},asetpts=PTS-STARTPTS[h];[b]atrim={cut:.4f},asetpts=PTS-STARTPTS[t];"
    f"[1:a]adelay={int(PRE*1000)},apad=pad_dur={POST}[c];[h][c][t]concat=n=3:v=0:a=1[o]",
    "-map", "[o]", f"{D}/voice_{PLAT}.wav")

cv = cut + OFF
sh = lambda x: round(x + shift, 3) if x > cv else x
words = [[sh(a), sh(b), w] for a, b, w in M["words"]]
phrases = [[sh(a), sh(b), p] for a, b, p in M["phrases"]]
c0, c1 = cv + PRE, cv + PRE + Lc
ws = LINES[PLAT].split()
clean = lambda w: re.sub(r"[^A-Za-z0-9'-]", "", w).lower()
from pocketsphinx import Decoder
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f"{D}/clip_{PLAT}.wav", "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
dec = Decoder(samprate=16000, bestpath=False, loglevel="FATAL")
dec.set_align_text(" ".join(clean(w) for w in ws))
dec.start_utt(); dec.process_raw(raw, full_utt=True); dec.end_utt()
dec.set_alignment()
dec.start_utt(); dec.process_raw(raw, full_utt=True); dec.end_utt()
al = [(a.start / 100, (a.start + a.duration) / 100) for a in dec.get_alignment() if a.name not in ("<sil>", "<s>", "</s>")]
assert len(al) == len(ws), (len(al), len(ws))
cw = [[round(c0 + a, 3), round(c0 + b, 3), w] for (a, b), w in zip(al, ws)]
words = [w for w in words if w[0] < cv] + cw + [w for w in words if w[0] > cv]
phrases = [p for p in phrases if p[0] < cv] + [[round(c0, 3), round(c1, 3), LINES[PLAT]]] + [p for p in phrases if p[0] > cv]
t2 = next(a for a, b, w in cw if clean(w) == KEY2[PLAT])
t3 = next(a for a, b, w in cw if clean(w) == KEY3[PLAT])
M2 = dict(M, words=words, phrases=phrases, video_dur=round(M["video_dur"] + shift, 2), voice=f"{D}/voice_{PLAT}.wav",
          callout={"plat": PLAT, "start": round(c0, 3), "end": round(c1, 3), "cut": round(cv, 3), "shift": round(shift, 3),
                   "lights": [round(c0 - 0.12, 3), max(t2, c0 + 0.05), t3]})
json.dump(M2, open(f"{D}/vomap_{PLAT}.json", "w"), indent=0)
print(f"{PLAT}: cut at {cv:.2f}s (video), callout {c0:.2f}-{c1:.2f}, video {M2['video_dur']}s")
