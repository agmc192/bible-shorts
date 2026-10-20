"""Psalm 2 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm3/voice.mp3"
OFFSET = 0.25
PHRASES = ["Ever been so worried you couldn't sleep?",
 "The heading of Psalm 3 says David wrote it while running from his own son, Absalom.",
 "Absalom had turned Israel against him.", "David fled, weeping, his head covered in grief.",
 "Enemies everywhere.", "People saying,", "\"God won't save him now.\"", "But David prays,",
 "\"You, Lord, are a shield around me,", "my glory,", "the one who lifts my head.\"",
 "The head he covered in grief,", "God lifts up.", "Then he does something surprising.", "He lies down",
 "and sleeps.", "And he wakes again,", "because the Lord held him up.", "Here's the key.",
 "The word for \"salvation\" in this psalm is the Hebrew yeshuah.", "It shares its root with the name Yeshua.",
 "Jesus.", "A name that means \"the Lord saves.\"", "So tonight,", "hand God whatever is keeping you awake.",
 "Salvation belongs to the Lord.", "You can rest."]
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", VOICE, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-"],
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
           "video_dur": round(dur + OFFSET + 1.3, 2)}, open("/home/claude/psalm3/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.3, 2))
