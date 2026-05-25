from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name("xquik_evidence.py")
SPEC = importlib.util.spec_from_file_location("xquik_evidence", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load xquik_evidence.py")
xquik_evidence = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = xquik_evidence
SPEC.loader.exec_module(xquik_evidence)


class XquikEvidenceTest(unittest.TestCase):
    def test_build_headers_uses_x_api_key_header(self) -> None:
        self.assertEqual(xquik_evidence.build_headers("xq_test"), {"x-api-key": "xq_test"})

    def test_build_headers_uses_bearer_for_other_tokens(self) -> None:
        self.assertEqual(
            xquik_evidence.build_headers("token"),
            {"authorization": "Bearer token"},
        )

    def test_extract_tweets_normalizes_nested_shapes(self) -> None:
        payload = {
            "data": {
                "tweets": [
                    {
                        "id": "123",
                        "text": "  Useful   thread  ",
                        "author": {"username": "alice"},
                        "metrics": {"likes": 5, "retweets": 2, "replies": 1},
                    },
                    {
                        "id": "123",
                        "text": "  Useful   thread  ",
                        "author": {"username": "alice"},
                    },
                ]
            }
        }
        tweets = xquik_evidence.extract_tweets(payload, limit=5)
        self.assertEqual(len(tweets), 1)
        self.assertEqual(tweets[0].text, "Useful thread")
        self.assertEqual(tweets[0].author, "alice")
        self.assertEqual(tweets[0].url, "https://x.com/alice/status/123")
        self.assertEqual(tweets[0].likes, 5)
        self.assertEqual(tweets[0].reposts, 2)
        self.assertEqual(tweets[0].replies, 1)

    def test_missing_key_skips_without_error_exit(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            output = StringIO()
            with redirect_stdout(output):
                code = xquik_evidence.main(["search", "AI agents", "--format", "json"])

        self.assertEqual(code, 0)
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["skipped"])
        self.assertEqual(payload["items"], [])

    def test_markdown_table_renders_evidence(self) -> None:
        payload = {
            "schema_version": "x_skills.xquik_evidence.v1",
            "kind": "tweet_search",
            "source": "AI agents",
            "timestamp": "2026-01-01T00:00:00Z",
            "skipped": False,
            "success": True,
            "error": None,
            "items": [
                {
                    "text": "A practical launch note",
                    "author": "alice",
                    "url": "https://x.com/alice/status/123",
                    "likes": 3,
                    "reposts": 2,
                    "replies": 1,
                    "created_at": "",
                }
            ],
        }

        self.assertIn("| @alice | 6 |", xquik_evidence.markdown_table(payload))


if __name__ == "__main__":
    unittest.main()
