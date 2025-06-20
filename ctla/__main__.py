import logging
import pprint

import config
import delete
import setup
import update
from configs import args
from ct.ChurchTools import ChurchTools
from yt.YouTube import YouTube

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

args.parse()
config.load()

ct = ChurchTools()
yt = YouTube()

events = setup.gather_event_info(ct, yt)
events = (ev for ev in events if ev.category_id == 30)
pprint.pprint(list(events))

for event in events:
    if event.wants_stream:
        if not event.yt_broadcast:
            update.create_youtube(ct, yt, event)

        update.update_youtube(yt, event)  # TODO
