# backend/app/routers/documents.py

import os
from pathlib import Path
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.app.services.history_service import log_history

# 定义表现给前端的文档模型
class Document(BaseModel):
    filename: str
    size: int
    upload_time: str

# 使用本地路径
ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "backend" / "data" / "public" / "documents"
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=List[Document])
async def list_documents():
    """列出所有文档（前端页面用来渲染列表）"""
    docs = []
    for fname in os.listdir(DATA_DIR):
        fpath = DATA_DIR / fname
        if not fpath.is_file():
            continue
        stat = fpath.stat()
        docs.append(Document(
            filename=fname,
            size=stat.st_size,
            upload_time=datetime.fromtimestamp(stat.st_mtime).isoformat()
        ))
    return docs


@router.get("/download", summary="通过 ?filename= 下载文档")
async def download_document(
    filename: str = Query(..., description="文件名，会自动解码")
):
    """
    下载指定文件（查询参数方式，支持中文/空格/引号）。
    先确认文件存在，再记录到历史，最后返回 FileResponse。
    """
    file_path = DATA_DIR / filename

    # 1. 先检查文件是否存在
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在或已移除")

    # 2. 记录历史（日志出错不影响下载）
    try:
        await log_history(
            type="document",
            title="文档下载",
            description=f"下载文件：{filename}",
            user="测试管理员",
            status="success",
            details={"fileSize": f"{file_path.stat().st_size} bytes"}
        )
    except Exception:
        # 如果日志写入失败，吞掉异常，仅打印
        import logging
        logging.getLogger(__name__).exception("记录下载历史失败")

    # 3. 返回文件流
    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        filename=filename
    )
