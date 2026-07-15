from common.config.schemas.base_enum_model import BaseEnumModel


class KafkaTopicsConfig(BaseEnumModel):
    account_linkage: str
    notifications: str
    otp: str
