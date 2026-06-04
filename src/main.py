import logging

from fastapi import FastAPI

from src.api.v1 import chat
from src.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(title='IntelligentCustomerService', version='1.0.0')

app.include_router(chat.router, prefix='/api/v1')
