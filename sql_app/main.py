from fastapi import Depends, FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union
import jwt
from jwt.exceptions import InvalidTokenError
import jwt
from passlib.context import CryptContext

from . import crud, models, schemas
from .database import SessionLocal, engine
import datetime

models.Base.metadata.create_all(bind=engine)
# for jwt auth 
SECRET_KEY1 = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
SECRET_KEY2 = '09d25e094faa6ca2556c818166basfsdagafgvgdfjvsdfnoue2hf8gv2v7g2vgb'
ALGORITHM = 'HS256'

# hasing pw using algorithms
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_cur_time_int():
    return int(datetime.datetime.timestamp(datetime.datetime.now()))


def verify_pw(plain_pw, hashed_pw):
    return pwd_context.verify(plain_pw, hashed_pw)

def get_pw_hash(pw):
    return pwd_context.hash(pw)

def create_token(db_user: schemas.User, min: int, current_time: int):
    #access_min = 1
    #refresh_min = 3
    headers = {"alg": "HS256",
               "type": "JWT"}
    
    payload={
        # Registered Claim
        "iss": "main.py",
        "sub": "login_access_token",
        "exp" : current_time + min * 60,
        "iat": current_time,
         
        # Private Claim
        "user_name" : db_user.name,
        "user_id": db_user.id,
        "isAdmin": db_user.admin
        }
        
    
    encoded = jwt.encode(payload=payload, key=SECRET_KEY1, algorithm = ALGORITHM, headers=headers)
    return encoded

def verify_token(access_token: str, refresh_token: str):
        
    try:
        try:
            # verify access_token
            payload = jwt.decode(access_token, algorithms=ALGORITHM, key=SECRET_KEY1)
        
        except:
            # verify refresh_token
            payload = jwt.decode(refresh_token, algorithms=ALGORITHM, key=SECRET_KEY2)
   
        return {"payload" : payload, "status" : True, "required_update" : (True, False)}
    # tokens are wrong.
    except:
        return {"status" : False, "required_update" : (True, True)}
    

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
def get_current_timestr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_expired_timestr():
    refresh_min = 5
    return (datetime.datetime.now() + datetime.timedelta(minutes=refresh_min)).strftime('%Y-%m-%d %H:%M:%S')
