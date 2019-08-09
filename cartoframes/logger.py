# import logging
# import sys
# import colored

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter(colored.stylize('%(asctime)s - %(levelname)s: %(message)s', colored.fg("green")))
# handler.setFormatter(formatter)

# logger.addHandler(handler)



# class Logger(logging.Logger):
#     def __init__(self):




import logging
import sys

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def get_handler(stream=sys.stderr, level=logging.DEBUG, formatter=)
