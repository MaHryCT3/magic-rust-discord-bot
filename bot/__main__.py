import argparse

from bot.bot import MagicRustBot, all_apps
from bot.config import settings


def parse_setup_apps() -> list[str] | None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'apps',
        default=None,
        choices=all_apps,
        type=str,
        nargs='*',
    )

    args = parser.parse_args()
    return args.apps


setup_apps = parse_setup_apps() or settings.SETUP_APPS
MagicRustBot(setup_apps=setup_apps).run()
