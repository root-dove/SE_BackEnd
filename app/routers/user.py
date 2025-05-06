from fastapi import APIRouter, HTTPException
from app.database import database
from app.models import user
from pydantic import BaseModel
from typing import List
from datetime import date

from jose import jwt, JWTError
# from app.auth import verify_jwt_token

router = APIRouter()

# 요청용 스키마
class UserIn(BaseModel):
    UID: str
    NICKNAME: str
    PASSWORD: str
    EMAIL: str
    PHONE: str | None = None

# 응답용 스키마
class UserOut(UserIn):
    CREATE_DATE: date | None = None

# GET: 전체 유저 조회
@router.get("/users/", response_model=List[UserOut])
async def get_users():
    query = user.select()
    return await database.fetch_all(query)

# POST: 유저 추가
@router.post("/users/", response_model=UserOut)
async def create_user(user_data: UserIn):
    query = user.insert().values(**user_data.dict())
    await database.execute(query)
    return user_data

# GET: 특정 유저 조회
@router.get("/users/{uid}", response_model=UserOut)
async def get_user(uid: str):
    query = user.select().where(user.c.UID == uid)
    user_data = await database.fetch_one(query)
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

# PUT: 유저 정보 수정
@router.put("/users/{uid}", response_model=UserOut)
async def update_user(uid: str, user_data: UserIn, token_data: dict = Depends(verify_jwt_token)):
    # JWT 검증 및 사용자 정보 추출
    try:
        token = token_data["token"]
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id_from_token = token_data["sub"]
    query = user.update().where(user.c.UID == uid).values(**user_data.dict())
    await database.execute(query)
    return user_data