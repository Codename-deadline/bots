from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from common.application.enums import Language
from common.application.translation import TranslationKey

T = TypeVar("T")


class ParseFailureReason(StrEnum):
    MISSING_ARGUMENT = "missing_argument"
    TOO_MANY_ARGUMENTS = "too_many_arguments"
    INVALID_LANGUAGE = "invalid_language"
    INVALID_INTEGER = "invalid_integer"
    INVALID_FORMAT = "invalid_format"
    UNKNOWN_ARGUMENT = "unknown_argument"
    DUPLICATE_ARGUMENT = "duplicate_argument"
    INVALID_TIME_ZONE = "invalid_time_zone"


@dataclass
class ArgParseError:
    reason: ParseFailureReason
    message_key: TranslationKey


@dataclass(frozen=True)
class ArgParseResult[T]:
    value: T | None = None
    error: ArgParseError | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @classmethod
    def success(cls, value: T | None = None) -> ArgParseResult[T]:
        return cls(value=value)

    @classmethod
    def failure(
        cls, reason: ParseFailureReason, message_key: TranslationKey
    ) -> ArgParseResult[T]:
        return cls(error=ArgParseError(reason, message_key))

    def as_required_value(self) -> T:
        if not self.ok:
            raise ValueError("Attempted to get value when ok=False")
        if self.value is None:
            raise ValueError("Attempted to get required value which is None")
        return self.value

    def as_optional_value(self) -> T | None:
        if not self.ok:
            raise ValueError("Attempted to get value when ok=False")
        return self.value


@dataclass(frozen=True)
class ChatCommandArgs:
    language: Language | None = None
    time_zone: str | None = None


KNOWN_ARGUMENTS: set[str] = {"lang", "timezone"}


def _parse_named_arg(arg: str, values: dict[str, str]) -> ArgParseError | None:
    if arg.count("=") != 1:
        return ArgParseError(
            ParseFailureReason.INVALID_FORMAT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )

    raw_key, value = arg.split("=", 1)
    key: str = raw_key.lower()
    if key not in KNOWN_ARGUMENTS:
        return ArgParseError(
            ParseFailureReason.UNKNOWN_ARGUMENT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )
    if key in values:
        return ArgParseError(
            ParseFailureReason.DUPLICATE_ARGUMENT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )
    if not value:
        return ArgParseError(
            ParseFailureReason.MISSING_ARGUMENT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )
    values[key] = value
    return None


def parse_chat_args(
    args: tuple[str, ...], *, require_all: bool
) -> ArgParseResult[ChatCommandArgs]:
    values: dict[str, str] = {}
    for arg in args:
        if error := _parse_named_arg(arg, values):
            return ArgParseResult(error=error)

    if require_all and values.keys() != {"lang", "timezone"}:
        return ArgParseResult.failure(
            ParseFailureReason.MISSING_ARGUMENT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )

    language = None
    if raw_language := values.get("lang"):
        try:
            language = Language(raw_language.upper())
        except ValueError:
            return ArgParseResult.failure(
                ParseFailureReason.INVALID_LANGUAGE,
                TranslationKey.VALIDATION_UNSUPPORTED_LANGUAGE,
            )

    time_zone = values.get("timezone")
    if time_zone is not None:
        try:
            ZoneInfo(time_zone)
        except ValueError, ZoneInfoNotFoundError:
            return ArgParseResult.failure(
                ParseFailureReason.INVALID_TIME_ZONE,
                TranslationKey.VALIDATION_INVALID_TIME_ZONE,
            )

    return ArgParseResult.success(ChatCommandArgs(language, time_zone))


def parse_required_language(args: tuple[str, ...]) -> ArgParseResult[Language]:
    if len(args) == 0:
        return ArgParseResult.failure(
            ParseFailureReason.MISSING_ARGUMENT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )
    if len(args) > 1:
        return ArgParseResult.failure(
            ParseFailureReason.TOO_MANY_ARGUMENTS,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )

    try:
        return ArgParseResult.success(Language(args[0].upper()))
    except ValueError:
        return ArgParseResult.failure(
            ParseFailureReason.INVALID_LANGUAGE,
            TranslationKey.VALIDATION_UNSUPPORTED_LANGUAGE,
        )


def parse_optional_language(args: tuple[str, ...]) -> ArgParseResult[Language]:
    if len(args) == 0:
        return ArgParseResult.success()

    return parse_required_language(args)


def parse_required_int(args: tuple[str, ...]) -> ArgParseResult[int]:
    if len(args) == 0:
        return ArgParseResult.failure(
            ParseFailureReason.MISSING_ARGUMENT,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )
    if len(args) > 1:
        return ArgParseResult.failure(
            ParseFailureReason.TOO_MANY_ARGUMENTS,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )

    try:
        return ArgParseResult.success(int(args[0]))
    except ValueError:
        return ArgParseResult.failure(
            ParseFailureReason.INVALID_INTEGER,
            TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT,
        )
