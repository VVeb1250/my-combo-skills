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

def render_outputs(generator, renderer, target, failures):
    target.mkdir(parents=True, exist_ok=True)
    for seed in (17,41,83,109,151):
        data = target/f"seed-{seed}.json"
        try:
            subprocess.run([sys.executable,str(generator),str(seed),str(data)],
                           cwd=generator.parent,check=True,timeout=15,capture_output=True)
            subprocess.run([sys.executable,str(renderer),str(data),str(target/f"seed-{seed}.svg")],
                           check=True,timeout=15,capture_output=True)
        except (subprocess.SubprocessError,OSError) as exc:
            failures.append(f"independent render seed {seed}: {exc}")

def check_known_host_contamination(work_root):
    # Do not change global instructions. Reject known Combo injection in the
    # selected Codex home or inherited workspace guidance. This is not proof
    # that all possible host prompt sources are absent.
    home = Path(os.environ.get("CODEX_HOME",str(Path.home()/".codex")))
    locations = [home,work_root,*work_root.parents]
    for folder in locations:
        for name in ("AGENTS.md","AGENTS.override.md"):
            path = folder/name
            if path.is_file() and "combo" in path.read_text(encoding="utf-8-sig").lower():
                raise RuntimeError(f"Known Combo host guidance would contaminate A: {path}. "
                                   "Use a clean evaluation CODEX_HOME/workspace; do not edit the live installation.")

def capture(result, case, target, blind):
    cwd = Path(result["workdir"])
    target.mkdir(parents=True, exist_ok=True)
    if case["id"] == "river":
        # Preserve actual candidate outputs, independently render using the locked
        # source renderer; never accept agent-created preview files as proof.
        renderer = HERE/"fixtures/river/render.py"
        if (cwd/"generator.py").is_file():
            render_outputs(cwd/"generator.py",renderer,target,result["task_failures"])
            shutil.copy2(cwd/"generator.py",target/"generator.py")
        else:
            result["task_failures"].append("generator missing")
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
        if (cwd/"src/ui.py").is_file():
            shutil.copy2(cwd/"src/ui.py",target/"ui.py")
        else:
            result["task_failures"].append("label source missing")
        if any(r["path"] != "src/ui.py" for r in result["changed_files"]):
            result["task_failures"].append("label control changed unrelated files")
    events,_ = ab.SMOKE.parse_events(Path(result["events_path"]).read_text(encoding="utf-8"))
    if not any(e.get("type")=="turn.completed" for e in events):
        result["environment_failures"].append("no completed turn")
    # A local Combo reference in A invalidates the treatment, not the model.
    if result["variant"]=="A" and any("combo" in str(r).lower() for r in result["actual_references"]):
        result["environment_failures"].append("A loaded Combo; treatment contaminated")
    if case["id"]=="river" and result["variant"] in ("B","C") and not any(
        str(r).lower().startswith("combo/workflows/") for r in result["actual_references"]
    ):
        # Lack of a detected read is an evidence gap, not proof of non-use.
        result["environment_failures"].append("B/C workflow read not observed; treatment unverified")
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
    p.add_argument("--cli",help="native Codex executable or npm codex.js wrapper")
    p.add_argument("--codex-home",type=Path,help="prepared evaluation home; does not install or edit settings")
    p.add_argument("--allow-shared-host-policy",action="store_true",
                   help="acknowledge global instructions may contaminate all arms")
    a=p.parse_args()
    if a.codex_home:
        home=a.codex_home.resolve()
        if not home.is_dir():
            p.error("--codex-home must be an existing prepared directory")
        os.environ["CODEX_HOME"]=str(home)
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
    for source in (ROOT,a.baseline.resolve()):
        if any(path==source or source in path.parents for path in (a.output,a.work_root)):
            p.error("keep results/workspaces outside both source checkouts")
    if not a.stage_only and not a.allow_shared_host_policy:
        p.error("read README host caveats, use a clean matched host and acknowledge --allow-shared-host-policy")
    if not a.stage_only:
        check_known_host_contamination(a.work_root)
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
        _,cli=ab.SMOKE.find_cli(a.cli)
        mcp=ab.SMOKE.configured_mcp_names()
    if any(c["id"]=="river" for c in selected):
        reference=HERE/"fixtures/river"
        failures=[]
        render_outputs(reference/"generator.py",reference/"render.py",a.output/"reference",failures)
        if failures:
            raise RuntimeError("could not render baseline: "+str(failures))
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
                    symptom="disconnected water" if base["id"]=="river" else "label or unrelated behavior differs"
                    if check["passed"] or check.get("returncode") != 1 or symptom not in check.get("stdout",""):
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
