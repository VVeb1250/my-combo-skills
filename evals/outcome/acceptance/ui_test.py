"""Independent geometry and interaction acceptance at both reference viewports."""

import os
import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


class UIAcceptance(unittest.TestCase):
    def test_layout_and_saved_state(self):
        root = Path(os.environ["COMBO_EVAL_ROOT"])
        with tempfile.TemporaryDirectory() as profile, sync_playwright() as runtime:
            browser = runtime.chromium.launch_persistent_context(profile, headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1100, "height": 700})
            page.goto((root / "index.html").as_uri())
            copy = page.locator(".copy").bounding_box()
            self.assertTrue(74 <= copy["x"] <= 86, copy)
            page.locator("#save").click()
            self.assertEqual(page.locator("#status").inner_text(), "Saved")
            page.reload()
            self.assertEqual(page.locator("#status").inner_text(), "Saved")
            page.set_viewport_size({"width": 390, "height": 844})
            copy = page.locator(".copy").bounding_box()
            art = page.locator(".art").bounding_box()
            self.assertLess(copy["y"], art["y"])
            self.assertFalse(
                page.evaluate("document.documentElement.scrollWidth > innerWidth")
            )
            browser.close()


if __name__ == "__main__":
    unittest.main()
