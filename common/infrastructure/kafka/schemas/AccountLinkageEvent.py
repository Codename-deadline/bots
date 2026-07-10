from common.infrastructure.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent


class AccountLinkageEvent(BaseKafkaEvent):
    request_id: str
    account_id: int
