"""把从国家法律法规数据库下载的法律 Word/TXT 原文整理为"一条一段"的知识库文档与法条入库 SQL。

用法：python build_kb.py
输入：智能体/知识库原文/*.docx|*.txt（文件名即法律名称，如"中华人民共和国劳动合同法.docx"）
输出：智能体/知识库/<法律名>.txt（每条一段，段间空行，段首带《法律名》）
      code/sql/law_article_data.sql（导入 law_article 表）
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "知识库原文")
OUT = os.path.join(BASE, "知识库")
SQL = os.path.join(BASE, "..", "code", "sql", "law_article_data.sql")

ART = re.compile(r"^\s*(第[一二三四五六七八九十百千零〇]+条)\s*(.*)$")
CHAP = re.compile(r"^\s*(第[一二三四五六七八九十百千零〇]+[编章节])\s*(.*)$")


def read_lines(path):
    if path.lower().endswith(".docx"):
        from docx import Document
        return [p.text for p in Document(path).paragraphs]
    for enc in ("utf-8-sig", "gb18030"):
        try:
            with open(path, encoding=enc) as f:
                return f.read().splitlines()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法识别编码: {path}")


def parse(lines):
    articles, part, chap, cur = [], "", "", None
    for raw in lines:
        line = raw.strip().replace("\u3000", " ")
        if not line:
            continue
        m = ART.match(line)
        if m:
            if cur:
                articles.append(cur)
            chapter = "·".join(x for x in (part, chap) if x)
            cur = {"no": m.group(1), "chapter": chapter, "text": m.group(2).strip()}
            continue
        c = CHAP.match(line)
        if c and len(line) < 40:
            if cur:
                articles.append(cur)
                cur = None
            kind = c.group(1)[-1]
            if kind == "编":
                part, chap = line, ""
            elif kind == "章":
                chap = line
            continue
        if cur:
            cur["text"] += "\n" + line
    if cur:
        articles.append(cur)
    return articles


def esc(s):
    return s.replace("\\", "\\\\").replace("'", "''")


def main():
    if not os.path.isdir(SRC) or not os.listdir(SRC):
        print(f"请先把法律原文放到 {SRC}")
        sys.exit(1)
    os.makedirs(OUT, exist_ok=True)
    meta_path = os.path.join(SRC, "_来源记录.json")
    dates = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            dates = {m["name"]: m.get("sxrq") for m in json.load(f)}
    rows = []
    total = 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.lower().endswith((".docx", ".txt")):
            continue
        law = os.path.splitext(fn)[0]
        arts = parse(read_lines(os.path.join(SRC, fn)))
        if not arts:
            print(f"[警告] {fn} 未解析到条文")
            continue
        with open(os.path.join(OUT, law + ".txt"), "w", encoding="utf-8") as f:
            for a in arts:
                body = a["text"].replace("\n", " ")
                f.write(f"《{law}》{a['no']}（{a['chapter']}）{body}\n\n" if a["chapter"] else f"《{law}》{a['no']} {body}\n\n")
        d = f"'{dates[law]}'" if dates.get(law) else "NULL"
        for a in arts:
            rows.append(f"('{esc(law)}','{esc(a['chapter'])}','{a['no']}','{esc(a['text'])}',{d})")
        long_ = sum(1 for a in arts if len(a["text"]) > 800)
        print(f"{law}: {len(arts)} 条，超过800字的条文 {long_} 条")
        total += len(arts)
    head = "INSERT INTO law_article(law_name,chapter,article_no,content,effective_date) VALUES\n"
    body = "".join(head + ",\n".join(rows[i:i + 200]) + ";\n" for i in range(0, len(rows), 200))
    with open(SQL, "w", encoding="utf-8") as f:
        f.write("DELETE FROM law_article;\n" + body)
    print(f"合计 {total} 条；知识库输出 {OUT}；SQL 输出 {os.path.abspath(SQL)}")
    print("施行日期来自 知识库原文/_来源记录.json：", dates)


if __name__ == "__main__":
    main()
