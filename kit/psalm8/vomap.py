"""Psalm 8 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm8/voice.mp3"
OFFSET = 0.25
PHRASES = ["Have you ever looked up at the night sky and felt tiny?", "David did.", "In Psalm 8,",
 "he looks at the moon and the stars", "and calls them the work of God's fingers.", "Then he asks,",
 "\"What is man, that you are mindful of him?\"", "And God doesn't just notice us.",
 "He crowned human beings with glory and honor", "and put them in charge of his world,", "from the sheep and oxen",
 "to the fish of the sea.", "That word \"mindful\" is the Hebrew zah-KHAR:", "to remember.",
 "The God who set the stars in place", "keeps you in mind.", "Hebrews chapter two applies this psalm to Jesus:",
 "made lower", "for a little while,", "then crowned with glory and honor", "because he suffered death.", "So tonight,",
 "step outside and look up.", "Let it make you small,", "then grateful.", "Small,", "but remembered."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm8/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
