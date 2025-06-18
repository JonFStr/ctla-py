import logging

import configs
from configs import args
from ct import ChurchTools
from yt import YouTube

logging.basicConfig(level=logging.DEBUG)

args.parse()
configs.load()

ct = ChurchTools.create()
yt = YouTube()
