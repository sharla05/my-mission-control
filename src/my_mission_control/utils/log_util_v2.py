import logging
import os
import sys
from typing import Any

import structlog


LOG_CONFIGURED = "_log_configured"
DEV_ENVIRONMENT = "development"
PROD_ENVIRONMENT = "production"


def _get_log_render():
    """
    Determine log render based on enviorenment
    """
    app_env = os.getenv("ENVIRONMENT", DEV_ENVIRONMENT).lower()

    if app_env == PROD_ENVIRONMENT:
        return structlog.processors.JSONRenderer()
    return structlog.dev.ConsoleRenderer()


def setup_logging(
    default_log_level: int = logging.INFO,
    log_level_env_var: str = "LOG_LEVEL",
    **global_context: Any,
):
    """
    Setup structlog configuration and integration with standard logging library,
    creat global context variable for use across the application
    """

    if getattr(structlog, LOG_CONFIGURED, False):
        return

    env_log_level = os.getenv(log_level_env_var, "").upper()
    app_log_level = getattr(logging, env_log_level, default_log_level)
    app_log_render = _get_log_render()

    common_log_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
    ]

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *common_log_processors,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            app_log_render,
        ],
        cache_logger_on_first_use=True,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )

    app_log_formatter = logging.Formatter("%(message)s")

    stdout_log_handler = logging.StreamHandler(sys.stdout)
    stdout_log_handler.setFormatter(app_log_formatter)

    stderr_log_handler = logging.StreamHandler(sys.stderr)
    stderr_log_handler.setFormatter(app_log_formatter)
    stderr_log_handler.setLevel(logging.ERROR)

    root_logger = logging.getLogger()
    root_logger.setLevel(app_log_level)
    root_logger.addHandler(stdout_log_handler)
    root_logger.addHandler(stderr_log_handler)

    structlog.contextvars.bind_contextvars(**global_context)

    setattr(structlog, LOG_CONFIGURED, True)
