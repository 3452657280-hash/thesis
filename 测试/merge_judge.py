"""把评判 CSV 合并进结果 CSV，生成 *_judged.csv，并输出论文第5章所需统计。
用法：python merge_judge.py
"""
import csv
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, "评判")
COLS = ["judge_category", "judge_law_correct", "judge_refuse", "judge_disclaimer"]

# 人工复核修正：评判员C因公安部网站无法访问记为"无法核实"，复核时已在广东省人民政府门户网站
# (http://www.gd.gov.cn/zwgk/wjk/zcfgk/content/post_2723894.html，公安部令第146号全文)核对第六十条、第七十一条，内容相符。
OVERRIDES = {("baseline", "44"): {"judge_law_correct": "1",
                                  "note": "首次超时，以重试结果评判；《道路交通事故处理程序规定》第六十条与官方全文逐字相符，第七十一条（三日内书面申请复核）相符，复核后改为1"}}


def load(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def merge(results, judges, label, retry=None):
    rows = load(os.path.join(HERE, results))
    if retry:
        rmap = {r["id"]: r for r in load(os.path.join(HERE, retry))}
        for i, r in enumerate(rows):
            if r["id"] in rmap:
                r2 = dict(rmap[r["id"]])
                r2["error"] = f"首次调用失败（{r['error']}），重试成功" if r["error"] else r2["error"]
                rows[i] = r2
    jm = {}
    for jf in judges:
        for j in load(os.path.join(J, jf)):
            jm[j["id"]] = j
    for r in rows:
        j = dict(jm.get(r["id"], {}))
        j.update(OVERRIDES.get((label, r["id"]), {}))
        for c in COLS:
            r[c] = j.get(c, "")
        r["kb_external"] = j.get("kb_external", "")
        r["judge_note"] = j.get("note", "")
    out = os.path.join(HERE, results.replace(".csv", "_judged.csv"))
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows, out


def pct(a, b):
    return f"{a}/{b} = {a / b:.1%}" if b else "-"


def timing(rows):
    out = {}
    for col in ("client_first_token_ms", "client_total_ms"):
        xs = sorted(float(r[col]) for r in rows if r[col])
        p90 = xs[min(len(xs) - 1, int(len(xs) * 0.9))]
        out[col] = (statistics.mean(xs) / 1000, statistics.median(xs) / 1000, p90 / 1000, len(xs))
    return out


def report(rows, title):
    print(f"\n===== {title}（{len(rows)}题）=====")
    law = [r for r in rows if r["category"] != "非法律问题"]
    covered = [r for r in law if r["expected_law"] != "知识库未覆盖"]
    uncovered = [r for r in law if r["expected_law"] == "知识库未覆盖"]
    non = [r for r in rows if r["category"] == "非法律问题"]
    print("领域判断一致：", pct(sum(r["judge_category"] == "1" for r in law), len(law)))
    print("法律依据正确（全部法律题）：", pct(sum(r["judge_law_correct"] == "1" for r in law), len(law)))
    print("法律依据正确（知识库覆盖题）：", pct(sum(r["judge_law_correct"] == "1" for r in covered), len(covered)))
    if uncovered:
        print("知识库未覆盖题：", [(r["id"], r["judge_law_correct"], r["kb_external"]) for r in uncovered])
    if non:
        print("非法律问题拒答：", pct(sum(r["judge_refuse"] == "1" for r in non), len(non)))
    print("免责声明：", pct(sum(r["judge_disclaimer"] == "1" for r in rows), len(rows)))
    ext = [r for r in law if r["kb_external"] not in ("", "0")]
    print("引用了六部法律以外条文的法律题：", len(ext), [r["id"] for r in ext])
    print("调用失败/重试：", [(r["id"], r["error"]) for r in rows if r["error"]])
    for k, (m, med, p90, n) in timing(rows).items():
        print(f"{k}: 平均 {m:.1f}s 中位数 {med:.1f}s P90 {p90:.1f}s (n={n})")
    by = {}
    for r in law:
        by.setdefault(r["category"], []).append(r["judge_law_correct"] == "1")
    print("分类别法律依据正确：", {k: f"{sum(v)}/{len(v)}" for k, v in by.items()})
    print("0分题：", [(r["id"], r["judge_note"][:60]) for r in law if r["judge_law_correct"] != "1"])


kb, kb_out = merge("results_kb_20261103_153932.csv", ["judge_kb_A.csv", "judge_kb_B.csv"], "kb")
bl, bl_out = merge("results_baseline_20261103_155241.csv", ["judge_baseline.csv"], "baseline",
                   retry="results_baseline-retry_20261103_155916.csv")
report(kb, "知识库组")
report(bl, "对照组（无知识库）")
ids = {r["id"] for r in bl}
report([r for r in kb if r["id"] in ids], "知识库组·同20题")
law_bl = [r for r in bl]
kb20 = {r["id"]: r for r in kb if r["id"] in ids}
print("\n同题对照（id, 知识库组, 对照组）：", [(r["id"], kb20[r["id"]]["judge_law_correct"], r["judge_law_correct"]) for r in law_bl])
print("外部条文引用条数合计：知识库组20题", sum(int(kb20[i]["kb_external"] or 0) for i in ids),
      "对照组", sum(int(r["kb_external"] or 0) for r in bl))
print("\n已输出：", kb_out, bl_out)
