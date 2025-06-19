import logging
from datetime import datetime
from typing import Optional

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

import config
from . import oauth
from .type_hints import LiveBroadcast, PrivacyStatus

log = logging.getLogger(__name__)


class YouTube:
    """
    YouTube-API main class
    """
    credentials: Credentials
    _service: googleapiclient.discovery.Resource

    def __init__(self):
        log.info('Initializing YouTube API…')
        # Obtain Credentials
        self.credentials = oauth.load_credentials()
        if self.credentials is None:
            self.credentials = oauth.authorize()

        # Create client
        self._service = googleapiclient.discovery.build('youtube', 'v3', credentials=self.credentials)
        self._live_broadcasts = self._service.liveBroadcasts()

        self.check_stream_key_configured()

        log.info('YouTube ready.')

    def check_stream_key_configured(self):
        try:
            if config.youtube['stream_key_id'] == 'STREAM_KEY_ID_HERE':
                raise ValueError
        except (KeyError, ValueError):
            result = self._service.liveStreams().list(part='snippet', mine=True, maxResults=50).execute()
            log.critical(
                'No stream key ID has been set. '
                'Please choose a stream key from the list below and add its ID to Your configuration file:\n'
                'ID:' + ' ' * 39 + 'Name:\n' +
                '\n'.join(f'{sk['id']}    "{sk['snippet']['title']}"' for sk in result['items'])
            )
            exit(1)

    def close(self):
        oauth.save_credentials(self.credentials)

    def get_active_and_upcoming_broadcasts(self) -> list[LiveBroadcast]:
        """
        Return all scheduled and active broadcasts
        """
        # Get upcoming and active broadcasts
        upcoming_response = self._live_broadcasts.list(part='id,snippet,contentDetails,status', maxResults=50,
                                                       broadcastStatus='upcoming').execute()
        active_response = self._live_broadcasts.list(part='id,snippet,contentDetails,status', maxResults=50,
                                                     broadcastStatus='active').execute()
        return upcoming_response['items'] + active_response['items']

    def get_broadcast_with_id(self, br_id: str) -> Optional[LiveBroadcast]:
        """
        Fetch a broadcast with the given id
        :param br_id: The ID of the broadcast to retrieve
        :return: The broadcast, or None, if it wasn't found
        """
        live_broadcasts = self._service.liveBroadcasts()
        result = live_broadcasts.list(id=br_id)
        try:
            return result['items'][0]
        except KeyError | IndexError:
            return None

    def create_broadcast(self, title: str, start: datetime, privacy: PrivacyStatus) -> LiveBroadcast:
        """
        Create a new `LiveBroadcast` and return it
        :return: the newly created LiveBroadcast resource
        """
        if len(title) > 100:
            raise ValueError('Title may not be longer than 100 characters')
        if '<' in title or '>' in title:
            raise ValueError('Title may not contain "<" or ">"')

        result = self._live_broadcasts.insert(part='id,snippet,contentDetails,status', body={
            'snippet': {
                'title': title,
                'scheduledStartTime': start.astimezone(tz=None).isoformat(),
            },
            'status': {
                'privacyStatus': privacy
            }
        }).execute()
        return result
