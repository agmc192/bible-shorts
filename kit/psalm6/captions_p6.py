import sys, json, os, re
sys.path.insert(0, "/home/claude/psalm1")
from PIL import Image, ImageDraw
import render as R
M = json.load(open("/home/claude/psalm6/vomap.json"))
HL = {"cried", "noticed", "david", "raw", "groaning", "night", "floods", "tears", "bones", "soul", "shaken", "enemies", "end", "turns", "lord", "heard", "weeping", "accepts", "prayer", "changed", "hebrew", "ahdmahtie", "admatay", "until", "when", "finish", "sentence", "god", "hears", "tonight", "half"}
os.makedirs("/home/claude/psalm6/caps", exist_ok=True)
chunks = []
for a, b, ph in M["phrases"]:
    ws = [w for w in M["words"] if a - 0.001 <= w[0] < b - 0.001]
    groups, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 3 or w[2][-1] in ".,?!:\"" or w[2].endswith(',"'):
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    for gi, g in enumerate(groups):
        st = g[0][0] - 0.05
        en = groups[gi + 1][0][0] - 0.05 if gi + 1 < len(groups) else b + 0.15
        chunks.append([st, en, [w[2] for w in g]])
for i in range(len(chunks) - 1):
    if 0 < chunks[i + 1][0] - chunks[i][1] < 0.25:
        chunks[i][1] = chunks[i + 1][0]
def disp(w):
    w = w.replace("ahd-mah-TIE", "‘ad-matay").replace('"', "").replace("“", "").replace("”", "")
    return w if w.endswith("?") else w.rstrip(".,:;!")
def png(words, path):
    size, stroke = 92, 8
    while True:
        f = R.font(R.F_CAP, size)
        ds = [disp(w) for w in words]
        sp = f.getlength(" "); wd = [f.getlength(w) for w in ds]
        tot = sum(wd) + sp * (len(ds) - 1)
        if tot < 960 or size < 60: break
        size -= 4
    asc, desc = f.getmetrics(); pad = 24
    im = Image.new("RGBA", (int(tot + pad * 2 + stroke * 2), int(asc + desc + pad * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = pad + stroke
    for w, ww in zip(ds, wd):
        hl = re.sub(r"[^a-z]", "", w.lower().replace("'s", "")) in HL
        d.text((x, pad), w, font=f, fill=(227, 176, 75, 255) if hl else (255, 249, 238, 255),
               stroke_width=stroke, stroke_fill=(43, 29, 20, 255))
        x += ww + sp
    im.save(path); return im.size
inputs, filt, prev = [], [], "[0:v]"
for i, (s, e, g) in enumerate(chunks):
    p = f"/home/claude/psalm6/caps/c{i:03d}.png"; w, h = png(g, p)
    inputs += ["-i", p]; out = f"[v{i}]"
    filt.append(f"{prev}[{i+1}:v]overlay=x=(W-{w})/2:y=1560-{h}/2:enable='between(t,{s:.3f},{e:.3f})'{out}"); prev = out
open("/home/claude/psalm6/caps/filter.txt", "w").write(";".join(filt))
json.dump({"inputs": inputs, "last": prev}, open("/home/claude/psalm6/caps/meta.json", "w"))
for s, e, g in chunks[:8]: print(f"{s:6.2f}-{e:6.2f} {' '.join(g)}")
print(len(chunks), "chunks")
