from typing import Callable

from common.logic.types import T
from telegram.src.exceptions import InvalidMessageFormatException


def parse_command(text: str, command_parser: Callable[[str], T | None]) -> T:
    """
    Parses the provided `text` using `command_parser`
    Throws `InvalidMessageFormat` if `command_parser` fails to extract at least one argument
    """
    arguments: T | None = command_parser(text)
    if arguments is None:
        raise InvalidMessageFormatException
    return arguments
