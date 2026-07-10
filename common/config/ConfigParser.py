import logging
from os.path import expandvars
from pathlib import Path
from typing import Self

import yaml
from dotenv import load_dotenv

from common.config.schemas.BaseEnumModel import BaseEnumModel

logger = logging.getLogger(__name__)


class ConfigParser(BaseEnumModel):
    def model_save_yaml(self, save_path: Path) -> None:
        with open(save_path, "w") as f:
            f.write(yaml.safe_dump(self.model_dump(), sort_keys=True))

    @classmethod
    def from_yaml(cls, config_path: Path) -> Self:
        load_dotenv()
        # Create config with default values if not present
        if not config_path.is_file():
            logger.info("Configuration file not found. Using default values")
            cls().model_save_yaml(config_path)

        if config_path.suffix != ".yaml" or not config_path.is_file():
            raise FileNotFoundError("Configuration file must have .yaml extension")

        with open(config_path) as config_file:
            data = yaml.safe_load(expandvars(config_file.read())) or {}
        logger.info("Configuration loaded!")
        return cls.model_validate(data)
