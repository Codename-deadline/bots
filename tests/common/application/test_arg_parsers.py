import pytest

from common.application.arg_parsers import (
    ParseFailureReason,
    parse_optional_language,
    parse_required_int,
    parse_required_language,
)
from common.application.enums import Language


def test_parse_required_language_accepts_supported_language_case_insensitive():
    result = parse_required_language(("en",))

    assert result.ok
    assert result.as_required_value() == Language.EN


@pytest.mark.parametrize(
    ("args", "reason"),
    [
        ((), ParseFailureReason.MISSING_ARGUMENT),
        (("en", "extra"), ParseFailureReason.TOO_MANY_ARGUMENTS),
        (("xyz",), ParseFailureReason.INVALID_LANGUAGE),
    ],
)
def test_parse_required_language_returns_specific_failures(args, reason):
    result = parse_required_language(args)

    assert not result.ok
    assert result.error is not None
    assert result.error.reason == reason


def test_parse_optional_language_accepts_missing_argument():
    result = parse_optional_language(())

    assert result.ok
    assert result.as_optional_value() is None


def test_parse_optional_language_parses_present_argument():
    result = parse_optional_language(("ru",))

    assert result.ok
    assert result.as_optional_value() == Language.RU


def test_parse_required_int_accepts_integer():
    result = parse_required_int(("42",))

    assert result.ok
    assert result.as_required_value() == 42


@pytest.mark.parametrize(
    ("args", "reason"),
    [
        ((), ParseFailureReason.MISSING_ARGUMENT),
        (("1", "2"), ParseFailureReason.TOO_MANY_ARGUMENTS),
        (("abc",), ParseFailureReason.INVALID_INTEGER),
    ],
)
def test_parse_required_int_returns_specific_failures(args, reason):
    result = parse_required_int(args)

    assert not result.ok
    assert result.error is not None
    assert result.error.reason == reason
