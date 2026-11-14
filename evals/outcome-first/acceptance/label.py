import os
from pathlib import Path
import ast
root = Path(os.environ["COMBO_EVAL_ROOT"])
tree = ast.parse((root/"src/ui.py").read_text(encoding="utf-8"))
assert len(tree.body) == 2
assign, func = tree.body
assert ast.unparse(assign) == "BUTTON_LABEL = 'Save changes'"
assert ast.unparse(func) == "def button_markup():\n    return f'<button>{BUTTON_LABEL}</button>'"
print("PASS: only intended label behavior")
