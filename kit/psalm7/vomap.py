"""Psalm 7 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm7/voice.mp3"
OFFSET = 0.25
PHRASES = ["What do you do when someone is telling lies about you?", "Psalm 7 is a song of David about the words of Cush,",
 "a Benjaminite.", "David runs to God for refuge.", "He even says:", "if I've really done this wrong, let my enemy catch me.",
 "Then he leaves his case with God,", "the righteous judge.", "And here's the twist.", "The one who plots evil digs a pit...",
 "and falls into the hole he made.", "His trouble comes back on his own head.", "In verse nine,",
 "David says God tests the heart and mind.", "The Hebrew literally says hearts and kidneys,", "klah-YOTE:",
 "the seat of your deepest feelings.", "God sees all the way down.", "So today, don't dig a pit of your own.",
 "Bring your case to God,", "and let him judge.", "Leave the verdict.", "Keep your peace."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm7/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
