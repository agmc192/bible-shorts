"""Map the uploaded voiceover onto the v2 timeline: phrases from silence detection, words by length."""
import re, subprocess, json
import numpy as np
import render as R

VOICE = "/home/claude/psalm1/vo/voice.mp3"
OFFSET = 0.25          # voice starts this long after the video
TAIL = 1.4             # end card holds this long after the last word

PHRASES = ["Ever notice how some people stay steady when life falls apart?",
 "Psalm 1 opens the whole book with the answer.", "Picture a tree in dry, cracked ground,",
 "planted right beside a stream.", "The heat comes,", "but its leaves stay green.",
 "The psalm says that's the person who delights in God's word.", "They're like that tree by the stream.",
 "Here's the key.", "The word for \"meditate\" is the Hebrew hagah.",
 "Isaiah uses that same word for a lion growling over its prey.", "It's not skimming,", "it's chewing.",
 "That's how we're meant to come to God's word.", "Devoted.", "Hungry.", "It's the water our roots drink from.",
 "Then the psalm shows the other path:", "a life like chaff,", "dry and weightless,", "blown away by the wind.",
 "So what keeps you standing isn't how strong you are.", "It's where your roots go.", "Start today.",
 "One verse,", "read slowly,", "chewed on all day.", "Be rooted in God's word."]

def speech_spans():
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", VOICE, "-af", "silencedetect=noise=-38dB:d=0.18",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOICE],
                               capture_output=True, text=True).stdout)
    spans, cur = [], 0.0
    for s, e in zip(starts, ends):
        if s - cur > 0.05:
            spans.append((cur, s))
        cur = e
    if dur - cur > 0.05:
        spans.append((cur, dur))
    return spans, dur

spans, VDUR = speech_spans()
assert len(spans) == len(PHRASES), (len(spans), len(PHRASES))

new_words = []
for (a, b), ph in zip(spans, PHRASES):
    ws = ph.split()
    wts = [len(R.clean(w)) + 2 for w in ws]
    tot, t = sum(wts), a
    for w, k in zip(ws, wts):
        new_words.append((t + OFFSET, R.clean(w).lower().strip("?")))
        t += (b - a) * k / tot

import render_v2 as V
orig_words = V.WT
assert [w for _, w in orig_words] == [w for _, w in new_words], "word lists differ"

KEY = {"steady", "cracked", "stream", "green", "delights", "hagah", "lion", "chewing", "devoted", "hungry",
       "water", "chaff", "roots", "rooted", "verse"}
phrase_first = set()
i = 0
for ph in PHRASES:
    phrase_first.add(i)
    i += len(ph.split())
anchors = [(0.0, 0.0)]
for i, ((to, w), (tn, _)) in enumerate(zip(orig_words, new_words)):
    if i in phrase_first or w in KEY:
        anchors.append((to, tn))
last_orig_end = 47.9
new_end = VDUR + OFFSET
anchors.append((last_orig_end, new_end))
NEW_DUR = round(new_end + TAIL, 2)
anchors.append((50.0, NEW_DUR))
anchors.sort()
o = [a for a, _ in anchors]; n = [b for _, b in anchors]
assert all(x < y for x, y in zip(o, o[1:])) and all(x < y for x, y in zip(n, n[1:])), "non-monotonic"
json.dump({"orig": o, "new": n, "new_dur": NEW_DUR, "offset": OFFSET}, open("/home/claude/psalm1/vo/timemap.json", "w"))
print("voice", round(VDUR, 2), "-> video", NEW_DUR, "s;", len(anchors), "anchors")
for to, tn in anchors:
    print(f"{to:6.2f} -> {tn:6.2f}")
