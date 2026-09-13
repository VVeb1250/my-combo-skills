"""Read-only Codex app-server skill discovery. Never starts a model turn."""

import argparse
import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def snapshot(cwd, overrides=()):
    cli = Path(os.environ["APPDATA"]) / "npm/node_modules/@openai/codex/bin/codex.js"
    command = ["node", str(cli)]
    for override in overrides:
        command.extend(["-c", override])
    command.append("app-server")
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        creationflags=0x08000000,
    )
    messages = queue.Queue()
    assert proc.stdout is not None and proc.stdin is not None
    stdout, stdin = proc.stdout, proc.stdin

    def reader():
        for line in stdout:
            try:
                messages.put(json.loads(line))
            except json.JSONDecodeError:
                pass

    threading.Thread(target=reader, daemon=True).start()

    def send(msg):
        stdin.write(json.dumps(msg) + "\n")
        stdin.flush()

    def response(id):
        deadline = time.monotonic() + 55
        while time.monotonic() < deadline:
            try:
                msg = messages.get(timeout=1)
            except queue.Empty:
                continue
            if msg.get("id") == id:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg["result"]
        raise TimeoutError(f"app-server request {id} did not return")

    try:
        send(
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {"name": "combo-audit", "version": "0.1.0"},
                    "capabilities": {"experimentalApi": True},
                },
            }
        )
        initialization = response(1)
        send({"method": "initialized", "params": {}})
        send(
            {
                "id": 2,
                "method": "skills/list",
                "params": {"cwds": [str(cwd)], "forceReload": True},
            }
        )
        return {
            "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "initialization": initialization,
            "skills": response(2),
        }
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--cwd", default=str(ROOT))
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        help="Process-only Codex config override",
    )
    args = parser.parse_args()
    result = snapshot(Path(args.cwd), args.config)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved real app-server discovery to {out}")
