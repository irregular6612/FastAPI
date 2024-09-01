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
    id : str

class UserCreate(UserBase):
    name : str
    password: str

class User(UserBase):
    is_active: bool = False
    items: list[Item] = []
    session_id : str

    class Config:
        orm_mode = True

class Session(BaseModel):
    session_id: str
    last_access: str
    
    class Config:
        orm_mode = True



class CourseBase(BaseModel):
    code : str
    name : str    

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    division : Union[str, None]
    professor : Union[str, None]
    schedules : Union[List[Dict[str,str]], None] = []
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
    name : Union[str, None]
    code : Union[str, None]
    
    class Config:
        orm_mode : True

class LoginForm(BaseModel):
    id : str
    password : str
    
    class Config:
        orm_mode : True
    
    