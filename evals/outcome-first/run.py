"""Three-arm behavioral experiment using the existing Codex A/B runner.

A: no staged Combo; B: pinned main; C: this candidate. Trusted synthetic
fixtures only: the inherited runner uses danger-full-access, not isolation.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "2ec0e2033bdcc783ab021efa508eaf98d0c28786"
ARMS = ("A", "B", "C")
spec = importlib.util.spec_from_file_location("outcome_first_ab", ROOT/"scripts/run-ab-eval.py")
assert spec and spec.loader
ab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)

CASES = [
    {"id":"river", "fixture":"river", "sandbox":"workspace-write",
     "prompt":"Improve the existing river confluence generator to produce natural-looking, varied connected channels and a convincing merge, while preserving the protected vehicle approach and the contract in README.md. Use the actual generator and renderer to inspect several seeds including 17 and 41, refine if necessary, and deliver the working generator. Change only generator.py; put inspection artifacts under previews/. Do not modify the renderer or specification. Report remaining visual or gameplay limits honestly.",
     "acceptance":{"before":"river.py","after":"river.py","before_must_fail":True,"after_must_pass":True}},
    {"id":"label", "fixture":"trivial-label", "sandbox":"workspace-write",
     "prompt":"In src/ui.py, change the visible button label from Save to Save changes. Make only that small edit and finish.",
     "allowed_changed_paths":["src/ui.py"],
     "acceptance":{"before":"label.py","after":"label.py","before_must_fail":True,"after_must_pass":True}},
]

def order(rep, case_index):
    shift = (rep + case_index) % 3
    return ARMS[shift:] + ARMS[:shift]

def revision(path):
    return subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()

def stage(arm, source, case, dest):
    dest.mkdir(parents=True)
    skills = dest/"skills"
    if arm == "A":
        skills.mkdir()
    else:
        shutil.copytree(source/"skills", skills)
    fixture = dest/"fixtures"/case["fixture"]
    original = HERE/"fixtures"/"river" if case["id"] == "river" else ROOT/"evals/ab/fixtures/trivial-label"
    shutil.copytree(original, fixture)
    common = ("Preserve supplied constraints and reference files. Do not install tools, "
              "publish, delegate, inspect other arms or results, or write outside this workspace.\n")
    if arm != "A":
        shutil.copy2(source/"POLICY.md", fixture/"POLICY.md")
        common += "For substantive work use the matching local .agents/skills/combo-* entry and its linked workflow. Read local POLICY.md.\n"
    (fixture/"AGENTS.md").write_text(common,encoding="utf-8")
    return fixture

def save_json(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def capture(result, case, target, blind):
    cwd = Path(result["workdir"])
    target.mkdir(parents=True, exist_ok=True)
    if case["id"] == "river":
        # Preserve actual candidate outputs, independently render using the locked
        # source renderer; never accept agent-created preview files as proof.
        renderer = HERE/"fixtures/river/render.py"
        for seed in (17,41,83,109,151):
            data = target/f"seed-{seed}.json"
            try:
                subprocess.run([sys.executable,str(cwd/"generator.py"),str(seed),str(data)],
                               cwd=cwd,check=True,timeout=15,capture_output=True)
                subprocess.run([sys.executable,str(renderer),str(data),str(target/f"seed-{seed}.svg")],
                               check=True,timeout=15,capture_output=True)
            except (subprocess.SubprocessError,OSError) as exc:
                result["task_failures"].append(f"independent render seed {seed}: {exc}")
        shutil.copy2(cwd/"generator.py",target/"generator.py")
        if (cwd/"previews").is_dir():
            shutil.copytree(cwd/"previews", target/"agent-previews")
        for file in target.glob("*.svg"):
            shutil.copy2(file,blind/file.name)
        changed = [r["path"] for r in result["changed_files"]]
        illegal = [p for p in changed if p != "generator.py" and not p.startswith("previews/")]
        if illegal:
            result["task_failures"].append("protected/out-of-scope changes: "+", ".join(illegal))
        if "generator.py" not in changed:
            result["task_failures"].append("generator unchanged")
    else:
        shutil.copy2(cwd/"src/ui.py",target/"ui.py")
        if any(r["path"] != "src/ui.py" for r in result["changed_files"]):
            result["task_failures"].append("label control changed unrelated files")
    events,_ = ab.SMOKE.parse_events(Path(result["events_path"]).read_text(encoding="utf-8"))
    if not any(e.get("type")=="turn.completed" for e in events):
        result["environment_failures"].append("no completed turn")
    # A local Combo reference in A invalidates the treatment, not the model.
    if result["variant"]=="A" and any("combo" in str(r).lower() for r in result["actual_references"]):
        result["environment_failures"].append("A loaded Combo; treatment contaminated")
    result["classification"] = "environmental" if result["environment_failures"] else (
        "task" if result["task_failures"] else "passed")
    result["quality_verdict"] = "pending-human-review" if case["id"]=="river" else "not-applicable"
    result["blind_id"] = blind.name
    save_json(Path(result["result_path"]),result)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--work-root",type=Path,required=True)
    p.add_argument("--case",choices=["river","label"],action="append")
    p.add_argument("--repeat",type=int,default=1)
    p.add_argument("--model",default="gpt-5.6-luna")
    p.add_argument("--effort",default="max")
    p.add_argument("--timeout",type=int,default=300)
    p.add_argument("--stage-only",action="store_true")
    p.add_argument("--allow-shared-host-policy",action="store_true",
                   help="acknowledge global instructions may contaminate all arms")
    a=p.parse_args()
    if not 1<=a.repeat<=5 or not 60<=a.timeout<=600:
        p.error("repeat 1..5; timeout 60..600")
    if revision(a.baseline)!=BASE:
        p.error("baseline must be pinned main revision "+BASE)
    if subprocess.check_output(["git","-C",str(a.baseline),"status","--porcelain"],text=True).strip():
        p.error("baseline must be clean")
    if subprocess.check_output(["git","-C",str(ROOT),"status","--porcelain"],text=True).strip():
        p.error("candidate checkout must be clean")
    a.output=a.output.resolve()
    a.work_root=a.work_root.resolve()
    if a.output.exists():
        p.error("choose a new output directory; existing evidence is never overwritten")
    if a.output==ROOT or ROOT in a.output.parents or a.work_root==ROOT or ROOT in a.work_root.parents:
        p.error("keep results/workspaces outside the source checkout")
    if not a.stage_only and not a.allow_shared_host_policy:
        p.error("read README host caveats, use a clean matched host and acknowledge --allow-shared-host-policy")
    a.output.mkdir(parents=True)
    a.work_root.mkdir(parents=True,exist_ok=True)
    root=Path(tempfile.mkdtemp(prefix="outcome-first-",dir=a.work_root))
    selected=[c for c in CASES if not a.case or c["id"] in a.case]
    suite={"model":a.model,"reasoning_effort":a.effort}
    manifest={"baseline":BASE,"candidate":revision(ROOT),"suite":suite,"timeout":a.timeout,
              "repeat":a.repeat,"work_root":str(root),"stage_only":a.stage_only,
              "cases":selected,"limitations":"synthetic 2D proxy; shared global policy; not filesystem isolation"}
    save_json(a.output/"run.json",manifest)
    ab.ACCEPTANCE=HERE/"acceptance"
    original_rows=ab.rows_for
    def rows(variant,global_combo):
        result=original_rows(variant,global_combo)
        roots={Path.home()/".codex/skills",Path.home()/".agents/skills"}
        if os.environ.get("CODEX_HOME"):
            roots.add(Path(os.environ["CODEX_HOME"])/"skills")
        for parent in roots:
            for entry in parent.glob("combo*/SKILL.md"):
                target=str(entry.resolve())
                if not any(r.get("path")==target for r in result):
                    result.append({"path":target,"enabled":False})
        return result
    ab.rows_for=rows
    if not a.stage_only:
        _,cli=ab.SMOKE.find_cli()
        mcp=ab.SMOKE.configured_mcp_names()
    results=[]
    blind_key=[]
    for rep in range(a.repeat):
        for ci,base in enumerate(selected):
            case={**base,"id":f"{base['id']}-r{rep+1}"}
            for arm in order(rep,ci):
                name=case["id"]
                dest=root/"staging"/name/arm
                source=a.baseline if arm=="B" else ROOT
                fixture=stage(arm,source,base,dest)
                if a.stage_only:
                    check=ab.acceptance(base["acceptance"]["before"],fixture)
                    if check["passed"] or check.get("returncode") != 1:
                        raise RuntimeError(f"invalid seeded failure: {check}")
                    print("STAGED",name,arm,flush=True)
                    continue
                work=root/"executions"/name/arm
                work.mkdir(parents=True)
                print("START",name,arm,flush=True)
                # A dummy path is sufficient when no globally installed router exists.
                global_path=Path(os.environ.get("CODEX_HOME",str(Path.home()/".codex")))/"skills/combo/SKILL.md"
                result=ab.run_arm(cli,suite,case,arm,dest,global_path,mcp,a.output,work,
                                  a.timeout,rep*len(selected)+ci+1,order(rep,ci)[0],True)
                token=hashlib.sha256(os.urandom(32)).hexdigest()[:12]
                blind=a.output/"blind"/name/token
                blind.mkdir(parents=True)
                capture(result,base,a.output/"artifacts"/arm/name,blind)
                blind_key.append({"case":name,"blind_id":token,"arm":arm})
                save_json(a.output/"blind-key.json",blind_key)
                results.append(result)
                save_json(a.output/"summary.json",results)
                print("END",name,arm,result["classification"],flush=True)
    if a.stage_only:
        print("Staging and seeded-failure checks complete; no model invoked.")
    else:
        print("Mechanical results only. Grade blind SVGs before opening blind-key.json.")
    return int(any(r["classification"]!="passed" for r in results))

if __name__=="__main__":
    sys.exit(main())
