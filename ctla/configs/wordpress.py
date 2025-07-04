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
    
    (set from the `Application Password <https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/>`__)
    """
    days_to_show_in_advance: int
    """How many days in advance a stream should be displayed"""
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
    content_templates: dict[str, str]
    """
    Dictionary of content templates. Mapped to different pages via the :py:attr:`pages` dictionary
    
    Substitution variables can be specified in a manner consistent with
    `string.Template <https://docs.python.org/3/library/string.html#string.Template>`__.
    
    Available variables are:
    
    - title
    - pre_timestamp
    - start_timestamp
    - end_timestamp
    - datetime
    - video_link
    """
    datetime_format: str
    """
    Format string for the ``datetime`` variable in :py:attr:`content_templates`.
    
    Must be compatible with ``datetime.datetime.strptime()``
    """
