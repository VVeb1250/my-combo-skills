"""Fixture for the P0 compaction pilot: a tiny repo with three ordered steps and planted state.

    py -I fixture.py <dir>

Step 1 (verify early, never touch again): shop/money.py parse_amount ignores accounting negatives "(12.50)".
Step 2 (tempting wrong fix first): tests/test_report.py fails; the failure is shown in report.total, but
  the cause is truncation in shop/fmt.py to_cents. Changing rounding in report.py cannot fix it.
Step 3 (decision by investigation): the default currency must become EUR. Two files look authoritative:
  settings.json (read by nothing) and config/defaults.toml (read by shop/config.py).
The tests are visible and are the acceptance. Padding docs make the context grow during step 2.
"""
import sys, textwrap
from pathlib import Path

FILES = {
"shop/__init__.py": "",
"shop/money.py": '''"""Money parsing. Amounts are integer cents."""
import re


def parse_amount(text):
    """Parse '12', '12.5', '$1,234.50' into integer cents."""
    s = text.strip().replace("$", "").replace(",", "")
    if not re.fullmatch(r"-?\\d+(\\.\\d{1,2})?", s):
        raise ValueError(f"bad amount: {text!r}")
    whole, _, frac = s.partition(".")
    cents = int(whole) * 100 + int((frac + "00")[:2]) * (-1 if whole.startswith("-") else 1)
    return cents
''',
"shop/fmt.py": '''"""Formatting helpers shared by reports and the CLI."""


def to_cents(price):
    """Convert a float price in major units to integer cents."""
    return int(price * 100)


def cents_to_str(cents, currency):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d} {currency}"
''',
"shop/report.py": '''"""Order totals."""
from shop import fmt


def line_total(price, qty):
    return fmt.to_cents(price) * qty


def total(items):
    """items: list of (price_float, qty). Returns integer cents."""
    return sum(line_total(price, qty) for price, qty in items)
''',
"shop/config.py": '''"""Configuration: defaults from config/defaults.toml, overridden by SHOP_* environment variables."""
import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    with open(ROOT / "config" / "defaults.toml", "rb") as handle:
        data = tomllib.load(handle)
    if "SHOP_CURRENCY" in os.environ:
        data["currency"] = os.environ["SHOP_CURRENCY"]
    return data
''',
"shop/cli.py": '''"""Command line entry point: prints the order total."""
from shop import config, fmt, report


def run(argv=None):
    cfg = config.load()
    items = [(19.99, 3), (5.00, 2)]
    return fmt.cents_to_str(report.total(items), cfg["currency"])
''',
"config/defaults.toml": 'currency = "USD"\ntax_rate = 0.07\n',
"settings.json": '{\n  "currency": "USD",\n  "note": "legacy file from the old deployment scripts"\n}\n',
"tests/__init__.py": "",
"tests/test_money.py": '''import unittest

from shop.money import parse_amount


class MoneyTest(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(parse_amount("12"), 1200)
        self.assertEqual(parse_amount("$1,234.50"), 123450)

    def test_negative(self):
        self.assertEqual(parse_amount("-3.05"), -305)

    def test_accounting_negative(self):
        self.assertEqual(parse_amount("(12.50)"), -1250)


if __name__ == "__main__":
    unittest.main()
''',
"tests/test_report.py": '''import unittest

from shop import report


class ReportTest(unittest.TestCase):
    def test_total_is_exact(self):
        self.assertEqual(report.total([(19.99, 3), (5.00, 2)]), 6997)

    def test_single_line(self):
        self.assertEqual(report.line_total(0.29, 100), 2900)


if __name__ == "__main__":
    unittest.main()
''',
"tests/test_cli.py": '''import os
import unittest

from shop import cli


class CliTest(unittest.TestCase):
    def setUp(self):
        os.environ.pop("SHOP_CURRENCY", None)

    def test_default_currency_is_eur(self):
        self.assertEqual(cli.run([]), "69.97 EUR")


if __name__ == "__main__":
    unittest.main()
''',
"docs/cli.md": "# CLI\n\n`shop` prints the order total. New installs default to EUR; `SHOP_CURRENCY` overrides.\n",
}


def filler(title, lines):
    out = [f"# {title}", ""]
    for i in range(lines):
        out.append(f"{i + 1}. Note on {title.lower()} item {i + 1}: behaviour is documented here for completeness and "
                   f"does not change the three tasks. Reference code is under shop/ and tests/.")
    return "\n".join(out) + "\n"


def build(dest):
    dest = Path(dest)
    for rel, body in FILES.items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body) if rel.endswith(".md") else body, encoding="utf-8")
    (dest / "docs" / "architecture.md").write_text(filler("Architecture", 160), encoding="utf-8")
    (dest / "docs" / "money-rules.md").write_text(filler("Money rules", 160), encoding="utf-8")
    (dest / "CHANGELOG.md").write_text(filler("Changelog", 220), encoding="utf-8")
    return dest


if __name__ == "__main__":
    print(build(sys.argv[1]))
