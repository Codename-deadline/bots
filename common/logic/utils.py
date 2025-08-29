import logging
import os


def get_logger_from_filepath(filepath: os.PathLike):
    return logging.getLogger(os.path.basename(filepath))
