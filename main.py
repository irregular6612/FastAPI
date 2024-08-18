from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

##preprocessing

class Lecture(BaseModel):
    division : str
    code : str
    name : str
    professor : str
    time : tuple
    
DB_path = "./datasets/GIST24-2.csv"
DB = []

def preprocessing():

    #get info of courses / data-type : pandas.DataFrame
    data = pd.read_csv(DB_path)

    #remove useless data columns
    data = data.drop(['NO','세부분류','강/실/학','과정\n구분','강의실','강의\n계획서','강의언어','설명\n영상','이수구분','교과연구','수강\n정원'], axis=1)

    #change data types object -> str
    data.astype('str')


    #fill unexpexted value such like nan, None to ""(default string)
    data['담당교수'] = data['담당교수'].fillna("")
    data['시간표'] = data['시간표'].fillna("")

    #change data-type pandas.DataFrame -> list of list
    data = data.values
    
    for lec in data:
        
        #요일
        day = [False, False, False, False, False]
        #시간대
        timePeriod = [False, False, False, False, False, False]
    
        if "월" in lec[4]:
            day[0] = True
        if "화" in lec[4]:
            day[1] = True
        if "수" in lec[4]:
            day[2] = True
        if "목" in lec[4]:
            day[3] = True
        if "금" in lec[4]:
            day[4] = True
    
        if "09:00~10:30" in lec[4]:
            timePeriod[0] = True
        if "10:30~12:00" in lec[4]:
            timePeriod[1] = True
        if "13:00~14:30" in lec[4]:
            timePeriod[3] = True
        if "14:30~16:00" in lec[4]:
            timePeriod[4] = True
        if "16:00~17:30" in lec[4]:
            timePeriod[5] = True
        
        lecture = Lecture(division=lec[0], code=lec[1], name=lec[2], professor=lec[3], time=tuple((day, timePeriod)))
        DB.append(lecture)
preprocessing()


## Lecture search
def serachLecture(data : dict):
    
    # code only input -> return single or multi element arrays
    # code and name input -> return single or multi element arrays 
    
    code = data['code'] # str
    name = data['name'] # str or None
    
    isReady = False
    target_list = []
    
    for index, lec in enumerate(DB):
        if code in lec.code:
            isReady = True
            target_list.append({'index' : index, 'lec' : lec})
    
    if isReady is False:
        return {'isExist' : False}
    else:
        if name == None:
            return {'isExist' : True, 'courses' : target_list}
        else:
            for lec in target_list:
                if data['name'] in lec['lec'].name:
                    return {'isExist' : True, 'courses' : [lec['lec']]}
            
            return {'isExist' : True, 'courses' : target_list}
                    

def all_lecture():
    return DB
#timetable
'''
시간표 정리 할 때 복잡한 시간은 고려하지 않음. 3학점에 레시 없는 일반적인 수업 시간의 기준으로 데이터 구성.
정규 시간이 아닌 예체능 과목이나, 주 1회 수업, 혹은 1시간 반 수업이 아닌 경우에 대한 처리는 하지 않음.
'''

class TimeTable(BaseModel):
    data : List
    
period1 = ['0900-1030','', '', '', '','' ]
period2 = ['1030-1200','', '', '', '', '']
lunch = ['Lunch','','','','','']
period3 = ['1300-1430', '', '', '', '', '']
period4 =['1430-1600', '', '', '', '', '']
period5 = ['1600-1730', '', '', '', '', '']

timeTable = [period1, period2, lunch, period3, period4, period5]


def addCourse(course : dict):
    day, time = course.time
    course_days = list(filter(lambda x : day[x] == True, range(len(day))))
    course_times = list(filter(lambda x : time[x] == True, range(len(time))))
    
    isReady = False
    
    for course_time in course_times:
        for course_day in course_days:
            if timeTable[course_time][course_day + 1] != '':
                isReady = True
                break
    
    if isReady == True:
        return False
    
    for course_time in course_times:
        for course_day in course_days:    
            timeTable[course_time][course_day + 1] = course.name
    
    return True

