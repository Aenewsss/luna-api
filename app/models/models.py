from app.database.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer,primary_key=True,nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String,unique=True, nullable=False)
    phone = Column(String,unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    infos = relationship('Info', back_populates='user')
    routines = relationship('Routine', back_populates='user')

class Info(Base):
    __tablename__ = "info"

    id = Column(Integer,primary_key=True,nullable=False, index=True)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    user = relationship("User", back_populates="infos")
    
class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer,primary_key=True,nullable=False, index=True)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    finished = Column(String,nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    user = relationship("User", back_populates="routines")