from dataclasses import dataclass

from common.application.translation import TranslationKey


@dataclass(frozen=True)
class Choice:
    value: str
    label_key: TranslationKey
