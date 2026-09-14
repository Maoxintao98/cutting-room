#!/usr/bin/env python3
"""Inventory a media directory: list duration, resolution, frame rate, orientation and audio for every clip.

Usage
    python3 probe.py <dir-or-files...>          # print a Markdown table
    python3 probe.py <dir> --contact 6          # also print contact-sheet commands
    python3 probe.py <dir> --json               # print JSON

Why this exists: the first step of editing is knowing what you hold. This turns
"what footage is there" from an impression into a comparable table.
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
        orientation = "landscape"
    elif ratio < 0.9:
        orientation = "portrait"
    else:
        orientation = "square"

    notes = []
    if not audios:
        notes.append("no audio")
    if fps and (fps < 23 or fps > 61):
        notes.append(f"off-spec fps {fps}")
    if orientation == "portrait":
        notes.append("needs safe margins")

    return {
        "file": path.name,
        "duration": round(float(fmt.get("duration") or 0), 2),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": fps,
        "orientation": orientation,
        "codec": video.get("codec_name"),
        "audio": f"{len(audios)} track(s)" if audios else "none",
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
    head = "| File | Length | Resolution | FPS | Orient | Codec | Audio | Size | Notes |"
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
    lines.append(f"{len(rows)} clips, {total}s total")
    return "\n".join(lines)


def contact_sheet_cmd(path: Path, every: int) -> str:
    """Print the ffmpeg command for a contact sheet, so content can be inspected."""
    return (
        f'ffmpeg -v error -i "{path.name}" -vf '
        f'"fps=1/{every},scale=320:-1,tile=4x4" -frames:v 1 '
        f'"{path.stem}_contact.jpg"'
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Inventory a media directory with ffprobe")
    ap.add_argument("paths", nargs="+", help="directories or video files")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--contact", type=int, metavar="N",
                    help="print a contact-sheet ffmpeg command every N seconds per clip")
    args = ap.parse_args()

    if not shutil.which("ffprobe"):
        print("ffprobe not found. Install ffmpeg first.", file=sys.stderr)
        return 2

    files = collect(args.paths)
    if not files:
        print("No video files found.", file=sys.stderr)
        return 1

    rows = []
    for f in files:
        try:
            rows.append(summarise(f))
        except subprocess.CalledProcessError:
            print(f"Skipping (ffprobe cannot read): {f.name}", file=sys.stderr)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(to_table(rows))
        if args.contact:
            print("\nContact-sheet commands (to see what is in each clip):")
            for f in files:
                print("  " + contact_sheet_cmd(f, args.contact))
    return 0


if __name__ == "__main__":
    sys.exit(main())
