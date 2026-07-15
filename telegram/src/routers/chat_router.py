from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from common.application.services.chat_service import ChatService
from common.contracts.incoming_command import CommandName
from telegram.src.mapping.commands import to_incoming_command

chat_router: Router = Router()


@chat_router.message(Command("reg_chat"))
async def register_chat(
    message: Message, command: CommandObject, bot: Bot, chat_service: ChatService
):
    await chat_service.register_chat(
        await to_incoming_command(
            message, CommandName.REGISTER_CHAT, command, bot, resolve_admin=True
        )
    )


@chat_router.message(Command("dereg_chat"))
async def deregister_chat(
    message: Message, command: CommandObject, bot: Bot, chat_service: ChatService
):
    await chat_service.deregister_chat(
        await to_incoming_command(
            message, CommandName.DEREGISTER_CHAT, command, bot, resolve_admin=True
        )
    )


@chat_router.message(Command("update_chat_info"))
async def update_chat_info(
    message: Message, command: CommandObject, bot: Bot, chat_service: ChatService
):
    await chat_service.update_chat_info(
        await to_incoming_command(
            message, CommandName.UPDATE_CHAT_INFO, command, bot, resolve_admin=True
        )
    )
