from fastapi import APIRouter
from app.auth import get_m2m_token

router = APIRouter()

@router.get("/token/m2m")
async def m2m_token():
    """Retrieve M2M access token."""
    token = await get_m2m_token()
    return {"access_token": token}