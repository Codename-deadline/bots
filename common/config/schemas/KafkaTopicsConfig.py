from pydantic import Field

from common.config.schemas.BaseEnumModel import BaseEnumModel


class KafkaTopicsConfig(BaseEnumModel):
    account_linkage: str = Field(default="private.integration.accountlinkage")
    notifications: str = Field(default="private.integration.notifications")
    otp: str = Field(default="private.auth.otp")
