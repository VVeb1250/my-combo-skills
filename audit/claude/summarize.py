"""Compact evidence for human review, without account metadata or full listings."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
baseline = json.loads((HERE / "smoke-baseline.json").read_text(encoding="utf-8"))
summary = {"baseline_skills": len(baseline["init"]["skills"]), "cases": []}
for name in ("diagnosis", "delivery", "learning", "simple"):
    path = HERE / f"smoke-{name}.json"
    if not path.exists():
        continue
    case = json.loads(path.read_text(encoding="utf-8"))
    init = case.get("init", {})
    skills = init.get("skills") or []
    tools = case["tools"]
    summary["cases"].append(
        {
            "case": name,
            "exit_code": case["exit_code"],
            "result_error": case.get("result", {}).get("is_error"),
            "seconds": case["seconds"],
            "model": init.get("model"),
            "total_skills": len(skills),
            "combo_skills": sorted(
                s for s in skills if s == "combo" or s.startswith("combo-")
            ),
            "retired_remaining": [
                s
                for s in skills
                if s.startswith(("ecc:", "ecc-hubs:", "mattpocock-skills:"))
                or s == "multi-model-orchestrator"
            ],
            "worker_discovered": "combo-worker" in (init.get("agents") or []),
            "skill_calls": [t for t in tools if t["name"] == "Skill"],
            "workflow_reads": [
                t
                for t in tools
                if t["name"] == "Read" and "workflows" in str(t["input"])
            ],
            "tool_errors": [t for t in tools if t.get("is_error")],
            "files_changed": case["files_changed"],
            "independent_test": case.get("independent_test"),
            "final_response": case.get("result", {}).get("result"),
        }
    )
audit = json.loads((HERE / "installed-audit.json").read_text(encoding="utf-8"))
summary["lexical_findings"] = audit["findings"]
(HERE / "smoke-summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
