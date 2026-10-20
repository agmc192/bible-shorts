import json, os, sys, subprocess
import numpy as np
os.environ["CAPTIONS"] = "0"
import render_v2 as V

M = json.load(open("/home/claude/psalm1/vo/timemap.json"))
NEW, ORIG = np.array(M["new"]), np.array(M["orig"])
FPS = V.FPS

def video(path, n0, n1):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{V.W}x{V.H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n0, n1):
        t = float(np.interp(i / FPS, NEW, ORIG))
        p.stdin.write(bytes(V.render_frame(t).get_data()))
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    video(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
