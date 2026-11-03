"""为人工评判生成材料：逐题列出回答全文，以及回答中每条"《法律》第X条"在知识库原文中是否存在、原文内容。
不自动判分，只提供核对依据。用法：python make_judge_packet.py results_xxx.csv [更多 csv]
"""
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(HERE, "..", "智能体", "知识库")
CITE = re.compile(r"《([^》]{2,40})》\s*第([零〇一二三四五六七八九十百千]+)条")
SEG = re.compile(r"^《([^》]+)》第([零〇一二三四五六七八九十百千]+)条（[^）]*）(.*)$", re.S)


def short(name):
    return name.replace("中华人民共和国", "").strip()


def load_kb():
    kb = {}
    for f in glob.glob(os.path.join(KB_DIR, "*.txt")):
        for seg in open(f, encoding="utf-8").read().strip().split("\n\n"):
            m = SEG.match(seg.strip())
            if m:
                kb[(short(m.group(1)), m.group(2))] = m.group(3).strip()
    return kb


def main():
    kb = load_kb()
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        out = os.path.splitext(path)[0] + "_评判材料.md"
        with open(out, "w", encoding="utf-8") as w:
            w.write(f"# 评判材料：{os.path.basename(path)}\n\n知识库条目数：{len(kb)}\n\n")
            for r in rows:
                w.write(f"## 第{r['id']}题 [{r['category']}] {r['question']}\n\n")
                w.write(f"- 预期法律：{r['expected_law']}\n- 预期条文：{r['expected_articles'] or '无'}\n")
                if r["error"]:
                    w.write(f"- **调用错误**：{r['error']}\n")
                w.write("\n### 回答原文\n\n")
                ans = re.sub(r"\[(\d+)\] \[[^\]]*\]\(https?://[^)]*\)", r"[\1] (知识库来源链接已省略)", r["answer"])
                w.write(ans.strip() + "\n\n### 引用核对\n\n")
                seen = []
                for m in CITE.finditer(r["answer"]):
                    key = (short(m.group(1)), m.group(2))
                    if key not in seen:
                        seen.append(key)
                if not seen:
                    w.write("（回答中没有\"《法律》第X条\"形式的引用）\n\n")
                for law, no in seen:
                    text = kb.get((law, no))
                    if text is None:
                        w.write(f"- 《{law}》第{no}条：**知识库中不存在该条**（可能为知识库外法律或编造，需人工判断）\n")
                    else:
                        w.write(f"- 《{law}》第{no}条：存在。原文：{text}\n")
                w.write("\n---\n\n")
        print("已生成", out)


if __name__ == "__main__":
    main()
