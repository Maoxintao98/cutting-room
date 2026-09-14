#!/usr/bin/env python3
"""直连 DaVinci Resolve 官方 MCP 服务器（stdio），作为 MCP 工具不可用时的保底路径。

当 Codex 已经把 ResolveMCP 挂成 MCP 工具时，直接用那些工具即可，不必跑这个脚本。
当工具没挂上时（例如 MCP 进程没被拉起），用这个脚本仍然能完成同样的事。

用法
    python3 resolve_mcp.py tools                 列出全部工具
    python3 resolve_mcp.py status                查询 Resolve 是否在运行
    python3 resolve_mcp.py search Timeline       搜索脚本 API
    python3 resolve_mcp.py api Timeline,MediaPool 拉取指定类型的完整声明
    python3 resolve_mcp.py docs                  开发者文档目录
    python3 resolve_mcp.py run cut.py            执行一个脚本文件（沙箱 Python，可访问 Resolve API）
    python3 resolve_mcp.py raw <tool> '<json>'   调用任意工具，参数为 JSON

注意：run 用的是沙箱模式，只能访问 Resolve API。需要读写文件或调用子进程时，
改用 `raw run_script_unsafe '{"code": "..."}'`，并自行确认风险。
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
            raise SystemExit(f"找不到 MCP 服务器：{server}")
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
            raise SystemExit("MCP 握手失败。Resolve 是否已安装？")
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, name: str, arguments: dict, timeout: int = TIMEOUT) -> str:
        self._id += 1
        mid = self._id
        self._send({"jsonrpc": "2.0", "id": mid, "method": "tools/call",
                    "params": {"name": name, "arguments": arguments}})
        msg = self._read(mid, timeout)
        if msg is None:
            return "（无响应，可能超时）"
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
                return print("用法：run <脚本.py>") or 1
            code = Path(rest[0]).read_text()
            print(c.call("run_script", {"code": code}, timeout=300))
        elif cmd == "raw":
            if len(rest) < 2:
                return print("用法：raw <tool> '<json>'") or 1
            print(c.call(rest[0], json.loads(rest[1]), timeout=300))
        else:
            print(__doc__)
            return 1
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
