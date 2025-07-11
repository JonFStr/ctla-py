from dataclasses import dataclass
from enum import Enum, auto

import config


class ManageStreamBehavior(Enum):
    YES = auto()
    NO = auto()
    IGNORE = auto()


class YtVisibility(Enum):
    VISIBLE = auto()
    UNLISTED = auto()
    PRIVATE = auto()


@dataclass
class Facts:
    """Class holding facts for an event"""
    behavior: ManageStreamBehavior
    visibility: YtVisibility
    link_in_cal: bool
    on_homepage: bool

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

        # Link in Calendar
        lf_conf = config.churchtools['include_in_cal_fact']
        if lf_conf is None:
            link_in_cal = False
        else:
            link_in_cal = lf_conf['default']
            lf = facts.get(lf_conf['name'])
            if lf is not None:
                if lf == lf_conf['yes_value']:
                    link_in_cal = True
                elif lf == lf_conf['no_value']:
                    link_in_cal = False

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

        # On Homepage
        hf = facts.get(config.churchtools['show_on_homepage_fact']['name'])
        if hf is not None:
            on_homepage = hf == config.churchtools['show_on_homepage_fact']['yes_value']
        else:
            on_homepage = config.churchtools['show_on_homepage_fact']['default']

        return Facts(
            behavior=behavior,
            link_in_cal=link_in_cal,
            visibility=visibility,
            on_homepage=on_homepage
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
