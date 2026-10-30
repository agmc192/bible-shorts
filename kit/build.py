"""Build all three platform versions of an episode.
Usage: python3 build.py <ep> <render_script> <sfx_script> <highlight,words> [stage]
  <ep> is the folder suffix (13, 18a ...). Requires vomap_<plat>.json from callout.py.
Stages: video | audio | all (default all) | tail (re-render only the part after the callout cut, then mix). Outputs <dir>/out/psalm<ep>_<plat>.mp4"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
EP, RS, SS, HL = sys.argv[1:5]
STAGE = sys.argv[5] if len(sys.argv) > 5 else "all"
D = f"/home/claude/psalm{EP}"
PL = ["youtube", "instagram", "tiktok"]
FPS = 30
os.makedirs(f"{D}/out", exist_ok=True)
os.makedirs(f"{D}/seg", exist_ok=True)
VM = {p: json.load(open(f"{D}/vomap_{p}.json")) for p in PL}
cutF = int(VM["youtube"]["callout"]["cut"] * FPS)


def render(plat, path, n0, n1):
    env = dict(os.environ, VOMAP=f"{D}/vomap_{plat}.json")
    subprocess.run(["python3", RS, "video", path, str(n0), str(n1)], env=env, check=True)
    return path


def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *a], check=True)


def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


if STAGE in ("video", "all", "tail"):
    half = cutF // 2
    jobs = [] if STAGE == "tail" else [("youtube", f"{D}/seg/a1.mp4", 0, half), ("youtube", f"{D}/seg/a2.mp4", half, cutF)]
    jobs += [(p, f"{D}/seg/b_{p}.mp4", cutF, int(round(VM[p]["video_dur"] * FPS))) for p in PL]
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(lambda j: render(*j), jobs))
    for p in PL:
        lst = f"{D}/seg/list_{p}.txt"
        open(lst, "w").write(f"file '{D}/seg/a1.mp4'\nfile '{D}/seg/a2.mp4'\nfile '{D}/seg/b_{p}.mp4'\n")
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{D}/video_only_{p}.mp4")
    print("video done")

if STAGE in ("audio", "all", "tail"):
    for p in PL:
        env = dict(os.environ, VOMAP=f"{D}/vomap_{p}.json")
        subprocess.run(["python3", SS], env=env, check=True)
        subprocess.run(["python3", "/home/claude/captions_gen.py", EP, HL], env=env, check=True)
        dur = VM[p]["video_dur"]
        sfx = f"{D}/sfx_{p}.wav"
        voice = f"{D}/voice_{p}.wav"
        lv, ls = lufs(voice), lufs(sfx)
        gdb = (lv - 6.0) - ls
        g = 10 ** (gdb / 20)
        print(f"{p}: voice {lv} LUFS, sfx {ls} LUFS -> sfx gain {gdb:.1f} dB")
        fc = (f"[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay=250:all=1,apad,asplit=2[v1][vsc];[2:a]aresample=48000,volume={g:.4f}[sfx];"
              f"[sfx][vsc]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=300[duck];"
              f"[v1][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.84:level=false[a]")
        nc = f"{D}/out/psalm{EP}_{p}_nocaptions.mp4"
        ff("-i", f"{D}/video_only_{p}.mp4", "-i", voice, "-i", sfx, "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(dur), "-movflags", "+faststart", nc)
        m = json.load(open(f"{D}/caps_{p}/meta.json"))
        ff("-i", nc, *m["inputs"], "-filter_complex_script", f"{D}/caps_{p}/filter.txt", "-map", m["last"], "-map", "0:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy",
           "-movflags", "+faststart", f"{D}/out/psalm{EP}_{p}.mp4")
        print(p, "final written")
