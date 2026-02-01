import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QStackedWidget, QStatusBar, QProgressBar, 
                             QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal


# Import your modules based on your directory structure
from ui.case_details import CaseDetailsPage # Ensure class name matches your file
from core.case_management import CaseDatabase

DARK_STYLE = """
    QMainWindow, QWidget { background-color: #121212; color: #e0e0e0; }
    #wizardSidebar { background-color: #1e1e1e; border-right: 1px solid #333; }
    QPushButton { background-color: #4CAF50; color: white; border-radius: 4px; padding: 8px; }
    QLineEdit, QTextEdit { background-color: #2b2b2b; border: 1px solid #444; color: white; }
"""

LIGHT_STYLE = """
    QMainWindow, QWidget { background-color: #ffffff; color: #000000; }
    #wizardSidebar { background-color: #f0f0f0; border-right: 1px solid #ccc; }
    QPushButton { background-color: #2196F3; color: white; }
"""


class StartScreen(QWidget):
    new_case = pyqtSignal()
    open_case = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel("memfor")
        lbl.setStyleSheet("font-size: 50px; color: #4CAF50; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(lbl)

        self.btn_new = QPushButton("New Case")
        self.btn_open = QPushButton("Open Case")
        
        for btn in [self.btn_new, self.btn_open]:
            btn.setFixedSize(280, 50)
            btn.setStyleSheet("font-size: 16px; font-weight: 500;")
            layout.addWidget(btn)

        self.btn_new.clicked.connect(self.new_case.emit)
        self.btn_open.clicked.connect(self.open_case.emit)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle("memfor - Forensic Analyzer")
        self.resize(1100, 750)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Screens
        self.start_screen = StartScreen()
        self.wizard = CaseDetailsPage() 
        
        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.wizard)

        # Signals
        self.start_screen.new_case.connect(lambda: self.stack.setCurrentIndex(1))
        self.start_screen.open_case.connect(self.open_existing_case)
        self.wizard.case_completed.connect(self.finalize_new_case)

        # Status Bar (Ghidra style)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(180)
        self.progress_bar.setVisible(False)
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def finalize_new_case(self, data):
        # Logic is now error-proof thanks to ORM
        db_path = f"{data['base_dir']}/{data['case_name']}.memfor"
        db = CaseDatabase(db_path)
        db.save_case_data(data)
        self.status_label.setText("Case Database Created Successfully")
        
        try:
            db_path = os.path.join(data['base_dir'], f"{data['case_name']}.memfor")
            db = CaseDatabase(db_path)
            db.save_case_data(data)
            
            QMessageBox.information(self, "Success", f"Case created at:\n{db_path}")
            self.load_dashboard(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create case: {e}")
        finally:
            self.progress_bar.setVisible(False)

    def open_existing_case(self):
        """Opens a file dialog to pick an existing .memfor database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Case Database", "", "MemFor Cases (*.memfor);;All Files (*)"
        )
        if file_path:
            db = CaseDatabase(file_path)
            data = db.load_last_case()
            if data:
                self.load_dashboard(data)
            else:
                QMessageBox.warning(self, "Empty Case", "This database contains no case data.")

    def load_dashboard(self, data):
        """Logic to switch to the main analysis dashboard."""
        self.status_label.setText(f"Active Case: {data['case_name']}")
        print(f"Loading UI for: {data['memdump_path']}")
        # For now, we stay on the wizard or clear the stack for a new 'Dashboard' widget
        self.status_label.setText("Ready for Analysis.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())