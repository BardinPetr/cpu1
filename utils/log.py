import logging
import os

IS_DEBUG = True
# IS_DEBUG = os.getenv("DEBUG") is not None

logging.basicConfig(
    level=logging.DEBUG,
    format="%(relativeCreated)dms [%(levelname)s] (%(module)s) %(message)s",
    force=True
)


def get_logger(name=None):
    l = logging.getLogger(name)
    if not IS_DEBUG:
        l.setLevel(logging.INFO)
    return l
