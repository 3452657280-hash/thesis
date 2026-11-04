"""讲解视频流水线的公共路径与环境修正（通用模板：工具和渲染脚本自动查找）。"""
import os
import pathlib
import ssl

import truststore

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build"
OUT = ROOT / "out"
# VIO Companion 的全局 skill 目录（优先），其次 ~/.vio/skills
GLOBAL_DIRS = [pathlib.Path(os.path.expandvars(r"%LOCALAPPDATA%\VIOCompanion\.vio\skills")),
               pathlib.Path.home() / ".vio" / "skills"]
if os.environ.get("EXPLAINER_SKILL_DIR"):
    GLOBAL_DIRS.insert(0, pathlib.Path(os.environ["EXPLAINER_SKILL_DIR"]).parent)


def _first(paths, probe):
    for p in paths:
        if (p / probe).exists():
            return p
    raise FileNotFoundError(f"找不到 {probe}，已查找：" + "; ".join(str(p) for p in paths))


# node/ffmpeg：优先项目内 video/tools，其次全局 skill 目录里的 tools
TOOLS = _first([ROOT / "tools"] + [g / "explainer-video" / "tools" for g in GLOBAL_DIRS],
               pathlib.Path("ffmpeg") / "ffmpeg.exe")
FFMPEG = TOOLS / "ffmpeg" / "ffmpeg.exe"
FFPROBE = TOOLS / "ffmpeg" / "ffprobe.exe"
NODE = TOOLS / "node" / "node.exe"

# motion-showreel 渲染脚本：优先项目内 .vio，其次全局目录
SHOWREEL = _first([ROOT.parent / ".vio" / "skills" / "motion-showreel" / "scripts"]
                  + [g / "motion-showreel" / "scripts" for g in GLOBAL_DIRS], "render.mjs")


def tool_env() -> dict:
    return {**os.environ, "PATH": f"{TOOLS / 'node'};{TOOLS / 'ffmpeg'};{os.environ.get('PATH', '')}"}


def patch_edge_tts_ssl() -> None:
    """公司网络做 SSL 解密，certifi 不认公司根证书；改用 Windows 证书库。"""
    import edge_tts.communicate as ec

    ec._SSL_CTX = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
