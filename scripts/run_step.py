#!/usr/bin/env python3
"""Send a step script into Resolve, concatenating shared code as needed.

The Resolve sandbox has no filesystem, so a step script cannot import local
modules. Shared code has to be concatenated into the script text first.
This script does the concatenation and the dispatch.

Usage
    python3 run_step.py steps/10_picture.py                # sandboxed
    python3 run_step.py steps/10_picture.py --unsafe       # with filesystem
    python3 run_step.py steps/30_titles.py --pre lib/titles.py lib/common.py
    python3 run_step.py steps/10_picture.py --timeout 60

The RMCP environment variable overrides the client path; by default it uses
resolve_mcp.py from the same directory.
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
    ap = argparse.ArgumentParser(description="Execute a step script inside Resolve")
    ap.add_argument("step", help="path to the step script")
    ap.add_argument("--pre", nargs="*", default=[], help="shared code files to concatenate first")
    ap.add_argument("--unsafe", action="store_true", help="use run_script_unsafe, allowing filesystem access")
    ap.add_argument("--timeout", type=int, default=60, help="script timeout in seconds, 60 max")
    args = ap.parse_args()

    step = pathlib.Path(args.step)
    if not step.exists():
        print(f"Step script not found: {step}", file=sys.stderr)
        return 2

    src = step.read_text()
    # A step may write an import of a shared module; concatenation replaces it
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
