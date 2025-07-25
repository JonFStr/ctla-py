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


def delete_post(ct: ChurchTools, ev: Event) -> bool:
    """
    Delete the event's post from ChurchTools

    :param ct: ChurchTools API instance
    :param ev: Event whose post shall be deleted
    :return: True if a deletion was executed
    """
    if ev.post_link:
        ct.delete_post(ev.post_id)
        ct.delete_link(ev.post_link.id)
        return True
    return False
