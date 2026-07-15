from common.application.translation import TranslationKey
from common.infrastructure.kafka.enums.time_remaining import TimeRemaining

TIME_REMAINING_TRANSLATION_KEYS: dict[TimeRemaining, TranslationKey] = {
    TimeRemaining.FIFTEEN_MINUTES: TranslationKey.TIME_FIFTEEN_MINUTES,
    TimeRemaining.ONE_HOUR: TranslationKey.TIME_ONE_HOUR,
    TimeRemaining.ONE_DAY: TranslationKey.TIME_ONE_DAY,
    TimeRemaining.ONE_WEEK: TranslationKey.TIME_ONE_WEEK,
    TimeRemaining.ONE_MONTH: TranslationKey.TIME_ONE_MONTH,
}
