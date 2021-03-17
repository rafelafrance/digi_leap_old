import logging
import sys
from os.path import basename, splitext


def setup_logger():
    """Setup the logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def module_name() -> str:
    """Get the current module name."""
    return splitext(basename(sys.argv[0]))[0]


def started() -> None:
    """Log the program start time."""
    setup_logger()
    logging.info('=' * 80)
    logging.info(f'{module_name()} started')


def finished() -> None:
    """Log the program end time."""
    logging.info(f'{module_name()} finished')
