import contextlib
import importlib
import io
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

import requests

from joplin_api import ConfigurationError, JoplinRequestError, JoplinTestClient, load_config


def test_environment():
    return {
        "JOPLIN_API_URL": "http://127.0.0.1:41184",
        "JOPLIN_API_TOKEN": "offline-fixture&value=?",
        "JOPLIN_TEST_PROFILE_ACKNOWLEDGED": "1",
    }


class ConfigurationTests(unittest.TestCase):
    def test_missing_or_invalid_configuration_prevents_session_creation(self):
        for key in test_environment():
            for value in (None, "", " "):
                environ = test_environment()
                if value is None:
                    del environ[key]
                else:
                    environ[key] = value
                with self.subTest(key=key, value=value), patch("joplin_api.requests.Session") as session:
                    with self.assertRaises(ConfigurationError):
                        JoplinTestClient(environ)
                    session.assert_not_called()

    def test_remote_or_ambiguous_origins_are_rejected(self):
        urls = (
            "https://example.com:41184",
            "http://localhost.example.com:41184",
            "http://192.168.1.1:41184",
            "file:///tmp/joplin",
            "http://user:secret@localhost:41184",
            "http://localhost:41184/notes",
            "http://localhost:41184?token=fixture",
            "http://localhost:41184#fixture",
            "http://localhost:invalid",
            "http://localhost:0",
            "http://[invalid",
        )
        for url in urls:
            with self.subTest(url=url):
                environ = test_environment()
                environ["JOPLIN_API_URL"] = url
                with self.assertRaises(ConfigurationError):
                    load_config(environ)

    def test_supported_loopback_origins_and_secret_repr(self):
        for url in ("http://localhost:41184", "http://127.0.0.1:41184/", "http://[::1]:41184"):
            with self.subTest(url=url):
                environ = test_environment()
                environ["JOPLIN_API_URL"] = url
                config = load_config(environ)
                self.assertEqual(config.base_url, url.rstrip("/"))
                self.assertNotIn(environ["JOPLIN_API_TOKEN"], repr(config))

    def test_existing_script_entry_points_fail_before_network_without_configuration(self):
        for filename in ("joplin_functional_tests.py", "joplin_performance_tests.py", "joplin_security_tests.py"):
            with self.subTest(filename=filename), patch.dict(os.environ, {}, clear=True):
                with patch("joplin_api.requests.Session") as session, patch.dict(sys.modules, {"psutil": Mock()}):
                    with self.assertRaises(ConfigurationError):
                        runpy.run_path(str(Path(__file__).with_name(filename)), run_name="__main__")
                    session.assert_not_called()


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.factory = patch("joplin_api.requests.Session", return_value=self.session)
        self.factory.start()
        self.addCleanup(self.factory.stop)
        self.client = JoplinTestClient(test_environment())

    def test_token_is_encoded_with_query_and_requests_are_bounded(self):
        original_params = {"query": "notes & tags"}
        self.client.get("/search", params=original_params)
        args, kwargs = self.session.request.call_args
        self.assertEqual(args, ("GET", "http://127.0.0.1:41184/search"))
        prepared = requests.Request(args[0], args[1], params=kwargs["params"]).prepare()
        query = parse_qs(urlsplit(prepared.url).query)
        self.assertEqual(query["token"], [test_environment()["JOPLIN_API_TOKEN"]])
        self.assertEqual(query["query"], ["notes & tags"])
        self.assertEqual(original_params, {"query": "notes & tags"})
        self.assertEqual(kwargs["timeout"], 10)
        self.assertIs(kwargs["allow_redirects"], False)
        self.assertIs(self.session.trust_env, False)

    def test_explicit_invalid_token_preserves_negative_test(self):
        self.client.get("/notes/unauthorized_note_id", params={"token": "INVALID_TOKEN"})
        self.assertEqual(self.session.request.call_args.kwargs["params"]["token"], "INVALID_TOKEN")

    def test_redirect_response_is_returned_without_another_request(self):
        self.session.request.return_value.status_code = 302
        response = self.client.get("/notes")
        self.assertEqual(response.status_code, 302)
        self.session.request.assert_called_once()
        self.assertIs(self.session.request.call_args.kwargs["allow_redirects"], False)

    def test_external_or_embedded_query_paths_are_rejected_without_requests(self):
        for path in ("https://example.com/notes", "//example.com/notes", "/notes?token=fixture", "/notes#fixture", "notes"):
            with self.subTest(path=path):
                with self.assertRaises(ConfigurationError):
                    self.client.get(path)
                self.session.request.assert_not_called()

    def test_request_error_does_not_disclose_token_or_url(self):
        secret = test_environment()["JOPLIN_API_TOKEN"]
        self.session.request.side_effect = requests.ConnectionError(f"http://localhost/notes?token={secret}")
        with self.assertRaises(JoplinRequestError) as raised:
            self.client.post("/notes", json={"title": "Offline fixture"})
        message = str(raised.exception)
        self.assertNotIn(secret, message)
        self.assertNotIn("http", message)
        self.assertIn("ConnectionError", message)

    def test_each_legacy_script_uses_configured_client_under_mocks(self):
        cases = (
            ("joplin_functional_tests", "create_note", "POST", "/notes"),
            ("joplin_performance_tests", "test_note_save_time", "POST", "/notes"),
            ("joplin_security_tests", "test_encryption", "GET", "/notes"),
        )
        response = Mock(status_code=200, text="encrypted", json=Mock(return_value={"id": "fixture-id"}))
        self.session.request.return_value = response
        for module_name, function_name, method, path in cases:
            with self.subTest(module_name=module_name), patch.dict(os.environ, test_environment(), clear=True), patch.dict(sys.modules, {"psutil": Mock()}):
                self.session.request.reset_mock()
                sys.modules.pop(module_name, None)
                self.addCleanup(sys.modules.pop, module_name, None)
                module = importlib.import_module(module_name)
                with contextlib.redirect_stdout(io.StringIO()):
                    getattr(module, function_name)()
                self.session.request.assert_called_once()
                args, kwargs = self.session.request.call_args
                self.assertEqual(args, (method, test_environment()["JOPLIN_API_URL"] + path))
                self.assertEqual(kwargs["params"]["token"], test_environment()["JOPLIN_API_TOKEN"])
                self.assertTrue(module.test_results[-1]["success"])


if __name__ == "__main__":
    unittest.main()
