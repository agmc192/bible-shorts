"""Psalm 10 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm10/voice.mp3"
OFFSET = 0.25
PHRASES = ["Why does God feel far away when everything is falling apart?", "Psalm 10 opens with that exact question:",
 "\"Why, Lord,", "do you stand far away?", "Why do you hide yourself in times of trouble?\"",
 "The psalmist watches the proud hunt down the weak,", "like a lion in ambush.", "And the wicked man tells himself,",
 "\"God has forgotten.", "He will never see it.\"", "But the psalm answers him.", "\"You do see.\"",
 "God takes note of trouble and grief,", "and the helpless can commit themselves to him.",
 "He hears the desire of the afflicted, and he brings justice to the fatherless and the oppressed.",
 "In Hebrew, it's one word:", "rah-EE-tah.", "\"You have seen.\"", "The wicked say God will never see.",
 "The psalm says he already has.", "So today,", "bring God your honest \"why.\"", "He can handle the question.",
 "Ask why.", "He sees."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm10/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
