"""TypedDict classes for type hints"""
import base64
import logging
import re
import urllib.parse
from typing import TypedDict, NamedTuple, NotRequired, Any, Optional

import config

log = logging.getLogger(__name__)


class WordPressContentPart(NamedTuple):
    """Metadata holder for a WordPress page content substring"""
    content: str
    """The content part"""
    isTemplate: bool
    """Whether this content part is inside a CTLA-Tag"""


class WordPressContent(TypedDict):
    """
    The ``content`` field of WordPress pages
    """
    raw: str


class WordPressPage(TypedDict):
    """
    A WordPress page object
    """
    title: NotRequired[WordPressContent]
    id: NotRequired[int]
    content: WordPressContent


def template_tags() -> tuple[str, str]:
    """
    The HTML-Comment "tags" to use for determining where to put our generated content
    :return: A tuple containing the opening and closing tags
    """
    return f'<!-- {config.wordpress['content_tag']} -->', f'<!-- /{config.wordpress['content_tag']} -->'


def split_page_content(page: WordPressPage) -> Optional[list[Any]]:
    """
    Split the page's content into parts at the CTLA-Tag comments defined in config with ``wordpress.content-tag``
    :param page: The page which content is to be split
    :return: A list of split contents
    """
    tag_open, tag_close = template_tags()
    parts = []

    is_in_tag = False
    remaining = page['content']['raw']
    while True:
        current_tag = tag_close if is_in_tag else tag_open

        split = remaining.split(current_tag, maxsplit=1)
        part = split[0]

        parts.append(WordPressContentPart(content=part, isTemplate=is_in_tag))

        is_in_tag = not is_in_tag

        if split[1]:
            remaining = split[1]
        else:
            if is_in_tag:
                log.warning(f'Missing close tag in page "{page['title']['raw']}". Refusing to overwrite.')
                return None
            break

    return parts


def reassemble_page(parts: list[WordPressContentPart]) -> WordPressPage:
    """
    Reassemble content parts into one ``WordPressPage``
    :param parts: The parts to reassemble
    :return: The reassembled page
    """
    tag_open, tag_close = template_tags()

    content = ''

    for part, is_template in parts:
        if is_template:
            content += tag_open + part + tag_close
        else:
            content += part

    return WordPressPage(content=WordPressContent(raw=content))


def _insert_plain_content(page: WordPressPage, content: str) -> Optional[WordPressPage]:
    """Implementation for :py:func:`insert_content` in normal mode (``config.wordpress.wpbakery_compat`` is disabled)"""
    content_parts = split_page_content(page)
    if not content_parts:
        return None

    new_parts: list[WordPressContentPart] = []
    for part in content_parts:
        if part.isTemplate:
            new_parts.append(WordPressContentPart(content=content, isTemplate=True))
        else:
            new_parts.append(part)

    return reassemble_page(new_parts)


def _insert_bakery_content(page: WordPressPage, content: str) -> Optional[WordPressPage]:
    """Implementation for :py:func:`insert_content` when ``config.wordpress.wpbakery_compat`` is enabled"""
    # Quote and encode the content
    content = base64.b64encode(urllib.parse.quote(content, safe='').encode('utf-8')).decode('utf-8')

    new_content, n = re.subn(
        rf'(?<=\[vc_raw_html el_class="{config.wordpress['content_tag']}"])[a-zA-Z0-9+=/]*?(?=\[/vc_raw_html])',
        content,
        page['content']['raw']
    )
    log.info(f'Inserted content {n} times into "{page['title']['raw']}" (#{page['id']})')
    return WordPressPage(content=WordPressContent(raw=new_content))


def insert_content(page: WordPressPage, content: str) -> Optional[WordPressPage]:
    """
    Insert the rendered template into the page.

    :param page: The WordPressPage to modify
    :param content: The rendered template
    :return: A new ``WordPressPage`` dictionary containing only the new content
    """
    if config.wordpress['wpbakery_compat']:
        return _insert_bakery_content(page, content)
    else:
        return _insert_plain_content(page, content)
