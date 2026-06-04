from fastapi import APIRouter

from src.utils.response import UnifiedResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register():
    # TODO: 用户注册
    return UnifiedResponse.success(data={"user_id": "xxx"})


@router.post("/login")
async def login():
    # TODO: JWT登录
    return UnifiedResponse.success(data={"token": "xxx"})
