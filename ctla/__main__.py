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
from data import RuntimeStats
from wp.WordPress import WordPress
from yt.YouTube import YouTube

start_time = time.time()
stats = RuntimeStats()


def elapsed_ms() -> int:
    """
    Program runtime, in ms

    Used for reporting to uptime monitor
    """
    return int((time.time() - start_time) * 1000)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

args.parse()
config.load()

clean_exit = False
"""Check if a failure occurred"""


@atexit.register
def notify_exit():
    """Notify external monitor in case of unclean exit"""
    if not clean_exit and config.monitor_url:
        msg = ''
        if 'event' in globals() and event is not None:
            msg = f' during handling of event "{event.title}" ({event.id})'
        if 'wp' in globals() and wp is not None:
            msg = f' during update of WordPress'
        requests.get(config.monitor_url.format(status='down', msg=f'Something went wrong{msg}.', ping=elapsed_ms()))


ct = ChurchTools()
yt = YouTube()

if args.parsed.show_stream_keys:
    print("These YouTube-Stream keys are available:\n" + yt.format_stream_keys())
    clean_exit = True
    exit(1)

events = list(setup.gather_event_info(ct, yt, stats))
stats.total = len(events)

log.debug(pprint.pformat(events))

for event in events:
    if event.wants_stream:
        change = False

        if not event.yt_broadcast:
            if event.yt_link:
                # Link is present, but Stream isn't: Delete the old link
                ct.delete_link(event.yt_link.id)

            update.create_youtube(ct, yt, event)
            stats.new += 1

        change |= update.update_youtube(yt, event)

        if event.facts.create_post:
            if not event.post_link:
                update.create_post(ct, event)
                change |= True
            else:
                change |= update.update_post(ct, event)
        else:
            change |= delete.delete_post(ct, event)

        if change:
            stats.updated += 1

    else:
        if not event.yt_broadcast or event.yt_broadcast['status']['lifeCycleStatus'] in {'created', 'ready'}:
            # Only delete Broadcast if it hasn't happened yet
            delete.delete_stream(ct, yt, event)
            stats.deleted += 1
        delete.delete_post(ct, event)

# WordPress
if config.wordpress['enabled']:
    wp = WordPress()
    update.update_wordpress(wp, [ev for ev in events if ev.yt_link and ev.facts.on_homepage])

if config.monitor_url:
    requests.get(config.monitor_url.format(
        status='up',
        msg='OK: '
            f'change:{stats.updated} (new:{stats.new}),del:{stats.deleted} | '
            f'total:{stats.total} (skip:{stats.skipped})',
        ping=elapsed_ms()
    ))

clean_exit = True
