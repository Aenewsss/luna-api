from app.database.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer,primary_key=True,nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String,unique=True, nullable=False)
    phone = Column(String,unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer,primary_key=True,nullable=False, index=True)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    finished = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

class Info(Base):
    __tablename__ = "info"

    id = Column(Integer,primary_key=True,nullable=False, index=True)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))