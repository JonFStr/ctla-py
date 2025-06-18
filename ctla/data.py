"""
Dataclasses that combine information from different sources
"""
import string
import urllib.parse
from dataclasses import dataclass
from typing import Optional

from ct.CtEvent import CtEvent
from ct.Facts import ManageStreamBehavior
from yt.type_hints import LiveBroadcast


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


def _is_video_id(match: str):
    """Returns true if the given string contains only characters that would appear in a YouTube video ID"""
    allowed_chars = set(string.ascii_letters + string.digits + '_-')
    return set(match) <= allowed_chars
