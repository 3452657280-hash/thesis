"""读取人工评判后的结果 CSV，计算论文第5章指标。用法：python stats.py results_kb_xxx.csv [results_baseline_xxx.csv]"""
import csv
import statistics
import sys


def load(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def rate(rows, col):
    vals = [r[col] for r in rows if r[col] in ("0", "1")]
    if not vals:
        return None, 0
    return sum(v == "1" for v in vals) / len(vals), len(vals)


def report(path):
    rows = load(path)
    law = [r for r in rows if r["category"] != "非法律问题"]
    non = [r for r in rows if r["category"] == "非法律问题"]
    unjudged = [r["id"] for r in law if r["judge_law_correct"] not in ("0", "1")]
    print(f"== {path}  共{len(rows)}题")
    if unjudged:
        print(f"  [注意] 以下法律题尚未人工评判 judge_law_correct：{unjudged}")
    for name, col, sub in [("领域判断一致率", "judge_category", law), ("法律依据正确率", "judge_law_correct", law),
                           ("非法律问题拒答率", "judge_refuse", non), ("免责声明附带率", "judge_disclaimer", rows)]:
        v, n = rate(sub, col)
        print(f"  {name}: {'未评判' if v is None else f'{v:.1%} ({n}题)'}")
    for col in ("client_first_token_ms", "client_total_ms"):
        xs = sorted(float(r[col]) for r in rows if r[col])
        if xs:
            p90 = xs[min(len(xs) - 1, int(len(xs) * 0.9))]
            print(f"  {col}: 平均 {statistics.mean(xs):.0f} ms, 中位数 {statistics.median(xs):.0f} ms, P90 {p90:.0f} ms")
    errs = [r["id"] for r in rows if r["error"]]
    print(f"  调用失败: {len(errs)} 题 {errs}")


for p in sys.argv[1:]:
    report(p)
