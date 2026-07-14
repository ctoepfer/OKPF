from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import httpx
import pytest

from okpf_prep.ai.ollama import DEFAULT_NUM_PREDICT, DEFAULT_TIMEOUT, OllamaBackend


def _mock_response(json_body: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


class OllamaBackendTimeoutConfigTest(unittest.TestCase):
    def test_default_timeout_used_when_unset(self):
        backend = OllamaBackend()
        self.assertEqual(backend.timeout, DEFAULT_TIMEOUT)

    def test_custom_timeout_is_stored(self):
        backend = OllamaBackend(timeout=300.0)
        self.assertEqual(backend.timeout, 300.0)

    def test_timeout_reaches_httpx_call(self):
        """The configured timeout must actually be passed to the httpx request —
        not just stored on the object."""
        backend = OllamaBackend(timeout=273.0)
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _mock_response({"response": "ok"})
            backend.generate(prompt="hi")
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["timeout"], 273.0)

    def test_num_predict_defaults_and_reaches_payload(self):
        backend = OllamaBackend()
        self.assertEqual(backend.num_predict, DEFAULT_NUM_PREDICT)
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _mock_response({"response": "ok"})
            backend.generate(prompt="hi")
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["options"]["num_predict"], DEFAULT_NUM_PREDICT)

    def test_num_predict_none_omits_option(self):
        backend = OllamaBackend(num_predict=None)
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _mock_response({"response": "ok"})
            backend.generate(prompt="hi")
        _, kwargs = mock_post.call_args
        self.assertNotIn("num_predict", kwargs["json"]["options"])


class OllamaBackendErrorClassificationTest(unittest.TestCase):
    def test_timeout_raises_distinct_timeout_error(self):
        backend = OllamaBackend(timeout=5.0)
        with patch("httpx.post", side_effect=httpx.TimeoutException("timed out")):
            with self.assertRaises(TimeoutError) as ctx:
                backend.generate(prompt="hi")
        self.assertIn("timed out after 5.0s", str(ctx.exception))

    def test_connect_error_raises_connection_error_not_timeout(self):
        backend = OllamaBackend()
        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            with self.assertRaises(ConnectionError):
                backend.generate(prompt="hi")

    def test_http_status_error_raises_runtime_error_not_timeout(self):
        backend = OllamaBackend()
        with patch("httpx.post") as mock_post:
            mock_post.return_value = _mock_response({"error": "model not found"}, status_code=404)
            with self.assertRaises(RuntimeError) as ctx:
                backend.generate(prompt="hi")
        self.assertIn("404", str(ctx.exception))


class OllamaBackendDiagnosticsTest(unittest.TestCase):
    def test_success_logs_timing_metadata_without_content(self):
        backend = OllamaBackend()
        payload = {
            "response": "the generated text should not appear in logs",
            "total_duration": 2_000_000_000,
            "load_duration": 100_000_000,
            "prompt_eval_count": 42,
            "prompt_eval_duration": 300_000_000,
            "eval_count": 128,
            "eval_duration": 1_500_000_000,
        }
        with patch("httpx.post") as mock_post, \
             self.assertLogs("okpf_prep.ai.ollama", level="INFO") as log_ctx:
            mock_post.return_value = _mock_response(payload)
            backend.generate(prompt="some prompt text", system="some system text")

        joined = " ".join(log_ctx.output)
        self.assertIn("total_duration_s", joined)
        self.assertIn("eval_count", joined)
        self.assertNotIn("the generated text should not appear in logs", joined)
        self.assertNotIn("some prompt text", joined)

    def test_failure_logs_do_not_contain_prompt_text(self):
        backend = OllamaBackend(timeout=1.0)
        with patch("httpx.post", side_effect=httpx.TimeoutException("timed out")), \
             self.assertLogs("okpf_prep.ai.ollama", level="WARNING") as log_ctx:
            with pytest.raises(TimeoutError):
                backend.generate(prompt="secret prompt contents", system="secret system text")
        joined = " ".join(log_ctx.output)
        self.assertNotIn("secret prompt contents", joined)
        self.assertIn("prompt_chars", joined)
