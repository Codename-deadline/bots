import re
from functools import singledispatch

import i18n
from telegramify_markdown import markdownify

from common.config.bot_config import config
from common.logic.constants import TRANSLATIONS_PATH
from common.logic.enums import Language
from common.logic.grpc.GrpcResponse import GrpcResponse


def configure_i18n(locale: Language):
    i18n.load_path.append(str(TRANSLATIONS_PATH))
    i18n.set("file_format", "yml")
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("fallback", locale.name.lower())


__characters_to_escape: list[str] = [
    "[",
    "]",
    "(",
    ")",
    ">",
    "#",
    "+",
    "-",
    "=",
    "{",
    "}",
    ".",
    "!",
]

# Escape underscores in commands if not already
# E.g /long_command -> /long\\_command, /long\\_command -> no changes
COMMAND_UNDERSCORES_RE = re.compile(r"/[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+")


def escape_md_v2(s: str) -> str:
    return markdownify(rf"{s}")
    for c in __characters_to_escape:
        s = s.replace(c, f"\\{c}")
    print(
        COMMAND_UNDERSCORES_RE.sub(lambda m: re.sub(r"(?<!\\)_", r"\\_", m.group(0)), s)
    )
    return COMMAND_UNDERSCORES_RE.sub(
        lambda m: re.sub(r"(?<!\\)_", r"\\_", m.group(0)), s
    )


def get_translation(key: str, language: Language = config.fallback_language, **kwargs):
    i18n.set("locale", language.name.lower())
    return i18n.t(key, **kwargs)


@singledispatch
def format_with_locale(arg, **kwargs) -> str:
    raise TypeError("Unsupported type for format_with_locale")


@format_with_locale.register
def _(response: GrpcResponse, **kwargs):
    i18n.set("locale", response.language.name.lower())
    message = i18n.t(response.key, **kwargs)
    return escape_md_v2(message)


@format_with_locale.register
def _(key: str, locale: Language = config.fallback_language, **kwargs):
    i18n.set("locale", locale.name.lower())
    message = i18n.t(key, **kwargs)
    return escape_md_v2(message)
