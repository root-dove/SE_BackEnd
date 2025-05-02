from fastapi import APIRouter, HTTPException
from app.database import database
from app.models import project, user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlalchemy as sa
from datetime import date

router = APIRouter()

# 요청용 스키마
class ProjectIn(BaseModel):
    P_ID: str
    P_NAME: str
    P_STATUS: str = "IN_PROGRESS"
    UID: str

# 응답용 스키마
class ProjectOut(ProjectIn):
    P_CDATE: datetime | None = None

# GET: 전체 프로젝트 조회
@router.get("/projects/", response_model=List[ProjectOut])
async def get_projects():
    query = project.select()
    return await database.fetch_all(query)

# POST: 프로젝트 생성
@router.post("/projects/", response_model=ProjectOut)
async def create_project(data: ProjectIn):
    query = project.insert().values(**data.dict())
    await database.execute(query)
    return data

# 사용자 검색 API (UID 또는 NICKNAME으로 검색) 나중에 POST로 변경하면 좋을듯
@router.get("/projects/search", response_model=List[ProjectOut])
async def search_projects_by_user(uid: Optional[str] = None, nickname: Optional[str] = None):

    query = project.select().join(user, project.c.UID == user.c.UID)

    if uid:
        query = query.where(user.c.UID == uid)
    if nickname:
        query = query.where(user.c.NICKNAME == nickname)

    return await database.fetch_all(query)
