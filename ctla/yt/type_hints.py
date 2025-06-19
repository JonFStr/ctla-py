"""
This file holds helper classes for type hints
"""
from typing import TypedDict, Literal

PrivacyStatus = Literal['private', 'public', 'unlisted']


class BroadcastSnippet(TypedDict):
    """
    YouTube Broadcast basic details
    """
    publishedAt: str
    title: str
    description: str
    scheduledStartTime: str
    scheduledEndTime: str
    thumbnails: dict


class BroadcastStatus(TypedDict):
    """
    YouTube Broadcast status information
    """
    lifeCycleStatus: str
    privacyStatus: str


class BroadcastDetails(TypedDict):
    """
    YouTube Broadcast details
    """


class LiveBroadcast(TypedDict):
    """
    A YouTube Broadcast resource

    For brevity, this contains only fields used in this application
    """
    id: str
    snippet: BroadcastSnippet
    status: BroadcastStatus
    contentDetails: BroadcastDetails
