# Bible Shorts production pipeline (Psalm 13 on)

Every episode ships as **three platform versions** that differ only in the spoken callout near the end,
plus one thumbnail. Everything below runs from `/home/claude`.

## Setup in a fresh session
```
git clone https://github.com/agmc192/bible-shorts /home/claude/bible-shorts
cd /home/claude
cp bible-shorts/kit/*.py .                       # engine, build, callout, aligner, captions, sfx loader
for d in bible-shorts/kit/psalm*; do cp -r $d .; done   # art libraries (psalm1 has fonts) + past episodes
cp -r bible-shorts/kit/callouts .                # the nine callout clips (never ask Anthony for these again)
pip install --break-system-packages pycairo pocketsphinx
```

## Per episode (folder /home/claude/psalmN, N can be 18a / 18b for split psalms)
1. `voice.mp3` = the ElevenLabs voiceover. Confirm which file is which psalm by its length against the
   take durations recorded in the Script Library, and by the hook's length.
2. `phrases.json` = the approved script split into caption phrases (break at commas, full stops, colons).
   `subs.json` = how the aligner should hear non-English words, e.g. `{"KHEH-sed.": "heck said"}`,
   `{"nah-VAHL.": "naval"}`, `{"GOOR:": "gore"}`.
3. `python3 vomap_align.py /home/claude/psalmN` -> `vomap.json` with real word timings (pocketsphinx forced
   alignment). Read the printout and sanity-check it against the pauses (`python3 spans.py psalmN/voice.mp3`).
4. Callouts: for each platform
   `python3 callout.py /home/claude/psalmN <youtube|instagram|tiktok> callouts/<voice>_<platform>.mp3 "<first words of the closing line>"`
   Voices: christopher, verity, frederick (rotation Christopher -> Verity X -> Frederick Surrey).
   Splices the clip into the pause before the memorable closing line and writes `voice_<plat>.wav` and
   `vomap_<plat>.json`. The engine draws the Like / Subscribe-or-Follow / Share-or-Send buttons automatically.
5. `render_pN.py` (new scenes every episode, house style) and `sfx_pN.py`. Use `wt("word", k)` for timings.
   **The final scene must end with the standard end card**:
   `end_card(ctx, t, "PSALM N", ICON, "<closing line part 1>", "<part 2>", T_PART1, T_PART2)`
   then the 0.55 s loop fade back to scene 1. `ICON(ctx, x, y)` draws the episode's icon centred at (x, y).
   The end card is the thumbnail design (PSALM N, gold rule, "in a minute", icon) plus the closing line,
   so the Instagram/TikTok cover set by Buffer's thumbnailOffset IS the thumbnail. Never skip it.
   Add `python3 render_pN.py thumb` support: `end_thumbnail(...)` writes `psalmN_thumbnail.png` from the same card.
6. Check stills: `VOMAP=psalmN/vomap_instagram.json python3 psalmN/render_pN.py stills <times...>` then
   `engine.contact(N)`; fix clipping/legibility before rendering.
7. `python3 build.py N psalmN/render_pN.py psalmN/sfx_pN.py "<caption,highlight,words>"`
   renders the shared part once and the tail per platform, mixes (voice 100%, SFX ~6 dB under, ducked),
   burns captions, and writes `psalmN/out/psalmN_<platform>.mp4`. `tail` stage re-renders only the ending.
8. Check frames of the finished files, durations under 60 s, then commit:
   `episodes/psalm-NNN/psalmN_youtube.mp4`, `psalmN_instagram.mp4`, `psalmN_tiktok.mp4`, `psalmN_thumbnail.png`
   and the episode code to `kit/psalmN/` (phrases.json, subs.json, render_pN.py, sfx_pN.py, copy.json).

## Posting (Buffer)
Each platform gets its own file. thumbnailOffset = (video duration - 1.0 s) in ms on **all three** posts
(the end card is fully on screen then; the loop fade starts 0.55 s before the end).
