import sys
import logging


def init_logger(formatter):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(formatter))
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler])
    return handler, logging.getLogger('CARTOframes')


handler, log = init_logger('%(message)s')


def set_log_level(level):
    """Set the level of the log in the library.

    Args:
        level (str): log level name. By default it's set to "info". Valid log levels are:
        "critical", "error", "warning", "info", "debug", "notset".

    """
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'notset': logging.NOTSET
    }

    level = level.lower()
    if level not in levels:
        return ValueError('Wrong log level. Valid log levels are: critical, error, warning, info, debug, notset.')

    level = levels[level]

    if level == logging.DEBUG:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    else:
        handler.setFormatter(logging.Formatter('%(message)s'))

    log.setLevel(level)
