import os
from PyQt6.QtCore import QThread, pyqtSignal
from volatility3.framework import contexts, automagic
from volatility3.framework.interfaces import plugins

class VolatilityWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(object)  # Sends the context back to UI
    error = pyqtSignal(str)

    def __init__(self, mem_path):
        super().__init__()
        self.mem_path = mem_path

    def run(self):
        try:
            self.status.emit("Initializing Volatility Context...")
            ctx = contexts.Context()
            
            # Set the memory image location
            base_full_path = "file://" + os.path.abspath(self.mem_path)
            ctx.config['automagic.LayerStacker.single_location'] = base_full_path
            
            self.status.emit("Identifying OS & Scanning Banners...")
            
            # Run automagic (This is what detects the OS/Profiles)
            automagics = automagic.available(ctx)
            automagic.run(automagics, ctx, None, self.progress_callback)
            
            self.finished.emit(ctx)
        except Exception as e:
            self.error.emit(str(e))

    def progress_callback(self, percent, message):
        """Called by Volatility framework during analysis"""
        self.progress.emit(int(percent))
        if message:
            self.status.emit(message)