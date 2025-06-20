"""
Dataclasses that combine information from different sources
"""
import string
import urllib.parse
from dataclasses import dataclass
from string import Template
from typing import Optional

import config
from ct.CtEvent import CtEvent
from ct.Facts import ManageStreamBehavior, YtVisibility
from yt.type_hints import LiveBroadcast
from yt.type_hints import PrivacyStatus


@dataclass
class Event(CtEvent):
    """
    Extension of `CtEvent`, containing a reference to YouTube
    """
    # Attached broadcast
    yt_broadcast: Optional[LiveBroadcast] = None

    @property
    def wants_stream(self):
        """Whether a stream is desired for this `Event`. Does not differentiate between NO and IGNORE"""
        return self.facts.behavior == ManageStreamBehavior.YES

    def __str__(self):
        return f'"{self.title}" ({self.start_time.isoformat(sep=' ', timespec='minutes')}'

    @property
    def youtube_video_id(self) -> Optional[str]:
        """
        Attempt to parse the YouTube video id out of the url.

        This does not support embed URLs (/embed/…), the mobile site (m.youtube.com/…) or nocookie sites.
        """
        if not self.yt_link:
            return None

        query = urllib.parse.urlparse(self.yt_link.url)
        if query.hostname == 'youtu.be':
            return query.path[1:]  # youtu.be-Links have the ID as path
        elif query.hostname.endswith('youtube.com'):
            match = urllib.parse.parse_qs(query.query)['v'][0]
            if _is_video_id(match):
                return match
        return None

    @property
    def yt_visibility(self) -> PrivacyStatus:
        """Parse the visibility fact from ChurchTools into a privacy status for YouTube"""
        match self.facts.visibility:
            case YtVisibility.VISIBLE:
                return 'public'
            case YtVisibility.UNLISTED:
                return 'unlisted'
            case _:
                return 'private'

    @property
    def formatted_start(self) -> str:
        """Start datetime, formatted according to config.youtube.templates.dateformat"""
        return self.start_time.strftime(config.youtube['templates']['dateformat'])

    @property
    def formatted_end(self) -> str:
        """End datetime, formatted according to config.youtube.templates.dateformat"""
        return self.end_time.strftime(config.youtube['templates']['dateformat'])

    @property
    def yt_title(self) -> str:
        """Apply the YouTube title template configured"""
        return Template(config.youtube['templates']['title']).safe_substitute(**self._substitution_vars)

    @property
    def yt_description(self) -> str:
        """Apply the YouTube description template configured"""
        return Template(config.youtube['templates']['description']).safe_substitute(**self._substitution_vars)

    @property
    def _substitution_vars(self) -> dict[str, str]:
        """Pack the variables available in templates into one dict"""
        return dict(
            title=self.title,
            description=self.description,
            start=self.formatted_start,
            end=self.formatted_end
        )


def _is_video_id(match: str):
    """Returns true if the given string contains only characters that would appear in a YouTube video ID"""
    allowed_chars = set(string.ascii_letters + string.digits + '_-')
    return set(match) <= allowed_chars
