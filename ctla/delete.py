from ct.ChurchTools import ChurchTools
from data import Event
from yt.YouTube import YouTube


def delete_stream(ct: ChurchTools, yt: YouTube, ev: Event):
    """
    Remove every trace of a broadcast.

    Delete the Broadcast on YouTube and remove the ChurchTools event Link (also in the calendar, if set and matching)
    """
    if ev.yt_broadcast:
        yt.delete_broadcast(ev.yt_broadcast['id'])
        ev.yt_broadcast = None
    if ev.yt_link:
        ct.delete_link(ev.yt_link.id)
