import logging

import i18n

from common.application.constants import TRANSLATIONS_PATH
from common.application.enums import Language
from common.application.protocols.integration_gateway import IntegrationResponse
from common.application.protocols.translator import Translator
from common.application.translation import TranslationKey

logger = logging.getLogger(__name__)


class I18nTranslator(Translator):
    def __init__(self, fallback_language: Language):
        self.fallback_language = fallback_language
        if str(TRANSLATIONS_PATH) not in i18n.load_path:
            i18n.load_path.append(str(TRANSLATIONS_PATH))
        i18n.set("file_format", "yaml")
        i18n.set("filename_format", "{locale}.{format}")
        i18n.set("fallback", fallback_language.name.lower())

    def translate(
        self, key: TranslationKey, language: Language | None = None, **params
    ) -> str:
        locale = language or self.fallback_language
        i18n.set("locale", locale.name.lower())
        return i18n.t(key.value, **params)

    def translate_response(self, response: IntegrationResponse, **params) -> str:
        key = TranslationKey.from_raw(response.key)
        if key.value != response.key:
            logger.error("Unknown translation key returned by API: %s", response.key)
        return self.translate(key, response.language, **params)
