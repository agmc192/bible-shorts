BIBLE SHORTS PRODUCTION KIT (@thebibleexplainedai)
Attach this zip, plus the episode's ElevenLabs MP3, at the start of each new Claude session.

render.py          Art library: palette, fonts, captions, tree, stream, figure, lion, page, roots, shrubs, paper texture
render_v2.py       Effects engine (zooms, shakes, flashes, blur, grading, rays, dust, kinetic words) + the Psalm 1 scenes as the reference build
sfx.py             Sound-effects synthesiser and cue sheet (Psalm 1 reference)
retime_map.py      Finds the phrases in the voiceover and builds the time map to the video
render_retimed.py  Renders the video on the voiceover's timeline (no captions)
sfx_retimed.py     Places the sound effects on the voiceover's timeline
captions_vo.py     Builds captions from the voiceover timing and burns them in
thumbnail.py       Series thumbnail: "PSALM N / in a minute"

Setup in a fresh session:
  unzip into /home/claude/psalm1
  pip install --break-system-packages pycairo
  fonts: cd /home/claude/psalm1/fonts && for p in lora frank-ruhl-libre nunito; do npm pack @fontsource/$p && tar xzf fontsource-$p-*.tgz && mv package $p; done
