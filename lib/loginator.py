import logging
#import bokeh

# setup logger


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class Loginator():
    """A Super smooth logging setup. smooches"""
    def __init__(self, logger, lvl='DEBUG'):
        self.levels = {
           "NOTSET": 0,
           "DEBUG": 10,
           "INFO": 20,
           "WARNING": 30,
           "ERROR": 40,
           "CRITICAL": 50
        }
        self.logger = logger
        log_format = "%(levelname)s %(asctime)s - %(message)s"
        print(f"These handlers were already configured {self.logger.handlers}")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter(log_format)
        )
        self.logger.addHandler(stream_handler)
        self.logger.level = self.levels[lvl]
        self.logger.info(f"the logger is {self.logger}")
        #print(f"the logger is: {self.logger}")

    def get_logger(self) -> logging.Logger:
        """Placeholder"""
        return self.logger

    def set_logger(self,
                   log: logging.Logger):
        """Placeholder"""
        self.logger = log
