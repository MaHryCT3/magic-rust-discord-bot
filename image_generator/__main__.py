import sentry_sdk

from image_generator.application import start_generation
from image_generator.config import settings

sentry_sdk.init(settings.SENTRY_DSN)
start_generation()
