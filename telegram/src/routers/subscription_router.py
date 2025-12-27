from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram.src.services.SubscriptionService import SubscriptionService

subscription_router = Router()


@subscription_router.message(Command("sub_org"))
async def subscribe_to_organization(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.subscribe_to_organization(message)


@subscription_router.message(Command("sub_thr"))
async def subscribe_to_thread(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.subscribe_to_thread(message)


@subscription_router.message(Command("sub_ddl"))
async def subscribe_to_deadline(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.subscribe_to_deadline(message)


@subscription_router.message(Command("unsub_org"))
async def unsubscribe_from_organization(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.unsubscribe_from_deadline(message)


@subscription_router.message(Command("unsub_ерк"))
async def unsubscribe_from_thread(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.unsubscribe_from_thread(message)


@subscription_router.message(Command("unsub_ddl"))
async def unsubscribe_from_deadline(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.unsubscribe_from_deadline(message)


@subscription_router.message(Command("unsub_all"))
async def unsubscribe_from_all(
    message: Message, subscription_service: SubscriptionService
):
    await subscription_service.unsubscribe_from_all(message)
