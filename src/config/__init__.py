"""
This package loads the configuration and makes it available as Config dataclass instance in the `config` module variable
"""
from . import loader

# make config elements accessible as module properties
churchtools = loader.config.churchtools
youtube = loader.config.youtube
wordpress = loader.config.wordpress

del loader.config
