from dataclasses import dataclass

from enum import Enum
from typing import Any


class EventFileType(Enum):
    """Enum to distinguish between 'file' and 'link' attachments"""
    LINK = 'link'
    FILE = 'file'


@dataclass
class EventFile:
    """ChurchTools Event Attachment Information"""
    id: int
    type: EventFileType
    name: str
    url: str

    @classmethod
    def from_event_api_json(cls, file_data: dict[str | Any]):
        """Create instance from API results at /api/events/…"""
        return cls(
            id=file_data['domainIdentifier'],
            type=EventFileType(file_data['domainType']),
            name=file_data['title'],
            url=file_data['frontendUrl']
        )

    @classmethod
    def from_file_api_json(cls, file_data: dict[str | Any]):
        """Create instance from API results at /api/files/…"""
        return cls(
            id=file_data['id'],
            type=EventFileType(file_data['type']),
            name=file_data['name'],
            url=file_data['fileUrl']
        )
