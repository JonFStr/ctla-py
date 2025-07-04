import datetime
import logging
import urllib.parse
from collections.abc import Generator
from datetime import timedelta
from typing import Any

import config
from RestAPI import RestAPI
from .CtEvent import CtEvent
from .EventFile import EventFile, EventFileType

log = logging.getLogger(__name__)


class ChurchTools(RestAPI):
    """
    The ChurchTools-API main class.
    """

    urlbase: str
    token: str
    _facts_cache: dict[int, str] = None

    def __init__(self, instance: str = None, token: str = None):
        """
        Construct a new ChurchTools-Api instance.

        :param instance: The hostname of the instance
        :param token: The API Token of the user
        """
        try:
            if not instance:
                instance = config.churchtools['instance']
            if not token:
                token = config.churchtools['token']

            if instance == 'churchtools.test' or token == 'API_TOKEN_HERE':
                raise ValueError
        except (KeyError, ValueError):
            log.critical('Please configure Your ChurchTools instance and API token in the config'
                         'or via environment variables')
            exit(1)

        self.urlbase = urllib.parse.urlunsplit(('https', instance, '/api', '', ''))
        self._headers = {'Authorization': f'Login {token}'}

        log.info('Initialized ChurchTools API.')

    def cache_facts(self):
        """Cache the fact masterdata in this instance. Do nothing if cache exists"""
        if self._facts_cache is not None:
            return
        log.info('Caching fact masterdata…')
        r = self._do_get('/facts')
        if r.status_code != 200:
            log.error(f'Response error when fetching fact masterdata [{r.status_code}]: "{r.content}"')

        self._facts_cache = {fact['id']: fact['name'] for fact in r.json()['data']}

    def get_event_facts(self, event_id: int) -> dict[str, int | str] | None:
        """Get the facts for the event with id `event_id`, as dict"""
        self.cache_facts()

        log.info('Collecting event facts…')
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

        log.info('Retrieving upcoming event data…')
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
        r = self._do_post(f'/files/service/{event.id}/link', {
            'name': config.churchtools['stream_attachment_name'],
            'url': link
        })

        log.info(f'Attaching stream link {link} to "{event.title}" ({event.id})')
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
        log.info(f'Deleting stream link from "{event.title}" ({event.id})')
        r = self._do_delete(f'/files/{event.yt_link.id}')
        if r.status_code != 204:
            log.error(f'Error when deleting stream link on ChurchTools [{r.status_code}]: "{r.content}"')
            return False
        return True

    def get_calendar_entry(self, event: CtEvent) -> dict[str, Any]:
        """
        Get the calendar entry (appointment) corresponding to the given event
        :param event: The event to get the appointment for
        :return: The appointment
        """
        log.info(f'Fetching calendar entry ({event.appointment_id}) for "{event.title}" ({event.id})')
        r = self._do_get(f'/calendars/{event.category_id}/appointments/{event.appointment_id}')
        if r.status_code != 200:
            log.error(f'Error retrieving appointment for Event "{event.title}" '
                      f'(#{event.id}, appointmentId: {event.appointment_id}')
            r.raise_for_status()
        return r.json()['data']

    def update_calendar_link(self, event: CtEvent, link: str):
        """
        Update the calendar entry with the new link.

        This function does not ensure that the modified appointment is not repeating

        :param event: The event whose calendar event should be updated
        :param link: The link to be set
        :return:
        """
        raise NotImplementedError
        appointment = self.get_calendar_entry(event)
        appointment['link'] = link
