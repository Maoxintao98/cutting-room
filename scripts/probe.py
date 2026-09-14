#!/usr/bin/env python3
"""盘点素材目录：用 ffprobe 列出每个片段的时长、分辨率、帧率、画幅和音轨。

用法
    python3 probe.py <目录或文件...>            # 输出 Markdown 表格
    python3 probe.py <目录> --contact 6         # 附带每 N 秒抽帧的拼图命令
    python3 probe.py <目录> --json              # 输出 JSON

设计意图：剪辑的第一步是知道手里有哪些牌。这个脚本把"有哪些素材"从
模糊印象变成一张可比较的表，之后再谈选片和排序。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".mxf", ".mkv", ".avi", ".webm", ".m4v", ".r3d", ".braw"}


def ffprobe_json(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def parse_ratio(value: str | None) -> float | None:
    if not value or ":" not in value:
        return None
    a, b = value.split(":", 1)
    try:
        return float(a) / float(b)
    except (ValueError, ZeroDivisionError):
        return None


def summarise(path: Path) -> dict:
    info = ffprobe_json(path)
    streams = info.get("streams", [])
    fmt = info.get("format", {})
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audios = [s for s in streams if s.get("codec_type") == "audio"]

    num, den = video.get("avg_frame_rate", "0/1").split("/")
    fps = round(float(num) / float(den), 3) if float(den or 1) else None

    ratio = parse_ratio(video.get("display_aspect_ratio"))
    if ratio is None and video.get("width") and video.get("height"):
        ratio = video["width"] / video["height"]

    if ratio is None:
        orientation = "?"
    elif ratio > 1.2:
        orientation = "横"
    elif ratio < 0.9:
        orientation = "竖"
    else:
        orientation = "方"

    notes = []
    if not audios:
        notes.append("无音轨")
    if fps and (fps < 23 or fps > 61):
        notes.append(f"非标帧率 {fps}")
    if orientation == "竖":
        notes.append("需留安全区")

    return {
        "file": path.name,
        "duration": round(float(fmt.get("duration") or 0), 2),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": fps,
        "orientation": orientation,
        "codec": video.get("codec_name"),
        "audio": f"{len(audios)} 轨" if audios else "无",
        "size_mb": round(int(fmt.get("size") or 0) / 1048576, 1),
        "notes": "；".join(notes),
    }


def collect(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            found += sorted(
                q for q in p.rglob("*")
                if q.suffix.lower() in VIDEO_EXT and not q.name.startswith("._")
            )
        elif p.is_file():
            found.append(p)
    return found


def to_table(rows: list[dict]) -> str:
    head = "| 文件 | 时长 | 分辨率 | 帧率 | 画幅 | 编码 | 音频 | 大小 | 备注 |"
    sep = "|---|---|---|---|---|---|---|---|---|"
    lines = [head, sep]
    for r in rows:
        lines.append(
            f"| {r['file']} | {r['duration']}s | {r['width']}×{r['height']} | "
            f"{r['fps']} | {r['orientation']} | {r['codec']} | {r['audio']} | "
            f"{r['size_mb']}MB | {r['notes']} |"
        )
    total = round(sum(r["duration"] for r in rows), 1)
    lines.append("")
    lines.append(f"共 {len(rows)} 个片段，总时长 {total}s")
    return "\n".join(lines)


def contact_sheet_cmd(path: Path, every: int) -> str:
    """给出抽帧拼图的 ffmpeg 命令，供 agent 看图判断内容。"""
    return (
        f'ffmpeg -v error -i "{path.name}" -vf '
        f'"fps=1/{every},scale=320:-1,tile=4x4" -frames:v 1 '
        f'"{path.stem}_contact.jpg"'
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="用 ffprobe 盘点素材目录")
    ap.add_argument("paths", nargs="+", help="目录或视频文件")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--contact", type=int, metavar="N",
                    help="为每个片段给出每 N 秒抽帧拼图的 ffmpeg 命令")
    args = ap.parse_args()

    if not shutil.which("ffprobe"):
        print("找不到 ffprobe，请先安装 ffmpeg。", file=sys.stderr)
        return 2

    files = collect(args.paths)
    if not files:
        print("没有找到视频文件。", file=sys.stderr)
        return 1

    rows = []
    for f in files:
        try:
            rows.append(summarise(f))
        except subprocess.CalledProcessError:
            print(f"跳过（ffprobe 读不了）：{f.name}", file=sys.stderr)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(to_table(rows))
        if args.contact:
            print("\n抽帧拼图命令（看清每个片段里是什么）：")
            for f in files:
                print("  " + contact_sheet_cmd(f, args.contact))
    return 0


if __name__ == "__main__":
    sys.exit(main())
