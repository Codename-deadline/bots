from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.i18n import format_with_locale, get_translation
from common.kafka.schemas.AccountLinkageEvent import AccountLinkageEvent
from common.kafka.schemas.NotificationEvent import NotificationEvent
from common.kafka.schemas.OtpEvent import OtpEvent
from telegram.src.bot import bot
from telegram.src.markup.schemas.AccountLinkageCallbackData import (
    AccountLinkageCallbackData,
)


class MessageService:
    @staticmethod
    async def link_account_send_message(event: AccountLinkageEvent) -> None:
        # TODO: Markup builder
        await bot.send_message(
            event.account_id,
            format_with_locale("auth.account_linkage.text"),
            reply_markup=InlineKeyboardBuilder()
            .row(
                InlineKeyboardButton(
                    text="✅",
                    callback_data=AccountLinkageCallbackData(
                        request_id=event.request_id, is_accepted=True
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌",
                    callback_data=AccountLinkageCallbackData(
                        request_id=event.request_id, is_accepted=False
                    ).pack(),
                ),
            )
            .as_markup(),
        )

    @staticmethod
    async def deadline_notification_send_message(event: NotificationEvent):
        # TODO: Add a link to the deadline or a markup
        time_remaining_str: str = get_translation(
            f"time.{event.timeRemaining.name.lower()}", event.language
        )
        if time_remaining_str.startswith("time"):
            time_remaining_str = get_translation("errors.error", event.language)
        await bot.send_message(
            event.chat_id,
            format_with_locale(
                "notifications.deadline_expiry",
                event.language,
                title=event.deadline.title,
                due=f"{event.deadline.due.strftime('%H:%M %d.%m.%Y')} UTC+0",
                time_remaining=time_remaining_str,
            ),
        )

    @staticmethod
    async def otp_code_send_message(event: OtpEvent):
        await bot.send_message(
            event.account_id,
            format_with_locale("auth.otp.text", event.language, code=event.code),
        )
