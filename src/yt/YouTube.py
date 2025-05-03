import googleapiclient.discovery
from google.oauth2.credentials import Credentials

from . import oauth


class YouTube:
    """
    YouTube-API main class
    """
    credentials: Credentials
    service: googleapiclient.discovery.Resource

    def __init__(self):
        print('Initializing YouTube API…')
        # Obtain Credentials
        self.credentials = oauth.load_credentials()
        if self.credentials is None:
            self.credentials = oauth.authorize()

        # Create client
        self.service = googleapiclient.discovery.build('youtube', 'v3', credentials=self.credentials)

        print('YouTube ready.')

    def close(self):
        oauth.save_credentials(self.credentials)
