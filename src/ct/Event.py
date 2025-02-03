import typing
from dataclasses import dataclass
from datetime import datetime

from Facts import Facts


@dataclass
class Event:
    """Class holding data about an Event"""
    id: int
    category_id: int
    start_time: datetime
    end_time: datetime
    title: str
    description: str

    facts: Facts

    @classmethod
    def from_api_json(cls, event: dict[str, typing.Any], facts: dict[str, int | str]):
        """
        Create instance from API results
        :param event: Result from /events
        :param facts: Result from /events/`ID`/facts
        :return:
        """
        return cls(
            id=event['id'],
            category_id=event['calendar']['domainIdentifier'],
            start_time=datetime.fromisoformat(event['startDate']),
            end_time=datetime.fromisoformat(event['endDate']),
            title=event['name'],
            description=event['description'],
            facts=Facts.from_api_json(facts)
        )
