from typing import TypedDict


class WordPressConf(TypedDict):
    """
    Wordpress configuration
    """

    enabled: bool
    """Enable the Wordpress integration"""
    url: str
    """URL to the WordPress instance"""
    user: str
    """The WordPress username"""
    app_password: str
    """
    Application password for the :py:attr:`user`.
    
    (set from the
    `Application Password <https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/>`__)
    """
    hours_to_show_in_advance: int
    """At how many hours before the event the ``pre_iso`` variable should be set to"""
    allow_parallel_display: bool
    """Whether to allow multiple events to be displayed (before their respective start) together"""
    pages: dict[int, str]
    """Mapping of WordPress page ID to template name (set as key in :py:attr:`content_templates`` dict)"""
    content_tag: str
    """
    The HTML Tag comment where content will be placed between.
    
    Example: if ``content_tag = 'ct-livestreams'``, then CTLA will search for the HTML comments
    ``<!-- ct-livestreams --><-- /ct-livestreams -->`` and put its content between these tags. 
    """
    wpbakery_compat: bool
    """
    Enable compatibility with WPBakery.
    This changes the embedding process to put the content inside a `WPBakery Raw HTML` block and modifies the search
    to instead search for a raw html block with this class name.
    """
    content_templates: dict[str, str]
    """
    Dictionary of content templates. Mapped to different pages via the :py:attr:`pages` dictionary
    
    Substitution variables can be specified in a manner consistent with
    `string.Template <https://docs.python.org/3/library/string.html#string.Template>`__.
    
    Available variables are:
    
    - title
    - pre_iso  -- ISO format of when this event will start to be included
    - start_iso  -- ISO format of when this event will start
    - end_iso  -- ISO format of when this event will end
    - datetime  -- Start time formatted according to ``churchtools.templates.dateformat``
    - video_link  -- Link to the YouTube video
    - video_link_quoted -- Link to the YouTube video quoted with ``urllib.parse.quote``
    
    It is recommended to use the `Timed Content <https://wordpress.org/plugins/timed-content/>`__ plugin
    or something similar to select when the different streams are displayed
    """
