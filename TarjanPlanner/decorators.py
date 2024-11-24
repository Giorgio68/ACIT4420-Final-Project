"""
Module containing decorators
"""


from time import time
from functools import wraps
from .logger import get_logger


def log_func_call(f):
    """
    Log a function call
    """

    @wraps(f)
    def w(*args, **kwargs):
        logger = get_logger()
        logger.info("Function %s has been called", f.__name__)

        ret = f(*args, **kwargs)

        return ret

    return w


def time_func_call(f):
    """
    Log how long a function took to execute
    """

    @wraps(f)
    def w(*args, **kwargs):
        logger = get_logger()
        start_time = time()

        ret = f(*args, **kwargs)

        end_time = time()
        logger.info(
            "Function %s took %f seconds to execute", f.__name__, end_time - start_time
        )

        return ret

    return w


_cached_calls = {}


def cache(f):
    """
    Cache a function's result. Return the cached result if the function parameters are the same
    """

    @wraps(f)
    def w(*args, **kwargs):
        global _cached_calls  # pylint: disable=global-variable-not-assigned
        logger = get_logger()
        fname = f.__name__

        if (
            fname not in _cached_calls
            or _cached_calls[fname][0] != args
            or _cached_calls[fname][1] != kwargs
        ):
            ret = f(*args, **kwargs)
            _cached_calls[fname] = [args, kwargs, ret]

            logger.info("Caching results from function %s", fname)

        else:
            ret = _cached_calls[fname][2]
            logger.info(
                "Function %s has already been called, returning cached result", fname
            )

        return ret

    return w
