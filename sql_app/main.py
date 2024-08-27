from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items



### Course-function
@app.get("/courses/", response_model=list[schemas.Course])
def read_courses(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses

@app.post("/courses/")
def read_course(course_info : schemas.Course, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_code=course_info.code)
    return course

@app.post("/course/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_code=course.code)
    if db_course:
        raise HTTPException(status_code=400, detail="Course already exist")
    return crud.create_course(db=db, course=course)

@app.delete("/course/")
def delete_course(course: dict, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_code=course["code"])
    if db_course is None:
        raise HTTPException(status_code=400, detail="Course does not exist")
    return crud.delete_course(db=db, course=db_course)

@app.put("/course/")
def update_course(course : schemas.Course, db : Session = Depends(get_db)):
    db_course = crud.get_course(db, course_code=course.code)
    if db_course is None:
        return HTTPException(status_code=400, detail="Course does not exist")
    return crud.update_course(db, course=course)
    


### Timetable-function
@app.get("/timetable/{name}")
def read_timetable(name : str, db: Session = Depends(get_db)):
    timetable = crud.get_timetable(db=db,name=name)
    return timetable

@app.post("/timetable/", response_model=schemas.TimeTable)
def create_timetable(timetable: schemas.TimeTableCreate, db: Session = Depends(get_db)):
    db_timetable = crud.get_timetable(db, name=timetable.name)
    if db_timetable:
        raise HTTPException(status_code=400, detail="Timetable already existed")
    return crud.create_timetable(db=db, timetable=timetable)

@app.put("/timetable/")
def add_course(course_info : schemas.UpdateTimeTable, db : Session = Depends(get_db)):
    db_course = crud.get_course(db, course_code=course_info.code)
    
    if not db_course:
        raise HTTPException(status_code=400, detail="Course not exist")
    if course_info.method.lower() == "add":
        return crud.add_course(db, course=db_course, stu_name=course_info.stu_name)
    elif course_info.method.lower() == "drop":
        return crud.drop_course(db, course=db_course, stu_name=course_info.stu_name)
    else:
        raise HTTPException(status_code=400, detail="Not allowed method.")



@app.delete("/timetable/")
def delete_timetable(timetable_info: dict, db: Session = Depends(get_db)):
    db_timetable = crud.get_timetable(db, name=timetable_info["name"])
    if not db_timetable:
        raise HTTPException(status_code=400, detail="Timetable does not exist")
    
    return crud.delete_timetable(db, db_timetable)
        
        
    