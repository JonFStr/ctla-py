import logging
from collections.abc import Mapping
from typing import Any, Optional

import requests

log = logging.getLogger(__name__)


class RestAPI:
    """Base class for REST API classes that use the ``requests`` module"""

    urlbase: str
    """Base URL of the REST API"""
    _headers: Optional[Mapping[str, str | bytes | None]] = None
    """Headers to send with every request"""
    _auth: Optional[tuple[str, str]] = None
    """Authentication details (username password)"""

    def _do_get(self, path: str, **kwargs) -> requests.Response:
        """
        Perform GET request

        :param path: The API endpoint
        :param kwargs: Query parameters
        :return: The `requests`-library's Response-object.
        """
        url = self.urlbase + path
        log.debug(f'Perform GET request to {url} (parameters: {kwargs})')
        return requests.get(url, params=kwargs, headers=self._headers, auth=self._auth)

    def _do_post(self, path: str, json: dict[str, Any]):
        """
        Perform POST request to ChurchTools

        :param path: The API endpoint
        :param json: JSON encodable request body
        :return: The `requests`-library's Response-object.
        """
        url = self.urlbase + path
        log.debug(f'Perform POST request to {url} (data: {json})')
        return requests.post(url, json=json, headers=self._headers, auth=self._auth)

    def _do_delete(self, path: str):
        """
        Perform DELETE request to ChurchTools

        :param path: The API endpoint
        :return: The `requests`-library's Response-object.
        """
        url = self.urlbase + path
        log.debug(f'Perform DELETE request to {url}')
        return requests.delete(url, headers=self._headers, auth=self._auth)
