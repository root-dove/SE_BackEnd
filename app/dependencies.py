from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "UID": payload["sub"],
        "NICKNAME": payload.get("nickname")
    }
