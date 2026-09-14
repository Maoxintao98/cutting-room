#!/usr/bin/env python3
"""Talk to the official DaVinci Resolve MCP server over stdio.

The fallback path for when the MCP tools are not mounted in the agent.

When the MCP tools are available, call those instead. This does the same work
when they are not.

Usage
    python3 resolve_mcp.py tools                 list every tool
    python3 resolve_mcp.py status                is Resolve running
    python3 resolve_mcp.py search Timeline       search the scripting API
    python3 resolve_mcp.py api Timeline,MediaPool  full declaration of given types
    python3 resolve_mcp.py docs                  developer documentation
    python3 resolve_mcp.py run cut.py            run a script file (sandboxed; resolve/project injected)
    python3 resolve_mcp.py raw <tool> '<json>'   call any tool with JSON arguments

Script contract, which the tools enforce
  - the parameter is script, not code
  - resolve and project are injected into the sandbox
  - return structured data via result; print output is captured too
  - timeout is 10s by default, 60s maximum
  - the sandbox blocks os, sys, pathlib, shutil; for filesystem or
    subprocess access use run_script_unsafe
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

SERVER = ("/Applications/DaVinci Resolve/DaVinci Resolve.app"
          "/Contents/Applications/ResolveMCP")
TIMEOUT = 120


class Client:
    def __init__(self, server: str = SERVER) -> None:
        if not Path(server).exists():
            raise SystemExit(f"MCP server not found: {server}")
        self.proc = subprocess.Popen(
            [server], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        self._id = 0
        self._handshake()

    def _send(self, obj: dict) -> None:
        assert self.proc.stdin
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _read(self, want_id: int, timeout: int = TIMEOUT) -> dict | None:
        assert self.proc.stdout
        end = time.time() + timeout
        while time.time() < end:
            line = self.proc.stdout.readline()
            if not line:
                return None
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == want_id:
                return msg
        return None

    def _handshake(self) -> None:
        self._send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "cutting-room", "version": "1.0"}}})
        if not self._read(1, timeout=60):
            raise SystemExit("MCP handshake failed. Is Resolve installed?")
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, name: str, arguments: dict, timeout: int = TIMEOUT) -> str:
        self._id += 1
        mid = self._id
        self._send({"jsonrpc": "2.0", "id": mid, "method": "tools/call",
                    "params": {"name": name, "arguments": arguments}})
        msg = self._read(mid, timeout)
        if msg is None:
            return "(no response, possibly timed out)"
        if "error" in msg:
            return "ERROR " + json.dumps(msg["error"], ensure_ascii=False)
        parts = [c.get("text", "") for c in msg.get("result", {}).get("content", [])]
        return "\n".join(parts)

    def close(self) -> None:
        self.proc.terminate()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, rest = argv[1], argv[2:]
    c = Client()
    try:
        if cmd == "tools":
            raw = c.call("tools/list", {}, timeout=30)
            print(raw)
        elif cmd == "status":
            print(c.call("get_resolve_status", {}))
        elif cmd == "search":
            print(c.call("search_scripting_api", {"pattern": " ".join(rest)}))
        elif cmd == "api":
            types = [t.strip() for t in ",".join(rest).split(",") if t.strip()]
            print(c.call("get_scripting_api", {"types": types}))
        elif cmd == "docs":
            print(c.call("get_scripting_docs", {}))
        elif cmd == "run":
            if not rest:
                return print("usage: run <script.py>") or 1
            code = Path(rest[0]).read_text()
            print(c.call("run_script", {"script": code}, timeout=120))
        elif cmd == "raw":
            if len(rest) < 2:
                return print("usage: raw <tool> '<json>'") or 1
            print(c.call(rest[0], json.loads(rest[1]), timeout=120))
        else:
            print(__doc__)
            return 1
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
