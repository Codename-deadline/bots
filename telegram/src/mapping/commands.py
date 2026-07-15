import shlex

from aiogram import Bot
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from common.contracts.incoming_command import CommandName, IncomingCommand
from telegram.src.exceptions.invalid_message_format_exception import (
    InvalidMessageFormatException,
)
from telegram.src.mapping.messages import to_incoming_message


def command_args(command: CommandObject | None) -> tuple[str, ...]:
    if command is None or command.args is None:
        return ()
    try:
        return tuple(shlex.split(command.args))
    except ValueError as exc:
        raise InvalidMessageFormatException from exc


async def to_incoming_command(
    message: Message,
    command_name: CommandName,
    command: CommandObject | None,
    bot: Bot,
    resolve_admin: bool = True,
) -> IncomingCommand:
    return IncomingCommand(
        message=await to_incoming_message(message, bot, resolve_admin),
        name=command_name,
        args=command_args(command),
    )
