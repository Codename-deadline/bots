from enum import StrEnum


class TranslationKey(StrEnum):
    VALIDATION_INVALID_COMMAND_FORMAT = "validation.invalid_cmd_format"
    VALIDATION_UNSUPPORTED_LANGUAGE = "validation.unsupported_language"

    ERRORS_ERROR = "errors.error"
    ERRORS_REQUEST_NOT_FOUND = "errors.request_not_found"
    ERRORS_USER_NOT_FOUND = "errors.user_not_found"
    ERRORS_LINKED_ACCOUNT_NOT_FOUND = "errors.linked_account_not_found"
    ERRORS_CHAT_MANAGEMENT_DENIED = "errors.chat_management_denied"
    ERRORS_CHAT_ALREADY_REGISTERED = "errors.chat_already_registered"
    ERRORS_CHAT_NOT_FOUND = "errors.chat_not_found"
    ERRORS_ORGANIZATION_NOT_FOUND = "errors.organization_not_found"
    ERRORS_ORGANIZATION_ACCESS_DENIED = "errors.organization_access_denied"
    ERRORS_THREAD_NOT_FOUND = "errors.thread_not_found"
    ERRORS_THREAD_ACCESS_DENIED = "errors.thread_access_denied"
    ERRORS_DEADLINE_NOT_FOUND = "errors.deadline_not_found"
    ERRORS_DEADLINE_ACCESS_DENIED = "errors.deadline_access_denied"
    ERRORS_SERVER_INTERNAL = "errors.server_internal"
    ERRORS_SERVER_UNAVAILABLE = "errors.server_unavailable"

    AUTH_ACCOUNT_LINKAGE_TEXT = "account_linkage.text"

    PROMPT_ACCEPT = "prompt.accept"
    PROMPT_REJECT = "prompt.reject"

    ACCOUNT_LINKAGE_SUCCESS = "account_linkage.success"
    ACCOUNT_LINKAGE_IGNORED = "account_linkage.ignored"

    REGISTER_CHAT_SUCCESS = "register_chat.success"
    DEREGISTER_CHAT_SUCCESS = "deregister_chat.success"
    DEREGISTER_CHAT_NOT_REGISTERED = "deregister_chat.not_registered"
    CHAT_INFO_UPDATE_SUCCESS = "chat_info_update.success"

    SUB_ORGANIZATION_SUCCESS = "sub.organization.success"
    SUB_ORGANIZATION_ALREADY_SUBSCRIBED = "sub.organization.already_subscribed"
    SUB_THREAD_SUCCESS = "sub.thread.success"
    SUB_THREAD_ALREADY_SUBSCRIBED = "sub.thread.already_subscribed"
    SUB_DEADLINE_SUCCESS = "sub.deadline.success"
    SUB_DEADLINE_ALREADY_SUBSCRIBED = "sub.deadline.already_subscribed"

    UNSUB_ORGANIZATION_SUCCESS = "unsub.organization.success"
    UNSUB_ORGANIZATION_NOT_SUBSCRIBED = "unsub.organization.not_subscribed"
    UNSUB_THREAD_SUCCESS = "unsub.thread.success"
    UNSUB_THREAD_NOT_SUBSCRIBED = "unsub.thread.not_subscribed"
    UNSUB_DEADLINE_SUCCESS = "unsub.deadline.success"
    UNSUB_DEADLINE_NOT_SUBSCRIBED = "unsub.deadline.not_subscribed"
    UNSUB_ALL_SUCCESS = "unsub.all.success"

    @classmethod
    def from_raw(cls, value: str) -> TranslationKey:
        try:
            return cls(value)
        except ValueError:
            return cls.ERRORS_ERROR
