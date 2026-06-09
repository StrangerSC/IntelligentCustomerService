from fastapi import APIRouter

from src.core.response import UnifiedResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/transfer")
async def transfer_to_agent():
    # TODO: 转人工客服
    return UnifiedResponse.success(data={"agent_session_id": "xxx"})


@router.get("/sessions")
async def list_agent_sessions():
    # TODO: 客服工作台：待接入列表
    return UnifiedResponse.success(data={"items": []})
