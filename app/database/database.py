from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import environments

engine = create_engine(environments.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    print('here 14')
    db = SessionLocal()
    print('here 16')

    try:
        yield db
    finally:
        db.close()