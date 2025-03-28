import logging
formatter = logging.Formatter('%(filename)s %(lineno)d - %(message)s')
logger = logging.getLogger('arc_tools')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
logger.propagate = False