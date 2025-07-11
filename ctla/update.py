"""
Update functions: create & update events, broadcasts, stuff
"""
import datetime
import logging
import operator
from string import Template

import config
from ct.ChurchTools import ChurchTools
from data import Event
from wp import WordPressPage
from wp.WordPress import WordPress
from yt.YouTube import YouTube
from yt.type_hints import LiveBroadcast

log = logging.getLogger(__name__)


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
    ct.set_stream_link(event, f'https://youtu.be/{bc['id']}')


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
    if yt_desc != bc_snippet.get('title'):
        data['desc'] = yt_desc

    start_str = bc_snippet.get('scheduledStartTime')
    if not start_str or ev.start_time != datetime.datetime.fromisoformat(start_str):
        data['start'] = ev.start_time

    end_str = bc_snippet.get('scheduledEndTime')
    if not end_str or ev.end_time != datetime.datetime.fromisoformat(end_str):
        data['end'] = ev.end_time

    if ev.yt_visibility != bc['status']['privacyStatus']:
        data['privacy'] = ev.yt_visibility

    bc = yt.set_broadcast_info(bc, **data)
    bc = yt.set_thumbnails(bc, ev.yt_thumbnail.url if ev.yt_thumbnail else config.youtube['thumbnail_uri'])
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

        prev_end: datetime = datetime.datetime.fromtimestamp(0)
        for event in events:
            if not event.facts.on_homepage:
                continue

            # If the pre_time is before the end of the previous event and parallel display is disabled,
            # Set its pre_time to the end of the previous event.
            pre_time = event.start_time - datetime.timedelta(config.wordpress['days_to_show_in_advance'])
            if not config.wordpress['allow_parallel_display'] and pre_time < prev_end:
                pre_time = prev_end

            rendered += '\n' + template.safe_substitute({
                'title': event.title,
                'pre_iso': pre_time.isoformat(),
                'start_iso': event.start_time.isoformat(),
                'end_iso': event.end_time.isoformat(),
                'datetime': event.start_time.strftime(config.wordpress['datetime_format']),
                'video_link': event.yt_link.url
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
    log.info(f'Adding {len(events)} to WordPress pages…')

    # Update all pages
    for page_id, template_key in config.wordpress.get('pages', {}).items():
        page = wp.get_page(page_id)

        new_page = WordPressPage.insert_content(page, rendered_templates[template_key])

        if new_page:
            wp.update_page(page_id, new_page)
            log.info(f'Updated page {page_id}.')
        else:
            log.error(f'Could not update page {page_id} because the content could not be inserted.')
