import logging

import config
from config import args
from ct.ChurchTools import ChurchTools
from ct.Event import Event
from ct.Facts import ManageStreamBehavior
from yt.YouTube import YouTube
from yt.type_hints import LiveBroadcast

logging.basicConfig(level=logging.DEBUG)

args.parse()
configs.load()

ct = ChurchTools.create()
yt = YouTube()
