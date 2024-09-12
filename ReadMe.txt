# FastAPI Server : sql_app/main.py 
# api server에 요청하는 file : tester.ipynb
# data preprocessing file : preprocessing.ipynb (api sever file에도 해당 내용 존재, 자세한 내용은 notebook file에)

# 시작할 떄
command: uvicorn sql_app.main:app --reload 

# 종료할 때:
PID를 찾아 확실히 종료해야 다음 실행 시 address 문제가 발생하지 않는다.

- PID 검색
lsof -i :portnum
portnum : 일반적으로 8000, 이 중 listen을 찾는다. 
- 프로세스 종료
kill -9 (pid)
