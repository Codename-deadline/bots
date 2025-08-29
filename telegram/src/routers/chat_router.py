from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram.src.services.ChatService import ChatService

chat_router: Router = Router()


@chat_router.message(Command("reg_chat"))
async def register_chat(message: Message, chat_service: ChatService):
    await chat_service.register_chat(message)


@chat_router.message(Command("dereg_chat"))
async def deregister_chat(message: Message, chat_service: ChatService):
    await chat_service.deregister_chat(message)


@chat_router.message(Command("upd_chat_info"))
async def update_chat_info(message: Message, chat_service: ChatService):
    await chat_service.update_chat_info(message)
