import logging
from PyQt6.QtCore import QObject, pyqtSignal

class QtLogHandler(logging.Handler, QObject):
    # Signal to send log messages to the UI thread safely
    new_log = pyqtSignal(str, int) 

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        # Emit the message and its level (so we can colorize it in UI)
        self.new_log.emit(msg, record.levelno)

def setup_volatility_logging(handler):
    """Connects Volatility 3's internal loggers to our Qt Handler"""
    logger = logging.getLogger("volatility3")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO) # Default level
    return logger