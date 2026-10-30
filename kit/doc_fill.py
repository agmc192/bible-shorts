"""Build a Script Library update for finished psalms.
Usage: doc_fill.py <saved read_doc json> <status> <ep:tabId> [<ep:tabId> ...]  -> prints {rev, requests}
Fills STATUS, platform copy, VIDEO (three links) and THUMBNAIL for each tab from /home/claude/psalm<ep>/copy.json."""
import json, sys
f, status, pairs = sys.argv[1], sys.argv[2], sys.argv[3:]
d = json.load(open(f))["content"]
def walk(tabs):
    for t in tabs:
        yield t; yield from walk(t.get("childTabs", []))
tabs = {t["tabProperties"]["tabId"]: t for t in walk(d["tabs"])}
u16 = lambda s: len(s.encode("utf-16-le")) // 2
reqs = []
for pr in pairs:
    ep, tid = pr.split(":")
    cells = []
    for el in tabs[tid]["documentTab"]["body"]["content"]:
        if "table" in el:
            for r in el["table"]["tableRows"]:
                c = r["tableCells"][0]
                txt = "".join(pe.get("textRun", {}).get("content", "") for p in c["content"] if "paragraph" in p for pe in p["paragraph"]["elements"])
                cells.append((c["content"][0]["startIndex"], c["content"][-1]["endIndex"], txt.strip()))
            break
    lab = {cells[i][2]: i + 1 for i in range(0, len(cells), 2)}
    cp = json.load(open(f"/home/claude/psalm{ep}/copy.json"))
    num = ep
    N = "".join(ch for ch in ep if ch.isdigit()).zfill(3) + "".join(ch for ch in ep if ch.isalpha())
    base = f"https://github.com/agmc192/bible-shorts/blob/main/episodes/psalm-{N}/"
    edits = {"STATUS": status, "YOUTUBE TITLE": cp["youtube_title"], "YOUTUBE DESCRIPTION": cp["youtube_description"],
             "INSTAGRAM CAPTION": cp["instagram_caption"], "TIKTOK CAPTION": cp["tiktok_caption"],
             "VIDEO": f"YouTube: {base}psalm{num}_youtube.mp4\nInstagram: {base}psalm{num}_instagram.mp4\nTikTok: {base}psalm{num}_tiktok.mp4",
             "THUMBNAIL": f"{base}psalm{num}_thumbnail.png"}
    items = sorted(((cells[lab[k]], k, v) for k, v in edits.items()), key=lambda x: -x[0][0])
    for (s, e, old), k, txt in items:
        if e - 1 > s:
            reqs.append({"deleteContentRange": {"range": {"startIndex": s, "endIndex": e - 1, "tabId": tid}}})
        reqs.append({"insertText": {"location": {"index": s, "tabId": tid}, "text": txt}})
        if k in ("VIDEO", "THUMBNAIL"):
            off = 0
            for line in txt.split("\n"):
                url = line.split(": ", 1)[-1]
                st = s + off + u16(line) - u16(url)
                reqs.append({"updateTextStyle": {"range": {"startIndex": st, "endIndex": st + u16(url), "tabId": tid}, "textStyle": {"link": {"url": url}}, "fields": "link"}})
                off += u16(line) + 1
print(json.dumps({"rev": d["revisionId"], "requests": reqs}, ensure_ascii=False))
