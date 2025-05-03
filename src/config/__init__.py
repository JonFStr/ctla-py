"""
This package loads the configuration and makes it available as Config dataclass instance in the `config` module variable
"""
from . import loader

# make config elements accessible as module properties
(churchtools, youtube, wordpress) = loader.load_config()
