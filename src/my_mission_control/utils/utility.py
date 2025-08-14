import os
import re

from structlog.stdlib import get_logger

logger = get_logger(__name__)


def snake_to_camel(snake_str: str) -> str:
    # Handle _leading underscores
    leading_underscores = re.match(r"^_+", snake_str)
    prefix = leading_underscores.group(0) if leading_underscores else ""

    without_prefix = snake_str[len(prefix) :]
    camel_without_prefix = re.sub(r"_([a-zA-Z])", lambda match: match.group(1).upper(), without_prefix)

    return prefix + camel_without_prefix


def get_env_var_int(env_var_name: str, default_value: int) -> int:
    env_var_value = os.getenv(env_var_name)
    if env_var_value is None:
        return default_value

    try:
        return int(env_var_value)
    except ValueError:
        logger.warning(f"Invalid integer value for {env_var_name}, using default {default_value}")
        return default_value
