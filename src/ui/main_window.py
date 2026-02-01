from PyQt6.QtWidgets import QPlainTextEdit, QComboBox
from utils.logger import QtLogHandler, setup_volatility_logging
import logging

# Inside MainWindow.__init__
self.console = QPlainTextEdit()
self.console.setReadOnly(True)
self.console.setMaximumHeight(150)
self.console.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")

# Verbosity Selector
self.verb_box = QComboBox()
self.verb_box.addItems(["Quiet (WARNING)", "Normal (INFO)", "Verbose (DEBUG)", "Deep (TRACE)"])
self.verb_box.currentIndexChanged.connect(self.change_verbosity)

# Setup Logging
self.log_handler = QtLogHandler()
self.log_handler.new_log.connect(self.append_to_console)
self.vol_logger = setup_volatility_logging(self.log_handler)

def change_verbosity(self, index):
    levels = [logging.WARNING, logging.INFO, logging.DEBUG, 5] # 5 is Volatility's 'Trace'
    self.vol_logger.setLevel(levels[index])

def append_to_console(self, text, level):
    # Optional: Add colors based on level (Error = Red, Warning = Yellow)
    self.console.appendPlainText(text)