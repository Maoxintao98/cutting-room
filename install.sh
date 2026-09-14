#!/usr/bin/env bash
# 一键安装 cutting-room skill 到 Codex 的用户级技能目录。
#
#   curl -fsSL https://raw.githubusercontent.com/Maoxintao98/cutting-room/main/install.sh | bash
#
# 可用环境变量覆盖安装位置：
#   CODEX_SKILLS_DIR=/path/to/skills   默认 ~/.agents/skills
set -euo pipefail

REPO="https://github.com/Maoxintao98/cutting-room.git"
ROOT="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
DEST="$ROOT/cutting-room"

say() { printf '%s\n' "$*"; }

say "→ 安装到 $DEST"

if [ -d "$DEST/.git" ]; then
  say "→ 已存在，拉取最新版本"
  git -C "$DEST" pull --ff-only --quiet
elif [ -e "$DEST" ]; then
  say "✗ $DEST 已存在，但不是 git 仓库。先把它移走再装。" >&2
  exit 1
else
  mkdir -p "$ROOT"
  git clone --depth 1 --quiet "$REPO" "$DEST"
fi

if [ ! -f "$DEST/SKILL.md" ]; then
  say "✗ 缺 SKILL.md，安装失败。" >&2
  exit 1
fi
if ! grep -q '^name: cutting-room' "$DEST/SKILL.md"; then
  say "✗ SKILL.md 的 name 字段不是 cutting-room，安装失败。" >&2
  exit 1
fi

chmod +x "$DEST"/scripts/*.py 2>/dev/null || true

say ""
say "✓ 装好了 $DEST"
say ""
say "调用方式，写 \$cutting-room，或者直接描述任务由 description 匹配。"
say "Codex 会自动扫描这个目录。如果没出现，重启一次 Codex。"
say ""
say "可选自检（需要 DaVinci Resolve 正在运行）："
say "  python3 \"$DEST/scripts/resolve_mcp.py\" status"
say ""
if command -v ffprobe >/dev/null 2>&1; then
  say "可选依赖 ffmpeg 与 ffprobe 已就绪，素材盘点可用。"
else
  say "未检测到 ffprobe。素材盘点脚本需要它，建议 brew install ffmpeg。"
fi