"""

        
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/users/", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, response : Response, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    #hash the pw
    user.password = get_pw_hash(user.password)
    db_user = crud.create_user(db=db, user=user)

    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db=db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login/", response_model=schemas.UserBase)
def login(login_form : schemas.LoginForm, request: Request, response: Response, db: Session= Depends(get_db)):
    db_user = crud.get_user_by_id(db, login_form.id)
    
    if db_user:
        if verify_pw(login_form.password, db_user.password):
    
            current_time = get_cur_time_int()
            access_token = create_token(db_user=db_user, min=1,current_time=current_time)
            refresh_token = create_token(db_user=db_user, min=3,current_time=current_time)
            
            response.set_cookie(key="access_token", value=access_token)
            response.set_cookie(key="refresh_token", value=refresh_token)
            
            #crud.user_activate(db=db, user=db_user)
            return db_user
        else:
            raise HTTPException(status_code=400, detail="Wrong password")
    raise HTTPException(status_code=400, detail="No account")


@app.get("/logout/")
def logout(request: Request, response: Response, db: Session= Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    payload = verify_token(access_token, refresh_token)
    
    # valid access, access_token is expired or not.
    if payload["status"]:
        db_user = crud.get_user_by_id(db, id= payload['payload']['user_id'])
        
        if not payload["required_update"][0]:
            access_token = create_token(db_user=db_user, min=1, current_time= get_cur_time_int())
        
        response.set_cookie(key="access_token", value=access_token)
        response.set_cookie(key="refresh_token", value=refresh_token)
        return {"msg": f"Goodbye. {db_user.name}"}
    
    raise HTTPException(status_code=400, detail="No permission")


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
def create_course(request: Request, response: Response, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    payload = verify_token(access_token, refresh_token)
    
    # valid token -> user or admin
    if payload["status"]:
        db_user = crud.get_user_by_id(db, id= payload['payload']['user_id'])        
        if payload["required_update"][0] == True:
            access_token = create_token(db_user=db_user, min=1, current_time=get_cur_time_int())
        
        # user account
        if not db_user.admin:
            raise HTTPException(status_code=400, detail="No permission")
    
        db_course = crud.get_course(db, code=course.code)
        
        # course is already
        if db_course:
            raise HTTPException(status_code=400, detail="Course already exist")
        return crud.create_course(db=db, course=course)
    raise HTTPException(status_code=400, detail="Not allowed access.")

# course 삭제
@app.delete("/course/")
def delete_course(request: Request, response: Response, info: schemas.SearchInfo, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    payload = verify_token(access_token, refresh_token)
    
    #user or admin
    if payload["status"]:
        db_user = crud.get_user_by_id(db, id= payload['payload']['user_id'])        
        if payload["required_update"][0] == True:
            access_token = create_token(db_user=db_user, min=1, current_time=get_cur_time_int())
                    
        if not db_user.admin:
            raise HTTPException(status_code=400, detail="No permission")
        
        if info.name == None and info.code == None:
            raise HTTPException(status_code=400, detail="No query")
    
        db_course = crud.get_course(db, code=info.code)
        if db_course is None:
            raise HTTPException(status_code=400, detail="Course does not exist")
        return crud.delete_course(db=db, course=db_course)
    raise HTTPException(status_code=400, detail="Not allowed access")

# course 수정
@app.put("/course/")
def update_course(request: Request, response: Response, course : schemas.Course, db : Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    payload = verify_token(access_token, refresh_token)
    
    #admin or user    
    if payload["status"]:
        # if not admin account
        db_user = crud.get_user_by_id(db, id= payload['payload']['user_id'])        
        if payload["required_update"][0] == True:
            access_token = create_token(db_user=db_user, min=1, current_time=get_cur_time_int())

        if not db_user.admin:
            raise HTTPException(status_code=400, detail="No permission")
        
        db_course = crud.get_course(db, code=course.code)
        if db_course is None:
            raise HTTPException(status_code=400, detail="Course does not exist")
        return crud.update_course(db, course=course)
    
    raise HTTPException(status_code=400, detail="Not allowed access.")
    
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
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    payload = verify_token(access_token, refresh_token)
    
    if payload["status"]:
        db_user = crud.get_user_by_id(db, id= payload['payload']['user_id'])        
        if payload["required_update"][0] == True:
            access_token = create_token(db_user=db_user, min=1, current_time=get_cur_time_int())
        
        response.set_cookie(key="access_token", value=access_token)
        response.set_cookie(key="refresh_token", value=refresh_token)
        
        # is timetable already exists, 
        if db_user.timetable:
            raise HTTPException(status_code=400, detail="Timetable already existed")
        
        timetable = crud.create_timetable(db=db, id=db_user.id)
        return timetable
        
    raise HTTPException(status_code=400, detail="No permission to access")


# timetable 수정 / add, drop
@app.put("/timetable/")
def add_course(course_info : schemas.UpdateTimeTable, request: Request, response: Response, db : Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    payload = verify_token(access_token, refresh_token)
    
    # can decode the jwt
    if payload["status"]:
        db_user = crud.get_user_by_id(db, id= payload['payload']['user_id']) 
        if payload["required_update"][0] == True:
            access_token = create_token(db_user=db_user, min=1, current_time=get_cur_time_int())
        
        # input has valid course_info
        db_course = crud.get_course(db, code=course_info.code)
        
        if not db_course:
            raise HTTPException(status_code=400, detail="Course not exist")
        
        # add the course
        if course_info.method.lower() == "add":
            timetable = crud.add_course(db, course=db_course, user= db_user)
            response.set_cookie(key="access_token", value=access_token)
            response.set_cookie(key="refresh_token", value=refresh_token)
            return timetable
        
        # drop the course
        elif course_info.method.lower() == "drop":
            timetable = crud.drop_course(db, course=db_course, user=db_user)
            response.set_cookie(key="access_token", value=access_token)
            response.set_cookie(key="refresh_token", value=refresh_token)
            return timetable
        
    raise HTTPException(status_code=400, detail="No permission to access")
    
# timetable 삭제
@app.delete("/timetable/")
def delete_timetable(request: Request, response: Response,  db: Session = Depends(get_db)):
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get("refresh_token")
    payload = verify_token(access_token, refresh_token)
    
    if payload["status"]:
        db_user = crud.get_user_by_id(db=db, id= payload['payload']['user_id']) 
        if payload["required_update"][0] == True:
            access_token = create_token(db_user=db_user, min=1, current_time=get_cur_time_int())
               
        response.set_cookie(key="access_token", value=access_token)
        response.set_cookie(key="refresh_token", value=refresh_token)
        
        # is timetable already exists, 
        if not db_user.timetable:
            raise HTTPException(status_code=400, detail="Timetable does not exist.")
        
        timetable = crud.delete_timetable(db=db, timetable=db_user.timetable)
        return timetable
        
    raise HTTPException(status_code=400, detail="No permission to access")
