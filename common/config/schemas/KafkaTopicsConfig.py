from common.config.schemas.BaseEnumModel import BaseEnumModel


class KafkaTopicsConfig(BaseEnumModel):
    account_linkage: str
    notifications: str
    otp: str
