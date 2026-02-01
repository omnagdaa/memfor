import hashlib
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from PyQt6.QtCore import QThread, pyqtSignal

Base = declarative_base()

class CaseModel(Base):
    __tablename__ = 'case_info'
    
    # Fixed: lowercase primary_key=True
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_name = Column(String)
    base_dir = Column(String)
    memdump_path = Column(String)
    md5 = Column(String)
    sha256 = Column(String)
    case_number = Column(String)
    examiner_name = Column(String)
    examiner_phone = Column(String)
    examiner_email = Column(String)
    organization = Column(String)
    notes = Column(Text)

class CaseDatabase:
    def __init__(self, db_path):
        # sqlite://// for absolute paths on Windows
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_case_data(self, data_dict):
        session = self.Session()
        try:
            new_case = CaseModel(**data_dict)
            session.add(new_case)
            session.commit()
        finally:
            session.close()

class HashWorker(QThread):
    hash_ready = pyqtSignal(str, str)
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        md5, sha256 = hashlib.md5(), hashlib.sha256()
        with open(self.file_path, "rb") as f:
            while chunk := f.read(1024 * 1024): # 1MB chunks
                md5.update(chunk)
                sha256.update(chunk)
        self.hash_ready.emit(md5.hexdigest(), sha256.hexdigest())