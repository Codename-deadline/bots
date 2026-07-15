import logging
import os
from pathlib import Path
from typing import Any, Self

import yaml
from dotenv import load_dotenv

from common.config.schemas.base_enum_model import BaseEnumModel

logger = logging.getLogger(__name__)


def _resolve_placeholders(value: Any, path: str = "") -> Any:
    if isinstance(value, dict):
        return {
            key: _resolve_placeholders(item, f"{path}.{key}" if path else str(key))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            _resolve_placeholders(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if not isinstance(value, str):
        return value

    if "${" not in value:
        return value
    if not value.startswith("${") or not value.endswith("}"):
        raise ValueError(
            f"Invalid placeholder for {path}; use ${{ENV}} or ${{ENV:default}}"
        )

    # Remove prefix "${" and suffix '}'
    expression: str = value[2:-1]
    name, separator, default = expression.partition(":")
    if not name.isidentifier() or "${" in expression or "}" in expression:
        raise ValueError(
            f"Invalid placeholder for {path}; use ${{ENV}} or ${{ENV:default}}"
        )

    environment_value: str | None = os.getenv(name)
    if environment_value is not None:
        return environment_value
    if separator:
        return default
    raise ValueError(f"Missing required environment variable {name} for {path}")


class ConfigParser(BaseEnumModel):
    @classmethod
    def from_yaml(cls, config_path: Path) -> Self:
        if config_path.suffix != ".yaml" or not config_path.is_file():
            raise FileNotFoundError(
                "Configuration file must exist and have a .yaml extension: "
                f"{config_path}"
            )

        load_dotenv(config_path.parent / ".env", override=False)
        with config_path.open(encoding="utf-8") as config_file:
            data = yaml.safe_load(config_file) or {}
        if not isinstance(data, dict):
            raise ValueError("Configuration root must be a YAML mapping")
        logger.info("Configuration loaded!")
        return cls.model_validate(_resolve_placeholders(data))
