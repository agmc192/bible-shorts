"""Psalm 6 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm6/voice.mp3"
OFFSET = 0.25
PHRASES = ["Have you ever cried yourself to sleep and wondered if anyone noticed?", "Psalm 6 is a prayer of David,", "and it's raw.",
 "He's worn out from groaning.", "Every night he floods his bed with tears.", "His bones ache,", "his soul is shaken,",
 "and his enemies won't let up.", "Then, near the end,", "everything turns.", "\"The Lord has heard the sound of my weeping.",
 "The Lord accepts my prayer.\"", "Nothing around him has changed yet,", "but David knows his tears were heard.",
 "Look at verse three.", "In Hebrew, David cries,", "\"And you, Lord...", "ahd-mah-TIE?\"", "\"Until when?\"",
 "He doesn't even finish the sentence.", "And God still hears it.", "So tonight, if the words won't come,",
 "give God the half sentence.", "Give him the tears.", "Your tears are heard."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm6/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
