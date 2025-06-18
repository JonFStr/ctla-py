from typing import TypedDict


class ManageStreamBehaviorConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for Stream Behavior

    Attributes:

    - *name*: Name of the Fact
    - *yes_value*: Value equaling to "yes" (create a stream)
    - *ignore_value*: Value equaling to "ignore" (don't touch this event)
    - *default*: Default value to use when any other value is set
    """
    name: str
    yes_value: str
    ignore_value: str
    default: str


class StreamVisibilityConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for Stream Visibility

    Attributes:

    - *name*: Name of the Fact
    - *visible_value*: Value for a public YouTube Stream
    - *unlisted_value*: Value for an unlisted YouTube Stream
    - *private_value*: Value for a private YouTube Stream
    - *default*: Default value to use when any other value is set
    """
    name: str
    visible_value: str
    unlisted_value: str
    private_value: str
    default: str


class IncludeInCalConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for including the stream link inside the calendar entry

    Attributes:

    - *name*: Name of the Fact
    - *yes_value*: Value equaling to 'yes' / True (do include in calendar)
    - *default*: Default behavior
    """
    name: str
    yes_value: str
    default: bool


class ShowOnHomepageConf(TypedDict):
    """
    Dataclass configuring the ChurchTools fact for showing the stream on the WordPress site

    Attributes:

    - *name*: Name of the Fact
    - *yes_value*: Value equaling to 'yes' / True (do include in calendar)
    - *default*: Default behavior
    """
    name: str
    yes_value: str
    default: bool


class ChurchToolsConf(TypedDict):
    """
    Dataclass holding configuration about ChurchTools

    Attributes:

    - *instance*: URL to your ChurchTools instance
    - *token*: API Token string
    - *days_to_load*: How many days to load in advance

    - *speaker_service_name*: Title of the ChurchTools service name containing the speaker's name
    - *thumbnail_name*: Name of the service attachment containing the streams Thumbnail
    - *stream_attachment_name*: Name of the service attachment pointing to the YouTube stream

    The other attributes are described in the documentation of the respective classes
    """
    instance: str
    token: str
    days_to_load: int

    manage_stream_behavior_fact: ManageStreamBehaviorConf
    stream_visibility_fact: StreamVisibilityConf
    include_in_cal_fact: IncludeInCalConf | None
    show_on_homepage_fact: ShowOnHomepageConf | None

    speaker_service_name: str | None

    thumbnail_name: str | None
    stream_attachment_name: str
