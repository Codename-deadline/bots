import os

import yaml
from os.path import expandvars

from typing import Type
from pathlib import Path
from dotenv import load_dotenv

from common.config.schemas.BaseEnumModel import BaseEnumModel
from common.logic.utils import get_logger_from_filepath


logger = get_logger_from_filepath(__file__)


class ConfigParser(BaseEnumModel):
    def model_save_yaml(self, save_path: Path) -> None:
        with open(save_path, "w") as f:
            f.write(yaml.safe_dump(self.model_dump(), sort_keys=True))

    @staticmethod
    def from_yaml(config_type: Type, config_path: Path):
        load_dotenv()
        # Create config with default values if not present
        if not config_path.is_file():
            logger.info("Configuration file not found. Using default values")
            config_type().model_save_yaml(config_path)

        if config_path.is_file() and config_path.suffix != ".yaml":
            raise FileNotFoundError("Configuration file must have .yaml extension")

        with open(config_path, "r") as config_file:
            data = yaml.safe_load(expandvars(config_file.read()))
        logger.info("Configuration loaded!")
        return config_type().model_validate(data)
