from fastapi import APIRouter

from src.core.response import UnifiedResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    return UnifiedResponse.success(data={"status": "ok"})