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


def combine_into(delta: dict, combined: dict) -> None:
    """
    Recursively combine dictionaries together, with `delta` taking priority in choosing the value for non-dict entries.

    Stolen from https://stackoverflow.com/a/70310511
    """
    for k, v in delta.items():
        if isinstance(v, dict):
            combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v


def load_config() -> tuple[ChurchToolsConf, None, None]:
    """
    Load the configuration in the following order (later takes precedence):

    1. Default config
    2. User-supplied config file
    3. Environment Variables
    4. CLI Parameters


    :return: The three top-tier config dicts
    """
    # Order is: file < envvar < CLI (CLI takes precedence)
    config: Config = dict()

    # ====================
    # Load default config
    default_file = open(os.path.join(os.path.dirname(__file__), 'default_config.json'), 'r')
    default_config: Config = json.load(default_file)
    default_file.close()
    del default_file

    combine_into(default_config, config)
    del default_config

    # ====================
    # Load user-given config
    user_config = dict()  # TODO

    combine_into(user_config, config)
    del user_config

    # ====================
    # Load ENV parameters
    env_config = dict()  # TODO

    combine_into(env_config, config)
    del env_config

    # ====================
    # Load CLI parameters
    cli_config = dict()  # TODO

    combine_into(cli_config, config)
    del cli_config

    return config['churchtools'], config['youtube'], config['wordpress']
