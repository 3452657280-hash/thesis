"""配音时长 → <motion>/timing.js，配音整轨 → <motion>/audio/voice.wav，
可选调用 motion-showreel 的 render.mjs 逐帧渲染 + inspect.mjs 技术检查。

用法（在 video/ 目录下，用装了 edge-tts 的 python）:
  python motion_prep.py                                   # 全部场景，只配音+时间轴
  python motion_prep.py --render --out Explainer_v1.mp4   # 全片渲染
  python motion_prep.py --script script_en.yaml --motion motion_en --render --out Explainer_EN_v1.mp4
  python motion_prep.py --stills "12,40,95"               # 静帧预览 → <motion>/qa/stills/sheet.png
--scenes 不填 = yaml 里全部场景（只做样片时才填子集，渲全片前务必恢复全部）。
"""
import argparse
import json
import math
import re
import subprocess

import yaml

from common import BUILD, FFMPEG, NODE, OUT, ROOT, SHOWREEL, tool_env
from tts import synth_lines

PAD_LEAD, PAD_LINE, PAD_TAIL = 0.60, 0.30, 0.90   # 段首 / 句间 / 段尾留白（秒）
ZH_SUB_MAX, EN_SUB_MAX = 22, 62                     # 每条字幕最多字数 / 字符数


def split_sub_zh(text, start, end):
    parts = [p for p in re.split(r"(?<=[，、；：,])", text) if p.strip()]
    chunks, buf = [], ""
    for p in parts:
        if buf and len(buf) + len(p) > ZH_SUB_MAX:
            chunks.append(buf)
            buf = p
        else:
            buf += p
    if buf:
        if chunks and len(buf) <= 6 and len(chunks[-1]) + len(buf) <= ZH_SUB_MAX + 6:
            chunks[-1] += buf
        else:
            chunks.append(buf)
    return _spread(chunks, start, end, "，、；：,")


def split_sub_en(text, start, end):
    words = text.split()
    n = max(1, math.ceil(len(text) / EN_SUB_MAX))
    target = len(text) / n
    chunks, buf = [], ""
    for w in words:
        cand = f"{buf} {w}".strip()
        if buf and len(cand) > EN_SUB_MAX:
            chunks.append(buf)
            buf = w
            continue
        buf = cand
        if len(chunks) < n - 1 and ((w[-1] in ",;:.?!" and len(buf) >= 0.55 * target) or len(buf) >= target):
            chunks.append(buf)
            buf = ""
    if buf:
        if chunks and len(buf) < 18 and len(chunks[-1]) + 1 + len(buf) <= EN_SUB_MAX + 12:
            chunks[-1] += " " + buf
        else:
            chunks.append(buf)
    return _spread(chunks, start, end, ",;:")


def _spread(chunks, start, end, strip):
    total = sum(len(c) for c in chunks)
    out, t = [], start
    for c in chunks:
        d = (end - start) * len(c) / total
        out.append((t, t + d, c.rstrip(strip)))
        t += d
    return out


