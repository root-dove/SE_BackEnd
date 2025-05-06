from fastapi import APIRouter, Depends
from app.database import database
from app.models import team, user, project
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app.dependencies import get_current_user
import sqlalchemy as sa

router = APIRouter()

# ✅ 요청 스키마: 클라이언트가 팀원을 추가할 때 사용하는 입력 형식
class TeamIn(BaseModel):
    ROLE: str | None = None            # 역할 (예: 팀장, 기획자 등)
    P_ID: str                          # 참여할 프로젝트 ID
    CREATE_DATE: date | None = None    # 생성일 (선택사항)

# ✅ 응답 스키마: 팀 정보를 반환할 때 사용되는 형식
class TeamOut(TeamIn):
    T_ID: int                          # 팀원 고유 ID
    U_ID: str                          # 추가된 사용자 ID 포함 (응답용)

# ✅ 전체 팀원 조회 (인증 필요 없음: 공개 정보면 허용)
@router.get("/teams/", response_model=List[TeamOut])
async def get_teams():
    query = team.select()
    return await database.fetch_all(query)

# ✅ 팀원 추가 (로그인한 사용자 본인이 추가됨)
@router.post("/teams/", response_model=TeamOut)
async def add_team_member(
    team_data: TeamIn,
    current_user: dict = Depends(get_current_user)  # JWT에서 사용자 추출
):
    # 현재 사용자 UID를 직접 주입해서 저장
    values = team_data.dict()
    values["U_ID"] = current_user["UID"]

    query = team.insert().values(**values)
    last_id = await database.execute(query)

    return {**values, "T_ID": last_id}  # 응답에 T_ID 포함해서 반환

@router.get("/teams/my", response_model=List[TeamOut])
async def get_my_teams(current_user: dict = Depends(get_current_user)):
    """
    로그인한 사용자가 속한 팀 목록을 조회합니다.
    JWT에서 UID를 추출하여 해당 사용자의 팀만 반환합니다.
    """
    uid = current_user["UID"]
    query = team.select().where(team.c.U_ID == uid)
    return await database.fetch_all(query)

# ✅ 팀 검색 API: 닉네임 또는 프로젝트 이름 기반 검색 (내부 사용자 인증 필요)
@router.get("/teams/search", response_model=List[TeamOut])
async def search_teams(
    nickname: Optional[str] = None,
    project_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user)  # JWT 검증용
):
    # 팀, 사용자, 프로젝트 테이블을 조인
    query = sa.select(team).select_from(
        team.join(user, team.c.U_ID == user.c.UID)
            .join(project, team.c.P_ID == project.c.P_ID)
    )

    # 검색 조건: 닉네임
    if nickname:
        query = query.where(user.c.NICKNAME == nickname)

    # 검색 조건: 프로젝트 이름
    if project_name:
        query = query.where(project.c.P_NAME == project_name)

    return await database.fetch_all(query)