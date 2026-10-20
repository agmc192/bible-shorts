"""Psalm 2 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm4/voice.mp3"
OFFSET = 0.25
PHRASES = ["Ever replayed an argument in your head for hours?", "David knew the feeling.", "In Psalm 4,",
 "people are turning his honor into shame", "and chasing lies.", "So he writes:", "\"Be angry,", "and do not sin.",
 "On your bed,", "search your heart,", "and be still.\"", "Here's the key.",
 "The Hebrew word for \"be angry\" is rigzu.", "It means to tremble,", "to shake.",
 "And the apostle Paul quotes this exact line, then adds,", "\"Don't let the sun go down on your anger.\"",
 "Feeling it isn't the sin.", "Feeding it is.", "David's answer is trust.",
 "And God fills him with a joy bigger than a full harvest,", "and a peace so deep", "he can lie down and sleep.",
 "So before the sun goes down today,", "hand that anger to God.", "Feel it.", "Don't feed it."]
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", VOICE, "-af", "silencedetect=noise=-34dB:d=0.18", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOICE],
                           capture_output=True, text=True).stdout)
spans, cur = [], 0.0
for s, e in zip(st, en):
    if s - cur > 0.05: spans.append((cur, s))
    cur = e
if dur - cur > 0.05: spans.append((cur, dur))
assert len(spans) == len(PHRASES), (len(spans), len(PHRASES))
clean = lambda w: re.sub(r"[^A-Za-z0-9'-]", "", w).lower()
words, phrases = [], []
for (a, b), ph in zip(spans, PHRASES):
    ws = ph.split(); wts = [len(clean(w)) + 2 for w in ws]; tot, t = sum(wts), a
    for w, k in zip(ws, wts):
        words.append([round(t + OFFSET, 3), round(t + OFFSET + (b - a) * k / tot, 3), w]); t += (b - a) * k / tot
    phrases.append([round(a + OFFSET, 3), round(b + OFFSET, 3), ph])
json.dump({"words": words, "phrases": phrases, "voice_dur": dur, "offset": OFFSET,
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm4/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
