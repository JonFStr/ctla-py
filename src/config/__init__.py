"""
This package loads the configuration and makes it available as Config dataclass instance in the `config` module variable
"""
from loader import config

# make config elements accessible as module properties
churchtools = config.churchtools
youtube = config.youtube
wordpress = config.wordpress

del config
