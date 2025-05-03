"""
Parse CLI arguments and hold them accessible for the application
"""
from argparse import ArgumentParser, Namespace, FileType

# parsed arguments
parsed: Namespace


def _setup_parser() -> ArgumentParser:
    """
    Set up the ArgumentParser with all supported parameters and respective descriptions
    :return: The created ArgumentParser
    """
    parser = ArgumentParser(
        description='This program scrapes a ChurchTools instance and automatically creates YouTube streams for future '
                    'events.'
    )
    parser.add_argument(
        '-c', '--config',
        type=FileType('r', encoding='utf-8'),
        default='ctla_config.json',
        help='Path to the config file. Defaults to searching for "ctla_config.json" in the current working directory.'
    )
    return parser


def parse():
    """
    Parse the given CLI parameters and store them in the file-level variable `parsed`
    """
    global parsed

    parser = _setup_parser()
    parsed = parser.parse_args()
