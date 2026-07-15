from dataclasses import dataclass

from common.contracts.interaction import VerificationInteraction


@dataclass(frozen=True)
class OptionSelection:
    prompt_id: str
    account_id: int
    chat_id: int
    message_id: int
    interaction: VerificationInteraction
    value: str
