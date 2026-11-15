"""Self-tests for the evaluation, not a candidate model solution."""
import importlib.util
import inspect
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
FIXTURE = HERE/"fixtures/river"

def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

with patch.dict(os.environ,{"COMBO_EVAL_ROOT":str(FIXTURE)}):
    acceptance = load("river_acceptance",HERE/"acceptance/river.py")
legacy = load("river_legacy",FIXTURE/"generator.py")
runner = load("outcome_first_runner",HERE/"run.py")
SEEDS = acceptance.SEEDS

def connected_sample(seed):
    # Mathematical positive control ONLY: deliberately not an art reference.
    # Small smooth seed shift, a west branch merging near y=50.
    wet = []
    for y in range(96):
        main = 49 + (SEEDS.index(seed) - 2) * 2 * math.sin(y/22)
        tributary = 10 + (main - 10) * y/50
        radius = 2 if y < 45 else 4
        for x in range(96):
            if abs(x-main) <= radius or (y <= 50 and abs(x-tributary) <= 1):
                wet.append([x,y])
    return {"size":96,"seed":seed,"water":wet}

class MechanicalTests(unittest.TestCase):
    def test_legacy_rejected_for_real_defect(self):
        for seed in acceptance.SEEDS:
            with self.subTest(seed=seed), self.assertRaisesRegex(AssertionError,"disconnected water"):
                acceptance.check(legacy.generate(seed),seed)

    def test_connected_sample_passes(self):
        for seed in acceptance.SEEDS:
            with self.subTest(seed=seed):
                self.assertTrue(acceptance.check(connected_sample(seed),seed))

    def test_flooded_approach_rejected(self):
        data = connected_sample(17)
        data["water"].append([3,20])
        with self.assertRaisesRegex(AssertionError,"protected approach"):
            acceptance.check(data,17)

    def test_disconnected_puddle_rejected(self):
        data = connected_sample(17)
        data["water"].append([80,30])
        with self.assertRaisesRegex(AssertionError,"disconnected water"):
            acceptance.check(data,17)

    def test_duplicate_rejected(self):
        data = connected_sample(17)
        data["water"].append(data["water"][0])
        with self.assertRaisesRegex(AssertionError,"duplicate"):
            acceptance.check(data,17)

    def test_early_merge_rejected(self):
        data = connected_sample(17)
        # Flood an interior band joining both streams above the required merge.
        data["water"] = [list(p) for p in sorted({tuple(p) for p in data["water"]} |
                                                {(x,y) for x in range(10,54) for y in range(29,33)})]
        with self.assertRaisesRegex(AssertionError,"merge outside middle third"):
            acceptance.check(data,17)

    def test_label_immutable_acceptance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path=root/"src/ui.py"
            path.parent.mkdir()
            original='BUTTON_LABEL = "Save"\n\ndef button_markup():\n    return f\'<button>{BUTTON_LABEL}</button>\'\n'
            env={**os.environ,"COMBO_EVAL_ROOT":d}
            def check(text):
                path.write_text(text,encoding="utf-8")
                return subprocess.run([sys.executable,str(HERE/"acceptance/label.py")],
                                      env=env,capture_output=True,text=True)
            self.assertEqual(check(original).returncode,1)
            self.assertEqual(check(original.replace('"Save"','"Save changes"')).returncode,0)
            self.assertEqual(check(original.replace('"Save"','"Save changes"').replace("<button>","<div>")).returncode,1)

    def test_full_acceptance_pass_and_reject_no_variation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root/"generator.py"
            sample = inspect.getsource(connected_sample)
            header = f"import json, math, sys\nfrom pathlib import Path\nSEEDS = {SEEDS!r}\n"
            footer = '\nseed = int(sys.argv[1])\ndata = connected_sample(seed)\nPath(sys.argv[2]).write_text(json.dumps(data),encoding="utf-8")\n'
            env = {**os.environ,"COMBO_EVAL_ROOT":d}
            def check(body):
                path.write_text(header+sample+body,encoding="utf-8")
                return subprocess.run([sys.executable,str(HERE/"acceptance/river.py")],
                                      env=env,capture_output=True,text=True,timeout=30)
            good = check(footer)
            self.assertEqual(good.returncode,0,good.stdout+good.stderr)
            constant = footer.replace("connected_sample(seed)","connected_sample(SEEDS[0])").replace(
                'Path(sys.argv[2])','data["seed"] = seed\nPath(sys.argv[2])')
            bad = check(constant)
            self.assertEqual(bad.returncode,1,bad.stdout+bad.stderr)
            self.assertIn("insufficient distinct geometry",bad.stdout)

    def test_stage_three_treatments(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for arm in ("B","C"):
                source=root/arm
                (source/"skills/combo").mkdir(parents=True)
                (source/"skills/combo/SKILL.md").write_text(arm,encoding="utf-8")
                (source/"POLICY.md").write_text(arm,encoding="utf-8")
            case=runner.CASES[0]
            for arm in runner.ARMS:
                dest=root/f"stage-{arm}"
                fixture=runner.stage(arm,root/arm,case,dest)
                self.assertEqual((fixture/"generator.py").read_bytes(),(FIXTURE/"generator.py").read_bytes())
                self.assertEqual((fixture/"render.py").read_bytes(),(FIXTURE/"render.py").read_bytes())
                if arm=="A":
                    self.assertEqual(list((dest/"skills").iterdir()),[])
                    self.assertFalse((fixture/"POLICY.md").exists())
                    self.assertNotIn("combo", (fixture/"AGENTS.md").read_text().lower())
                else:
                    self.assertEqual((dest/"skills/combo/SKILL.md").read_text(),arm)
                    self.assertEqual((fixture/"POLICY.md").read_text(),arm)
                    self.assertIn("combo-", (fixture/"AGENTS.md").read_text())

    def test_locked_renderer_produces_all_seed_views(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)
            failures=[]
            runner.render_outputs(FIXTURE/"generator.py",FIXTURE/"render.py",target,failures)
            self.assertFalse(failures)
            self.assertEqual(len(list(target.glob("*.svg"))),len(SEEDS))
            for seed in SEEDS:
                svg=ET.parse(target/f"seed-{seed}.svg").getroot()
                self.assertEqual(svg.attrib["viewBox"],"0 0 96 96")

    def test_order_rotates(self):
        for i in range(2):
            self.assertEqual({runner.order(r,i)[0] for r in range(3)},set(runner.ARMS))
            for r in range(3):
                self.assertEqual(set(runner.order(r,i)),set(runner.ARMS))

if __name__=="__main__":
    unittest.main()
