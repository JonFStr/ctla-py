"""
Dataclasses that combine information from different sources
"""
import logging
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

log = logging.getLogger(__name__)


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
    def yt_title(self) -> str:
        """Apply the YouTube title template configured"""
        return Template(config.youtube['templates']['title']).safe_substitute(**self._substitution_vars).strip()

    @property
    def yt_description(self) -> str:
        """Apply the YouTube description template configured"""
        return Template(config.youtube['templates']['description']).safe_substitute(**self._substitution_vars).strip()

    @property
    def post_id(self) -> int:
        """
        Extract the post ID from the attachment link :py:attr:`post_link`

        :return: The ID
        :raise RuntimeError: if any error occurs (post_link not set, unable to extract ID from URL)
        """
        try:
            return int(self.post_link.url.split('/')[-1])
        except ValueError:
            log.error(f'Could not parse post id from "{self.post_link.url}"')
            raise RuntimeError

    @property
    def post_title(self) -> str:
        """Apply the post title template configured"""
        return Template(
            config.churchtools['post_settings']
            .get('title', config.youtube['templates']['title'])
        ).safe_substitute(
            **self._substitution_vars | {'link': self.yt_link.url}
        ).strip()

    @property
    def post_content(self) -> str:
        """Apply the post description template configured"""
        return Template(
            config.churchtools['post_settings']['content']
        ).safe_substitute(
            **self._substitution_vars | {'link': self.yt_link.url}
        ).strip()

    @property
    def _substitution_vars(self) -> dict[str, str]:
        """Pack the variables available in templates into one dict"""
        fmt_start = self.start_time.strftime(config.churchtools['templates']['dateformat'])
        fmt_end = self.end_time.strftime(config.churchtools['templates']['dateformat'])

        spkr_tmplt = config.churchtools['templates']['speaker']
        speaker_short = Template(spkr_tmplt['short']).safe_substitute(name=self.speaker) if self.speaker else ''
        speaker_long = Template(spkr_tmplt['long']).safe_substitute(name=self.speaker) if self.speaker else ''

        return dict(
            title=self.title,
            note=self.note,
            start=fmt_start,
            end=fmt_end,
            speaker_s=speaker_short,
            speaker_l=speaker_long
        )


@dataclass
class RuntimeStats:
    """Dataclass to store runtime stats to report to monitor"""
    total: int = 0
    new: int = 0
    updated: int = 0
    deleted: int = 0
    skipped: int = 0


def _is_video_id(match: str):
    """Returns true if the given string contains only characters that would appear in a YouTube video ID"""
    allowed_chars = set(string.ascii_letters + string.digits + '_-')
    return set(match) <= allowed_chars
