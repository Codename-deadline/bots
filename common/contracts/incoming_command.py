from dataclasses import dataclass
from enum import StrEnum

from common.contracts.incoming_message import IncomingMessage


class CommandName(StrEnum):
    REGISTER_CHAT = "reg_chat"
    DEREGISTER_CHAT = "dereg_chat"
    UPDATE_CHAT_INFO = "update_chat_info"

    SUBSCRIBE_TO_ORGANIZATION = "sub_org"
    SUBSCRIBE_TO_THREAD = "sub_thr"
    SUBSCRIBE_TO_DEADLINE = "sub_ddl"

    UNSUBSCRIBE_FROM_ORGANIZATION = "unsub_org"
    UNSUBSCRIBE_FROM_THREAD = "unsub_thr"
    UNSUBSCRIBE_FROM_DEADLINE = "unsub_ddl"
    UNSUBSCRIBE_FROM_ALL = "unsub_all"


@dataclass(frozen=True)
class IncomingCommand:
    message: IncomingMessage
    name: CommandName
    args: tuple[str, ...]

    def match_or_raise(self, expected_command: CommandName):
        if self.name != expected_command:
            raise ValueError(
                f'Expected "{expected_command.name}", found: {self.name} provided'
            )
