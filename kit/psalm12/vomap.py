"""Psalm 12 voiceover map: phrases from pauses, words placed by length within each phrase."""
import re, subprocess, json
VOICE = "/home/claude/psalm12/voice.mp3"
OFFSET = 0.25
PHRASES = ["Ever feel like you can't trust anything anyone says anymore?", "David felt that way.", "In Psalm 12, he cries,",
 "\"Save, Lord,", "for the faithful have vanished.\"", "Everyone lies to their neighbor.", "They flatter with their lips and boast,",
 "\"With our tongues we will win.", "Who is master over us?\"", "Then God speaks.", "\"Because the poor are plundered",
 "and the needy groan,", "I will now arise.\"", "And against all that noise,", "the psalm sets God's words:", "pure,",
 "like silver", "refined in a furnace seven times.", "Look at verse two.", "The flatterers speak with a double heart.",
 "In Hebrew,", "beh-LEV vah-LEV:", "with a heart", "and a heart.", "One heart for show,", "another underneath.", "So today,",
 "guard your own words.", "Mean what you say,", "and fill your mind with words you can trust.", "One heart.", "One word."]
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
           "video_dur": round(dur + OFFSET + 1.5, 2)}, open("/home/claude/psalm12/vomap.json", "w"), indent=0)
for a, b, ph in phrases: print(f"{a:6.2f}-{b:6.2f}  {ph}")
print("video", round(dur + OFFSET + 1.5, 2))
