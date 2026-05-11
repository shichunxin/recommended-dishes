from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from models.base import Base
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        db_url = f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB}"
        self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info("Database connection initialized")
    
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
    
    def get_session(self) -> Session:
        return self.Session()

db = Database()