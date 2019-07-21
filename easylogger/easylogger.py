import logging
import sys

import colorlog
from colorlog import escape_codes
from tqdm import tqdm

log_colors = {
    'DEBUG': 'white',
    'INFO': 'cyan',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'black,bg_green',
}


class Logger(logging.Logger):
    def __init__(self, name, log_file=None, log_level_file=logging.DEBUG, log_level_console=logging.INFO,
                 color_file=True, color_console=True):
        self.log_level_console = log_level_console
        self.log_level_file = log_level_file
        self.log_file = log_file
        self.name = name
        super(Logger, self).__init__(name)
        using_log_file = log_file is not None
        self.setLevel(log_level_file if using_log_file else log_level_console)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        colored_formatter = colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:   %(message)s',
                                                      log_colors=log_colors)
        if using_log_file:
            fh = logging.FileHandler(log_file)
            fh.setLevel(log_level_file)
            fh.setFormatter(colored_formatter if color_file else formatter)
            self.addHandler(fh)
        ch = colorlog.StreamHandler()
        ch.setLevel(log_level_console)
        ch.setFormatter(colored_formatter if color_console else formatter)
        self.addHandler(ch)

    def copy(self, new_name=None):
        if new_name is None:
            new_name = self.name
        return Logger(new_name, **self.logging_options)

    @property
    def logging_options(self):
        return dict(log_file=self.log_file, log_level_file=self.log_level_file,
                    log_level_console=self.log_level_console)


class LoggingClass(object):
    def __init__(self, name=None, log=None, **kwargs):
        self.name = name = name if name is not None else self.__class__.__name__
        if log is not None:
            self.__log = log.copy(name)
        else:
            self.__log = Logger(name, **kwargs)

    def __del__(self):
        for i in self.__log.handlers:
            i.close()

    @property
    def log(self):
        return self.__log

    def reset_log(self):
        self.__log = Logger(self.name, **self.logging_options)

    def warning(self, *args, **kwargs):
        self.__log.warning(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.__log.debug(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.__log.error(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.__log.info(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.__log.critical(*args, **kwargs)

    @staticmethod
    def tqdm(it=None, log_level=logging.DEBUG, **kwargs):
        # noinspection PyProtectedMember
        level_name = logging._levelToName[log_level]
        colors = (escape_codes[log_colors[level_name]], escape_codes["reset"])
        if "bar_format" not in kwargs:
            kwargs["bar_format"] = "{l_bar}{bar}{r_bar}"
        kwargs["bar_format"] = kwargs["bar_format"].replace("{bar}", "%s{bar}%s" % colors)
        return tqdm(it, file=sys.stdout, **kwargs)

    @property
    def logging_options(self):
        return dict(log_file=self.__log.log_file, log_level_file=self.__log.log_level_file,
                    log_level_console=self.__log.log_level_console)
