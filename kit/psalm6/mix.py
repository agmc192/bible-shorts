import json, re, subprocess, sys
D = json.load(open("/home/claude/psalm6/vomap.json"))["video_dur"]
def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
lv, ls = lufs("voice.mp3"), lufs("sfx.wav")
gain_db = (lv - 6.0) - ls
g = 10 ** (gain_db / 20)
print(f"voice {lv} LUFS, sfx {ls} LUFS -> sfx gain {gain_db:.1f} dB ({g:.3f})")
fc = (f"[1:a]aresample=48000,adelay=250|250,apad,asplit=2[v1][vsc];[2:a]volume={g:.4f}[sfx];"
      f"[sfx][vsc]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=300[duck];"
      f"[v1][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.84:level=false[a]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "video_only.mp4", "-i", "voice.mp3", "-i", "sfx.wav",
                "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-t", str(D), "-movflags", "+faststart", "psalm6_nocaptions.mp4"], check=True)
m = json.load(open("caps/meta.json"))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "psalm6_nocaptions.mp4", *m["inputs"],
                "-filter_complex_script", "caps/filter.txt", "-map", m["last"], "-map", "0:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy",
                "-movflags", "+faststart", "psalm6_final.mp4"], check=True)
print("done")
