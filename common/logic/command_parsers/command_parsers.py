from common.logic.command_parsers.parse_message import (
    __parse_message,
    __parse_message_optional,
)
from common.logic.enums import Language


def one_int_arg_parser(text: str) -> int | None:
    return __parse_message(text, lambda x: int(x[0]), lambda x: x[0].isnumeric(), 1)


def one_language_arg_parser(text: str) -> Language | None:
    return __parse_message(
        text,
        lambda args: Language(args[0].upper()),
        lambda args: args[0].upper() in Language.__members__.keys(),
        1,
    )


def one_language_optional_arg_parser(text: str) -> Language | None:
    return __parse_message_optional(
        text,
        lambda args: None if len(args) == 0 else Language(args[0].upper()),
        lambda args: len(args) == 0 or args[0].upper() in Language.__members__.keys(),
        1,
    )
