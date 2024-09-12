from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base
from typing import List


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, unique=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    password = Column(String)
    #is_active = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    timetable = relationship("TimeTable", back_populates="owner", uselist=False)
    #session = relationship("Session", back_populates="owner", uselist=False)
    
    
class Course(Base):
    __tablename__ = "courses"
    
    code = Column(String, primary_key=True)
    name = Column(String, index=True)
    division = Column(String, index=True)
    professor = Column(String, index=True)
    schedules = Column(JSON, index=True)
    

class TimeTable(Base):
    __tablename__ = "timetables"
    
    id = Column(String, ForeignKey("users.id"), primary_key=True)
    schedules = Column(JSON, index=True)
    
    owner = relationship("User", back_populates="timetable")
    
"""
class Session(Base):
    __tablename__ = "sessions"
    
    user_id = Column(String, ForeignKey("users.id"), primary_key= True)
    session_id = Column(String, index=True)
    last_access = Column(String, index=True)
    
    owner = relationship("User", back_populates="session")
"""
    
    