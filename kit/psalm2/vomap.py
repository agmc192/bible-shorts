"""Psalm 2 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm2/voice.mp3"
OFFSET = 0.25
PHRASES = ["Ever feel like the whole world is spinning out of control?", "Psalm 2 opens right there.",
 "Nations raging.", "Rulers plotting to break free from God and his chosen King.",
 "The New Testament tells us David wrote it.", "And heaven?", "God isn't worried.", "He laughs.",
 "Then he speaks:", "\"I have set my King on my holy hill.\"", "Here's the key.", "The word for God's \"Anointed\"",
 "is the Hebrew mashiach.", "Messiah.", "In Greek,", "that's Christos.", "Christ.",
 "And when God tells his King, \"You are my Son,\"", "the New Testament applies those very words to Jesus.",
 "So the chaos is real,", "but it isn't in charge.", "And the psalm ends the way Psalm 1 began,", "with the word",
 "\"blessed.\"", "Blessed are all who take refuge in him.", "Next time the news feels loud,", "take it to the King.",
 "The world rages.", "Jesus reigns."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm2/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
