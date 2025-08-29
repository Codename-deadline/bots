# Error handlers are imported in /telegram/src/main.py
# ruff: noqa: F401

from .global_error_handler import (
    invalid_message_format_handler,
    telegram_bad_request_handler,
)
