import datetime
import logging
import urllib.parse
from collections.abc import Generator
from datetime import timedelta
from typing import Any

import requests

import config
from .CtEvent import CtEvent
from .EventFile import EventFile, EventFileType

log = logging.getLogger(__name__)


class ChurchTools:
    """
    The ChurchTools-API main class.
    """

    urlbase: str
    token: str
    _facts_cache: dict[int, str] = None

    @classmethod
    def create(cls):
        """Helper method to create object with default configuration parameters"""
        return cls(config.churchtools['instance'], config.churchtools['token'])

    def __init__(self, instance: str, token: str):
        """
        Construct a new ChurchTools-Api instance.

        :param instance: The hostname of the instance
        :param token: The API Token of the user
        """
        self.urlbase = urllib.parse.urlunsplit(('https', instance, '/api', '', ''))
        self.token = token

        log.info('Initialized ChurchTools API.')

    @property
    def __headers(self):
        return {'Authorization': f'Login {self.token}'}

    def _do_get(self, path: str, **kwargs) -> requests.Response:
        """
        Perform GET request to ChurchTools

        :param path: The API endpoint
        :param kwargs: Query parameters
        :return: The `requests`-library's Response-object.
        """
        url = self.urlbase + path
        log.debug(f'Perform GET request to {url} (parameters: {kwargs})')
        return requests.get(url, params=kwargs, headers=self.__headers)

    def _do_post(self, path: str, json: dict[str, Any]):
        """
        Perform POST request to ChurchTools

        :param path: The API endpoint
        :param json: JSON encodable request body
        :return: The `requests`-library's Response-object.
        """
        url = self.urlbase + path
        log.debug(f'Perform POST request to {url} (data: {json})')
        return requests.post(url, json=json, headers=self.__headers)

    def _do_delete(self, path: str):
        """
        Perform DELETE request to ChurchTools

        :param path: The API endpoint
        :return: The `requests`-library's Response-object.
        """
        url = self.urlbase + path
        log.debug(f'Perform DELETE request to {url}')
        return requests.delete(url, headers=self.__headers)

    def cache_facts(self):
        """Cache the fact masterdata in this instance. Do nothing if cache exists"""
        if self._facts_cache is not None:
            return
        r = self._do_get('/facts')
        if r.status_code != 200:
            log.error(f'Response error when fetching fact masterdata [{r.status_code}]: "{r.content}"')

        self._facts_cache = {fact['id']: fact['name'] for fact in r.json()['data']}

    def get_event_facts(self, event_id: int) -> dict[str, int | str] | None:
        """Get the facts for the event with id `event_id`, as dict"""
        self.cache_facts()

        r = self._do_get(f'/events/{event_id}/facts')
        if r.status_code != 200:
            log.error(f'Response error when fetching facts for {event_id} [{r.status_code}]: "{r.content}"')
            return None

        return {self._facts_cache[fact['factId']]: fact['value'] for fact in r.json()['data']}

    def get_upcoming_events(self, days: int) -> Generator[CtEvent]:
        """
        Load and return events from ChurchTools
        :param days: How many days to load in advance (including the current day)
        :return: A generator creating the events
        :raise HttpError (directly passed down from the requests module) if an error occurred
        """
        # Compute date instance for filter end date
        from_limit = datetime.date.today().isoformat()
        to_limit = (datetime.date.today() + timedelta(days=days)).isoformat()

        r = self._do_get('/events', canceled=True, **{'from': from_limit}, to=to_limit)
        if r.status_code != 200:
            log.error(f'Response error when fetching upcoming events [{r.status_code}]: "{r.content}"')
            r.raise_for_status()

        for event in r.json()['data']:
            facts = self.get_event_facts(event['id'])
            # noinspection PyTypeChecker
            yield CtEvent.from_api_json(event, facts)

    def set_stream_link(self, event: CtEvent, link: str) -> bool:
        """
        Set the YT-Stream Link for an event to the given link
        :param event: The ChurchTools Event to set the link for
        :param link: The link to be set
        :return True, if successful
        """
        r = self._do_post(f'/files/service/{event.id}/link', {'name': 'YouTube-Stream', 'url': link})

        if r.status_code != 201:
            log.error(f'Error when setting stream link on ChurchTools [{r.status_code}]: "{r.content}"')
            return False

        # Write new link into Event object
        response_data = r.json()['data']
        event.yt_link = EventFile(
            id=response_data['domainId'],
            type=EventFileType.LINK,
            name=response_data['name'],
            url=response_data['fileUrl']
        )
        return True

    def delete_stream_link(self, event: CtEvent) -> bool:
        """
        Delete the Stream Link from an event
        :param event: The event to delete the stream link from
        :return: True on success
        """
        r = self._do_delete(f'/files/{event.yt_link.id}')
        if r.status_code != 204:
            log.error(f'Error when deleting stream link on ChurchTools [{r.status_code}]: "{r.content}"')
            return False
        return True
