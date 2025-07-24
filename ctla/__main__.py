import atexit
import logging
import pprint
import time

import requests

import config
import delete
import setup
import update
from configs import args
from ct.ChurchTools import ChurchTools
from wp.WordPress import WordPress
from yt.YouTube import YouTube

start_time = time.time()


def elapsed_ms() -> int:
    """Program runtime, in ms"""
    return int((time.time() - start_time) * 1000)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

args.parse()
config.load()

ct = ChurchTools()
yt = YouTube()

events = list(setup.gather_event_info(ct, yt))

clean_exit = False
"""failure occurred during run"""


@atexit.register
def notify_exit():
    """Notify external monitor in case of unclean exit"""
    if not clean_exit and config.monitor_url:
        requests.get(config.monitor_url.format(status='down', msg='Something went wrong.', ping=elapsed_ms()))


log.debug(pprint.pformat(events))

for event in events:
    if event.wants_stream:
        if not event.yt_broadcast:
            if event.yt_link:
                # Link is present, but Stream isn't: Delete the old link
                ct.delete_link(event.yt_link.id)
            update.create_youtube(ct, yt, event)

        update.update_youtube(yt, event)

        if event.facts.create_post:
            if not event.post_link:
                update.create_post(ct, event)
            else:
                update.update_post(ct, event)
        else:
            delete.delete_post(ct, event)

    else:
        delete.delete_stream(ct, yt, event)
        delete.delete_post(ct, event)

# WordPress
if config.wordpress['enabled']:
    wp = WordPress()
    update.update_wordpress(wp, [ev for ev in events if ev.yt_link and ev.facts.on_homepage])

if config.monitor_url:
    requests.get(config.monitor_url.format(status='up', msg='OK', ping=elapsed_ms()))

clean_exit = True
