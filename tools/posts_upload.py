import dataclasses
import html
import logging
import operator
import re
from argparse import Namespace
from urllib.parse import urlunsplit, urlsplit, parse_qsl, urlencode
from zoneinfo import ZoneInfo

import config
from ct.ChurchTools import ChurchTools
from tools.posts_migration import Post

ignore_link_titles = [
    re.compile(r".*Hier geht.{0,5}?s zu.*", flags=re.IGNORECASE),
    re.compile('Youtube', flags=re.IGNORECASE)
]

LINK_SEARCH_PATTERN = re.compile(r'(<([^ ]+) [^>]*?(?:href|src)=".+?".*?(?:/|>.*?</\2)>)', flags=re.DOTALL)
LINK_EXTRACT_PATTERN = re.compile(r'<([^ ]+) [^>]*?(?:href|src)="(.+?)".*?(?:/|>(.*?)</\1)>', flags=re.DOTALL)


def prepare_youtube_posts(targets: list[Post]):
    new_posts = []
    for p in targets:
        if p.ct_status:
            if p.ct_status == 'skip':
                logging.info(f'Skipping post {p.title}: Configured to skip')
                continue
            try:
                if int(p.ct_status):
                    logging.info(f'Skipping post {p.title}: Post already exists')
                    continue
            except ValueError:
                pass

        # convert &amp; to literal '&'
        content = html.unescape(p.content)
        content = content.replace('<div>', '')
        content = content.replace('</div>', '')

        # Extract YouTube links
        split = re.split(LINK_SEARCH_PATTERN, content)
        new_content = ''
        i = 0
        for substr in split:
            i += 1  # Skip every third item because of the HTML-Tag capturing group
            if i % 3 == 0:
                continue

            if re.fullmatch(LINK_SEARCH_PATTERN, substr):
                new_content += '\n'

                url, title = re.fullmatch(LINK_EXTRACT_PATTERN, substr).group(2, 3)
                if title and url != title and not any(re.fullmatch(p, title) for p in ignore_link_titles):
                    new_content += title + ': '  # Custom (non-ignored) link title: prepend before link

                _, netloc, path, query, _ = urlsplit(url)
                qs = dict(parse_qsl(query))

                n_netloc = 'youtu.be'
                n_path = ''
                n_query = {}
                if 't' in qs:
                    n_query['t'] = qs['t']

                if netloc == 'youtu.be':
                    n_path = path
                elif 'youtube.com' in netloc:
                    if 'list' in qs:
                        # Playlist
                        n_netloc = 'youtube.com'
                        n_path = '/playlist'
                        if 'v' in qs:
                            n_query['v'] = qs['v']
                        n_query['list'] = qs['list']
                    elif 'embed' in path:
                        # Embed string
                        n_path = path.split('/')[-1]
                    else:
                        # Only video
                        n_path = qs['v']
                else:  # Not YouTube
                    n_netloc = netloc
                    n_path = path
                    n_query = query

                new_content += urlunsplit(('https', n_netloc, n_path, urlencode(n_query), ''))
                new_content += '\n'
            else:
                new_content += substr

        new_posts.append(dataclasses.replace(p, content=new_content.strip()))

    return new_posts


# ===== YouTube preformat =====
# from pathlib import Path
#
# posts = Post.schema().loads(Path('posts_json/for_youtube.json').read_text(), many=True)
#
# new = prepare_youtube_posts(posts)
#
# Path('posts_json/ref_youtube.json').write_text(Post.schema().dumps(new, many=True, ensure_ascii=False))


def upload_youtube_posts(group_id: int, targets: list[Post]):
    config.args.parsed = Namespace(config=open('ctla_config.json'))
    config.load()
    ct = ChurchTools()

    for p in sorted(targets, key=operator.attrgetter('date')):
        try:
            int(p.ct_status)
            print(p.title, 'SKIPPED')
            continue  # Skip if already has post ID
        except (ValueError, TypeError):
            pass

        print(p.title)
        r = ct._do_post('/posts', dict(
            title=p.title,
            content=p.content,
            visibility='group_visible',
            commentsActive=False,
            groupId=group_id
        ))
        if r.status_code != 201:
            logging.error(f'Could not create post for "{p.title}": {r.status_code}[{r.reason}] -- {r.content}')
            ans = input('continue? ')
            if ans != 'y':
                break
            continue

        response = r.json()['data']
        p.ct_status = int(response['id'])

        # Backdating
        r = ct._do_patch(f'/posts/{p.ct_status}', {
            'publicationDate': p.date
                         .replace(tzinfo=ZoneInfo('Europe/Berlin'))
                         .astimezone(ZoneInfo('UTC'))
                         .strftime('%Y-%m-%dT%H:%M:%SZ')
        })

        if r.status_code != 200:
            logging.error(
                f'Could not backdate post "{p.title}" ({p.ct_status}): {r.status_code}[{r.reason}] -- {r.content}')
            ans = input('continue? ')
            if ans != 'y':
                break

    return targets

# ===== ChurchTools YouTube upload =====
# from pathlib import Path
#
# posts = Post.schema().loads(Path('posts_json/remaining_youtube.json').read_text(), many=True)
#
# remaining = upload_youtube_posts(408, posts)
#
# if remaining:
#    Path('posts_json/remaining_youtube.json').write_text(Post.schema().dumps(remaining, many=True, ensure_ascii=False))
