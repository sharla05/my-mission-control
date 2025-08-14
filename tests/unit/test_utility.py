import pytest

from my_mission_control.utils.utility import get_env_var_int, snake_to_camel


# Tests for snake_to_camel
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("simple_case", "simpleCase"),
        ("multiple_words_case", "multipleWordsCase"),
        ("_single_leading_underscore", "_singleLeadingUnderscore"),
        ("__multiple_leading_underscore", "__multipleLeadingUnderscore"),
        ("noChange", "noChange"),
        ("", ""),
    ],
)
def test_snake_to_camel(input_str, expected):
    assert snake_to_camel(input_str) == expected


# Tests for get_env_var_int
def test_get_env_var_int_valid(monkeypatch):
    """Environment variable is defined"""
    monkeypatch.setenv("TEST_INT_VAR", 99)
    assert get_env_var_int("TEST_INT_VAR", 0) == 99


def test_get_env_var_int_missing(monkeypatch):
    """Environment variable not defined"""
    monkeypatch.delenv("MISSING_VAR", raising=False)
    assert get_env_var_int("MISSING_VAR", 88) == 88


def test_get_env_var_int_invalid(monkeypatch):
    """Environment variable is a string"""
    monkeypatch.setenv("INVALID_INT_VAR", "string_value")
    assert get_env_var_int("INVALID_INT_VAR", 77) == 77
