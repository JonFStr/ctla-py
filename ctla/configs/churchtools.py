from typing import TypedDict, Optional, Literal


class ManageStreamBehaviorConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for Stream Behavior
    """

    name: str
    """Name of the Fact"""
    yes_value: str
    """Value equaling to "yes" (create a stream)"""
    ignore_value: str
    """Value equaling to "ignore" (don't touch this event)"""
    no_value: str
    """Value equaling to "no" (don't create a stream, and delete existing streams)"""
    default: str
    """Default value to use when any other value is set"""


class StreamVisibilityConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for Stream Visibility
    """

    name: str
    """Name of the Fact"""
    visible_value: str
    """Value for a public YouTube Stream"""
    unlisted_value: str
    """Value for an unlisted YouTube Stream"""
    private_value: str
    """Value for a private YouTube Stream"""
    default: str
    """Default value to use when any other value is set"""


class BooleanFactConf(TypedDict):
    """
    Dataclass a ChurchTools fact that will be parsed to a boolean value
    """

    name: str
    """Name of the Fact"""
    yes_value: str
    """Value equaling to 'yes' / True"""
    no_value: str
    """Value equaling to 'no' / False"""
    default: bool
    """Default behavior"""


type PostVisibility = Literal['group_visible', 'group_intern']
"""Visibility values for posts"""


class PostSettingsConf(TypedDict):
    """
    Dataclass holding configuration for the creation of posts
    """

    group_id: int
    """ID of the ChurchTools group to post in"""
    attachment_name: str
    """Name of the Event attachment that will link to the created post"""
    post_visibility: PostVisibility
    """Visibility of the created post"""
    comments_active: bool
    """Whether to enable comments"""


class ChurchToolsTemplateConf(TypedDict):
    """
    Dataclass for templates regarding ChurchTools data
    """
    dateformat: str
    """String understood by ``datetime.strftime``` to format dates"""


class ChurchToolsConf(TypedDict):
    """
    Dataclass holding configuration about ChurchTools
    """

    instance: str
    """URL to your ChurchTools instance"""
    token: str
    """API Token string"""
    days_to_load: int
    """How many days to load in advance"""

    manage_stream_behavior_fact: ManageStreamBehaviorConf
    stream_visibility_fact: StreamVisibilityConf
    include_in_cal_fact: Optional[BooleanFactConf]
    show_on_homepage_fact: Optional[BooleanFactConf]
    create_post_fact: Optional[BooleanFactConf]

    post_settings: Optional[PostSettingsConf]

    speaker_service_name: Optional[str]
    """Title of the ChurchTools service name containing the speaker's name"""
    thumbnail_name: Optional[str]
    """Name of the service attachment containing the streams Thumbnail"""
    stream_attachment_name: str
    """Name of the service attachment pointing to the YouTube stream"""

    templates: ChurchToolsTemplateConf
    """Template configurations"""
