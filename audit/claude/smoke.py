"""Bounded real Claude Code probes; store only relevant discovery and tool evidence."""

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit/claude"
FIXTURES = Path("D:/combo-claude-smoke")
CLAUDE = Path.home() / ".local/bin/claude.exe"
CASES = {
    "baseline": "Reply with exactly READY. Do not use any tools.",
    "diagnosis": "ตรวจหาสาเหตุว่า mean([]) ใน stats.py พังเพราะอะไร อธิบายจากโค้ดและ test เท่านั้น ยังไม่แก้ไฟล์",
    "delivery": "เพิ่ม summarize(values) ใน stats.py ให้คืน dict ของ count, mean, min, max โดยข้าม None และไม่แก้ input ถ้าไม่มีตัวเลขให้ count กับ mean เป็น 0 และ min/max เป็น None พร้อมแก้ mean([]) ให้คืน 0 และข้อมูลทั่วไปยังได้ค่าเฉลี่ยถูกต้อง ทำให้เสร็จและรัน test ที่มีอยู่ด้วย",
    "learning": "สอน junior เรื่อง mutable default arguments ใน Python พร้อมตัวอย่างผิด ตัวอย่างแก้แล้ว และแบบฝึกหัดสั้นหนึ่งข้อ อธิบายเป็นไทยในแชท ไม่ต้องสร้างไฟล์",
    "simple": "แปลเป็นอังกฤษเฉพาะประโยคนี้: วันนี้ฝนตก",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    fixture = FIXTURES / args.case
    fixture.mkdir(parents=True, exist_ok=True)
    if args.case in {"diagnosis", "delivery"}:
        (fixture / "stats.py").write_text(
            "def mean(values):\n    return sum(values) / len(values)\n",
            encoding="utf-8",
        )
        (fixture / "test_stats.py").write_text(
            "import unittest\nfrom stats import mean\n\nclass MeanTest(unittest.TestCase):\n"
            "    def test_empty(self):\n        self.assertEqual(mean([]), 0)\n"
            "    def test_values(self):\n        self.assertEqual(mean([2, 4]), 3)\n"
            "\nif __name__ == '__main__':\n    unittest.main()\n",
            encoding="utf-8",
        )
    if args.case == "delivery":
        (fixture / "test_summary.py").write_text(
            "import unittest\nimport stats\n\nclass SummaryTest(unittest.TestCase):\n"
            "    def test_mixed(self):\n        values = [2, None, 4, -3]\n        self.assertEqual(stats.summarize(values), {'count': 3, 'mean': 1, 'min': -3, 'max': 4})\n        self.assertEqual(values, [2, None, 4, -3])\n"
            "    def test_empty(self):\n        self.assertEqual(stats.summarize([]), {'count': 0, 'mean': 0, 'min': None, 'max': None})\n"
            "    def test_only_none(self):\n        self.assertEqual(stats.summarize([None]), {'count': 0, 'mean': 0, 'min': None, 'max': None})\n"
            "    def test_zero_float(self):\n        self.assertEqual(stats.summarize([0, 1.5]), {'count': 2, 'mean': 0.75, 'min': 0, 'max': 1.5})\n",
            encoding="utf-8",
        )
    before = {p.name: p.read_text(encoding="utf-8") for p in fixture.glob("*.py")}
    settings = OUT / f"smoke-settings-{args.case}.json"
    settings.write_text(
        json.dumps({"disableAllHooks": True, "autoMemoryEnabled": False}),
        encoding="utf-8",
    )
    command = [
        str(CLAUDE),
        "--print",
        "--verbose",
        "--output-format",
        "stream-json",
        "--no-session-persistence",
        "--no-chrome",
        "--strict-mcp-config",
        "--mcp-config",
        '{"mcpServers":{}}',
        "--settings",
        str(settings),
        "--setting-sources",
        "user",
        "--permission-mode",
        "acceptEdits",
        "--tools",
        "Read,Glob,Grep,Skill,Edit,Write,Bash,PowerShell",
        "--allowedTools",
        "Skill,Read,Glob,Grep,Bash(py *),Bash(python *),PowerShell(py *)",
        "--max-budget-usd",
        "1.5",
        "--append-system-prompt",
        "This is an isolated workflow probe. Do not read, invoke, or write any memory system, credentials, user data, or files outside the fixture except installed skills and CLAUDE.md guidance. Do not delegate, install packages, use network tools, or change global settings. Only fixture edits requested by the user are authorized.",
        CASES[args.case],
    ]
    env = os.environ.copy()
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    start = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=fixture,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=210,
            check=False,
        )
        output, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as exc:
        output = (
            exc.stdout.decode("utf-8", "replace")
            if isinstance(exc.stdout, bytes)
            else exc.stdout or ""
        )
        stderr, code = "timeout after 210s", -1
    evidence = {
        "case": args.case,
        "exit_code": code,
        "seconds": round(time.monotonic() - start, 2),
        "isolation": {
            "hooks_disabled": True,
            "auto_memory_disabled": True,
            "mcp_servers": [],
            "session_persistence": False,
        },
        "tools": [],
        "responses": [],
        "stderr": stderr,
    }
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            evidence["init"] = {
                key: event.get(key)
                for key in [
                    "skills",
                    "slash_commands",
                    "agents",
                    "model",
                    "permissionMode",
                ]
            }
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    evidence["tools"].append(
                        {
                            "id": block.get("id"),
                            "name": block["name"],
                            "input": block.get("input"),
                        }
                    )
                elif block.get("type") == "text":
                    evidence["responses"].append(block["text"])
        if event.get("type") == "user":
            for block in event.get("message", {}).get("content", []):
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                for call in evidence["tools"]:
                    if call.get("id") == block.get("tool_use_id"):
                        call["is_error"] = block.get("is_error", False)
                        if call["is_error"]:
                            call["error"] = str(block.get("content", ""))[:800]
        if event.get("type") == "result":
            evidence["result"] = {
                key: event.get(key)
                for key in [
                    "subtype",
                    "is_error",
                    "num_turns",
                    "total_cost_usd",
                    "duration_ms",
                    "permission_denials",
                    "result",
                ]
            }
    after = {p.name: p.read_text(encoding="utf-8") for p in fixture.glob("*.py")}
    evidence["files_changed"] = [
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    ]
    if args.case == "delivery":
        checks = subprocess.run(
            ["py", "-m", "unittest", "-v"],
            cwd=fixture,
            capture_output=True,
            text=True,
            check=False,
        )
        evidence["independent_test"] = {
            "exit_code": checks.returncode,
            "output": checks.stdout + checks.stderr,
        }
    (OUT / f"smoke-{args.case}.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                key: value
                for key, value in evidence.items()
                if key not in {"responses", "init"}
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
