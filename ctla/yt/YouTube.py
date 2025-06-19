import logging
import os
import urllib.parse
import urllib.request
from datetime import datetime
from http.client import HTTPResponse
from pathlib import Path
from typing import Optional, Any

import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

import config
import utils
from . import oauth
from .type_hints import LiveBroadcast, PrivacyStatus

log = logging.getLogger(__name__)

DEFAULT_PART = 'id,snippet,contentDetails,status'  # Default value for 'part' parameter in requests


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
        upcoming_response = self._live_broadcasts.list(part=DEFAULT_PART, maxResults=50,
                                                       broadcastStatus='upcoming').execute()
        active_response = self._live_broadcasts.list(part=DEFAULT_PART, maxResults=50,
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
        # noinspection GrazieInspection
        """
                Create a new `LiveBroadcast` and return it.

                This applies the configuration from "youtube.broadcast_settings" in the config file
                :return: the newly created LiveBroadcast resource
                """
        if len(title) > 100:
            raise ValueError('Title may not be longer than 100 characters')
        if '<' in title or '>' in title:
            raise ValueError('Title may not contain "<" or ">"')

        broadcast_settings = config.youtube['broadcast_settings']

        result = self._live_broadcasts.insert(part=DEFAULT_PART, body={
            'snippet': {
                'title': title,
                'scheduledStartTime': start.astimezone(None).isoformat(),
            },
            'status': {
                'privacyStatus': privacy
            },
            'contentDetails': {
                'monitorStream': {
                    'enableMonitorStream': broadcast_settings['enable_monitor_stream'],
                    'broadcastStreamDelayMs': broadcast_settings['broadcast_stream_delay_ms']
                },
                'enableEmbed': broadcast_settings['enable_embed'],
                'enableDvr': broadcast_settings['enable_dvr'],
                'recordFromStart': broadcast_settings['record_from_start'],
                'closedCaptionsType': broadcast_settings['closed_captions_type'],
                'latencyPreference': broadcast_settings['latency_preference'],
                'enableAutoStart': broadcast_settings['enable_auto_start'],
                'enableAutoStop': broadcast_settings['enable_auto_stop'],
            }
        }).execute()
        return result

    def set_broadcast_info(self, broadcast: LiveBroadcast, title: str = None, desc: str = None, start: datetime = None,
                           end: datetime = None, privacy: PrivacyStatus = None) -> LiveBroadcast:
        """
        Update the broadcast information with the one given.
        Optional parameters may be omitted, in which case they won't be updated

        :param broadcast: The ID of the broadcast to update
        :param title: The title to set. Must be at most 100 characters long and may not contain '<' or '>'
        :param desc: The description of the broadcast. Restrictions like for title, but 5000 bytes in length
        :param start: The scheduled time
        :param end: The scheduled end time
        :param privacy: The visibility of the broadcast
        :return: The updated LiveBroadcast resource. This property will have been merged with the passed `broadcast`,
            since not all parts are updated in this request
            (at least all 'contentDetails' settings always remain untouched)
        """
        parts_to_update = {'id'}
        body: dict[str, Any] = {'id': broadcast['id']}
        # Insert defined parameters into `body`
        if title or desc or start or end:
            parts_to_update.add('snippet')
            body['snippet'] = {
                'title': title if title else broadcast['snippet']['title'],
                'description': desc if desc else broadcast['snippet']['description'],
                'scheduledStartTime': start.astimezone(None).isoformat() if start else broadcast['snippet'][
                    'scheduledStartTime'],
                'scheduledEndTime': end.astimezone(None).isoformat() if end else broadcast['snippet'][
                    'scheduledEndTime']
            }

        if privacy:
            parts_to_update.add('status')
            body['status'] = {'privacyStatus': privacy}

        result = self._live_broadcasts.update(part=','.join(parts_to_update), body=body).execute()
        utils.combine_into(result, broadcast)
        return broadcast

    def bind_stream_to_broadcast(self, br_id: str, stream_id: Optional[str] = None) -> LiveBroadcast:
        """
        Bind a stream to the broadcast

        :param br_id: The ID (YouTube Video ID) of the broadcast to update
        :param stream_id: The ID of the stream to attach to the broadcast
        :return: The updated LiveBroadcast resource
        """
        if not stream_id:
            stream_id = config.youtube['stream_key_id']
        result = self._live_broadcasts.bind(id=br_id, part=DEFAULT_PART, streamId=stream_id).execute()
        return result

    def set_thumbnails(self, broadcast: LiveBroadcast, thumbnail_uri: str) -> LiveBroadcast:
        """
        Set the thumbnail of a broadcast
        :param broadcast: The broadcast to update
        :param thumbnail_uri: The URI to the thumbnail.
            If the scheme is 'file://' or unset, load the file at the specified path, otherwise treat as http URL
        :return: The updated LiveBroadcast resource
        """
        parsed_uri = urllib.parse.urlparse(thumbnail_uri)
        if parsed_uri.scheme == '' and Path(thumbnail_uri).exists():
            media_upload = MediaFileUpload(thumbnail_uri)
        elif parsed_uri.scheme == 'file':
            media_upload = MediaFileUpload(urllib.parse.unquote_plus(os.path.join(parsed_uri.netloc + parsed_uri.path)))
        else:
            response: HTTPResponse = urllib.request.urlopen(thumbnail_uri)
            media_upload = MediaIoBaseUpload(response, response.headers.get_content_type())

        result = self._service.thumbnails().set(videoId=broadcast['id'], media_body=media_upload).execute()
        broadcast['snippet']['thumbnails'] = result['items'][0]
        return broadcast
