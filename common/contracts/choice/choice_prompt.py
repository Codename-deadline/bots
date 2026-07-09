from dataclasses import dataclass

from common.contracts.choice.choice import Choice


@dataclass(frozen=True)
class ChoicePrompt:
    id: str
    text: str
    interaction: str
    choices: list[Choice]
