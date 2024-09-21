import asyncio
import sys
from functools import wraps
from logging import getLogger
from time import time

import sentry_sdk

from core.utils.exceptions import LoopUnstableException

logger = getLogger()


def suppress_exceptions(func):

    if asyncio.iscoroutinefunction(func):

        async def decorator(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                logger.error(f'Suppressed exception in {func.__name__}', exc_info=e)

    else:

        def decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sentry_sdk.capture_exception(e)
                logger.error(f'Suppressed exception in {func.__name__}', exc_info=e)

    return decorator


def loop_stability_checker(seconds: float, max_relative_deviation=0.1, is_fatal=False):
    def decorator(func):
        last_time: float | None = None

        async def wrapper(*args, **kwargs):
            nonlocal last_time
            if not last_time:
                last_time = time()
                return await func(*args, **kwargs)
            time_passed = time() - last_time
            last_time = time()
            deviation = abs(time_passed - seconds)
            if deviation / seconds > max_relative_deviation:
                if is_fatal:
                    raise LoopUnstableException(seconds, time_passed)
                logger.warning(
                    f'{func} should have been called after {seconds} seconds, but was called after {time_passed}'
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def patch_traceback(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        exception = sys.exc_info()[1]
        sentry_sdk.capture_exception(exception)
        return func(*args, **kwargs)

    return decorator
