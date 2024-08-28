from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base
from typing import List


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    session_id = Column(String, index=True)
    
    items = relationship("Item", back_populates="owner")
    timetable = relationship("TimeTable", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
    
class Course(Base):
    __tablename__ = "courses"
    
    code = Column(String, primary_key=True)
    name = Column(String, index=True)
    division = Column(String, index=True)
    professor = Column(String, index=True)
    schedules = Column(JSON, index=True)
    

class TimeTable(Base):
    __tablename__ = "timetables"
    
    id = Column(Integer, primary_key=True)
    schedules = Column(JSON, index=True)
    name = Column(Integer, ForeignKey("users.name"))
    
    owner = relationship("User", back_populates="timetable")