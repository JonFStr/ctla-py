import json
import os.path
from typing import TypedDict

from . import args
from .configs.churchtools import ChurchToolsConf


class Config(TypedDict):
    """
    CTLA Main Configuration
    """
    churchtools: ChurchToolsConf
    youtube: None
    wordpress: None


# Easy access to loaded config
churchtools: ChurchToolsConf
youtube: None
wordpress: None
# noinspection PyTypeChecker
churchtools, youtube, wordpress = {}, {}, {}


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


def filter_none[T: dict](target: T) -> T:
    """
    Recursively filter `None`-values and empty dictionaries from dictionary target

    :param target: The dictionary to operate on
    :return: The new dictionary, with `None`-values filtered
    """
    result = {}
    for k, v in target.items():
        # Recurse into sub-dicts
        if isinstance(v, dict):
            v = filter_none(v)
            # Skip now-empty dicts
            if not v:
                continue
        # Filter out None-values
        if v is not None:
            result[k] = v
    return result


def _load_default_config() -> Config:
    with open(os.path.join(os.path.dirname(__file__), 'configs/default_config.json'), 'r') as default_file:
        return json.load(default_file)


def _load_user_config() -> Config:
    """
    Load user-defined configuration file.

    Defaults to the file named '`ctla_config.json`' in the current working directory,
    or the file passed via `-c` / `--config`, if set

    :return: The config dict parsed from the file
    """
    return json.load(args.parsed.config)


def _load_env_config() -> Config:
    """
    Load known environment variables into a Config dict and return it.

    Values that are not set from environment variables will be stripped from the dictionary.
    This function ensures proper types for the returned values.

    :return: The config dict
    """
    # noinspection PyTypeChecker
    raw_values: Config = {
        'churchtools': {
            'instance': os.getenv('CTLA_CT_INSTANCE'),
            'token': os.getenv('CTLA_CT_TOKEN'),
            'days_to_load': None,
            'manage_stream_behavior_fact': None,
            'stream_visibility_fact': None,
            'include_in_cal_fact': None,
            'show_on_homepage_fact': None,
            'speaker_service_name': None,
            'thumbnail_name': None,
            'stream_attachment_name': None
        },
        'youtube': {},
        'wordpress': {}
    }
    # Filter out undefined values (from when an environment variable was not set)
    # to avoid overriding the other config sources
    return filter_none(raw_values)


def _load_cli_params() -> Config:
    pass  # TODO


def load():
    """
    Load the configuration in the following order (later takes precedence):

    1. Default config
    2. User-supplied config file
    3. Environment Variables
    4. CLI Parameters
    """
    # Order is: file < environment < CLI (CLI takes precedence)
    config: Config = dict()

    # Load default config
    combine_into(_load_default_config(), config)

    # Load user-given config
    combine_into(_load_user_config(), config)

    # Load ENV parameters
    envc = _load_env_config()
    combine_into(envc, config)

    # Load CLI parameters
    combine_into(_load_cli_params(), config)

    global churchtools, youtube, wordpress
    churchtools = config['churchtools']
    youtube = config['youtube']
    wordpress = config['wordpress']
