from fastapi import APIRouter, UploadFile, File

from src.utils.response import UnifiedResponse

router = APIRouter(prefix="/kb", tags=["kb"])


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    # TODO: 文档解析 + 向量化入库
    return UnifiedResponse.success(data={"doc_id": "xxx", "filename": file.filename})


@router.get("/documents")
async def list_documents():
    # TODO: 查询知识库文档列表
    return UnifiedResponse.success(data={"items": [], "total": 0})