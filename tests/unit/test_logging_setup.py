import json
import os
import logging

import pytest
import structlog

from my_mission_control.utils.log_util_v2 import (
    setup_logging,
    LOG_CONFIGURED,
    DEV_ENVIRONMENT,
    PROD_ENVIRONMENT,
)


@pytest.fixture(autouse=True)
def reset_logging_config():
    """
    Resets the structlog configuration before each test.
    """
    if hasattr(structlog, LOG_CONFIGURED):
        delattr(structlog, LOG_CONFIGURED)
    root_logger = logging.getLogger()
    root_logger.handlers = []


def test_console_renderer_development_env(capsys):
    os.environ["ENVIRONMENT"] = DEV_ENVIRONMENT
    setup_logging(app_name=f"Test-{os.environ['ENVIRONMENT']}")
    logger = structlog.get_logger()

    test_event_msg = f"{os.environ['ENVIRONMENT']} test event msg"
    test_key_value = f"{os.environ['ENVIRONMENT']} test key value"

    with capsys.disabled():
        logger.info(test_event_msg, test_key=test_key_value)

    output_not_json = False
    output = capsys.readouterr().out
    try:
        json.loads(output)
    except json.JSONDecodeError:
        output_not_json = True

    assert output_not_json is True
    assert test_event_msg in output
    assert "test_key" in output


def test_console_renderer_production_env(capsys):
    os.environ["ENVIRONMENT"] = PROD_ENVIRONMENT
    setup_logging(app_name=f"Test-{os.environ['ENVIRONMENT']}")
    logger = structlog.get_logger()

    test_event_msg = f"{os.environ['ENVIRONMENT']} test event msg"
    test_key_value = f"{os.environ['ENVIRONMENT']} test key value"

    with capsys.disabled():
        logger.info(test_event_msg, test_key=test_key_value)

    output = capsys.readouterr().out
    try:
        log_entry = json.loads(output)
    except json.JSONDecodeError:
        pytest.fail(f"Log output is not a valid JSON. output: {output}")

    assert log_entry["event"] == test_event_msg
    assert log_entry["test_key"] == test_key_value
    assert log_entry["level"] == "info"
    assert "logger" in log_entry
    assert "timestamp" in log_entry


def test_console_renderer_unknown_env(capsys):
    os.environ["ENVIRONMENT"] = "UAT"
    setup_logging(app_name=f"Test-{os.environ['ENVIRONMENT']}")
    logger = structlog.get_logger()

    test_event_msg = f"{os.environ['ENVIRONMENT']} test event msg"
    test_key_value = f"{os.environ['ENVIRONMENT']} test key value"

    with capsys.disabled():
        logger.info(test_event_msg, test_key=test_key_value)

    output_not_json = False
    output = capsys.readouterr().out
    try:
        json.loads(output)
    except json.JSONDecodeError:
        output_not_json = True

    assert output_not_json is True
    assert "info" in output
    assert test_event_msg in output
    assert "test_key" in output
