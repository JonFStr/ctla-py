from dataclasses import dataclass
from enum import Enum, auto

import config
from configs.churchtools import BooleanFactConf


class ManageStreamBehavior(Enum):
    YES = auto()
    NO = auto()
    IGNORE = auto()


class YtVisibility(Enum):
    VISIBLE = auto()
    UNLISTED = auto()
    PRIVATE = auto()


def _parse_boolean_fact(conf_name: str, facts: dict[str, int | str]) -> bool:
    """Parse a boolean fact"""
    # noinspection PyTypeChecker,PyTypedDict
    conf: BooleanFactConf = config.churchtools.get(conf_name)
    if conf is None:
        result = False
    else:
        fact_val = facts.get(conf['name'])
        result = conf['default']
        if fact_val is not None:
            if fact_val == conf['yes_value']:
                result = True
            elif fact_val == conf['no_value']:
                result = False
    return result


@dataclass
class Facts:
    """Class holding facts for an event"""
    behavior: ManageStreamBehavior
    visibility: YtVisibility
    link_in_cal: bool
    on_homepage: bool
    create_post: bool

    @classmethod
    def from_api_json(cls, facts: dict[str, int | str]):
        """Create instance from API results"""
        # Behavior
        behavior = _get_default_behavior_value()
        bf = facts.get(config.churchtools['manage_stream_behavior_fact']['name'],  # Get the value from Churchtools,
                       config.churchtools['manage_stream_behavior_fact']['default'])  # Default if unset
        if bf == config.churchtools['manage_stream_behavior_fact']['yes_value']:
            behavior = ManageStreamBehavior.YES
        elif bf == config.churchtools['manage_stream_behavior_fact']['ignore_value']:
            behavior = ManageStreamBehavior.IGNORE
        elif bf == config.churchtools['manage_stream_behavior_fact']['no_value']:
            behavior = ManageStreamBehavior.NO

        # Visibility
        vf = facts.get(config.churchtools['stream_visibility_fact']['name'],
                       config.churchtools['stream_visibility_fact']['default'])
        if vf == config.churchtools['stream_visibility_fact']['visible_value']:
            visibility = YtVisibility.VISIBLE
        elif vf == config.churchtools['stream_visibility_fact']['unlisted_value']:
            visibility = YtVisibility.UNLISTED
        elif vf == config.churchtools['stream_visibility_fact']['private_value']:
            visibility = YtVisibility.PRIVATE
        else:
            raise ValueError(
                f'Unexpected Value for YouTube-Visibility-Fact '
                f'("{config.churchtools['stream_visibility_fact']['name']}"): "{vf}"\n'
                f'Needs to be one of "{config.churchtools['stream_visibility_fact']['visible_value']}", '
                f'"{config.churchtools['stream_visibility_fact']['unlisted_value']}" or '
                f'"{config.churchtools['stream_visibility_fact']['private_value']}", according to configuration.')

        return Facts(
            behavior=behavior,
            link_in_cal=_parse_boolean_fact('include_in_cal_fact', facts),
            visibility=visibility,
            on_homepage=_parse_boolean_fact('show_on_homepage', facts),
            create_post=_parse_boolean_fact('create_post_fact', facts)
        )


def _get_default_behavior_value() -> ManageStreamBehavior:
    """Retrieve the default value for the Stream Behavior Fact from config"""
    bf_conf = config.churchtools['manage_stream_behavior_fact']
    default = bf_conf['default']
    if default == bf_conf['yes_value']:
        return ManageStreamBehavior.YES
    elif default == bf_conf['no_value']:
        return ManageStreamBehavior.NO
    elif default == bf_conf['ignore_value']:
        return ManageStreamBehavior.IGNORE
    else:
        raise ValueError('Config value for "churchtools.manage_stream_behavior_fact.default" must match one of '
                         'the given values for Yes, No or Ignore')
