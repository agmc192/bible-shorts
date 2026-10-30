"""Forced alignment of a script to a voiceover with pocketsphinx. Usage: align.py <voice> <text> -> JSON [[start,end,word],...]"""
import sys, json, subprocess
from pocketsphinx import Decoder
voice, text = sys.argv[1], sys.argv[2]
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", voice, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
d = Decoder(samprate=16000, bestpath=False, loglevel="FATAL")
d.set_align_text(text)
d.start_utt(); d.process_raw(raw, full_utt=True); d.end_utt()
d.set_alignment()
d.start_utt(); d.process_raw(raw, full_utt=True); d.end_utt()
al = d.get_alignment()
out = [[round(w.start / 100, 3), round((w.start + w.duration) / 100, 3), w.name] for w in al]
print(json.dumps(out))
