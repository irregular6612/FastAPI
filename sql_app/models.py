from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base
from typing import List


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


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
    
    #times = relationship("Schedule", back_populates="owner")
    

class TimeTable(Base):
    __tablename__ = "timetables"
    
    name = Column(String, primary_key=True)
    schedules = Column(JSON, index=True)
    
    #times = relationship("Schedule", back_populates="owner")

    
"""
class Schedule(Base):
    __tablename__ = "schedules"
    
    dayOfWeek = Column(Integer, primary_key=True)
    # 0900-1030 :1, 1030-1200 : 2, 1300-1430 : 3, 1430-1600 : 4, 1600-1730 : 5
    time = Column(Integer, index=True)
    code = Column(String, ForeignKey("courses.code"))
    
    owner = relationship("Course", back_populates="times")
"""

    
    