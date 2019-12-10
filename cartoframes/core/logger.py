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


def log_debug():
    log.setLevel(logging.DEBUG)


def log_info():
    log.setLevel(logging.INFO)


log = init_logger()
