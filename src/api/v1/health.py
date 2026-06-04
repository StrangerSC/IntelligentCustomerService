from fastapi import APIRouter

from src.utils.response import UnifiedResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    return UnifiedResponse.success(data={"status": "ok"})