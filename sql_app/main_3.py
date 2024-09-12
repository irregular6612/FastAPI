from fastapi import Depends, FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union

from . import crud, models, schemas
from .database import SessionLocal, engine
import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_current_timestr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        
def verify_session(request_session_id: str, session: schemas.Session):
    
    refresh_min = 10
    
    current_time = datetime.datetime.now()
    last_access_time = session.last_access
    last_access_time = datetime.datetime.strptime(last_access_time,'%Y-%m-%d %H:%M:%S')
    
    time_diff = current_time - last_access_time
    
    if time_diff.seconds / 60 > refresh_min:
        return False
    return True


@app.post("/users/", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, response : Response, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.create_user(db=db, user=user)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_session = crud.create_session(db=db, user_id=db_user.id, last_access=current_time)
    response.set_cookie(key="session_id", value=db_user.session.session_id)
    return db_user


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: str, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.post("/login/", response_model=schemas.UserBase)
def login(login_form : schemas.LoginForm, request: Request, response: Response, db: Session= Depends(get_db)):
    db_user = crud.get_user_by_id(db, login_form.id)
    
    if db_user:
        if db_user.password == login_form.password:
            crud.set_cookie(db= db, session=db_user.session, last_access=get_current_timestr())
            response.set_cookie(key="session_id", value=crud.get_cookie(db,db_user.id))
            return db_user
        else:
            raise HTTPException(status_code=400, detail="Wrong password")
    raise HTTPException(status_code=400, detail="No account")

@app.get("/logout/", response_model=schemas.UserBase)
def logout(request: Request, response: Response, db: Session= Depends(get_db)):
    db_session = crud.get_session_by_session_id(db, session_id= request.cookies.get("session_id"))
    
    if db_session:
        crud.set_cookie(db= db,session= db_session, last_access=get_current_timestr())
        return db_session.owner
    raise HTTPException(status_code=400, detail="No Account")


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
@app.get("/timetable/{id}", response_model=schemas.TimeTable)
def read_timetable(id : str, db: Session = Depends(get_db)):
    timetable = crud.get_timetable(db=db,id=id)
    if timetable:
        return timetable
    raise HTTPException(status_code=400, detail="No timetable")

# timetable 생성
@app.post("/timetable/", response_model = schemas.TimeTable)
def create_timetable(request: Request, response: Response, db: Session = Depends(get_db)):
    session_id = request.cookies.get('session_id')
    db_session = crud.get_session_by_session_id(db, session_id=session_id)
    
    if verify_session(session_id, db_session) == False:
        raise HTTPException(status_code=400, detail='session expired')
    
    if db_session:
        if db_session.owner.timetable:
            raise HTTPException(status_code=400, detail="Timetable already existed")
        
        timetable = crud.create_timetable(db=db, id=db_session.owner.id)
        crud.set_cookie(db= db, session=db_session, last_access=get_current_timestr())
        response.set_cookie(key='session_id', value=db_session.session_id)
        
        return timetable
    raise HTTPException(status_code=400, detail="No account")

# timetable 수정 / add, drop
@app.put("/timetable/")
def add_course(course_info : schemas.UpdateTimeTable, request: Request, response: Response, db : Session = Depends(get_db)):
    session_id = request.cookies.get('session_id')
    db_session = crud.get_session_by_session_id(db= db, session_id=session_id)
    

    
    if db_session:
        if verify_session(session_id, db_session) == False:
            raise HTTPException(status_code=400, detail='session expired')
        db_course = crud.get_course(db, code=course_info.code)
        
        if not db_course:
            raise HTTPException(status_code=400, detail="Course not exist")
        if course_info.method.lower() == "add":
            timetable = crud.add_course(db, course=db_course, user= db_session.owner)
            crud.set_cookie(db= db, session=db_session, last_access=get_current_timestr())
            response.set_cookie(key='session_id', value=db_session.session_id)
            return timetable
        elif course_info.method.lower() == "drop":
            timetable = crud.drop_course(db, course=db_course, user=db_session.owner)
            crud.set_cookie(db= db, session=db_session, last_access=get_current_timestr())
            response.set_cookie(key='session_id', value=db_session.session_id)
            return timetable
        else:
            raise HTTPException(status_code=400, detail="Not allowed method.")
    
    raise HTTPException(status_code=400, detail="No account")

# timetable 삭제
@app.delete("/timetable/")
def delete_timetable(request: Request, response: Response,  db: Session = Depends(get_db)):
    session_id = request.cookies.get('session_id')
    db_session = crud.get_session_by_session_id(db, session_id=session_id)
    
    if verify_session(session_id, db_session) == False:
        raise HTTPException(status_code=400, detail='session expired')
    
    if db_session:
        if db_session.owner.timetable:
            timetable = crud.delete_timetable(db=db, timetable=db_session.owner.timetable)
            crud.set_cookie(db= db, session=db_session, last_access=get_current_timestr())
            response.set_cookie(key='session_id', value=db_session.session_id)
            return timetable
        raise HTTPException(status_code=400, detail="Timetable does not exist")
    
    raise HTTPException(status_code=400, detail="No acount")