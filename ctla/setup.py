"""
Functions used solely to gather information
"""
import logging
from collections.abc import Generator

import config
from ct.ChurchTools import ChurchTools
from ct.Facts import ManageStreamBehavior
from data import Event
from yt.YouTube import YouTube
from yt.type_hints import LiveBroadcast

log = logging.getLogger(__name__)


def get_relevant_events(ct: ChurchTools, yt: YouTube) -> Generator[Event]:
    """
    Fetch and return all events to act upon.

    This also searches for matching YouTube broadcasts and attaches them, if found.

    :param ct: The ChurchTools API Instance
    :param yt: The YouTube service instance
    :return: A list of events
    """
    ct_events = ct.get_upcoming_events(config.churchtools['days_to_load'])
    yt_broadcasts = yt.get_active_and_upcoming_broadcasts()

    for ct_evt in ct_events:
        event = Event(**vars(ct_evt))

        if event.facts.behavior == ManageStreamBehavior.IGNORE:
            log.info(f'Skipping event {event}, as it is ignored.')
            continue

        attach_youtube_broadcast(event, yt, yt_broadcasts)

        yield event


def attach_youtube_broadcast(event: Event, yt: YouTube, broadcasts: list[LiveBroadcast]):
    """
    Try to find a matching broadcast in the given list of available broadcasts

    :param event: The event to search for
    :param yt: YouTube service instance
    :param broadcasts: Pre-fetched active and upcoming broadcasts
    :return: True, if a broadcast was found and attached
    """
    # Needs to have a
    if not event.yt_link:
        return

    # Check if a broadcast was ever attached
    vid_id = event.youtube_video_id
    if not vid_id:
        return

    # Try to find the broadcast in upcoming and active broadcasts
    for bc in broadcasts:
        if bc['id'] == vid_id:
            event.yt_broadcast = bc
            return

    # Not found, try to find it in completed broadcasts
    bc = yt.get_broadcast_with_id(vid_id)
    if bc:
        event.yt_broadcast = bc
