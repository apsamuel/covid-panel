import logging
#import bokeh 

# setup logger 



class Loginator():
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
