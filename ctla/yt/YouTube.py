import logging

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

from . import oauth

log = logging.getLogger(__name__)


class YouTube:
    """
    YouTube-API main class
    """
    credentials: Credentials
    service: googleapiclient.discovery.Resource

    def __init__(self):
        log.info('Initializing YouTube API…')
        # Obtain Credentials
        self.credentials = oauth.load_credentials()
        if self.credentials is None:
            self.credentials = oauth.authorize()

        # Create client
        self.service = googleapiclient.discovery.build('youtube', 'v3', credentials=self.credentials)

        log.info('YouTube ready.')

    def close(self):
        oauth.save_credentials(self.credentials)