def removeCourse(course : Lecture):
    name = course.name
    success = True
    
    for period_cnt, period in enumerate(timeTable):
        for day, lec in enumerate(period):
            if lec == name:
                timeTable[period_cnt][day] = ''
    
    return success
            

#app
app = FastAPI()

# Retrieve - get
@app.get("/")
def read_root():
    return {"Hello" : "World!"}


#Courses api
@app.get('/course-search/{lecture_code}')
def getLecture(lecture_code : str):
    return serachLecture({"code" : lecture_code, "name" : None})

@app.get("/course-all")
def getAllLecture():
    return all_lecture()

# Create - post
@app.post("/course-add")
def updateCourse(lecture : dict):
    before_lectures = len(DB)
    new_lecture = Lecture(division=lecture['division'], code=lecture['code'], name=lecture['name'],
                          professor=lecture['professor'], time=lecture['time'])
    DB.append(new_lecture)
    after_lectures = len(DB)
    return {'status' : True, 'before_cnt' : before_lectures, 'after_cnt' : after_lectures}

# Delete - delete
@app.delete("/course-remove")
def updateCourse(data : dict):
    lec_cnt = len(DB)
    lec = serachLecture({"code" : data['code'], "name" : data['name']})
    
    if lec['isExist'] == True:
        if len(lec['courses']) == 1:
            DB.remove(lec['courses'][0])
            return {'success' : True, 'before_lec' : lec_cnt, 'current_len' : len(DB) }
        
        elif data['name'] != None:
            for lec_item in lec['courses']:
                if data['name'] in lec_item.name:
                    DB.remove(lec_item)
                    return {'success' : True, 'before_lec' : lec_cnt, 'current_len' : len(DB) }
                
            return {'success' : False, 'before_lec' : lec_cnt, 'current_len' : len(DB) }
        
        return {'success' : False, 'before_lec' : lec_cnt, 'current_len' : len(DB) }
    else:
        return {'success' : False, 'before_lec' : lec_cnt, 'current_len' : len(DB) }

# Update - put
@app.put("/course-update")
def updateCourse(data : dict):
    lec = serachLecture({"code" : data['code'], "name" : data['name']})
    
    if lec['isExist'] == False:
        return {'success' : False, 'msg' : "does not exist."}
    
    if len(lec['courses']) == 1:
        new_lecture = Lecture(division=data['division'], code=data['code'], name=data['name'],
                          professor=data['professor'], time=data['time'])
        DB[lec['courses'][0]['index']] = new_lecture
        return {'success' : True, 'index' : lec['courses'][0]['index']}    
    
    else:
        return {'success' : False, 'msg' : "pass the course name name exactly"}
    
    


# timatable api
@app.get("/timetable", response_model=TimeTable)
async def getTimeTeble():
    return TimeTable(data=timeTable)

@app.put("/timetable/add")
def addTimeTable(data : dict):
    success = True
    
    code = data['code']
    name = data['name']
    response = serachLecture({"code" : code, "name" : name})
    if response['isExist'] == False:
        return {'success' : False, "msg" : "No Courses."}
    elif len(response['courses']) == 1:
        success = addCourse(response['courses'][0])
    else:
        courses = response['courses']
        for course in courses:
            if name in course['lec'].name:
                success = addCourse(course)
                break
    
    return {"success" : success, "timetable" : timeTable}

@app.delete("/timetable/remove")
def removeTimeTable(data : dict):
    success = True
    
    code = data['code']
    name = data['name']
    response = serachLecture({"code" : code, "name" : name})
    
    if response['isExist'] == False:
        return {'success' : False, "msg" : "No Courses."}
    elif len(response['courses']) == 1:
        success = removeCourse(response['courses'][0])
    else:
        courses = response['courses']
        for course in courses:
            if name in course['lec'].name:
                success = removeCourse(course)
                break
    
    return {"success" : success, "timetable" : timeTable}