import ipaddress
import json
import os.path
import socket
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import cast

import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from oauthlib.oauth2 import OAuth2Error

import configs

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']


def save_credentials(credentials):
    """
    Save API credentials to the save file

    :param credentials: The credentials to save
    """
    cred_path = configs.youtube['credentials_file']
    with open(cred_path, 'w') as cred_file:
        # noinspection PyTypeChecker
        json.dump({'token': credentials.token,
                   'refresh_token': credentials.refresh_token,
                   'token_uri': credentials.token_uri,
                   'client_id': credentials.client_id,
                   'client_secret': credentials.client_secret,
                   'granted_scopes': credentials.granted_scopes},
                  cred_file)


def load_credentials() -> Credentials | None:
    """
    Load API credentials from the save file.

    :return: The loaded credentials, or None, if none were found.
    """
    cred_path = configs.youtube['credentials_file']
    if os.path.exists(cred_path):
        with open(cred_path, 'r') as cred_file:
            return Credentials(**json.load(cred_file))


# helper variables for passing information between callback and main app flow
_oauth_state: str
_oauth_success = False


def _get_oauth_flow(state=None):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        configs.youtube['client_secrets_file'],
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = configs.youtube['redirect_url']
    return flow


class OAuthHTTPRequestHandler(BaseHTTPRequestHandler):
    # noinspection PyShadowingBuiltins
    def log_message(self, format, *args):
        pass  # Do nothing, don't want to log httpd stuff to stderr/stdout

    def get_request_url(self) -> str:
        """Patch together the request URL from different headers"""
        ip = ipaddress.ip_address(self.address_string())
        scheme = 'http'
        host, port = cast(socket.socket, self.request).getsockname()
        if ip.is_loopback:
            scheme = 'https'
        if ip.is_private:
            # Source IP is in private subnet -> trust proxy headers
            scheme = self.headers.get('X-Forwarded-Proto', scheme)
            host = self.headers.get('X-Forwarded-Host', host)
            port = self.headers.get('X-Forwarded-Port', port)

        return str(urllib.parse.urlunsplit((scheme, host + ':' + str(port), self.path, '', '')))

    # noinspection PyPep8Naming
    def do_GET(self):
        """Handle GET requests"""
        try:
            flow = _get_oauth_flow(_oauth_state)
            request_url = self.get_request_url()

            # Check if this is a valid OAuth return
            if urllib.parse.parse_qs(urllib.parse.urlsplit(request_url).query).get('state', None) is None:
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    HTTPStatus.BAD_REQUEST.description,
                    'No CSRF state present'
                )
                return

            flow.fetch_token(authorization_response=request_url)
            credentials = flow.credentials
            save_credentials(credentials)
            print('Credentials saved')

            self.send_response(HTTPStatus.OK, HTTPStatus.OK.description)
            response = '<html><body><h1>Credentials saved</h1>\nYou can now close this page.</body></html>' \
                .encode('utf-8')
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            global _oauth_success
            _oauth_success = True
        except OAuth2Error as e:
            self.send_error(e.status_code, e.error, e.description)
            # Re-raise exception to print stack trace to stderr
            raise e


def authorize() -> Credentials:
    """
    Follow the OAuth flow to let the user grant this app permissions to the target YouTube channel

    :return: The acquired credentials
    """
    flow = _get_oauth_flow()

    global _oauth_state
    authorization_url, _oauth_state = flow.authorization_url(access_type='offline', prompt='consent')
    print('Please authorize this app to access your Google Account:\n'
          f'Open the following URL in your browser: {authorization_url}')

    # Start server for listening for OAuth redirects
    server_address = ('', configs.youtube['redirect_port'])
    # noinspection PyTypeChecker
    with HTTPServer(server_address, OAuthHTTPRequestHandler) as httpd:
        print(f'Now listening on port {server_address[1]} for authorization result…')
        while not _oauth_success:
            httpd.handle_request()

    print('Authorization done.')
    return load_credentials()
