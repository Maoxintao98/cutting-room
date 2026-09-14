#!/usr/bin/env python3
"""把步骤脚本送进 Resolve 执行，并支持拼接共享代码。

Resolve 的沙箱没有文件系统，步骤脚本不能 import 本地模块，所以共享代码
必须在执行前拼进脚本文本。这个脚本负责拼接和投递。

用法
    python3 run_step.py steps/10_picture.py                # 沙箱执行
    python3 run_step.py steps/10_picture.py --unsafe       # 放开文件系统
    python3 run_step.py steps/30_titles.py --pre lib/titles.py lib/common.py
    python3 run_step.py steps/10_picture.py --timeout 240

环境变量 RMCP 可以指定客户端路径，默认用同目录的 resolve_mcp.py。
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser(description="在 Resolve 里执行一个步骤脚本")
    ap.add_argument("step", help="步骤脚本路径")
    ap.add_argument("--pre", nargs="*", default=[], help="先拼进来的共享代码文件")
    ap.add_argument("--unsafe", action="store_true", help="用 run_script_unsafe，放开文件系统")
    ap.add_argument("--timeout", type=int, default=60, help="脚本内部超时秒数，上限 60")
    args = ap.parse_args()

    step = pathlib.Path(args.step)
    if not step.exists():
        print(f"找不到步骤脚本：{step}", file=sys.stderr)
        return 2

    src = step.read_text()
    # 步骤脚本里允许写 import 共享模块，实际由拼接替代
    pre = "".join(pathlib.Path(p).read_text() + "\n" for p in args.pre)
    body = pre + src

    tool = "run_script_unsafe" if args.unsafe else "run_script"
    client = os.environ.get("RMCP", str(HERE / "resolve_mcp.py"))

    tmp = pathlib.Path("/tmp/cutting_room_step.json")
    tmp.write_text(json.dumps({"script": body, "timeout": min(args.timeout, 60)}, ensure_ascii=False))

    proc = subprocess.run(
        [sys.executable, client, "raw", tool, tmp.read_text()],
        capture_output=True, text=True, timeout=args.timeout + 120,
    )
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
