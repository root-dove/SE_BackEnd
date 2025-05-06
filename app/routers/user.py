from fastapi import APIRouter, HTTPException, Depends
from app.database import database
from app.models import user
from pydantic import BaseModel
from typing import List
from datetime import date
from app.dependencies import get_current_user
from app.auth import get_password_hash

router = APIRouter()

jwt = Depends(get_current_user)

# ✅ 요청용 스키마: 회원가입 시 클라이언트가 보내는 데이터 형식
class UserIn(BaseModel):
    UID: str                   # 사용자 ID
    NICKNAME: str             # 닉네임
    PASSWORD: str             # 평문 비밀번호 (서버에서 해시함)
    EMAIL: str                # 이메일
    PHONE: str | None = None  # 전화번호 (선택사항)

# ✅ 응답용 스키마: 사용자 정보를 반환할 때 사용되는 형식
class UserOut(UserIn):
    CREATE_DATE: date | None = None  # 가입일

# ✅ 전체 사용자 조회 (관리자 기능 또는 인증 사용자만 접근)
@router.get("/users/", response_model=List[UserOut])
async def get_users(current_user: dict = Depends(get_current_user)):
    """
    모든 사용자 정보를 조회합니다. (JWT 인증 필요)
    """
    query = user.select()
    return await database.fetch_all(query)

# ✅ 회원가입 (비인증 사용자도 가능해야 하므로 JWT 필요 없음)
@router.post("/users/", response_model=UserOut)
async def create_user(user_data: UserIn):
    """
    새 사용자를 등록합니다. 비밀번호는 서버에서 해시되어 저장됩니다.
    JWT 인증 불필요한 공개 API입니다.
    """
    # 비밀번호 해시 처리
    hashed_password = get_password_hash(user_data.PASSWORD)
    new_user = user_data.dict()
    new_user["PASSWORD"] = hashed_password

    # DB 삽입 쿼리 실행
    query = user.insert().values(**new_user)
    await database.execute(query)

    # 평문 비밀번호는 응답에 포함시키지 않음
    return user_data

# ✅ 현재 로그인한 사용자 정보 반환 (JWT 토큰 필수)
@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    로그인한 사용자의 UID와 닉네임을 반환합니다.
    Authorization 헤더에 Bearer 토큰이 필요합니다.
    """
    return {"user": current_user}