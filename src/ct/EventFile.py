from dataclasses import dataclass

from enum import Enum


class EventFileType(Enum):
    LINK = 'link'
    FILE = 'file'


@dataclass
class EventFile:
    """ChurchTools Event Attachment Information"""
    id: int
    type: EventFileType
    title: str
    url: str

    @classmethod
    def from_api_json(cls, file_data):
        """Create instance from API results"""
        return cls(
            id=file_data['domainIdentifier'],
            type=EventFileType(file_data['domainType']),
            title=file_data['title'],
            url=file_data['frontendUrl']
        )
