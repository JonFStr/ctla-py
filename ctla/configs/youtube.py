from typing import TypedDict


class YouTubeConf(TypedDict):
    """
    Dataclass holding configuration about the YouTube API connection

    Attributes:

    - `redirect_uri`: Redirection URI for the OAuth flow, including scheme and optional path.
    - `redirect_port`: Port to listen on for OAuth redirects.
    - `client_secrets_file`: Path to the file containing the Google API client secret
    - `credentials_file`: Path where the app stores the API Tokens received from Google
    """
    redirect_url: str
    redirect_port: int
    client_secrets_file: str
    credentials_file: str
