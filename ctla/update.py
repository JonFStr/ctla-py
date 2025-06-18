"""
Update functions: create & update events, broadcasts, stuff
"""

import logging

from ct.ChurchTools import ChurchTools
from data import Event
from yt.YouTube import YouTube
from yt.type_hints import LiveBroadcast

log = logging.getLogger(__name__)


def create_youtube(ct: ChurchTools, yt: YouTube, event: Event):
    """
    Create a YouTube broadcast for the given event, attach it and upload the link to ChurchTools.

    This still requires `update_youtube()` to be called in order to set all attributes correctly

    :param ct: ChurchTools API instance
    :param yt: YouTube service instance
    :param event: The event wanting a broadcast
    """
    bc: LiveBroadcast = yt.create_broadcast(event.title, event.start_time, event.yt_visibility)
    event.yt_broadcast = bc
    ct.set_stream_link(event, f'https://youtu.be/{bc['id']}')
