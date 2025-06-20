from typing import TypedDict, Literal


class YouTubeTemplateConf(TypedDict):
    """
    Dataclass holding templates for YouTube information.

    The templates use ${}-substitutions. Valid substitutions are:
    - title
    - description
    - start (formatted with `dateformat`)
    - end (formatted with `dateformat`)

    Attributes:

    - `title`: Template for the title
    - `description`: Template for the broadcast description
    - `dateformat`: Template understood by `datetime.strftime()`, used to format dates
    """
    title: str
    description: str
    dateformat: str


class YouTubeBroadcastSettingsConf(TypedDict):
    """
    Dataclass holding technical settings for broadcasts

    Attributes:

    - `enable_monitor_stream`: Whether the monitoring stream should be enabled
    - `broadcast_stream_delay_ms`: If there is a monitoring stream, how much delay should be added to the public stream
    - `enable_embed`: Enable embedding
    - `enable_dvr`: Enable DVR controls during the livestream
    - `record_from_start`: Record the stream and publish it as video later
    - `closed_captions_type`: Whether to provide closed captions
    - `latency_preference`: The latency preference. either 'normal', 'low', or 'ultraLow'
    - `enable_auto_start`: Whether to automatically "Go Live" when receiving data on the bound stream
    - `enable_auto_stop`: Whether to automatically stop the broadcast around 1min after receiving data
    """
    enable_monitor_stream: bool
    broadcast_stream_delay_ms: int
    enable_embed: bool
    enable_dvr: bool
    record_from_start: bool
    closed_captions_type: Literal['closedCaptionsDisabled', 'closedCaptionsHttpPost', 'closedCaptionsEmbedded']
    latency_preference: Literal['normal', 'low', 'ultraLow']
    enable_auto_start: bool
    enable_auto_stop: bool


class YouTubeConf(TypedDict):
    """
    Dataclass holding configuration about the YouTube API connection

    Attributes:

    - `redirect_uri`: Redirection URI for the OAuth flow, including scheme and optional path.
    - `redirect_port`: Port to listen on for OAuth redirects.
    - `client_secrets_file`: Path to the file containing the Google API client secret
    - `credentials_file`: Path where the app stores the API Tokens received from Google
    - `templates`: Template configuration for YouTube title / description
    - `thumbnail_uri`: URI to a default thumbnail to be set on all new streams.
      Can be a path to a file, a `file://`-URI or web address
    - `stream_key_id`: The identifier of the stream key to use (not the key itself!)
    - `broadcast_settings`: Setting to apply to newly created broadcasts
    """
    redirect_url: str
    redirect_port: int
    client_secrets_file: str
    credentials_file: str
    templates: YouTubeTemplateConf
    thumbnail_uri: str
    stream_key_id: str
    broadcast_settings: YouTubeBroadcastSettingsConf
