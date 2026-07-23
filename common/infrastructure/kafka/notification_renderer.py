from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from common.application.protocols.translator import Translator
from common.application.translation import TranslationKey
from common.infrastructure.i18n.mappings import TIME_REMAINING_TRANSLATION_KEYS
from common.infrastructure.kafka.enums.time_remaining import TimeRemaining
from common.infrastructure.kafka.schemas.notification_event import NotificationEvent


def _format_utc_offset(offset: timedelta) -> str:
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    hours, minutes = divmod(abs(total_minutes), 60)
    return f"UTC{sign}{hours:02d}:{minutes:02d}"


def render_notification(event: NotificationEvent, translator: Translator) -> str:
    if event.deadline.due.tzinfo is None or event.deadline.due.utcoffset() is None:
        raise ValueError("Deadline due must be timezone-aware")
    due: datetime = event.deadline.due.astimezone(ZoneInfo(event.time_zone))
    offset: timedelta | None = due.utcoffset()
    if offset is None:
        raise ValueError("Deadline due must be timezone-aware")

    translation_key = TranslationKey.NOTIFICATIONS_DEADLINE_OVERDUE
    params = {
        "title": event.deadline.title,
        "organization": event.organization.title,
        "thread": event.thread.title,
        "due": f"{due.strftime('%H:%M %d.%m.%Y')} {_format_utc_offset(offset)}",
    }
    if event.timeRemaining is not TimeRemaining.NO_TIME:
        translation_key = TranslationKey.NOTIFICATIONS_DEADLINE_EXPIRY
        params["time_remaining"] = translator.translate(
            TIME_REMAINING_TRANSLATION_KEYS[event.timeRemaining], event.language
        )

    return translator.translate(translation_key, event.language, **params)
