from dataclasses import dataclass


@dataclass(frozen=True)
class Choice:
    value: str
    label: str
