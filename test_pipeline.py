"""Tests for Beancount capital gains demo."""

import unittest
from oa_client import OAClient
import cap_gains_check
import beancount_client


class BeancountTaxDemoTests(unittest.TestCase):
    def setUp(self):
        self.oa = OAClient(token=None)
        self.plan = self.oa.start("Determine short vs long term capital gains tax treatment", "US")
        slug = (self.plan.get("skills_to_load") or [None])[0]
        self.skill = self.oa.get_skill(slug)

    def test_mock_oa_client(self):
        self.assertEqual(self.plan["jurisdiction"], "US")
        self.assertEqual(self.skill["tier"], 1)
        self.assertIn("Amir Pelinkovic", self.skill["verifier"])

    def test_short_term_gain(self):
        gain = {
            "symbol": "AAPL",
            "units": 10.0,
            "gain": 500.0,
            "holding_days": 212,
        }
        res = cap_gains_check.check(gain, self.skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("Short-term gain", res["headline"])

    def test_long_term_gain(self):
        gain = {
            "symbol": "BTC",
            "units": 0.5,
            "gain": 27500.0,
            "holding_days": 1118,
        }
        res = cap_gains_check.check(gain, self.skill)
        self.assertEqual(res["status"], "ok")
        self.assertIn("Long-term gain", res["headline"])

    def test_capital_loss(self):
        gain = {
            "symbol": "TSLA",
            "units": 5.0,
            "gain": -250.0,
            "holding_days": 146,
        }
        res = cap_gains_check.check(gain, self.skill)
        self.assertEqual(res["status"], "info")
        self.assertIn("Capital loss", res["headline"])

    def test_sample_beancount_extraction(self):
        gains = beancount_client.parse("samples/portfolio.beancount")
        self.assertEqual(len(gains), 4)
        self.assertEqual(gains[0]["symbol"], "AAPL")
        self.assertEqual(gains[0]["gain"], 500.0)


if __name__ == "__main__":
    unittest.main()
