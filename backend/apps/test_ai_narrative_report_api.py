from django.test import SimpleTestCase

from apps.ai_narrative_report_api import AIRuntimeError, _extract_gemini_text, _parse_narrative


VALID_NARRATIVE = {
    "summary": "The learner is making steady progress.",
    "strengths": "The learner demonstrates curiosity.",
    "development_areas": "Continue practising written explanations.",
    "next_steps": "Use short, regular revision activities.",
    "teacher_note": "Review progress at the next reporting point.",
}


class ParseNarrativeTests(SimpleTestCase):
    def test_parses_valid_json(self):
        self.assertEqual(_parse_narrative(__import__("json").dumps(VALID_NARRATIVE)), VALID_NARRATIVE)

    def test_parses_json_inside_markdown_fence(self):
        import json

        output = "```json\n" + json.dumps(VALID_NARRATIVE) + "\n```"
        self.assertEqual(_parse_narrative(output), VALID_NARRATIVE)

    def test_parses_complete_json_after_short_preamble(self):
        import json

        output = "Here is the requested report:\n" + json.dumps(VALID_NARRATIVE)
        self.assertEqual(_parse_narrative(output), VALID_NARRATIVE)

    def test_rejects_malformed_or_truncated_json(self):
        with self.assertRaisesMessage(AIRuntimeError, "invalid narrative format"):
            _parse_narrative('{"summary": "unfinished"')

    def test_rejects_non_object_json(self):
        with self.assertRaisesMessage(AIRuntimeError, "invalid narrative format"):
            _parse_narrative("[]")

    def test_rejects_missing_sections(self):
        with self.assertRaisesMessage(AIRuntimeError, "incomplete narrative"):
            _parse_narrative('{"summary": "Only one section"}')

    def test_rejects_non_string_or_blank_sections(self):
        import json

        for invalid_value in (None, 42, "   "):
            payload = {**VALID_NARRATIVE, "teacher_note": invalid_value}
            with self.subTest(value=invalid_value):
                with self.assertRaisesMessage(AIRuntimeError, "teacher_note"):
                    _parse_narrative(json.dumps(payload))

    def test_rejects_empty_output(self):
        with self.assertRaisesMessage(AIRuntimeError, "empty narrative"):
            _parse_narrative("   ")


class GeminiResponseTests(SimpleTestCase):
    def test_extracts_text_from_first_candidate(self):
        payload = {
            "candidates": [{
                "finishReason": "STOP",
                "content": {"parts": [{"text": '{"summary": "ok"}'}]},
            }]
        }
        self.assertEqual(_extract_gemini_text(payload), '{"summary": "ok"}')

    def test_reports_prompt_block(self):
        with self.assertRaisesMessage(AIRuntimeError, "blocked the narrative prompt"):
            _extract_gemini_text({"promptFeedback": {"blockReason": "SAFETY"}})

    def test_reports_truncated_generation(self):
        payload = {
            "candidates": [{
                "finishReason": "MAX_TOKENS",
                "content": {"parts": [{"text": '{"summary":'}]},
            }]
        }
        with self.assertRaisesMessage(AIRuntimeError, "truncated the narrative"):
            _extract_gemini_text(payload)

    def test_reports_missing_candidate(self):
        with self.assertRaisesMessage(AIRuntimeError, "no narrative candidate"):
            _extract_gemini_text({"candidates": []})
