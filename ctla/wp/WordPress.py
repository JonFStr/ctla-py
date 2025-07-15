import logging
import urllib.parse

import config
from RestAPI import RestAPI
from wp.WordPressPage import WordPressPage

log = logging.getLogger(__name__)


class WordPress(RestAPI):
    """
    WordPress API class
    """

    def __init__(self, url: str = None, user: str = None, pwd: str = None):
        """
        :param url: URL of the WordPress instance
        :param user: Username for authentication
        :param pwd: App password for authentication
        """
        try:
            if not url:
                url = config.wordpress['url']
            if not user:
                user = config.wordpress['user']
            if not pwd:
                pwd = config.wordpress['app_password']
        except (KeyError, ValueError):
            log.critical('Please configure Your WordPress URL and credentials in the config or via environment '
                         'variables.')
            exit(1)

        self.urlbase = urllib.parse.urljoin(url, '/wp-json/wp/v2')
        self._auth = user, pwd

        log.info('Initialized WordPress API.')

    def get_page(self, page_id: int) -> WordPressPage:
        """
        Retrieve a page from WordPress

        :param page_id: The ``id`` of the page to fetch
        :return: The page
        """
        log.info(f'Fetching WordPress page {page_id}…')
        r = self._do_get(f'/pages/{page_id}', context='edit')
        if r.status_code != 200:
            log.error(f'Could not fetch wordpress pages: {r.reason}')
            r.raise_for_status()

        return r.json()

    def update_page(self, page_id: int, page: WordPressPage):
        """
        Update the WordPress page with id ``page_id`` and the given data
        :param page_id: ID of the page to update
        :param page: Page data to upload
        """
        log.info(f'Updating wordpress page {page_id}')
        # noinspection PyTypeChecker
        r = self._do_post(f'/pages/{page_id}', page)
        if r.status_code != 200:
            log.error(f'Could not update page {page_id}: {r.reason}')
            r.raise_for_status()
