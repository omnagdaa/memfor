from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal

class LandingPage(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        
        self.label = QLabel("\n\n [ Drag & Drop Memory Dump ] \n\n - or - \n")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel { 
                border: 3px dashed #555; 
                border-radius: 15px; 
                font-size: 18px; 
                color: #aaa; 
                background: #2b2b2b;
            }
        """)
        
        self.btn = QPushButton("Browse Files")
        self.btn.setFixedWidth(200)
        self.btn.clicked.connect(self.open_file_dialog)
        
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Memory Dump")
        if path: self.file_selected.emit(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files: self.file_selected.emit(files[0])