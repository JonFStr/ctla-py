from dataclasses import dataclass
from enum import Enum, auto

from ..config import churchtools as ctconf


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
        bf = facts.get(ctconf['manage_stream_behavior_fact']['name'], ctconf['manage_stream_behavior_fact']['default'])
        if bf == ctconf['manage_stream_behavior_fact']['yes_value']:
            behavior = ManageStreamBehavior.YES
        elif bf == ctconf['manage_stream_behavior_fact']['ignore_value']:
            behavior = ManageStreamBehavior.IGNORE
        else:
            behavior = ManageStreamBehavior.NO

        # Link in Calendar
        lf = facts.get(ctconf['include_in_cal_fact']['name'])
        if lf is not None:
            link_in_cal = lf == ctconf['include_in_cal_fact']['yes_value']
        else:
            link_in_cal = ctconf['include_in_cal_fact']['default']

        # Visibility
        vf = facts.get(ctconf['stream_visibility_fact']['name'], ctconf['stream_visibility_fact']['default'])
        if vf == ctconf['stream_visibility_fact']['visible_value']:
            visibility = YtVisibility.VISIBLE
        elif vf == ctconf['stream_visibility_fact']['unlisted_value']:
            visibility = YtVisibility.UNLISTED
        elif vf == ctconf['stream_visibility_fact']['private_value']:
            visibility = YtVisibility.PRIVATE
        else:
            raise ValueError(
                f'Unexpected Value for YouTube-Visibility-Fact ("{ctconf['stream_visibility_fact']['name']}"): "{vf}"\n'
                f'Needs to be one of "{ctconf['stream_visibility_fact']['visible_value']}", '
                f'"{ctconf['stream_visibility_fact']['unlisted_value']}" or '
                f'"{ctconf['stream_visibility_fact']['private_value']}", according to configuration.')

        # On Homepage
        hf = facts.get(ctconf['show_on_homepage_fact']['name'])
        if hf is not None:
            on_homepage = hf == ctconf['show_on_homepage_fact']['yes_value']
        else:
            on_homepage = ctconf['show_on_homepage_fact']['default']

        return Facts(
            behavior=behavior,
            link_in_cal=link_in_cal,
            visibility=visibility,
            on_homepage=on_homepage
        )
