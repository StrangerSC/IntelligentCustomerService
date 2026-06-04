from fastapi import APIRouter

from src.utils.response import UnifiedResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions")
async def chat_completions():
  # TODO: 接入RAG引擎 + LLM
  return UnifiedResponse.success(data={"answer": "占位回答", "session_id": "xxx", "sources": []})


@router.get("/history/{session_id}")
async def chat_history(session_id: str):
  # TODO: 查询对话历史
  return UnifiedResponse.success(data={"session_id": session_id, "messages": []})
