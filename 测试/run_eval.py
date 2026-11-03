"""通过系统后端接口批量运行智能体测试集，记录原始回答与耗时。不做自动判分。

用法：python run_eval.py --label kb [--base http://localhost:8080] [--user user1 --password 123456] [--limit N]
"""
import argparse
import csv
import datetime
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CITE = re.compile(r"《([^》]{2,40})》\s*(第[一二三四五六七八九十百千零〇]+条)?")


def call(base, path, token=None, body=None, method="GET"):
    req = urllib.request.Request(base + path, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(req, data=data, timeout=60) as r:
        res = json.loads(r.read().decode())
    if res.get("code") != 200:
        raise RuntimeError(res)
    return res["data"]


def chat(base, token, sid, question):
    req = urllib.request.Request(f"{base}/api/consult/sessions/{sid}/chat", method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "text/event-stream")
    t0 = time.perf_counter()
    first, parts, done, err, event = None, [], {}, "", None
    with urllib.request.urlopen(req, data=json.dumps({"content": question}).encode(), timeout=200) as r:
        for raw in r:
            line = raw.decode("utf-8").rstrip("\r\n")
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                payload = json.loads(line[5:].strip())
                if event == "delta":
                    if first is None:
                        first = (time.perf_counter() - t0) * 1000
                    parts.append(payload.get("content", ""))
                elif event == "done":
                    done = payload
                elif event == "error":
                    err = payload.get("msg", "")
    total = (time.perf_counter() - t0) * 1000
    return "".join(parts), first, total, done, err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="本次实验标签，如 kb / baseline")
    ap.add_argument("--base", default="http://localhost:8080")
    ap.add_argument("--user", default="user1")
    ap.add_argument("--password", default="123456")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids-file", default="", help="只跑文件中列出的题号（每行一个）")
    a = ap.parse_args()

    token = call(a.base, "/api/auth/login", body={"username": a.user, "password": a.password}, method="POST")["token"]
    with open(os.path.join(HERE, "testset.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if a.ids_file:
        with open(a.ids_file, encoding="utf-8") as f:
            ids = {line.split("#")[0].strip() for line in f} - {""}
        rows = [r for r in rows if r["id"] in ids]
    if a.limit:
        rows = rows[: a.limit]

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(HERE, f"results_{a.label}_{stamp}.csv")
    fields = ["id", "category", "question", "expected_law", "expected_articles", "answer", "citations",
              "client_first_token_ms", "client_total_ms", "server_first_token_ms", "server_response_ms", "error",
              "judge_category", "judge_law_correct", "judge_refuse", "judge_disclaimer"]
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            sid = call(a.base, "/api/consult/sessions", token, body={}, method="POST")["id"]
            try:
                ans, first, total, done, err = chat(a.base, token, sid, r["question"])
            except Exception as e:
                ans, first, total, done, err = "", None, None, {}, str(e)
            cites = ";".join(sorted({m.group(0).strip() for m in CITE.finditer(ans)}))
            w.writerow({**{k: r[k] for k in ("id", "category", "question", "expected_law", "expected_articles")},
                        "answer": ans, "citations": cites,
                        "client_first_token_ms": round(first) if first else "",
                        "client_total_ms": round(total) if total else "",
                        "server_first_token_ms": done.get("firstTokenMs", ""),
                        "server_response_ms": done.get("responseMs", ""), "error": err,
                        "judge_category": "", "judge_law_correct": "", "judge_refuse": "", "judge_disclaimer": ""})
            f.flush()
            print(f"[{r['id']}] {r['category']} {'ERR ' + err if err else 'ok'} {round(total or 0)}ms")
    print("结果已保存:", out)


if __name__ == "__main__":
    main()
