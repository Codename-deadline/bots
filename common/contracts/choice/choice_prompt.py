from dataclasses import dataclass

from common.application.translation import TranslationKey
from common.contracts.choice.choice import Choice
from common.contracts.interaction import VerificationInteraction


@dataclass(frozen=True)
class ChoicePrompt:
    id: str
    text_key: TranslationKey
    interaction: VerificationInteraction
    choices: list[Choice]
