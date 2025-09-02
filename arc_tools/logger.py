import logging
import os
formatter = logging.Formatter('%(levelname)s: %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger('arc_tools')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
DEBUG = os.environ.get('DEBUG', '0') == '1'
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
logger.propagate = False