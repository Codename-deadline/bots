from typing import Protocol

from common.application.enums import Language
from common.application.protocols.integration_gateway import IntegrationResponse
from common.application.translation import TranslationKey


class Translator(Protocol):
    def translate(
        self, key: TranslationKey, language: Language | None = None, **params
    ) -> str: ...

    def translate_response(self, response: IntegrationResponse, **params) -> str: ...
