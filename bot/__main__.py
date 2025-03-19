import argparse
import traceback

import sentry_sdk

from bot.apps.apps_config import APPS
from bot.bot import MagicRustBot
from bot.config import settings
from core.utils.decorators import patch_traceback

# Патч трейсбек функций, чтобы забирать из них эксепшены и отправлять в сентри
traceback.print_exception = patch_traceback(traceback.print_exception)
traceback.print_exc = patch_traceback(traceback.print_exc)


sentry_sdk.init(settings.SENTRY_DSN)


def parse_setup_apps() -> list[str] | None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'apps',
        default=None,
        choices=APPS.keys(),
        type=str,
        nargs='*',
    )

    args = parser.parse_args()
    return args.apps


setup_apps = parse_setup_apps() or settings.SETUP_APPS
MagicRustBot(setup_apps=setup_apps).run()
