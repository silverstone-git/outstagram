from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import getenv

DB_USERNAME = getenv("OUTSTAGRAM_USERNAME", "")
DB_PASSWORD = getenv("OUTSTAGRAM_PASSWORD", "")
DB_NAME = getenv("OUTSTAGRAM_DBNAME", "")

DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@localhost/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
