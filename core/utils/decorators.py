import asyncio
from logging import getLogger

logger = getLogger()


def suppress_exceptions(func):

    if asyncio.iscoroutinefunction(func):

        async def decorator(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f'Suppressed exception in {func.__name__}', exc_info=e)

    else:

        def decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'Suppressed exception in {func.__name__}', exc_info=e)

    return decorator
