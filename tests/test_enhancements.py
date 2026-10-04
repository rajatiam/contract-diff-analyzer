import unittest, json, csv, io
from contract_diff_analyzer.core import markdown


class FeatureTests(unittest.TestCase):
    def test_report_contains_findings_and_unsupported(self):
        report = {
            "breaking": 1,
            "fully_analyzed": False,
            "changes": [
                {"kind": "breaking", "location": "GET /a", "message": "Removed"}
            ],
            "unsupported": [{"location": "schema", "reason": "Review reference"}],
        }
        text = markdown(report)
        self.assertIn("Breaking findings: 1", text)
        self.assertIn("Review reference", text)

    def test_report_escapes_markup(self):
        text = markdown(
            {
                "breaking": 1,
                "fully_analyzed": True,
                "changes": [
                    {
                        "kind": "breaking",
                        "location": "a|b",
                        "message": "<script>alert(1)</script>",
                    }
                ],
                "unsupported": [],
            }
        )
        self.assertNotIn("<script>", text)
        self.assertIn("a\\|b", text)
