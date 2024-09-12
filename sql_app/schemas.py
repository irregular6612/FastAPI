from typing import Union, List, Dict
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    id : str

class UserCreate(UserBase):
    name : str
    password: str
    admin: bool

class User(UserBase):
    #is_active: bool = False
    #session_id : str

    class Config:
        orm_mode = True

"""
class Session(BaseModel):
    session_id: str
    last_access: str
    
    class Config:
        orm_mode = True
"""



class CourseBase(BaseModel):
    code : str
    name : str    


class CourseCreate(CourseBase):
    division : Union[str, None]
    professor : Union[str, None]
    schedules : Union[List[Dict[str,str]], None] = []
    
class Course(CourseCreate):
    
    class Config:
        orm_mode = True
        
 

class TimeTableBase(BaseModel):
    id : str = ""
    schedules : dict = {}

class TimeTableCreate(TimeTableBase):
    pass

class TimeTable(TimeTableBase):
    class Config:
        orm_mode = True

class UpdateTimeTable(BaseModel):
    method : str
    name : Union[str, None]
    code : Union[str, None]
    
    class Config:
        orm_mode = True

class SearchInfo(BaseModel):
    name : Union[str, None] | None
    code : Union[str, None] | None
    
    class Config:
        orm_mode : True

class LoginForm(BaseModel):
    id : str
    password : str
    
    class Config:
        orm_mode : True

class Token(BaseModel):
    access_token: str
    access_time: str

class TokenData(BaseModel):
    username: str

    