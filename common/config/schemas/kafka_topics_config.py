from pydantic import Field

from common.config.schemas.base_enum_model import BaseEnumModel


class KafkaTopicsConfig(BaseEnumModel):
    account_linkage: str = Field(default="${KAFKA_TOPICS_ACCOUNT_LINKAGE}")
    notifications: str = Field(default="${KAFKA_TOPICS_NOTIFICATIONS}")
    otp: str = Field(default="${KAFKA_TOPICS_OTP}")
