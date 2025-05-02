from fastapi import APIRouter
from app.database import database
from app.models import team, user, project
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import sqlalchemy as sa

router = APIRouter()

# 요청 스키마
class TeamIn(BaseModel):
    ROLE: str | None = None
    U_ID: str
    P_ID: str
    CREATE_DATE: date | None = None

# 응답 스키마
class TeamOut(TeamIn):
    T_ID: int

# 팀원 전체 조회
@router.get("/teams/", response_model=List[TeamOut])
async def get_teams():
    query = team.select()
    return await database.fetch_all(query)

# 팀원 추가
@router.post("/teams/", response_model=TeamOut)
async def add_team_member(team_data: TeamIn):
    query = team.insert().values(**team_data.dict())
    last_id = await database.execute(query)
    return {**team_data.dict(), "T_ID": last_id}

# 팀원 검색 API (UID 또는 NICKNAME으로 검색)
# 나중에 POST로 변경하면 좋을듯
@router.get("/teams/search", response_model=List[TeamOut])
async def search_teams(nickname: Optional[str] = None, project_name: Optional[str] = None):
    
    query = sa.select(team).select_from(
        team.join(user, team.c.U_ID == user.c.UID)
            .join(project, team.c.P_ID == project.c.P_ID)
    )

    if nickname:
        query = query.where(user.c.NICKNAME == nickname)
    if project_name:
        query = query.where(project.c.P_NAME == project_name)

    return await database.fetch_all(query)
