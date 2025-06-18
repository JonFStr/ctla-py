import logging

from . import args, config
from .ct import ChurchTools
from .yt.YouTube import YouTube

args.parse()
config.load()

logging.basicConfig(level=logging.DEBUG)
