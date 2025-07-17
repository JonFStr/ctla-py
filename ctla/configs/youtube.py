from typing import TypedDict, Literal


class YouTubeTemplateConf(TypedDict):
    """
    Dataclass holding templates for YouTube information.

    The templates use ${}-substitutions. Valid substitutions are:
    - title
    - note
    - start (formatted with `churchtools.templates.dateformat`)
    - end (formatted with `churchtools.templates.dateformat`)
    - speaker_s
    - speaker_l

    Attributes:

    - `title`: Template for the title
    - `description`: Template for the broadcast description
    """
    title: str
    description: str


class YouTubeBroadcastSettingsConf(TypedDict):
    """
    Dataclass holding technical settings for broadcasts
    """

    enable_monitor_stream: bool
    """Whether the monitoring stream should be enabled"""
    broadcast_stream_delay_ms: int
    """If there is a monitoring stream, how much delay should be added to the public stream"""
    enable_embed: bool
    """Enable embedding"""
    enable_dvr: bool
    """Enable DVR controls during the livestream"""
    record_from_start: bool
    """Record the stream and publish it as video later"""
    closed_captions_type: Literal['closedCaptionsDisabled', 'closedCaptionsHttpPost', 'closedCaptionsEmbedded']
    """Whether to provide closed captions"""
    latency_preference: Literal['normal', 'low', 'ultraLow']
    """The latency preference. either 'normal', 'low', or 'ultraLow'"""
    enable_auto_start: bool
    """Whether to automatically "Go Live" when receiving data on the bound stream"""
    enable_auto_stop: bool
    """Whether to automatically stop the broadcast around 1min after receiving data"""


class YouTubeConf(TypedDict):
    """
    Dataclass holding configuration about the YouTube API connection
    """

    redirect_url: str
    """Redirection URI for the OAuth flow, including scheme and optional path."""
    redirect_port: int
    """Port to listen on for OAuth redirects."""
    client_secrets_file: str
    """Path to the file containing the Google API client secret"""
    credentials_file: str
    """Path where the app stores the API Tokens received from Google"""
    templates: YouTubeTemplateConf
    """Template configuration for YouTube title / description"""
    default_thumbnail_uri: str
    """
    URI to a default thumbnail to be set on all new streams.
    Can be a path to a file, a `file://`-URI or web address
    """
    thumbnail_uris: list[tuple[str, str]]
    """
    List of lists for thumbnails of recurring events.
    
    If an event's title contains the first value of an entry (case-sensitive), the corresponding thumbnail (2nd value)
    will be used.
    """
    stream_key_id: str
    """The identifier of the stream key to use (not the key itself!)"""
    broadcast_settings: YouTubeBroadcastSettingsConf
    """Setting to apply to newly created broadcasts"""
    thumbnail_cache: str
    """
    Filename of a temporary file caching thumbnail information to avoid hitting YouTube rate limits.
    May be absolute, otherwise relative to ``tempfile.gettempdir()``
    """
