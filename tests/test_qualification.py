import unittest
from decimal import Decimal

from qualification import parse_budget, qualify_lead


class ParseBudgetTests(unittest.TestCase):
    def test_parses_plain_and_currency_amounts(self):
        self.assertEqual(parse_budget("1500"), Decimal("1500"))
        self.assertEqual(parse_budget("$2,000"), Decimal("2000"))
        self.assertEqual(parse_budget("2500 USD"), Decimal("2500"))

    def test_rejects_invalid_or_negative_amounts(self):
        for value in ("", "about 1000", "-1", "NaN"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_budget(value)


class QualificationTests(unittest.TestCase):
    def qualify(self, budget):
        return qualify_lead(
            Decimal(budget),
            "Within 1 month",
            "A client portal with payments",
            "Acme",
            "Avery",
        )

    def test_budget_thresholds_determine_lead_status(self):
        self.assertEqual(self.qualify("499.99").status, "Not qualified")
        self.assertEqual(self.qualify("500").status, "Qualified")
        self.assertEqual(self.qualify("1999.99").status, "Qualified")
        self.assertEqual(self.qualify("2000").status, "Hot lead")

    def test_scores_lead_on_a_100_point_scale(self):
        result = self.qualify("2000")
        self.assertEqual(result.score, 100)


if __name__ == "__main__":
    unittest.main()
