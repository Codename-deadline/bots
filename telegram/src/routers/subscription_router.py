from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from common.application.protocols.integration_gateway import ScopeType
from common.application.services.subscription_service import SubscriptionService
from common.contracts.incoming_command import CommandName
from telegram.src.mapping.commands import to_incoming_command

subscription_router = Router()


@subscription_router.message(Command("sub_org"))
async def subscribe_to_organization(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.subscribe_to(
        await to_incoming_command(
            message,
            CommandName.SUBSCRIBE_TO_ORGANIZATION,
            command,
            bot,
        ),
        ScopeType.ORGANIZATION,
    )


@subscription_router.message(Command("sub_thr"))
async def subscribe_to_thread(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.subscribe_to(
        await to_incoming_command(
            message, CommandName.SUBSCRIBE_TO_THREAD, command, bot
        ),
        ScopeType.THREAD,
    )


@subscription_router.message(Command("sub_ddl"))
async def subscribe_to_deadline(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.subscribe_to(
        await to_incoming_command(
            message, CommandName.SUBSCRIBE_TO_DEADLINE, command, bot
        ),
        ScopeType.DEADLINE,
    )


@subscription_router.message(Command("unsub_org"))
async def unsubscribe_from_organization(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.unsubscribe_from(
        await to_incoming_command(
            message,
            CommandName.UNSUBSCRIBE_FROM_ORGANIZATION,
            command,
            bot,
        ),
        ScopeType.ORGANIZATION,
    )


@subscription_router.message(Command("unsub_thr"))
async def unsubscribe_from_thread(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.unsubscribe_from(
        await to_incoming_command(
            message,
            CommandName.UNSUBSCRIBE_FROM_THREAD,
            command,
            bot,
        ),
        ScopeType.THREAD,
    )


@subscription_router.message(Command("unsub_ddl"))
async def unsubscribe_from_deadline(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.unsubscribe_from(
        await to_incoming_command(
            message,
            CommandName.UNSUBSCRIBE_FROM_DEADLINE,
            command,
            bot,
        ),
        ScopeType.DEADLINE,
    )


@subscription_router.message(Command("unsub_all"))
async def unsubscribe_from_all(
    message: Message,
    command: CommandObject,
    bot: Bot,
    subscription_service: SubscriptionService,
):
    await subscription_service.unsubscribe_from_all(
        await to_incoming_command(
            message, CommandName.UNSUBSCRIBE_FROM_ALL, command, bot
        )
    )
