"""从国家法律法规数据库(flk.npc.gov.cn)下载现行有效法律原文到 知识库原文/。只使用官方数据源。"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://flk.npc.gov.cn"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "知识库原文")
LAWS = [
    "中华人民共和国民法典",
    "中华人民共和国劳动合同法",
    "中华人民共和国劳动法",
    "中华人民共和国劳动争议调解仲裁法",
    "中华人民共和国消费者权益保护法",
    "中华人民共和国道路交通安全法",
]
UA = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json;charset=UTF-8",
      "Referer": BASE + "/search", "Origin": BASE}


def req(path, data=None, params=None, raw=False):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, headers=UA, method="POST" if body else "GET")
    with urllib.request.urlopen(r, timeout=30) as resp:
        b = resp.read()
        return b if raw else json.loads(b.decode("utf-8"))


def search(name):
    body = {"searchRange": 1, "sxrq": [], "gbrq": [], "searchType": 2, "sxx": [], "gbrqYear": [],
            "flfgCodeId": [], "zdjgCodeId": [], "searchContent": name, "orderByParam": {"order": "-1", "sort": ""},
            "pageNum": 1, "pageSize": 20}
    return req("/law-search/search/list", body)


def clean(t):
    return t.replace("<em class='highlight'>", "").replace("</em>", "")


def find_current(name):
    rows = search(name).get("rows", [])
    hits = [r for r in rows if clean(r["title"]) == name and r.get("sxx") == 3]
    hits.sort(key=lambda r: r.get("gbrq") or "", reverse=True)
    return hits[0] if hits else None


def download(name):
    h = find_current(name)
    if not h:
        print(f"[未找到现行有效版本] {name}")
        return None
    d = req("/law-search/download/pc", params={"format": "docx", "bbbs": h["bbbs"], "fileId": ""})
    url = (d.get("data") or {}).get("url")
    if not url:
        print(f"[无下载地址] {name}: {json.dumps(d, ensure_ascii=False)[:300]}")
        return None
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        data = resp.read()
    path = os.path.join(OUT, name + ".docx")
    with open(path, "wb") as f:
        f.write(data)
    meta = {"name": name, "title": clean(h["title"]), "bbbs": h["bbbs"], "gbrq": h.get("gbrq"),
            "sxrq": h.get("sxrq"), "zdjg": h.get("zdjgName"), "bytes": len(data)}
    print(meta)
    return meta


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    metas = []
    for n in LAWS:
        m = download(n)
        if m:
            metas.append(m)
        time.sleep(1.5)
    with open(os.path.join(OUT, "_来源记录.json"), "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)
    print(f"完成 {len(metas)}/{len(LAWS)}")
