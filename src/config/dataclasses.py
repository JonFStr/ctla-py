from dataclasses import dataclass


@dataclass
class ManageStreamBehaviorConf:
    name: str
    yes_value: str
    ignore_value: str
    default: str


@dataclass
class StreamVisibilityConf:
    name: str
    visible_value: str
    unlisted_value: str
    private_value: str
    default: str


@dataclass
class IncludeInCalConf:
    name: str
    yes_value: str
    default: bool


@dataclass
class ShowOnHomepageConf:
    name: str
    yes_value: str
    default: bool


@dataclass
class ChurchToolsConf:
    instance: str
    token: str
    days_to_load: int

    manage_stream_behavior_fact: ManageStreamBehaviorConf
    stream_visibility_fact: StreamVisibilityConf
    include_in_cal_fact: IncludeInCalConf
    show_on_homepage_fact: ShowOnHomepageConf

    speaker_service_name: str

    thumbnail_name: str
    stream_attachment_name: str


@dataclass
class Config:
    """
    CTLA Main Configuration
    """
    churchtools: ChurchToolsConf
    youtube: None
    wordpress: None
