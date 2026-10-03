import copy, unittest
from contract_diff_analyzer.core import analyze


class ContractTests(unittest.TestCase):
    def test_unsupported_constraint_requires_review(self):
        self.after["components"]["schemas"]["User"]["properties"]["name"][
            "minLength"
        ] = 20
        self.assertFalse(analyze(self.before, self.after)["fully_analyzed"])

    def setUp(self):
        self.before = {
            "openapi": "3.0.3",
            "paths": {
                "/users": {
                    "get": {
                        "responses": {"200": {"description": "ok"}},
                        "parameters": [],
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    }
                }
            },
        }
        self.after = copy.deepcopy(self.before)

    def test_unchanged(self):
        self.assertEqual(analyze(self.before, self.after)["breaking"], 0)

    def test_removed_operation(self):
        self.after["paths"] = {}
        self.assertEqual(analyze(self.before, self.after)["breaking"], 1)

    def test_required_parameter(self):
        self.after["paths"]["/users"]["get"]["parameters"] = [
            {"name": "account", "in": "query", "required": True}
        ]
        self.assertEqual(analyze(self.before, self.after)["breaking"], 1)

    def test_new_optional_parameter_is_compatible(self):
        self.after["paths"]["/users"]["get"]["parameters"] = [
            {"name": "page", "in": "query", "required": False}
        ]
        self.assertEqual(analyze(self.before, self.after)["breaking"], 0)

    def test_changed_property_type(self):
        self.after["components"]["schemas"]["User"]["properties"]["name"][
            "type"
        ] = "integer"
        self.assertGreater(analyze(self.before, self.after)["breaking"], 0)

    def test_new_required_property(self):
        self.after["components"]["schemas"]["User"]["required"] = ["name"]
        self.assertGreater(analyze(self.before, self.after)["breaking"], 0)

    def test_reference_requires_review(self):
        self.after["components"]["schemas"]["User"][
            "$ref"
        ] = "#/components/schemas/Other"
        self.assertFalse(analyze(self.before, self.after)["fully_analyzed"])

    def test_removed_response(self):
        self.after["paths"]["/users"]["get"]["responses"] = {}
        self.assertEqual(analyze(self.before, self.after)["breaking"], 1)
