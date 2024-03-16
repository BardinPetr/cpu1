import inspect
import logging
import os

IS_DEBUG = os.getenv("DEBUG") is not None

logging.basicConfig(
    level=logging.DEBUG,
    format="%(relativeCreated)dms [%(levelname)s] (%(module)s) %(message)s",
    force=True
)


def get_logger(name=None):
    if name is None:
        caller = inspect.stack()[1]
        name = inspect.getmodule(caller[0]).__name__

    l = logging.getLogger(name)
    if not IS_DEBUG:
        l.setLevel(logging.INFO)
    return l
