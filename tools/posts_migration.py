"""
Parse an export file of WordPress posts and upload them to ChurchTools posts

This is not a plug-and-play script, but most likely requires to be tested and modified before use:
- The server timezone might not match 'Europe/Berlin'
- The metadata parsing is tailored to the "Download Manager" WordPress-Plugin
- and probably more. Just test before you use it :)
"""
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import phpserialize
from dataclasses_json import DataClassJsonMixin


@dataclass
class Post(DataClassJsonMixin):
    id: int
    title: str
    date: datetime
    edit: datetime
    content: str
    categories: list[str]
    wpdm: dict
    meta: dict
    # xml: ET.Element


def _parse_all(path: str) -> list[Post]:
    """
    Parse all items from the given xml file
    """
    namespaces = {  # Namespace translations for parsing
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/'
    }
    wpdm_ignored_keys = {'access', 'cache_zip', 'custom_form_field', 'download_count', 'download_limit_per_user',
                         'email_lock_idl', 'email_lock_title', 'file_titles', 'gc_scopes_contacts',
                         'individual_file_download', 'items_per_page', 'link_template', 'masterkey', 'package_size',
                         'package_size_b', 'page_template', 'password_usage_limit', 'publish_date', 'quota',
                         'show_counter', 'show_quota', 'template', 'uid', 'view_count', 'zipped_file'}
    wpdm_serialize = {'fileinfo', 'files'}
    meta_ignored_keys = {'um_content_restriction', '_wp_old_slug', '_edit_last', '_wp_old_date', '_cs_replacements',
                         '__wpdmx_user_download_count', 'stackable_optimized_css_raw'}

    root = ET.parse(path)
    items = root.find('channel').findall('item')

    result = []

    for item in items:
        wpdm: dict[str, str | dict] = {}  # DownloadManager metadata
        meta: dict[str, str | dict] = {}  # General metadata
        for meta_tag in item.findall('wp:postmeta', namespaces):
            key = meta_tag.findtext('wp:meta_key', None, namespaces)
            value = meta_tag.findtext('wp:meta_value', None, namespaces)
            if not key or not value:
                continue
            if key.startswith('__wpdm_'):
                wpdm_key = key.removeprefix('__wpdm_')
                if wpdm_key in wpdm_serialize:
                    wpdm[wpdm_key] = phpserialize.loads(value.encode('utf-8'), decode_strings=True)
                elif not key.endswith('_lock') and wpdm_key not in wpdm_ignored_keys:
                    wpdm[wpdm_key] = value

            else:
                if not key.startswith('__wpdmkey') and not key.startswith('_oembed_') and key not in meta_ignored_keys:
                    if key == '_wp_attachment_metadata':
                        meta[key] = phpserialize.loads(value.encode('utf-8'), decode_strings=True)
                    else:
                        meta[key] = value

        result.append(Post(
            id=int(item.findtext('wp:post_id', None, namespaces)),
            title=item.findtext('title'),
            date=datetime
            .fromisoformat(item.findtext('wp:post_date', None, namespaces))
            .replace(tzinfo=ZoneInfo('Europe/Berlin')),
            edit=datetime
            .fromisoformat(item.findtext('wp:post_modified', None, namespaces))
            .replace(tzinfo=ZoneInfo('Europe/Berlin')),
            content=item.findtext('content:encoded', None, namespaces),
            categories=[i.text for i in item.findall("./category[@domain='wpdmcategory']")],
            wpdm=wpdm,
            meta=meta,
            # xml=item
        ))

    return result


def _split_parsed(parsed: list[Post]):
    """
    Split the parsed items into categories
    """

    def contains(p, search):
        """Case-insensitive search in title and content for substring ``search``"""
        search = search.lower()
        return p.title and search in p.title.lower() or p.content and search in p.content.lower()

    for post in parsed:
        all_posts.append(post)

        for cat in post.categories:
            if cat == 'Veranstaltungen' and 'Gottesdienste' in post.categories:
                continue  # Remove common duplicate pair of categories
            categorized.setdefault(cat, []).append(post)

        if contains(post, 'youtu'):
            # This post likely contains a YouTube link
            filtered.setdefault('youtube', []).append(post)
        elif not post.content or not post.content.strip():
            # This post does not have content (or only whitespace); probably only files
            filtered.setdefault('nocontent', []).append(post)
        else:
            filtered.setdefault(None, []).append(post)


all_posts = []
categorized = {}
filtered = {}

if __name__ == '__main__':
    _split_parsed(_parse_all('export.xml'))

    with open('parsed_export.json', 'w') as f:
        w: Post
        json.dump({k: [w.to_dict(True) for w in v] for k, v in categorized.items()}, f, ensure_ascii=False)

"""
Liederbuch-Kategorie weg
Neue Songs-Kategorie weg

Gäste:
- Veröffentlichungen
Rest in intern
"""
