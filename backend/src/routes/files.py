"""
文件管理API
提供文件上传、下载、删除功能

作者/日期：AI / 2026-03-25
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.file_attachment import FileAttachment
from backend.src.models.user import User
from backend.src.routes.dashboard import get_current_user_simple


router = APIRouter(prefix="/api/files", tags=["文件管理"])

# 文件上传配置
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()


def get_file_type(extension: str) -> str:
    """根据扩展名获取文件类型"""
    type_map = {
        '.pdf': 'pdf',
        '.doc': 'doc',
        '.docx': 'doc',
        '.xls': 'xls',
        '.xlsx': 'xls',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
    }
    return type_map.get(extension, 'unknown')


def generate_unique_filename(original_name: str) -> str:
    """生成唯一文件名"""
    ext = get_file_extension(original_name)
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    return unique_name


@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    order_id: int = Query(None, description="关联的需求单ID"),
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    上传文件
    
    支持 PDF、Word、Excel、图片格式
    单个文件最大50MB
    """
    # 检查文件扩展名
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。允许：{', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 检查文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小不能超过50MB"
        )
    
    # 生成唯一文件名并保存
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 保存到数据库
    attachment = FileAttachment(
        file_name=file.filename,
        file_path=str(file_path),
        file_size=len(contents),
        file_type=get_file_type(ext),
        order_id=order_id,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {
        "code": 200,
        "message": "上传成功",
        "data": {
            "id": attachment.id,
            "file_name": attachment.file_name,
            "file_size": attachment.file_size,
            "file_type": attachment.file_type,
            "uploaded_at": attachment.uploaded_at.isoformat(),
        }
    }


@router.get("", response_model=dict)
def get_files(
    order_id: int = Query(None, description="按需求单ID筛选"),
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    获取文件列表
    """
    query = db.query(FileAttachment).filter(
        FileAttachment.is_deleted == False
    )
    
    if order_id:
        query = query.filter(FileAttachment.order_id == order_id)
    
    # 按上传时间倒序
    files = query.order_by(FileAttachment.uploaded_at.desc()).all()
    
    return {
        "code": 200,
        "message": "查询成功",
        "data": [{
            "id": f.id,
            "file_name": f.file_name,
            "file_size": f.file_size,
            "file_size_display": f.get_file_size_display(),
            "file_type": f.file_type,
            "uploaded_by": f.uploaded_by,
            "uploaded_at": f.uploaded_at.isoformat(),
        } for f in files]
    }


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    下载文件
    """
    file = db.query(FileAttachment).filter(
        FileAttachment.id == file_id,
        FileAttachment.is_deleted == False
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    
    return FileResponse(
        path=file.file_path,
        filename=file.file_name,
        media_type="application/octet-stream"
    )


@router.delete("/{file_id}", response_model=dict)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    删除文件（软删除）
    只有上传者或管理员可以删除
    """
    file = db.query(FileAttachment).filter(
        FileAttachment.id == file_id,
        FileAttachment.is_deleted == False
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 权限检查：只有上传者或管理员可以删除
    if file.uploaded_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权删除该文件")
    
    # 软删除
    file.is_deleted = True
    file.deleted_at = datetime.now()
    file.deleted_by = current_user.id
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {"id": file_id}
    }
