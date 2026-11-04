"""后端并发性能测试（演示模式实例，不调用 Coze）：
1) 普通接口：N 个并发用户反复请求法条检索、会话列表，统计吞吐量与响应时间；
2) 流式对话：N 个用户各自在独立会话中同时发起流式问答，统计首个事件与完成耗时。
用法：python perf_test.py [--base http://localhost:8082]
"""
import argparse
import concurrent.futures as cf
import csv
import datetime
import json
import os
import statistics
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def req(base, method, path, token=None, body=None):
    r = urllib.request.Request(base + path, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    t = time.perf_counter()
    with urllib.request.urlopen(r, data=data, timeout=60) as resp:
        out = json.loads(resp.read().decode())
    return out, (time.perf_counter() - t) * 1000


def stream(base, token, sid, content):
    r = urllib.request.Request(f"{base}/api/consult/sessions/{sid}/chat", method="POST")
    r.add_header("Content-Type", "application/json")
    r.add_header("Authorization", "Bearer " + token)
    t0 = time.perf_counter()
    first = None
    ok = False
    with urllib.request.urlopen(r, data=json.dumps({"content": content}).encode(), timeout=120) as resp:
        ev = None
        for line in resp:
            line = line.decode().strip()
            if line.startswith("event:"):
                ev = line[6:].strip()
                if ev == "delta" and first is None:
                    first = (time.perf_counter() - t0) * 1000
                if ev == "done":
                    ok = True
    return first, (time.perf_counter() - t0) * 1000, ok


def summary(xs):
    xs = sorted(xs)
    return {"n": len(xs), "avg": statistics.mean(xs), "p50": statistics.median(xs),
            "p90": xs[min(len(xs) - 1, int(len(xs) * 0.9))], "max": xs[-1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8082")
    a = ap.parse_args()
    base = a.base
    stamp = datetime.datetime.now().strftime("%H%M%S")
    tokens = []
    for i in range(50):
        u = f"pf{stamp}_{i}"
        req(base, "POST", "/api/auth/register", body={"username": u, "password": "abc123", "role": "USER"})
        tokens.append(req(base, "POST", "/api/auth/login", body={"username": u, "password": "abc123"})[0]["data"]["token"])
    kw = urllib.parse.quote("工资")
    rows = []

    def api_round(tok):
        ts = []
        for _ in range(10):
            _, t1 = req(base, "GET", f"/api/public/laws?keyword={kw}&page=1&size=10")
            _, t2 = req(base, "GET", "/api/consult/sessions", tok)
            ts += [t1, t2]
        return ts

    for n in (10, 20, 50):
        t0 = time.perf_counter()
        with cf.ThreadPoolExecutor(n) as ex:
            res = list(ex.map(api_round, tokens[:n]))
        wall = time.perf_counter() - t0
        allt = [x for r in res for x in r]
        s = summary(allt)
        rows.append({"场景": "普通接口（法条检索+会话列表）", "并发数": n, "请求总数": s["n"], "失败数": 0,
                     "吞吐量(次/秒)": round(s["n"] / wall, 1), "平均(ms)": round(s["avg"], 1),
                     "P90(ms)": round(s["p90"], 1), "最大(ms)": round(s["max"], 1)})
        print(rows[-1])

    def chat_one(tok):
        sid = req(base, "POST", "/api/consult/sessions", tok, body={})[0]["data"]["id"]
        return stream(base, tok, sid, "公司拖欠工资怎么办？")

    for n in (10, 20, 50):
        with cf.ThreadPoolExecutor(n) as ex:
            res = list(ex.map(chat_one, tokens[:n]))
        firsts = [r[0] for r in res if r[0] is not None]
        totals = [r[1] for r in res]
        fail = sum(not r[2] for r in res)
        f, t = summary(firsts), summary(totals)
        rows.append({"场景": "流式对话（演示模式）", "并发数": n, "请求总数": n, "失败数": fail,
                     "吞吐量(次/秒)": "-", "平均(ms)": f"首事件{f['avg']:.0f}/完成{t['avg']:.0f}",
                     "P90(ms)": f"首事件{f['p90']:.0f}/完成{t['p90']:.0f}", "最大(ms)": f"完成{t['max']:.0f}"})
        print(rows[-1])

    out = os.path.join(HERE, f"性能测试结果_{datetime.date.today():%Y%m%d}.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("结果：", out)


if __name__ == "__main__":
    main()
