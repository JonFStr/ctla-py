import logging
import pprint

import configs
from configs import args
from ct import ChurchTools
from yt.YouTube import YouTube

args.parse()
configs.load()

logging.basicConfig(level=logging.DEBUG)
