import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.api.v1 import auth, chat, knowledgebase
from src.utils.response import UnifiedResponse
from src.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动中...")
    yield
    logger.info("应用关闭中...")


app: FastAPI = FastAPI(
    title='IntelligentCustomerService',
    version='1.0.0',
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
  )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("未捕获异常")
    return UnifiedResponse(
        data=None,
        code=500,
        message="服务器内部错误",
        status_code=500,
    )


app.include_router(auth.router, prefix='/api/v1')
app.include_router(chat.router, prefix='/api/v1')
app.include_router(knowledgebase.router, prefix='/api/v1')


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)