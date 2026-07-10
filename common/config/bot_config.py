from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from common.application.constants import CONFIG_PATH
from common.application.enums import Language

from .config_parser import ConfigParser
from .schemas.grpc_config import GrpcConfig
from .schemas.kafka_config import KafkaConfig

TOKEN_PARTS_COUNT: int = 2


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
        assert len(split_token) == TOKEN_PARTS_COUNT and split_token[0].isnumeric()
        return int(split_token[0])

    @field_validator("fallback_language_str")
    def language_match(cls, v: str, info: ValidationInfo):
        Language(v.upper())
        return v.lower()


config: BotConfig = BotConfig.from_yaml(CONFIG_PATH)
