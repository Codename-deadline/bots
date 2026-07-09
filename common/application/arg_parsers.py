from enum import IntEnum
from typing import TypeVar

from pydantic.dataclasses import dataclass

from common.logic.enums import Language

T = TypeVar("T")


class ParseFailureReason(IntEnum):
    MISSING = 0
    INVALID = 1


@dataclass
class ArgParseResult[T]:
    ok: bool
    reason: ParseFailureReason | None = None
    _value: T | None = None

    def as_required_value(self) -> T:
        if not self.ok:
            raise ValueError("Attempted to get value when ok=False")
        if self._value is None:
            raise ValueError("Attempted to get required value which is None")
        return self._value

    def as_optional_value(self) -> T | None:
        if not self.ok:
            raise ValueError("Attempted to get value when ok=False")
        return self._value


def parse_required_language(args: tuple[str, ...]) -> ArgParseResult[Language]:
    if len(args) != 1:
        return ArgParseResult(False, ParseFailureReason.MISSING)

    try:
        return ArgParseResult(True, _value=Language(args[0].upper()))
    except ValueError:
        return ArgParseResult(False)


def parse_optional_language(args: tuple[str, ...]) -> ArgParseResult[Language]:
    if len(args) == 0:
        return ArgParseResult(True)

    return parse_required_language(args)


def parse_required_int(args: tuple[str, ...]) -> ArgParseResult[int]:
    if len(args) != 1:
        return ArgParseResult(False, ParseFailureReason.MISSING)

    try:
        return ArgParseResult(True, _value=int(args[0]))
    except ValueError:
        return ArgParseResult(False, ParseFailureReason.INVALID)
