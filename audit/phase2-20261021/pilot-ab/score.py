"""Offline scorer for pilots A and B. No model calls. Criteria: PRE-REGISTRATION.md."""
import ast, json, operator, re, sys
from pathlib import Path

HERE = Path(__file__).parent
TRUTH = {1: 11 / 12, 2: 1.0, 3: 12.0, 4: 7.0, 5: 20.0, 6: 7.0, 7: 10.0, 8: 0.75, 9: 45.0}
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}


def arith(expr: str) -> float:
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.operand))
        raise ValueError("disallowed")
    return ev(ast.parse(expr, mode="eval").body)


def text_of(case: str) -> str:
    return json.loads((HERE / "results" / f"{case}.json").read_text(encoding="utf-8"))["result"].get("result", "")


def score_b(case: str):
    raw = text_of(case)
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return [("parse", "FAIL: no JSON list")]
    items = json.loads(m.group(0))
    out = []
    for it in items:
        sid, t, v = it["stem_id"], TRUTH[it["stem_id"]], it["options"]
        problems = []
        vals = {k: float(x) for k, x in v.items()}
        if sorted(vals) != ["A", "B", "C", "D"]:
            problems.append("options not A-D")
        if len({round(x, 6) for x in vals.values()}) < len(vals):
            problems.append("duplicate option values")
        hits = [k for k, x in vals.items() if abs(x - t) < 1e-4]
        if len(hits) != 1:
            problems.append(f"{len(hits)} options equal the truth {t:.6g} (Gate A): {hits}")
        elif it["key"] != hits[0]:
            problems.append(f"key {it['key']} is not the true option {hits[0]}")
        for k, d in it.get("distractors", {}).items():
            try:
                got = arith(d["computation"])
            except Exception as e:  # noqa: BLE001
                problems.append(f"{k}: computation not evaluable ({e})")
                continue
            if abs(got - vals[k]) > 1e-4:
                problems.append(f"{k}: computation gives {got:.6g} but option is {vals[k]:.6g} (Gate B)")
            if abs(vals[k] - t) < 1e-4:
                problems.append(f"{k}: distractor equals truth")
            if not d.get("misconception", "").strip():
                problems.append(f"{k}: no misconception")
        missing = [k for k in vals if k != it["key"] and k not in it.get("distractors", {})]
        if missing:
            problems.append(f"no distractor entry for {missing}")
        out.append((f"stem {sid}", "PASS" if not problems else "FAIL: " + "; ".join(problems)))
    return out


def show_a(case: str):
    t = text_of(case)
    first = t.strip().splitlines()[0] if t.strip() else ""
    print(f"--- {case} first line: {first!r}\n{t}\n")


if __name__ == "__main__":
    for c in sys.argv[1:]:
        if c.startswith("A"):
            show_a(c)
        else:
            for stem, verdict in score_b(c):
                print(c, stem, verdict)
