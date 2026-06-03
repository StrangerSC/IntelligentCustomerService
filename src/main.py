import logging
from fastapi import FastAPI
from src.api.v1 import chat

app = FastAPI(title="IntelligentCustomerService", version="1.0.0")

app.include_router(chat.router, prefix="/api/v1")
