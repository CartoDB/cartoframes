import logging
import sys


def set_handler():
    handler = logging.StreamHandler(sys.stdout)
    # handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)


log = logging.getLogger('CARTOframes')
log.setLevel(logging.INFO)
set_handler()
