from dataclasses import dataclass
from enum import Enum, auto

from .. import configs


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
        bf = facts.get(configs.churchtools['manage_stream_behavior_fact']['name'],
                       configs.churchtools['manage_stream_behavior_fact']['default'])
        if bf == configs.churchtools['manage_stream_behavior_fact']['yes_value']:
            behavior = ManageStreamBehavior.YES
        elif bf == configs.churchtools['manage_stream_behavior_fact']['ignore_value']:
            behavior = ManageStreamBehavior.IGNORE
        else:
            behavior = ManageStreamBehavior.NO

        # Link in Calendar
        lf = facts.get(configs.churchtools['include_in_cal_fact']['name'])
        if lf is not None:
            link_in_cal = lf == configs.churchtools['include_in_cal_fact']['yes_value']
        else:
            link_in_cal = configs.churchtools['include_in_cal_fact']['default']

        # Visibility
        vf = facts.get(configs.churchtools['stream_visibility_fact']['name'],
                       configs.churchtools['stream_visibility_fact']['default'])
        if vf == configs.churchtools['stream_visibility_fact']['visible_value']:
            visibility = YtVisibility.VISIBLE
        elif vf == configs.churchtools['stream_visibility_fact']['unlisted_value']:
            visibility = YtVisibility.UNLISTED
        elif vf == configs.churchtools['stream_visibility_fact']['private_value']:
            visibility = YtVisibility.PRIVATE
        else:
            raise ValueError(
                f'Unexpected Value for YouTube-Visibility-Fact '
                f'("{configs.churchtools['stream_visibility_fact']['name']}"): "{vf}"\n'
                f'Needs to be one of "{configs.churchtools['stream_visibility_fact']['visible_value']}", '
                f'"{configs.churchtools['stream_visibility_fact']['unlisted_value']}" or '
                f'"{configs.churchtools['stream_visibility_fact']['private_value']}", according to configuration.')

        # On Homepage
        hf = facts.get(configs.churchtools['show_on_homepage_fact']['name'])
        if hf is not None:
            on_homepage = hf == configs.churchtools['show_on_homepage_fact']['yes_value']
        else:
            on_homepage = configs.churchtools['show_on_homepage_fact']['default']

        return Facts(
            behavior=behavior,
            link_in_cal=link_in_cal,
            visibility=visibility,
            on_homepage=on_homepage
        )
