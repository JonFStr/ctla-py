import json
import os.path
from typing import TypedDict

from .config_churchtools_dataclasses import ChurchToolsConf


class Config(TypedDict):
    """
    CTLA Main Configuration
    """
    churchtools: ChurchToolsConf
    youtube: None
    wordpress: None


# TODO order is cli > envvar > file

default_file = open(os.path.join(os.path.dirname(__file__), 'default_config.json'), 'r')
config: Config = json.load(default_file)

default_file.close()
del default_file
