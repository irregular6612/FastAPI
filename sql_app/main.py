from fastapi import Depends, FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union

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
        
def verify_session():
    return True


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, response : Response, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.create_user(db=db, user=user)
    response.set_cookie(key="session_id", value=db_user.session_id)
    return db_user


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

@app.post("/login/", response_model=schemas.UserBase)
def login(login_form : schemas.LoginForm, request: Request, response: Response, db: Session= Depends(get_db)):
    db_user = crud.get_user_by_name(db, login_form.name)
    
    if db_user:
        if db_user.hashed_password == login_form.password:
            response.set_cookie(key="session_id", value=crud.get_cookie(db,db_user.name))
            return db_user
        else:
            raise HTTPException(status_code=400, detail="Wrong password")
    raise HTTPException(status_code=400, detail="No account")

@app.post("/logout/", response_model=schemas.UserBase)
def logout(logout_form : schemas.LoginForm, request: Request, response: Response, db: Session= Depends(get_db)):
    db_user = crud.get_user_by_name(db, logout_form.name)
    
    if db_user:
        if db_user.session_id == request.cookies.get("session_id"):
            crud.set_cookie(db,db_user.name)
            return db_user
        raise HTTPException(status_code=400, detail="No permission")
    
    raise HTTPException(status_code=400, detail="No account")


### Course-function
# 전체 course 조회(limit = 20)
@app.get("/courses/", response_model=list[schemas.Course])
def read_courses(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses

# course 조회
@app.post("/courses/", response_model=schemas.Course)
def read_course(info : schemas.SearchInfo, request: Request, db: Session = Depends(get_db)):
    
    if info.code == None and info.name == None:
        raise HTTPException(status_code=400, detail="No query")
    elif info.code:
        course = crud.get_course(db, code=info.code)
    else:
        pass # given name
        #course = crud.get_course_by_name()
        
    if course:
        return course
    raise HTTPException(status_code=400, detail="Course does not exist")

# course 등록
@app.post("/course/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, code=course.code)
    if db_course:
        raise HTTPException(status_code=400, detail="Course already exist")
    return crud.create_course(db=db, course=course)

# course 삭제
@app.delete("/course/")
def delete_course(info: schemas.SearchInfo, db: Session = Depends(get_db)):
    if info.name == None and info.code == None:
        raise HTTPException(status_code=400, detail="No query")
    
    db_course = crud.get_course(db, course_code=info.code)
    if db_course is None:
        raise HTTPException(status_code=400, detail="Course does not exist")
    return crud.delete_course(db=db, course=db_course)

# course 수정
@app.put("/course/")
def update_course(course : schemas.SearchInfo, db : Session = Depends(get_db)):
    db_course = crud.get_course(db, course_code=course.code)
    if db_course is None:
        return HTTPException(status_code=400, detail="Course does not exist")
    return crud.update_course(db, course=course)
    
### Timetable-function
# timetable 불러오기
@app.get("/timetable/{name}", response_model=schemas.TimeTable)
def read_timetable(name : str, db: Session = Depends(get_db)):
    timetable = crud.get_timetable(db=db,name=name)
    if timetable:
        return timetable
    raise HTTPException(status_code=400, detail="No timetable")

# timetable 생성
@app.post("/timetable/", response_model = schemas.TimeTable)
def create_timetable(info: schemas.SearchInfo, request: Request, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=info.name)
    
    if not db_user is None:
        if request.cookies.get("session_id") != db_user.session_id:
            raise HTTPException(status_code=400, detail="Invalid access")
    
        db_timetable = crud.get_timetable(db, name=info.name)
    
        if db_timetable:
            raise HTTPException(status_code=400, detail="Timetable already existed")
        return crud.create_timetable(db=db, name=info.name)
    raise HTTPException(status_code=400, detail="No account")

# timetable 수정 / add, drop
@app.put("/timetable/")
def add_course(course_info : schemas.UpdateTimeTable, request: Request, db : Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=course_info.stu_name)
    
    if db_user:
        if request.cookies.get("session_id") != db_user.session_id:
            raise HTTPException(status_code=400, detail="Invalid access")
    
        db_course = crud.get_course(db, code=course_info.code)
        
        if not db_course:
            raise HTTPException(status_code=400, detail="Course not exist")
        if course_info.method.lower() == "add":
            return crud.add_course(db, course=db_course, stu_name=course_info.stu_name)
        elif course_info.method.lower() == "drop":
            return crud.drop_course(db, course=db_course, stu_name=course_info.stu_name)
        else:
            raise HTTPException(status_code=400, detail="Not allowed method.")
    
    raise HTTPException(status_code=400, detail="No account")

# timetable 삭제
@app.delete("/timetable/")
def delete_timetable(info: schemas.SearchInfo, request: Request, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=info.name)
    if db_user:
        if request.cookies.get("session_id") != db_user.session_id:
            raise HTTPException(status_code=400, detail="Invalid access")
    
        db_timetable = crud.get_timetable(db, name=info.name)
        if not db_timetable:
            raise HTTPException(status_code=400, detail="Timetable does not exist")
    
        return crud.delete_timetable(db, db_timetable)
    
    raise HTTPException(status_code=400, detail="No acount")
        
        
    