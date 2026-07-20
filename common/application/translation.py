from enum import StrEnum


class TranslationKey(StrEnum):
    VALIDATION_INVALID_COMMAND_FORMAT = "validation.invalid_cmd_format"
    VALIDATION_DM_NOT_ALLOWED = "validation.dm_not_allowed"
    VALIDATION_UNSUPPORTED_LANGUAGE = "validation.unsupported_language"
    VALIDATION_CHAT_NOT_ALLOWED = "validation.chat_not_allowed"
    VALIDATION_ADMINS_ONLY_CMD = "validation.admins_only_cmd"

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
    AUTH_OTP_TEXT = "auth.otp.text"

    HELP_CURRENT_PAGE = "help.current_page"
    HELP_START_TITLE = "help.start.title"
    HELP_START_TEXT = "help.start.text"
    HELP_SUBSCRIPTION_TITLE = "help.subscription.title"
    HELP_SUBSCRIPTION_TEXT = "help.subscription.text"
    HELP_CHAT_TITLE = "help.chat.title"
    HELP_CHAT_TEXT = "help.chat.text"
    HELP_VERIFICATION_TITLE = "help.verification.title"
    HELP_VERIFICATION_TEXT = "help.verification.text"

    TIME_FIFTEEN_MINUTES = "time.fifteen_minutes"
    TIME_ONE_HOUR = "time.one_hour"
    TIME_ONE_DAY = "time.one_day"
    TIME_ONE_WEEK = "time.one_week"
    TIME_ONE_MONTH = "time.one_month"

    NOTIFICATIONS_DEADLINE_EXPIRY = "notifications.deadline_expiry"
    NOTIFICATIONS_GO_TO_DEADLINE = "notifications.go_to_deadline"

    PROMPT_ACCEPT = "prompt.accept"
    PROMPT_REJECT = "prompt.reject"

    ACCOUNT_LINKAGE_SUCCESS = "account_linkage.success"
    ACCOUNT_LINKAGE_IGNORED = "account_linkage.ignored"

    REGISTER_CHAT_SUCCESS = "register_chat.success"
    DEREGISTER_CHAT_SUCCESS = "deregister_chat.success"
    DEREGISTER_CHAT_NOT_REGISTERED = "deregister_chat.not_registered"
    CHAT_INFO_UPDATE_SUCCESS = "chat_info_update.success"
    USER_ID_SUCCESS = "user_id.success"

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
