from fastapi import APIRouter, HTTPException, Depends
from app.database import database
from app.models import user
from pydantic import BaseModel
from typing import List
from datetime import date
from app.dependencies import get_current_user


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

@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    return {"user": current_user}