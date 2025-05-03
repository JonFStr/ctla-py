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


def _load_default_config() -> Config:
    with open(os.path.join(os.path.dirname(__file__), 'default_config.json'), 'r') as default_file:
        return json.load(default_file)


def _load_user_config() -> Config:
    pass  # TODO


def _load_env_config() -> Config:
    for k, v in os.environ.items():
        if not k.startswith('CTLA_'):
            continue
        # TODO


def _load_cli_params() -> Config:
    pass  # TODO


def load_config() -> tuple[ChurchToolsConf, None, None]:
    """
    Load the configuration in the following order (later takes precedence):

    1. Default config
    2. User-supplied config file
    3. Environment Variables
    4. CLI Parameters


    :return: The three top-tier config dicts
    """
    # Order is: file < environment < CLI (CLI takes precedence)
    config: Config = dict()

    # Load default config
    combine_into(_load_default_config(), config)

    # Load user-given config
    combine_into(_load_user_config(), config)

    # Load ENV parameters
    combine_into(_load_env_config(), config)

    # Load CLI parameters
    combine_into(_load_cli_params(), config)

    return config['churchtools'], config['youtube'], config['wordpress']
