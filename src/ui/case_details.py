import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QFormLayout, QPushButton, QGroupBox, 
                             QTextEdit, QStackedWidget, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from core.case_management import HashWorker

class CaseDetailsPage(QWidget):
    case_completed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.case_data = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar with fixed Dark Object Name
        self.sidebar = QFrame()
        self.sidebar.setObjectName("wizardSidebar")
        self.sidebar.setFixedWidth(200)
        
        side_layout = QVBoxLayout(self.sidebar)
        self.step_labels = [QLabel("1. Case Details"), QLabel("2. Optional Info"), QLabel("3. Evidence")]
        for lbl in self.step_labels:
            lbl.setStyleSheet("font-weight: bold; padding: 10px; color: #888;")
            side_layout.addWidget(lbl)
        side_layout.addStretch()

        self.stack = QStackedWidget()
        # Adding the steps to the stack
        self.stack.addWidget(self._step1())
        self.stack.addWidget(self._step2())
        self.stack.addWidget(self._step3())

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)
        self._set_step(0)

    def _set_step(self, index):
        self.stack.setCurrentIndex(index)
        for i, lbl in enumerate(self.step_labels):
            lbl.setStyleSheet("color: #4CAF50; font-weight: bold;" if i == index else "color: #888; font-weight: bold;")

    # STEP 1: BASIC CASE INFO
    def _step1(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Case Information")
        form = QFormLayout(group)
        
        self.case_name = QLineEdit()
        self.base_dir = QLineEdit(os.getcwd())
        
        form.addRow("Case Name:", self.case_name)
        form.addRow("Base Directory:", self.base_dir)
        
        layout.addWidget(group)
        layout.addStretch()
        
        next_btn = QPushButton("Next >")
        next_btn.clicked.connect(lambda: self._set_step(1))
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignRight)
        return page

    # STEP 2: EXAMINER & OPTIONAL INFO
    def _step2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Optional Details")
        form = QFormLayout(group)
        
        self.case_num = QLineEdit()
        self.ex_name = QLineEdit()
        self.ex_phone = QLineEdit()
        self.ex_email = QLineEdit()
        self.org = QLineEdit()
        self.notes = QTextEdit()
        
        form.addRow("Case Number:", self.case_num)
        form.addRow("Examiner Name:", self.ex_name)
        form.addRow("Examiner Phone:", self.ex_phone)
        form.addRow("Examiner Email:", self.ex_email)
        form.addRow("Organization:", self.org)
        form.addRow("Notes:", self.notes)
        
        layout.addWidget(group)
        
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("< Back")
        back_btn.clicked.connect(lambda: self._set_step(0))
        next_btn = QPushButton("Next >")
        next_btn.clicked.connect(lambda: self._set_step(2))
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)
        layout.addLayout(nav_layout)
        return page

    # STEP 3: EVIDENCE DRAG & DROP
    def _step3(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.drop_zone = QLabel("\n\n DRAG & DROP MEMORY DUMP \n .raw, .mem, .dmp \n\n")
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setStyleSheet("border: 2px dashed #4CAF50; border-radius: 10px; margin: 20px;")
        
        # Event Overrides
        self.drop_zone.dragEnterEvent = lambda e: e.accept() if e.mimeData().hasUrls() else e.ignore()
        self.drop_zone.dropEvent = self._handle_drop
        
        self.hash_info = QLabel("Hashes will appear here...")
        
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("< Back")
        back_btn.clicked.connect(lambda: self._set_step(1))
        self.finish_btn = QPushButton("Finish Case Setup")
        self.finish_btn.setEnabled(False)
        self.finish_btn.clicked.connect(self._on_finish)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.finish_btn)

        layout.addWidget(self.drop_zone)
        layout.addWidget(self.hash_info)
        layout.addLayout(nav_layout)
        return page

    def _handle_drop(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
        self.case_data['memdump_path'] = path
        self.drop_zone.setText(f"Loaded: {os.path.basename(path)}")
        worker = HashWorker(path)
        worker.hash_ready.connect(self._hashes_ready)
        worker.start()
        self._w = worker # Keep alive

    def _hashes_ready(self, md5, sha):
        self.case_data['md5'] = md5
        self.case_data['sha256'] = sha
        self.hash_info.setText(f"MD5: {md5}\nSHA256: {sha}")
        self.finish_btn.setEnabled(True)

    def _on_finish(self):
        self.case_data.update({
            "case_name": self.case_name.text(),
            "base_dir": self.base_dir.text(),
            "case_number": self.case_num.text(),
            "examiner_name": self.ex_name.text(),
            "examiner_phone": self.ex_phone.text(),
            "examiner_email": self.ex_email.text(),
            "organization": self.org.text(),
            "notes": self.notes.toPlainText()
        })
        self.case_completed.emit(self.case_data)    