def lufs(path) -> float:
    err = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, errors="ignore").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="script.yaml")
    ap.add_argument("--motion", default="motion")
    ap.add_argument("--scenes", default="")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--out", default="Explainer_v1.mp4")
    ap.add_argument("--stills", default="", help='静帧秒数，如 "12,40,95"（不重配音）')
    args = ap.parse_args()
    motion = ROOT / args.motion

    if args.stills:
        stills(motion, args.stills)
        return

    spec = yaml.safe_load((ROOT / args.script).read_text(encoding="utf-8"))
    en = spec["voice"].startswith("en-")
    scenes = spec["scenes"]
    if args.scenes:
        want = args.scenes.split(",")
        scenes = [s for s in scenes if s["id"] in want]

    t, out_scenes, subs, parts = 0.0, [], [], []
    for sc in scenes:
        voiced = synth_lines(sc["lines"], spec["voice"], spec["rate"])
        lines, t0 = [], t
        for li, (text, (mp3, dur)) in enumerate(zip(sc["lines"], voiced)):
            lead = PAD_LEAD if li == 0 else 0.0
            tail = PAD_TAIL if li == len(sc["lines"]) - 1 else PAD_LINE
            a, b = t + lead, t + lead + dur
            lines.append({"t0": round(a, 3), "t1": round(b, 3), "text": text})
            pieces = split_sub_en(text, a, b) if en else split_sub_zh(text.rstrip("。"), a, b)
            subs += [{"t0": round(x, 3), "t1": round(y, 3), "text": s} for x, y, s in pieces]
            parts.append((mp3, lead, dur, tail))
            t += lead + dur + tail
        out_scenes.append({"id": sc["id"], "t0": round(t0, 3), "t1": round(t, 3), "lines": lines})

    (motion / "audio").mkdir(parents=True, exist_ok=True)
    (motion / "timing.js").write_text(
        "// 由 motion_prep.py 生成，勿手改：配音驱动的时间轴（秒）\n"
        f"export const SCENES = {json.dumps(out_scenes, ensure_ascii=False, indent=1)};\n"
        f"export const SUBS = {json.dumps(subs, ensure_ascii=False, indent=1)};\n"
        f"export const DUR = {round(t, 3)};\n", encoding="utf-8")

    inputs, chain, labels = [], [], []
    for k, (mp3, lead, dur, tail) in enumerate(parts):
        inputs += ["-i", mp3]
        chain.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,atrim=0:{dur:.3f},"
                     f"adelay={int(lead * 1000)}:all=1,apad=whole_dur={lead + dur + tail:.3f},"
                     f"atrim=0:{lead + dur + tail:.3f},asetpts=N/SR/TB[a{k}]")
        labels.append(f"[a{k}]")
    chain.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[a]")
    raw, final = motion / "audio" / "voice_raw.wav", motion / "audio" / "voice.wav"
    subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", *inputs,
                    "-filter_complex", ";".join(chain), "-map", "[a]", "-ar", "48000", str(raw)], check=True)
    gain = 0.0
    for _ in range(4):  # 压缩 + 增益 + 限幅，迭代逼近 -14 LUFS
        gain += -14.0 - (lufs(raw) if gain == 0.0 else lufs(final))
        subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-af",
                        f"acompressor=threshold=-24dB:ratio=3:attack=5:release=80,volume={gain:.2f}dB,"
                        "alimiter=limit=0.72:attack=2:release=50:level=false", "-ar", "48000", str(final)], check=True)
        if abs(lufs(final) + 14.0) < 0.5:
            break
    print(f"timing.js  DUR={t:.2f}s  scenes={[s['id'] for s in out_scenes]}  subs={len(subs)}")
    for s in out_scenes:
        print(f"  {s['id']:<20} t0={s['t0']:>7.1f}  lines t0: {[round(l['t0'], 1) for l in s['lines']]}")
    if args.render:
        render(motion, round(t, 3), args.out)


def node(*a):
    subprocess.run([str(NODE), *map(str, a)], check=True, env=tool_env(), cwd=ROOT)


def render(motion, dur, out_name) -> None:
    OUT.mkdir(exist_ok=True)
    out = OUT / out_name
    node(SHOWREEL / "render.mjs", motion, "--determinism")
    node(SHOWREEL / "render.mjs", motion, "--fps", 30, "--size", "1920x1080", "--workers", 4,
         "--audio", motion / "audio" / "voice.wav", "--out", out)
    node(SHOWREEL / "inspect.mjs", "qa", out, "--out", motion / "qa" / "final", "--expect-size", "1920x1080",
         "--expect-fps", 30, "--expect-duration", dur, "--audio", "required")


def stills(motion, times) -> None:
    node(SHOWREEL / "render.mjs", motion, "--still", times, "--out", motion / "qa" / "stills", "--sheet")


if __name__ == "__main__":
    main()
