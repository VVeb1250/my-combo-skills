"""Offline proof that the hard compare cases fail before, pass with a correct change, and reject shortcuts."""

import importlib.util
from pathlib import Path
import shutil
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("outcome_compare", ROOT / "scripts" / "run-outcome-compare.py")
oc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(oc)

USERS = '''
_USERS = {1: {"name": "Ada", "email": "ada@example.com"}, 2: {"name": "Lin", "email": "lin@example.com"}}


def find_user(user_id):
    return _USERS.get(user_id)
'''
GREETING = '''
from users import find_user


def greet(user_id):
    user = find_user(user_id)
    return "Hello, guest" if user is None else f"Hello, {user['name']}"
'''
BILLING = '''
from users import find_user


def invoice_email(user_id):
    user = find_user(user_id)
    if user is None:
        raise LookupError(user_id)
    return user["email"]
'''
EXPORT = '''
from users import find_user


def export_rows(user_ids):
    rows = []
    for uid in user_ids:
        user = find_user(uid)
        if user is None:
            continue
        rows.append(f"{uid},{user['name']},{user['email']}")
    return rows
'''
HANDLERS = '''
from users import find_user

HANDLERS = {"lookup": find_user}


def handle(name, user_id):
    user = HANDLERS[name](user_id)
    if user is None:
        return {"status": 404}
    return {"status": 200, "user": user}
'''


class HardCases(unittest.TestCase):
    def setUp(self):
        self.cases = {c["id"]: c for c in oc.load_cases()}

    def workdir(self, case_id):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        case = self.cases[case_id]
        shutil.copytree(case["_root"] / "fixtures" / case["fixture"], tmp.name, dirs_exist_ok=True)
        return case, Path(tmp.name)

    def accept(self, case, work):
        return oc.run_acceptance_script(case["_root"] / case["acceptance"]["after"], work)

    def write(self, work, files):
        for name, body in files.items():
            (work / "src" / name).write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")

    def test_contract_callers_fails_before_and_when_only_the_function_changes(self):
        case, work = self.workdir("contract-callers")
        self.assertFalse(self.accept(case, work)["passed"])
        self.write(work, {"users.py": USERS})
        self.assertFalse(self.accept(case, work)["passed"])

    def test_contract_callers_passes_when_every_caller_is_updated(self):
        case, work = self.workdir("contract-callers")
        self.write(work, {"users.py": USERS, "greeting.py": GREETING, "billing.py": BILLING,
                          "export.py": EXPORT, "handlers.py": HANDLERS})
        result = self.accept(case, work)
        self.assertTrue(result["passed"], result["tail"])

    def test_missing_one_caller_still_fails(self):
        case, work = self.workdir("contract-callers")
        self.write(work, {"users.py": USERS, "greeting.py": GREETING, "billing.py": BILLING,
                          "export.py": EXPORT})  # handlers.py (registry call) left as is
        self.assertFalse(self.accept(case, work)["passed"])

    def test_surgical_fix_accepts_minimal_change_and_rejects_cleanup(self):
        case, work = self.workdir("surgical-fix")
        self.assertFalse(self.accept(case, work)["passed"])
        path = work / "src" / "timefmt.py"
        original = path.read_text(encoding="utf-8")
        fixed = original.replace("    minutes = round(seconds / 60)\n    secs = seconds - minutes * 60\n",
                                 "    minutes, secs = divmod(seconds, 60)\n")
        self.assertNotEqual(fixed, original)
        path.write_text(fixed, encoding="utf-8")
        result = self.accept(case, work)
        self.assertTrue(result["passed"], result["tail"])
        cleaned = fixed.replace("import math\n", "")
        path.write_text(cleaned, encoding="utf-8")
        self.assertFalse(self.accept(case, work)["passed"])


if __name__ == "__main__":
    unittest.main()
