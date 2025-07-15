import typing
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import config
from .EventFile import EventFile
from .Facts import Facts


@dataclass
class CtEvent:
    """Class holding data about an Event"""
    id: int
    category_id: int
    appointment_id: int
    start_time: datetime
    end_time: datetime
    title: str
    note: str
    isCanceled: bool

    speaker: Optional[str]

    facts: Facts

    yt_link: Optional[EventFile] = None
    yt_thumbnail: Optional[EventFile] = None
    post_link: Optional[EventFile] = None

    @classmethod
    def from_api_json(
            cls,
            event: dict[str, typing.Any],
            facts: dict[str, int | str],
            service_mdata: dict[str, int]
    ) -> 'CtEvent':
        """
        Create instance from API results
        :param event: Result from /events
        :param facts: Result from /events/`ID`/facts
        :param service_mdata: Service masterdata to correlate service IDs to names
        :return:
        """
        # Find attached files we care about
        yt_link_data = next(
            (f for f in event['eventFiles'] if f['title'] == config.churchtools['stream_attachment_name']), None
        )
        yt_thumb_data = next(
            (f for f in event['eventFiles'] if f['title'] == config.churchtools['thumbnail_name']), None
        )
        post_link_data = next(
            (f for f in event['eventFiles']
             if f['title'] == config.churchtools.get('post_settings', {}).get('attachment_name')), None
        )

        # Get services
        speaker = None
        for service in event.get('eventServices', []):
            if service['serviceId'] == service_mdata[config.churchtools['speaker_service_name']]:
                speaker = service['name']
                break

        return cls(
            id=event['id'],
            category_id=int(event['calendar']['domainIdentifier']),
            appointment_id=int(event['appointmentId']),
            start_time=datetime.fromisoformat(event['startDate']),
            end_time=datetime.fromisoformat(event['endDate']),
            title=event['name'],
            note=event['note'],
            isCanceled=event['isCanceled'],
            speaker=speaker,
            facts=Facts.from_api_json(facts),
            yt_link=EventFile.from_event_api_json(yt_link_data) if yt_link_data else None,
            yt_thumbnail=EventFile.from_event_api_json(yt_thumb_data) if yt_thumb_data else None,
            post_link=EventFile.from_event_api_json(post_link_data) if post_link_data else None
        )
