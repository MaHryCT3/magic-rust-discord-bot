import inspect
import logging
import warnings

import colorama

# Logger settings taken from vkbottle (https://github.com/vkbottle/vkbottle/blob/dev/vkbottle/modules.py)


def showwarning(message, category, filename, lineno, file=None, line=None):  # noqa: ARG001
    new_message = f'{category.__name__}: {message}'
    logger.log(
        logging.WARNING,
        new_message,
        stacklevel=4,
    )


colorama.just_fix_windows_console()
LEVEL_COLORS = {
    'DEBUG': colorama.Style.BRIGHT + colorama.Fore.BLUE,
    'INFO': colorama.Style.BRIGHT + colorama.Fore.GREEN,
    'WARNING': colorama.Fore.YELLOW,
    'ERROR': colorama.Fore.RED,
    'CRITICAL': colorama.Style.BRIGHT + colorama.Fore.RED,
}

loguru_like_format = (
    '<level>{levelname: <8}</level> <bold><level>|</level></bold> '
    '{asctime} <bold><level>|</level></bold> '
    '{module}:{funcName}:{lineno}<bold><level> > </level></bold><level>{message}</level>'
)


class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, '')
        log_format = (
            loguru_like_format.replace('<level>', color)
            .replace('</level>', colorama.Style.RESET_ALL)
            .replace('<bold>', colorama.Style.BRIGHT)
            .replace('</bold>', colorama.Style.RESET_ALL)
        )
        if not record.funcName or record.funcName == '<module>':
            record.funcName = '\b'
        frame = next(
            (frame for frame in inspect.stack() if frame.filename == record.pathname and frame.lineno == record.lineno),
            None,
        )
        if frame:
            module = inspect.getmodule(frame.frame)
            record.module = module.__name__ if module else '<module>'
        return logging.Formatter(
            log_format,
            datefmt=self.datefmt,
            style='{',
        ).format(record)


logging.basicConfig(level=logging.DEBUG)
logging.root.handlers[0].setFormatter(ColorFormatter())


class LogMessage:
    def __init__(self, fmt, args, kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.fmt.format(*self.args)


class StyleAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})

    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            if 'stacklevel' not in kwargs:
                kwargs['stacklevel'] = 2
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(level, msg, args, **kwargs)

    def process(self, msg, args, kwargs):
        log_kwargs = {key: kwargs[key] for key in inspect.getfullargspec(self.logger._log).args[1:] if key in kwargs}
        if isinstance(msg, str):
            msg = LogMessage(msg, args, kwargs)
            args = ()
        return msg, args, log_kwargs


warnings.showwarning = showwarning

logger = StyleAdapter(logging.getLogger())  # type: ignore
