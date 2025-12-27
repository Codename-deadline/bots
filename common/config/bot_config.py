from pathlib import Path

from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import override

from common.logic.constants import CONFIG_PATH

from ..logic.enums import Language
from .ConfigParser import ConfigParser
from .schemas.GrpcConfig import GrpcConfig
from .schemas.KafkaConfig import KafkaConfig


class BotConfig(ConfigParser):
    dev_mode: bool = Field(default=False)
    token: str = Field(default="${BOT_TOKEN}")
    fallback_language_str: str = Field(default=Language.EN)

    grpc: GrpcConfig = Field(default_factory=GrpcConfig)
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)

    @property
    def fallback_language(self):
        return Language(self.fallback_language_str.upper())

    @property
    def id(self) -> int:
        split_token: list[str] = self.token.split(":")
        assert len(split_token) == 2 and split_token[0].isnumeric()
        return int(split_token[0])

    @field_validator("fallback_language_str")
    def language_match(cls, v: str, info: ValidationInfo):
        Language(v.upper())
        return v.lower()

    @classmethod
    @override
    def from_yaml(cls, config_path: Path) -> "BotConfig":
        return super().from_yaml(BotConfig, config_path)


config: BotConfig = BotConfig.from_yaml(CONFIG_PATH)
