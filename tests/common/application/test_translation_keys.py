from pathlib import Path

import yaml

from common.application.enums import Language
from common.application.translation import TranslationKey

TRANSLATIONS_DIR = Path(__file__).parents[3] / "translations"


def _flatten_keys(value: dict, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    for item_key, item_value in value.items():
        full_key = f"{prefix}.{item_key}" if prefix else item_key
        if isinstance(item_value, dict):
            keys.update(_flatten_keys(item_value, full_key))
        else:
            keys.add(full_key)
    return keys


def _load_locale_keys(locale: str) -> set[str]:
    with (TRANSLATIONS_DIR / f"{locale}.yaml").open() as file:
        data = yaml.safe_load(file)
    return _flatten_keys(data[locale])


def test_translation_key_values_are_unique():
    values = [key.value for key in TranslationKey]

    assert len(values) == len(set(values))


def test_translation_keys_exist_in_all_locales():
    expected = {key.value for key in TranslationKey}
    supported_languages: set[str] = {locale.value.lower() for locale in Language}

    for locale in supported_languages:
        assert expected <= _load_locale_keys(locale)


def test_translation_keys_match_in_all_locales():
    supported_languages: list[str] = [locale.value.lower() for locale in Language]
    expected = _load_locale_keys(supported_languages[0])

    for locale in supported_languages[1:]:
        assert expected == _load_locale_keys(locale)
