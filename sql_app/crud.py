from sqlalchemy.orm import Session
from typing import Union
from . import models, schemas
import copy
import random
import string

def create_cookie():
    source = string.ascii_letters + string.digits
    result = ''.join((random.choice(source) for i in range(10)))
    return result
    

def get_user_by_id(db: Session, id: str):
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_name(db: Session, name : str):
    return db.query(models.User).filter(models.User.name == name).first()

"""
def get_session_by_session_id(db: Session, session_id: str):
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()

def get_cookie(db: Session, id: str):
    db_user = get_user_by_id(db, id = id)
    return db_user.session.session_id

def set_cookie(db: Session, session: schemas.Session, last_access: str):
    session.session_id = create_cookie()
    session.last_access = last_access
    
    db.commit()
    db.refresh(session)
    return session.session_id
 
def create_session(db: Session, user_id: str, last_access: str):
    db_session = models.Session(user_id = user_id, session_id= create_cookie(), last_access= last_access)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session
"""


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password
    db_user = models.User(email=user.email, password=fake_hashed_password, name=user.name, id = user.id, admin=user.admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def user_activate(db: Session, user: schemas.User):
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

def user_deactivate(db: Session, user: schemas.User):
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def get_course(db : Session, code : str):
    return db.query(models.Course).filter(models.Course.code == code).first()

def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Course).offset(skip).limit(limit).all()

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(code = course.code, 
                              name = course.name, 
                              division = course.division, 
                              professor = course.professor,
                              schedules = course.schedules
                              )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def delete_course(db: Session, course : schemas.Course):
    db.delete(course)
    db.commit()
    return course

def update_course(db : Session, course : schemas.Course):
    db_course = db.query(models.Course).filter(models.Course.code == course.code).first()
    
    if course.name != None : db_course.name = course.name
    if course.division != None : db_course.division = course.division
    if course.professor != None : db_course.professor = course.professor
    if course.schedules != None : db_course.schedules = course.schedules
    
    db.commit()
    db.refresh(db_course)
    return db_course
    

def get_timetable(db: Session, id : str):
    return db.query(models.TimeTable).filter(models.TimeTable.id == id).first()
    
def create_timetable(db: Session, id: str):
    sample_schedules = {"Mon":["", "", "", "", ""],
                                  "Tue":["", "", "", "", ""],
                                  "Wed":["", "", "", "", ""],
                                  "Thu":["", "", "", "", ""],
                                  "Fri":["", "", "", "", ""]
                                }
    
    db_timetable = models.TimeTable(id= id, schedules = sample_schedules)
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable

def delete_timetable(db: Session, timetable: schemas.TimeTable):
    db.delete(timetable)
    db.commit()
    return timetable

def add_course(db: Session, course : schemas.Course, user: schemas.User):
    
    db_timetable = user.timetable
    new_timetable = copy.deepcopy(db_timetable)
        
    #check part
    # time : {"day" : str, "time" : str}
    for time in course.schedules:
        
        period = -1
        tilde_idx =  time["time"].find("~")
        if int(time["time"][:tilde_idx]) >= 900 and int(time["time"][tilde_idx+1:]) <= 1030: period = 0
        if int(time["time"][:tilde_idx]) >= 1030 and int(time["time"][tilde_idx+1:]) <= 1200: period = 1
        if int(time["time"][:tilde_idx]) >= 1300 and int(time["time"][tilde_idx+1:]) <= 1430: period = 2
        if int(time["time"][:tilde_idx]) >= 1430 and int(time["time"][tilde_idx+1:]) <= 1600: period = 3
        if int(time["time"][:tilde_idx]) >= 1600 and int(time["time"][tilde_idx+1:]) <= 1730: period = 4
        
        #db_timetables.schedules : {"Mon" : List, "Tue" : List, ...}
        if db_timetable.schedules[time["day"]][period] != "":
            return {"status" : False, "msg" : "Course are already at the time."}
        
        if period != -1:
            new_timetable.schedules[time["day"]][period] = course.name + " (" + time["time"] + ")"
        
    db_timetable.schedules = new_timetable.schedules
    
    db.commit()
    db.refresh(db_timetable)
    return {"status" : True, "table" : db_timetable.schedules}

def drop_course(db: Session, course : schemas.Course, user: schemas.User):
    
    db_timetable = user.timetable
    new_timetable = copy.deepcopy(db_timetable)
    
    alreadyTaken = False
    
    #check part
    # time : {"day" : str, "time" : str}
    for time in course.schedules:
        for idx, current_course in enumerate(new_timetable.schedules[time["day"]]):
            if course.name in current_course:
                alreadyTaken = True
                new_timetable.schedules[time["day"]][idx] = ""
    
    if alreadyTaken == False:
        return {"status" : False, "msg" : "You didn't take this course."}

    db_timetable.schedules = new_timetable.schedules
    
    db.commit()
    db.refresh(db_timetable)
    return {"status" : True, "table" : db_timetable.schedules}