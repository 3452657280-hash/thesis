"""逐句配音：每句一个 mp3，按「音色+语速+文本」哈希缓存，改哪句只重配哪句。"""
import asyncio
import hashlib
import subprocess

import edge_tts

from common import BUILD, FFPROBE, patch_edge_tts_ssl

patch_edge_tts_ssl()
AUDIO = BUILD / "audio"


def line_path(text: str, voice: str, rate: str):
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode("utf-8")).hexdigest()[:12]
    return AUDIO / f"{key}.mp3"


def duration(path) -> float:
    out = subprocess.run(
        [str(FFPROBE), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


async def _synth(text: str, voice: str, rate: str, path) -> None:
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(str(path))
            return
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(2)


def synth_lines(lines: list[str], voice: str, rate: str) -> list[tuple[str, float]]:
    """返回 [(mp3路径, 时长秒), ...]，与 lines 一一对应。"""
    AUDIO.mkdir(parents=True, exist_ok=True)
    todo = [(t, line_path(t, voice, rate)) for t in lines]
    missing = [(t, p) for t, p in todo if not p.exists() or p.stat().st_size == 0]

    async def run():
        for t, p in missing:
            await _synth(t, voice, rate, p)
            print("tts", p.name, t[:20])

    if missing:
        asyncio.run(run())
    return [(str(p), duration(p)) for _, p in todo]
