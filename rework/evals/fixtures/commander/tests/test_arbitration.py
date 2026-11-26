import unittest
from src.arbitration import Action, decide


class ContractTests(unittest.TestCase):
    def test_manual_hold(self):
        self.assertEqual(decide("hold", 100, True, True), Action("hold", True))

    def test_manual_move(self):
        self.assertEqual(decide("move", 100, False, True), Action("advance", True))

    def test_retreat_without_cover(self):
        self.assertEqual(decide("free", 70, False, True), Action("retreat", False))

    def test_low_risk(self):
        self.assertEqual(decide("free", 69, False, True), Action("hold", True))

    def test_unloaded(self):
        self.assertEqual(decide("free", 0, True, False), Action("hold", False))
