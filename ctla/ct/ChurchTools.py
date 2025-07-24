import datetime
import logging
import urllib.parse
from collections.abc import Generator
from datetime import timedelta
from typing import Any, Optional

import config
from RestAPI import RestAPI
from configs.churchtools import PostVisibility
from .CtEvent import CtEvent
from .EventFile import EventFile, EventFileType

log = logging.getLogger(__name__)


class ChurchTools(RestAPI):
    """
    The ChurchTools-API main class.
    """

    token: str
    _facts_cache: dict[int, str] = None
    _services_cache: dict[str, int] = None

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

    @property
    def fact_mdata(self) -> dict[int, str]:
        """ChurchTools Facts masterdata (id : name). Will be fetched and cached on first access."""
        if self._facts_cache is None:
            log.info('Caching fact masterdata…')
            r = self._do_get('/facts')
            if r.status_code != 200:
                log.error(f'Response error when fetching fact masterdata [{r.status_code}]: "{r.content}"')
                r.raise_for_status()

            self._facts_cache = {fact['id']: fact['name'] for fact in r.json()['data']}
        return self._facts_cache

    @property
    def service_mdata(self) -> dict[str, int]:
        """ChurchTools events service masterdata (name : id). Will be fetched and cached on first access."""
        if self._services_cache is None:
            log.info('Caching service masterdata…')
            r = self._do_get('/services')
            if r.status_code != 200:
                log.error(f'Response error when fetching service masterdata [{r.status_code}]: "{r.content}"')
                r.raise_for_status()

            self._services_cache = {service['name']: service['id'] for service in r.json()['data']}
        return self._services_cache

    def get_event_facts(self, event_id: int) -> dict[str, int | str]:
        """Get the facts for the event with id `event_id`, as dict"""
        log.info('Collecting event facts…')
        r = self._do_get(f'/events/{event_id}/facts')
        if r.status_code != 200:
            log.error(f'Response error when fetching facts for {event_id} [{r.status_code}]: "{r.content}"')
            r.raise_for_status()

        return {self.fact_mdata[fact['factId']]: fact['value'] for fact in r.json()['data']}

    def get_upcoming_events(self, days: int) -> Generator[CtEvent]:
        """
        Load and return events from ChurchTools
        :param days: How many days to load in advance (including the current day)
        :return: A generator creating the events
        :raise HttpError (directly passed down from the requests module) if an error occurred
        """
        # Compute date instance for filter end date
        from_limit = (datetime.date.today() - timedelta(days=1)).isoformat()
        to_limit = (datetime.date.today() + timedelta(days=days)).isoformat()

        log.info('Retrieving upcoming event data…')
        r = self._do_get('/events', canceled=True, **{'from': from_limit}, to=to_limit, include='eventServices')
        if r.status_code != 200:
            log.error(f'Response error when fetching upcoming events [{r.status_code}]: "{r.content}"')
            r.raise_for_status()

        for event in r.json()['data']:
            facts = self.get_event_facts(event['id'])
            # noinspection PyTypeChecker
            yield CtEvent.from_api_json(event, facts, self.service_mdata)

    def attach_link(self, event: CtEvent, name: str, link: str) -> Optional[EventFile]:
        """
        Attach a link to an event

        :param event: The ChurchTools Event to set the link for
        :param name: Name of the new attachment
        :param link: The link to be set
        :return: The created Link
        """
        r = self._do_post(f'/files/service/{event.id}/link', {
            'name': name,
            'url': link
        })

        log.info(f'Attaching link "name" ({link}) to "{event.title}" ({event.id})')
        if r.status_code != 201:
            log.error(f'Error when setting stream link on ChurchTools [{r.status_code}]: "{r.content}"')
            r.raise_for_status()

        # Write new link into Event object
        response_data = r.json()['data']
        return EventFile(
            id=response_data['domainId'],
            type=EventFileType.LINK,
            name=response_data['name'],
            url=response_data['fileUrl']
        )

    def delete_link(self, link_id: int):
        """
        Delete the Stream Link from an event

        :param link_id: The link to remove from the event
        """
        log.info(f'Deleting event link {link_id}')
        r = self._do_delete(f'/files/{link_id}')
        if r.status_code != 204:
            log.error(f'Error when deleting event link on ChurchTools [{r.status_code}]: "{r.content}"')
            r.raise_for_status()

    def create_post(
            self,
            group_id: int,
            title: str,
            content: str,
            date: datetime.datetime,
            visibility: PostVisibility,
            comments_active: bool
    ) -> int:
        """
        Create a post with the given details

        :param group_id: Group to post in
        :param title: Title
        :param content: Content
        :param date: Date of publication
        :param visibility: Post visibility
        :param comments_active: Whether to allow comments
        :return: The id of the newly created post
        """
        log.info(f'Creating post "{title}"')
        r = self._do_post('/posts', {
            'groupId': group_id,
            'title': title,
            'content': content,
            'publicationDate': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'visibility': visibility,
            'commentsActive': comments_active
        })
        if r.status_code != 201:
            log.error(f'Error creating post on ChurchTools [{r.status_code} - {r.reason}]: "{r.content}"')
            r.raise_for_status()
        post_id = int(r.json()['data']['id'])
        log.debug(f'Created post with id {post_id}')
        return post_id

    def get_post(self, post_id: int) -> dict:
        """
        Fetch a post from ChurchTools

        :param post_id: ID of the post to get
        :return: The post data
        """
        log.info(f'Fetching post {post_id}')
        r = self._do_get(f'/posts/{post_id}')
        if r.status_code != 200:
            log.error(f'Could not fetch post {post_id}: [{r.status_code} - {r.reason}] "{r.content}"')
            r.raise_for_status()
        return r.json()['data']

    def update_post(
            self,
            post_id: int,
            title: Optional[str],
            content: Optional[str],
            date: Optional[datetime.datetime],
            visibility: Optional[PostVisibility],
            comments_active: Optional[bool]
    ):
        """
        Update a post with the given parameters.
        All optional parameters may be omitted, and only set parameters will be changed.

        :param post_id: ID of the post to update
        :param title: New title
        :param content: New content
        :param date: New publication date
        :param visibility: new visibility
        :param comments_active: new comment setting
        """
        data = dict()
        if title:
            data['title'] = title
        if content:
            data['content'] = content
        if date:
            data['publicationDate'] = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        if visibility:
            data['visibility'] = visibility
        if comments_active is not None:
            data['commentsActive'] = comments_active

        if not data:
            log.info('No data passed. Will not update post')
            return

        r = self._do_patch(f'/posts/{post_id}', data)
        if r.status_code != 200:
            log.error(f'Could not update post {post_id}: [{r.status_code} - {r.reason}] "{r.content}"')
            r.raise_for_status()

        log.info(f'Updated post {post_id}')

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
