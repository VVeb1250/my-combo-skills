"""Independent check for the exact tiny change, ignoring formatting."""
import ast
import os
import sys
from pathlib import Path

root = Path(os.environ["COMBO_EVAL_ROOT"])
expected = ast.parse("""BUTTON_LABEL = "Save changes"

def button_markup():
    return f'<button>{BUTTON_LABEL}</button>'
""")
actual = ast.parse((root/"src/ui.py").read_text(encoding="utf-8"))
if ast.dump(actual) != ast.dump(expected):
    print("label or unrelated behavior differs")
    sys.exit(1)
print("PASS: only intended label behavior")
