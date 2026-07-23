import pytest

from common.application.arg_parsers import (
    ParseFailureReason,
    parse_chat_args,
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


def test_parse_chat_args_is_named_order_independent_and_preserves_time_zone_case():
    result = parse_chat_args(("TimeZone=Europe/Moscow", "LANG=ru"), require_all=True)

    assert result.ok
    assert result.as_required_value().language == Language.RU
    assert result.as_required_value().time_zone == "Europe/Moscow"


def test_parse_chat_args_allows_any_update_subset_and_no_args():
    language = parse_chat_args(("lang=en",), require_all=False)
    time_zone = parse_chat_args(("timezone=Etc/UTC",), require_all=False)
    empty = parse_chat_args((), require_all=False)

    assert language.as_required_value().language == Language.EN
    assert language.as_required_value().time_zone is None
    assert time_zone.as_required_value().time_zone == "Etc/UTC"
    assert empty.as_required_value().language is None
    assert empty.as_required_value().time_zone is None


@pytest.mark.parametrize(
    ("args", "require_all", "reason"),
    [
        (("lang=en",), True, ParseFailureReason.MISSING_ARGUMENT),
        (("timezone=Etc/UTC",), True, ParseFailureReason.MISSING_ARGUMENT),
        (
            ("lang=en", "timezone=Etc/UTC", "extra=x"),
            True,
            ParseFailureReason.UNKNOWN_ARGUMENT,
        ),
        (("lang=en", "LANG=ru"), False, ParseFailureReason.DUPLICATE_ARGUMENT),
        (("lang=",), False, ParseFailureReason.MISSING_ARGUMENT),
        (("lang",), False, ParseFailureReason.INVALID_FORMAT),
        (("lang=en=ru",), False, ParseFailureReason.INVALID_FORMAT),
        (("timezone=+05:45",), False, ParseFailureReason.INVALID_TIME_ZONE),
        (("timezone=Europe/moscow",), False, ParseFailureReason.INVALID_TIME_ZONE),
        (("timezone=Not/AZone",), False, ParseFailureReason.INVALID_TIME_ZONE),
    ],
)
def test_parse_chat_args_rejects_invalid_input(args, require_all, reason):
    result = parse_chat_args(args, require_all=require_all)

    assert not result.ok
    assert result.error is not None
    assert result.error.reason == reason


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
