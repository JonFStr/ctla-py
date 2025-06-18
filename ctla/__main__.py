import logging
import pprint

import config
import delete
import setup
import update
from config import args
from ct.ChurchTools import ChurchTools
from yt.YouTube import YouTube

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

args.parse()
config.load()

ct = ChurchTools()
yt = YouTube()
