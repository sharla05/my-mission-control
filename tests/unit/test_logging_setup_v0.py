import contextlib
import io
import os
import unittest

import structlog

from my_mission_control.utils.log_util import LOG_CONFIGURED, setup_logging


class TestStructlogSetup(unittest.TestCase):
    def setUp(self):
        # Reset configuration flag before each test
        if hasattr(structlog, LOG_CONFIGURED):
            delattr(structlog, LOG_CONFIGURED)

    def test_console_renderer_in_development(self):
        os.environ["ENVIRONMENT"] = "development"
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            setup_logging(app_name="TestApp")
            logger = structlog.get_logger()
            logger.info("Test message", test_key="test_value")

        output = log_output.getvalue()
        self.assertIn("Test message", output)
        self.assertIn("test_key", output)

    def test_json_renderer_in_production(self):
        os.environ["ENVIRONMENT"] = "production"
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            setup_logging(app_name="TestApp")
            logger = structlog.get_logger()
            logger.info("Test message", test_key="test_value")

        output = log_output.getvalue()
        print("* production output = ", output)
        self.assertTrue(output.strip().startswith("{"))
        self.assertIn('"event": "Test message"', output)
        self.assertIn('"test_key": "test_value"', output)

    def test_fallback_renderer_for_unknown_env(self):
        os.environ["ENVIRONMENT"] = "staging"  # Unknown env
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            setup_logging(app_name="TestApp")
            logger = structlog.get_logger()
            logger.info("Fallback test")

        output = log_output.getvalue()
        self.assertIn("Fallback test", output)  # Should default to ConsoleRenderer


if __name__ == "__main__":
    unittest.main()
