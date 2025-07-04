"""
Update functions: create & update events, broadcasts, stuff
"""
import datetime
import logging

import config
from ct.ChurchTools import ChurchTools
from data import Event
from yt.YouTube import YouTube
from yt.type_hints import LiveBroadcast

log = logging.getLogger(__name__)


def create_youtube(ct: ChurchTools, yt: YouTube, event: Event):
    """
    Create a YouTube broadcast for the given event and bind the stream id;
    then attach it and upload the link to ChurchTools.

    This still requires `update_youtube()` to be called in order to set all attributes correctly

    :param ct: ChurchTools API instance
    :param yt: YouTube service instance
    :param event: The event wanting a broadcast
    """
    bc: LiveBroadcast = yt.create_broadcast(event.title, event.start_time, event.yt_visibility)
    bc = yt.bind_stream_to_broadcast(bc['id'], config.youtube['stream_key_id'])
    event.yt_broadcast = bc
    ct.set_stream_link(event, f'https://youtu.be/{bc['id']}')


def update_youtube(yt: YouTube, ev: Event):
    """
    Update the information on YouTube to reflect the one given in ChurchTools.

    Only updates when necessary.

    :param yt: YouTube service instance
    :param ev: The event to update information for
    """
    if not ev.yt_broadcast:
        return
    bc = ev.yt_broadcast
    bc_snippet = bc.get('snippet', {})
    data = dict()

    yt_title = ev.yt_title
    if yt_title != bc_snippet.get('title'):
        data['title'] = yt_title

    yt_desc = ev.yt_description
    if yt_desc != bc_snippet.get('title'):
        data['desc'] = yt_desc

    start_str = bc_snippet.get('scheduledStartTime')
    if not start_str or ev.start_time != datetime.datetime.fromisoformat(start_str):
        data['start'] = ev.start_time

    end_str = bc_snippet.get('scheduledEndTime')
    if not end_str or ev.end_time != datetime.datetime.fromisoformat(end_str):
        data['end'] = ev.end_time

    if ev.yt_visibility != bc['status']['privacyStatus']:
        data['privacy'] = ev.yt_visibility

    bc = yt.set_broadcast_info(bc, **data)
    bc = yt.set_thumbnails(bc, ev.yt_thumbnail.url if ev.yt_thumbnail else config.youtube['thumbnail_uri'])
    ev.yt_broadcast = bc
