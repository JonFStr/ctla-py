"""
Update functions: create & update events, broadcasts, stuff
"""
import atexit
import datetime
import logging
import operator
import tempfile
import urllib.parse
from collections.abc import MutableMapping
from datetime import timedelta
from pathlib import Path
from string import Template
from typing import ClassVar

import config
from ct.ChurchTools import ChurchTools
from data import Event
from wp import WordPressPage
from wp.WordPress import WordPress
from yt.YouTube import YouTube
from yt.type_hints import LiveBroadcast

log = logging.getLogger(__name__)


class ThumbnailCache(MutableMapping):
    """Singleton class managing the caching of thumbnail information to avoid hitting YouTube API ratelimits"""

    _instance: ClassVar['ThumbnailCache']
    """Singleton instance"""

    _cache_dict: dict[str, str] = {}
    """Thumbnail cache: YouTube ID -> Thumbnail URI"""
    _accessed_keys: set[str] = set()
    """
    Stores keys that have been accessed during the lifetime of this cache.
    Only those keys will be written back when saving
    """

    def __new__(cls):
        """Implement the singleton pattern"""
        if not hasattr(cls, '_instance'):
            cls._instance = super(ThumbnailCache, cls).__new__(cls)
            # Load the cache
            if cls._instance._thumbs_filename.exists():
                cls._instance._cache_dict = dict(
                    line.split('|', maxsplit=1)
                    for line in cls._instance._thumbs_filename.read_text().splitlines()
                    if line
                )
            log.info(f'Loaded cached thumbnail information for {len(cls._instance._cache_dict)} broadcasts')
            # Setup saving
            atexit.register(cls._instance._save_cache)
        return cls._instance

    def _save_cache(self):
        self._thumbs_filename.write_text('\n'.join(f'{k}|{v}' for k, v in self._cache_dict.items()))
        log.info(f'Saved thumbnail information for {len(self._cache_dict)} broadcasts in {self._thumbs_filename}')

    @property
    def _thumbs_filename(self) -> Path:
        """return the configured path for the thumbnail cache"""
        return Path(tempfile.gettempdir()).joinpath(config.youtube['thumbnail_cache'])

    def __getitem__(self, item):
        self._accessed_keys.add(item)
        return self._cache_dict[item]

    def __delitem__(self, key, /):
        self._accessed_keys.remove(key)
        del self._cache_dict[key]

    def __len__(self):
        return len(self._cache_dict)

    def __iter__(self):
        return iter(self._cache_dict)

    def __setitem__(self, key, value, /):
        self._accessed_keys.add(key)
        self._cache_dict[key] = value


def create_youtube(ct: ChurchTools, yt: YouTube, event: Event):
    """
    Create a YouTube broadcast for the given event and bind the stream id;
    then attach it and upload the link to ChurchTools.

    This still requires `update_youtube()` to be called in order to set all attributes correctly

    :param ct: ChurchTools API instance
    :param yt: YouTube service instance
    :param event: The event wanting a broadcast
    """
    bc: LiveBroadcast = yt.create_broadcast(event.title, event.start_time, event.yt_visibility)
    bc = yt.bind_stream_to_broadcast(bc['id'], config.youtube['stream_key_id'])
    event.yt_broadcast = bc
    link_file = ct.attach_link(event, config.churchtools['stream_attachment_name'], f'https://youtu.be/{bc['id']}')
    if link_file:
        event.yt_link = link_file


def _get_thumbnail_uri(title: str) -> str:
    """
    Return the thumbnail URI for the given title from the config

    Scans through ``youtube.thumbnail_uris`` for a key that is contained in ``title``
    and returns the default thumbnail if no match was found
    """
    for search, uri in config.youtube.get('thumbnail_uris', []):
        if search in title:
            return uri
    return config.youtube['default_thumbnail_uri']


def update_youtube(yt: YouTube, ev: Event):
    """
    Update the information on YouTube to reflect the one given in ChurchTools.

    Only updates when necessary.

    :param yt: YouTube service instance
    :param ev: The event to update information for
    """
    if not ev.yt_broadcast:
        return
    bc = ev.yt_broadcast
    bc_snippet = bc.get('snippet', {})
    data = dict()

    yt_title = ev.yt_title
    if yt_title != bc_snippet.get('title'):
        data['title'] = yt_title

    yt_desc = ev.yt_description
    if yt_desc != bc_snippet.get('description'):
        data['desc'] = yt_desc

    start_str = bc_snippet.get('scheduledStartTime')
    if not start_str or ev.start_time != datetime.datetime.fromisoformat(start_str):
        data['start'] = ev.start_time

    end_str = bc_snippet.get('scheduledEndTime')
    if not end_str or ev.end_time != datetime.datetime.fromisoformat(end_str):
        data['end'] = ev.end_time

    if ev.yt_visibility != bc['status']['privacyStatus']:
        data['privacy'] = ev.yt_visibility

    if data:
        bc = yt.set_broadcast_info(bc, **data)

    # "instantiation" happens only once, because singleton
    thumbs_cache = ThumbnailCache()
    yt_id = ev.yt_broadcast['id']

    target_thumbnail = ev.yt_thumbnail.url if ev.yt_thumbnail else _get_thumbnail_uri(ev.title)
    if thumbs_cache.get(yt_id, '') == target_thumbnail:
        log.info(f'Thumbnail for "{yt_id} has not changed, not setting thumbnail "{target_thumbnail}".')
    else:
        bc = yt.set_thumbnails(bc, target_thumbnail)
        thumbs_cache[yt_id] = target_thumbnail

    ev.yt_broadcast = bc


