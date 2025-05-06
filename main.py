from fastapi import FastAPI, Depends, HTTPException, Request
from app.database import database, engine  # engine은 여기서 가져와야 함
from app.models import metadata            # metadata만 models.py에서 가져오면 됨
from jose import jwt, JWTError

from app.routers import user, project, team
app = FastAPI()

SECRET_KEY = "#"
ALGORITHM = "HS256"

# JWT 검증 함수
def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # 이게 사용자 정보가 될 수 있음
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


# DB 연결
@app.on_event("startup")
async def connect_to_db():
    await database.connect()

# DB 연결 해제
@app.on_event("shutdown")
async def disconnect_from_db():
    await database.disconnect()

# 테이블 생성 (최초 1회만 실행됨)
metadata.create_all(engine)

app.include_router(user.router)
app.include_router(project.router) 
app.include_router(team.router)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI with MariaDB!"}


