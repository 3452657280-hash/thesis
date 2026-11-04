"""生成评判复核清单：知识库组全部判错题 + 固定随机种子抽取的10道判对题，列出评判理由，供逐题复核。"""
import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "results_kb_20261103_153932_judged.csv"), encoding="utf-8-sig") as f:
    rows = [r for r in csv.DictReader(f) if r["category"] != "非法律问题"]
wrong = [r for r in rows if r["judge_law_correct"] != "1"]
random.seed(20261104)
right = random.sample([r for r in rows if r["judge_law_correct"] == "1"], 10)
out = os.path.join(HERE, "评判复核清单.md")
with open(out, "w", encoding="utf-8") as w:
    w.write("# 评判复核清单\n\n对照 `results_kb_20261103_153932_评判材料.md` 中对应题号的回答原文与法条原文逐题确认，确认无误在方框内打勾。\n\n")
    for title, group in (("一、判为不正确的题（全部）", wrong), ("二、判为正确的题（随机抽查10题）", right)):
        w.write(f"## {title}\n\n")
        for r in sorted(group, key=lambda x: int(x["id"])):
            w.write(f"- [ ] **第{r['id']}题** [{r['category']}] {r['question']}\n  - 评判：{'正确' if r['judge_law_correct'] == '1' else '不正确'}；理由：{r['judge_note']}\n\n")
print(out, len(wrong), len(right))
