import sys
import logging


def init_logger():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('CARTOframes')
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    return log


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
