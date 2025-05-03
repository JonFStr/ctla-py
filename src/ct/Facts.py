from dataclasses import dataclass
from enum import Enum, auto

from .. import config


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
        bf = facts.get(config.churchtools['manage_stream_behavior_fact']['name'],
                       config.churchtools['manage_stream_behavior_fact']['default'])
        if bf == config.churchtools['manage_stream_behavior_fact']['yes_value']:
            behavior = ManageStreamBehavior.YES
        elif bf == config.churchtools['manage_stream_behavior_fact']['ignore_value']:
            behavior = ManageStreamBehavior.IGNORE
        else:
            behavior = ManageStreamBehavior.NO

        # Link in Calendar
        lf = facts.get(config.churchtools['include_in_cal_fact']['name'])
        if lf is not None:
            link_in_cal = lf == config.churchtools['include_in_cal_fact']['yes_value']
        else:
            link_in_cal = config.churchtools['include_in_cal_fact']['default']

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
                f'Unexpected Value for YouTube-Visibility-Fact ("{config.churchtools['stream_visibility_fact']['name']}"): "{vf}"\n'
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
