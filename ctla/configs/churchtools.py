from typing import TypedDict, Optional


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


class IncludeInCalConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for including the stream link inside the calendar entry
    """

    name: str
    """Name of the Fact"""
    yes_value: str
    """Value equaling to 'yes' / True (do include in calendar)"""
    no_value: str
    """Value equaling to 'no' / False (don't include in calendar)"""
    default: bool
    """Default behavior"""


class ShowOnHomepageConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for showing the stream on the WordPress site
    """

    name: str
    """Name of the Fact"""
    yes_value: str
    """Value equaling to 'yes' / True (do show on homepage)"""
    no_value: str
    """Value equaling to 'no' / False (don't show on homepage)"""
    default: bool
    """Default behavior"""


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
    include_in_cal_fact: Optional[IncludeInCalConf]
    show_on_homepage_fact: Optional[ShowOnHomepageConf]

    speaker_service_name: Optional[str]
    """Title of the ChurchTools service name containing the speaker's name"""
    thumbnail_name: Optional[str]
    """Name of the service attachment containing the streams Thumbnail"""
    stream_attachment_name: str
    """Name of the service attachment pointing to the YouTube stream"""
