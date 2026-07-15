from common.infrastructure.kafka.schemas.base_kafka_event import BaseKafkaEvent


class AccountLinkageEvent(BaseKafkaEvent):
    request_id: str
    account_id: int
