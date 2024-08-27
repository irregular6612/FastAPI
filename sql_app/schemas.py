from typing import Union, List, Dict

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True



class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True



"""
class ScheduleBase(BaseModel):
    dayOfWeek : int
    time : int
    
class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    code : str
    
    # pydantic과 변환 가능
    class Config:
        orm_mdoe = True

"""

class CourseBase(BaseModel):
    code : str
    name : str
    division : Union[str, None]
    professor : Union[str, None]
    schedules : Union[List[Dict[str,str]], None] = []

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):

    class Config:
        orm_mode = True
        
 

class TimeTableBase(BaseModel):
    name : str
    schedules : dict = {}

class TimeTableCreate(TimeTableBase):
    pass

class TimeTable(TimeTableBase):

    class Config:
        orm_mode = True

class UpdateTimeTable(BaseModel):
    method : str
    stu_name : str
    name : Union[str, None]
    code : Union[str, None]
    
    class Config:
        orm_mode = True