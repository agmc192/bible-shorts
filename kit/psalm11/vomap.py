"""Psalm 11 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm11/voice.mp3"
OFFSET = 0.25
PHRASES = ["When everything around you is shaking, should you just run?", "In Psalm 11,", "David hears that advice.",
 "\"Flee like a bird to your mountain!", "The wicked have their arrows on the string.", "If the foundations are destroyed,",
 "what can the righteous do?\"", "David's answer:", "\"In the Lord I take refuge.\"", "Why?",
 "Because the Lord is in his holy temple,", "and his throne is in heaven.", "The ground may shake,", "but God's throne doesn't.",
 "And God isn't distant.", "Verse four says", "his eyes see,", "and his eyelids test every person.", "In Hebrew, ahf-ahp-PAHV:",
 "his eyelids.", "Picture someone narrowing their eyes to look closely.", "Nothing gets past him.", "So when fear says run,",
 "stop and look up first.", "Say it out loud:", "\"In the Lord I take refuge.\"", "Don't flee.", "Look up."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm11/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
