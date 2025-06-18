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
    start_time: datetime
    end_time: datetime
    title: str
    description: str
    isCanceled: bool

    facts: Facts

    yt_link: Optional[EventFile] = None
    yt_thumbnail: Optional[EventFile] = None

    @classmethod
    def from_api_json(cls, event: dict[str, typing.Any], facts: dict[str, int | str]) -> 'CtEvent':
        """
        Create instance from API results
        :param event: Result from /events
        :param facts: Result from /events/`ID`/facts
        :return:
        """
        # Find attached files we care about
        yt_link_data = next(
            (f for f in event['eventFiles'] if f['title'] == config.churchtools['stream_attachment_name']), None)
        yt_thumb_data = next((f for f in event['eventFiles'] if f['title'] == config.churchtools['thumbnail_name']),
                             None)

        return cls(
            id=event['id'],
            category_id=event['calendar']['domainIdentifier'],
            start_time=datetime.fromisoformat(event['startDate']),
            end_time=datetime.fromisoformat(event['endDate']),
            title=event['name'],
            description=event['description'],
            isCanceled=event['isCanceled'],
            facts=Facts.from_api_json(facts),
            yt_link=EventFile.from_event_api_json(yt_link_data) if yt_link_data is not None else None,
            yt_thumbnail=EventFile.from_event_api_json(yt_thumb_data) if yt_thumb_data is not None else None,
        )