def _render_templates(events: list[Event]) -> dict[str, str]:
    """
    Populate the templates from config with the given events
    :param events: The events to pull the data from
    :return: A dictionary mapping the template keys to the compiled content
    """
    events = sorted(events, key=operator.attrgetter('start_time'))

    # Render templates
    active_templates = set(config.wordpress.get('pages').values())
    rendered_templates: dict[str, str] = {}

    for template_key in active_templates:
        try:
            template = Template(config.wordpress['content_templates'][template_key])
        except KeyError:
            log.critical(f'Could not find template for key "{template_key}" in config "wordpress.content_templates".')
            exit(1)

        rendered = ''

        prev_end: datetime = datetime.datetime.fromtimestamp(0, tz=datetime.UTC)
        for event in events:
            if not event.facts.on_homepage:
                continue

            # If the pre_time is before the end of the previous event and parallel display is disabled,
            # Set its pre_time to the end of the previous event.
            pre_time = event.start_time - datetime.timedelta(hours=config.wordpress['hours_to_show_in_advance'])
            if not config.wordpress['allow_parallel_display'] and pre_time < prev_end:
                pre_time = prev_end

            rendered += '\n' + template.safe_substitute({
                'title': event.title,
                'pre_iso': pre_time.isoformat(),
                'start_iso': event.start_time.isoformat(),
                'end_iso': event.end_time.isoformat(),
                'datetime': event.start_time.strftime(config.churchtools['templates']['dateformat']),
                'video_link': event.yt_link.url,
                'video_link_quoted': urllib.parse.quote(event.yt_link.url)
            }) + '\n'

            prev_end = event.end_time

        rendered_templates[template_key] = rendered
    return rendered_templates


def update_wordpress(wp: WordPress, events: list[Event]):
    """
    Update all configured WordPress pages with event information
    :param wp: The WordPress API instance
    :param events: The list of events to display in WordPress
    """
    rendered_templates = _render_templates(events)
    log.info(f'Adding {len(events)} broadcast(s) to WordPress pages…')

    # Update all pages
    for page_id, template_key in config.wordpress.get('pages', {}).items():
        page = wp.get_page(page_id)

        new_page = WordPressPage.insert_content(page, rendered_templates[template_key])

        if new_page:
            if new_page['content']['raw'] == page['content']['raw']:
                log.info(f'Did not update page {page_id} because the content did not change.')
                continue
            wp.update_page(page_id, new_page)
            log.info(f'Updated page {page_id}.')
        else:
            log.error(f'Could not update page {page_id} because the content could not be inserted.')
            raise RuntimeError


def create_post(ct: ChurchTools, event: Event):
    """
    Create a post for the given event and add it to the attachments
    :param ct: ChurchTools API instance
    :param event: Event to act on
    """
    # Post creation must not backdate a post
    now = datetime.datetime.now(datetime.UTC)
    date = event.end_time
    if date < now:
        date = now + timedelta(days=1)
    post_id = ct.create_post(
        group_id=config.churchtools['post_settings']['group_id'],
        title=event.post_title,
        content=event.post_content,
        date=date,
        visibility=config.churchtools['post_settings']['post_visibility'],
        comments_active=config.churchtools['post_settings']['comments_active']
    )
    event.post_link = ct.attach_link(
        event=event,
        name=config.churchtools['post_settings']['attachment_name'],
        link=urllib.parse.urlunsplit(('https', config.churchtools['instance'], f'/posts/{post_id}', '', ''))
    )

    if date != event.end_time:
        # Post should be backdated but isn't: immediately update (updating a post allows backdating)
        update_post(ct, event)


def update_post(ct: ChurchTools, event: Event):
    """
    Updates the Post for an event, if necessary

    :param ct: ChurchTools API instance
    :param event: Event to act on
    """
    post = ct.get_post(event.post_id)

    title = event.post_title
    content = event.post_content
    date = event.end_time
    visibility = config.churchtools['post_settings']['post_visibility']
    comments = config.churchtools['post_settings']['comments_active']

    data = dict()
    if post['title'] != title:
        data['title'] = title
    if post['content'] != content:
        data['content'] = content
    if datetime.datetime.fromisoformat(post['publicationDate']) != date:
        data['publicationDate'] = date.strftime('%Y-%m-%dT%H:%M:%SZ')
    if post['visibility'] != visibility:
        data['visibility'] = visibility
    if post['commentsActive'] != comments:
        data['commentsActive'] = comments

    if not data:
        log.info('Post is already up-to-date, will not update.')
        return False

    ct.update_post(event.post_id, data)
    return True
