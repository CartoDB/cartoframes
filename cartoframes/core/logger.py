import sys
import logging


def init_logger():
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    return logging.getLogger('CARTOframes')


def set_log_level(level):
    """Set the level of the log in the library.

    Args:
        level (str): log level name. By default it's set to "info". Valid log levels are:
        critical, error, warning, info, debug, notset.

    """
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'notset': logging.NOTSET
    }

    if level not in levels:
        return ValueError('Wrong log level. Valid log levels are: critical, error, warning, info, debug, notset.')

    log.setLevel(levels[level])


log = init_logger()
