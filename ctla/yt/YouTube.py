import logging
from typing import Optional

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

from . import oauth
from .type_hints import LiveBroadcast

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

    def get_active_and_upcoming_broadcasts(self) -> list[LiveBroadcast]:
        """
        Return all scheduled and active broadcasts
        """
        live_broadcasts = self.service.liveBroadcasts()
        # Get upcoming and active broadcasts
        upcoming_response = live_broadcasts.list(part='id,snippet,contentDetails,status', maxResults=50,
                                                 broadcastStatus='upcoming').execute()
        active_response = live_broadcasts.list(part='id,snippet,contentDetails,status', maxResults=50,
                                               broadcastStatus='active').execute()
        return upcoming_response['items'] + active_response['items']

    def get_broadcast_with_id(self, br_id: str) -> Optional[LiveBroadcast]:
        """
        Fetch a broadcast with the given id
        :param br_id: The ID of the broadcast to retrieve
        :return: The broadcast, or None, if it wasn't found
        """
        live_broadcasts = self.service.liveBroadcasts()
        result = live_broadcasts.list(id=br_id)
        try:
            return result['items'][0]
        except KeyError | IndexError:
            return None
