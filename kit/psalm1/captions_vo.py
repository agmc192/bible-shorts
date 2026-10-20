import os, json, subprocess, io, contextlib
from PIL import Image, ImageDraw
with contextlib.redirect_stdout(io.StringIO()):
    import retime_map as M
import render as R

os.makedirs("/home/claude/psalm1/caps", exist_ok=True)
chunks, wi = [], 0
for (a, b), ph in zip(M.spans, M.PHRASES):
    ws = ph.split()
    times = [M.new_words[wi + k][0] for k in range(len(ws))]
    groups, cur = [], []
    for k, w in enumerate(ws):
        cur.append(k)
        if len(cur) >= 3 or w[-1] in ".,?!:":
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    for gi, g in enumerate(groups):
        st = times[g[0]] - 0.05
        en = times[groups[gi + 1][0]] - 0.05 if gi + 1 < len(groups) else b + M.OFFSET + 0.15
        chunks.append((st, en, [ws[k] for k in g]))
    wi += len(ws)
# close tiny gaps between phrases so captions don't flicker
for i in range(len(chunks) - 1):
    s, e, g = chunks[i]
    ns = chunks[i + 1][0]
    if 0 < ns - e < 0.25:
        chunks[i] = (s, ns, g)

def cap_png(words, path):
    size, stroke = 92, 8
    while True:
        f = R.font(R.F_CAP, size)
        disp = [R.clean(w) if not w.endswith("?") else w.strip('"') for w in words]
        sp = f.getlength(" ")
        wd = [f.getlength(w) for w in disp]
        tot = sum(wd) + sp * (len(disp) - 1)
        if tot < 960 or size < 60:
            break
        size -= 4
    asc, desc = f.getmetrics()
    pad = 24
    im = Image.new("RGBA", (int(tot + pad * 2 + stroke * 2), int(asc + desc + pad * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad + stroke
    for w, ww in zip(disp, wd):
        hl = w.lower().strip("?'").replace("'s", "") in R.HIGHLIGHT
        d.text((x, pad), w, font=f, fill=(227, 176, 75, 255) if hl else (255, 249, 238, 255),
               stroke_width=stroke, stroke_fill=(43, 29, 20, 255))
        x += ww + sp
    im.save(path)
    return im.size

inputs, filt, prev = [], [], "[0:v]"
for i, (s, e, g) in enumerate(chunks):
    p = f"/home/claude/psalm1/caps/c{i:03d}.png"
    w, h = cap_png(g, p)
    inputs += ["-i", p]
    out = f"[v{i}]"
    filt.append(f"{prev}[{i+1}:v]overlay=x=(W-{w})/2:y=1560-{h}/2:enable='between(t,{s:.3f},{e:.3f})'{out}")
    prev = out
open("/home/claude/psalm1/caps/filter.txt", "w").write(";".join(filt))
json.dump({"inputs": inputs, "last": prev, "n": len(chunks)}, open("/home/claude/psalm1/caps/meta.json", "w"))
for s, e, g in chunks[:6]:
    print(f"{s:6.2f}-{e:6.2f} {' '.join(g)}")
print(len(chunks), "caption chunks")
