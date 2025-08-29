from typing import Callable

from common.logic.types import T


def __parse_message(
    text: str,
    argument_converter: Callable[[list[str]], T],
    argument_validator: Callable[[list[str]], bool],
    argc: int,
) -> T | None:
    split_message: list[str] = text.replace("\n", " ").split(" ")
    if len(split_message) - 1 != argc or not argument_validator(split_message[1:]):
        return None
    return argument_converter(split_message[1:])


def __parse_message_optional(
    text: str,
    argument_converter: Callable[[list[str]], T],
    argument_validator: Callable[[list[str]], bool],
    argc: int,
) -> T | None:
    split_message: list[str] = text.replace("\n", " ").split(" ")
    if len(split_message) - 1 > argc or not argument_validator(split_message[1:]):
        return None
    return argument_converter(split_message[1:])
