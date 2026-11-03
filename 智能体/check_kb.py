"""校验知识库：条文数是否等于最后一条的条号、条号是否连续。"""
import glob
import os
import re

DIG = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
UNIT = {"十": 10, "百": 100, "千": 1000}


def cn2int(s):
    total, num = 0, 0
    for ch in s:
        if ch in DIG:
            num = DIG[ch]
        elif ch in UNIT:
            total += (num or 1) * UNIT[ch]
            num = 0
    return total + num


HERE = os.path.dirname(os.path.abspath(__file__))
ok = True
for f in sorted(glob.glob(os.path.join(HERE, "知识库", "*.txt"))):
    segs = open(f, encoding="utf-8").read().strip().split("\n\n")
    nos = [cn2int(re.search(r"》第([一二三四五六七八九十百千零〇]+)条", s).group(1)) for s in segs]
    gaps = [i + 1 for i, n in enumerate(nos) if n != i + 1]
    longest = max(len(s) for s in segs)
    status = "OK" if not gaps else f"不连续，首个异常位置 {gaps[:5]}"
    ok &= not gaps
    print(f"{os.path.basename(f)}: {len(segs)} 段, 最后条号 {nos[-1]}, 最长段 {longest} 字, {status}")
    print("   首段:", segs[0][:70].replace("\n", " "))
    print("   末段:", segs[-1][:70].replace("\n", " "))
print("全部通过" if ok else "存在问题")
