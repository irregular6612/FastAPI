from sqlalchemy.orm import Session
from typing import Union
from . import models, schemas
import copy


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


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
    

def get_timetable(db: Session, name : str):
    return db.query(models.TimeTable).filter(models.TimeTable.name == name).first()
    
def create_timetable(db: Session, name: str):
    sample_schedules = {"Mon":["", "", "", "", ""],
                                  "Tue":["", "", "", "", ""],
                                  "Wed":["", "", "", "", ""],
                                  "Thu":["", "", "", "", ""],
                                  "Fri":["", "", "", "", ""]
                                }
    
    db_timetable = models.TimeTable(name = name, schedules = sample_schedules)
    db.add(db_timetable)
    db.commit()
    db.refresh(db_timetable)
    return db_timetable

def delete_timetable(db: Session, timetable: schemas.TimeTable):
    db.delete(timetable)
    db.commit()
    return timetable

def add_course(db: Session, course : schemas.Course, stu_name: str):
    
    db_timetable = get_timetable(db, name=stu_name)
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

def drop_course(db: Session, course : schemas.Course, stu_name: str):
    
    db_timetable = get_timetable(db, name=stu_name)
    new_timetable = copy.deepcopy(db_timetable)
    
    alreadyTaken = False
    
    #check part
    # time : {"day" : str, "time" : str}
    for time in course.schedules:
        for idx, current_course in enumerate(new_timetable.schedules[time["day"]]):
            if current_course == course.name:
                alreadyTaken = True
                new_timetable.schedules[time["day"]][idx] = ""
    
    if alreadyTaken == False:
        return {"status" : False, "msg" : "You didn't take this course."}

    db_timetable.schedules = new_timetable.schedules
    
    db.commit()
    db.refresh(db_timetable)
    return {"status" : True, "table" : db_timetable.schedules}