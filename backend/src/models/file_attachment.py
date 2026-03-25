"""
文件附件模型
存储需求全流程中上传的各类文档

作者/日期：AI / 2026-03-25
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from backend.src.database import Base


class FileAttachment(Base):
    """
    文件附件表
    存储所有上传的文档信息
    """
    __tablename__ = "file_attachment"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 文件信息
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="存储路径")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    file_type = Column(String(50), nullable=False, comment="文件类型：pdf/doc/xlsx/image")
    
    # 关联需求单（可选，MVP阶段可先不关联）
    order_id = Column(Integer, nullable=True, comment="关联的需求单ID")
    
    # 上传信息
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上传人ID")
    uploaded_at = Column(DateTime, server_default=func.now(), comment="上传时间")
    
    # 软删除
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="删除人ID")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "order_id": self.order_id,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "is_deleted": self.is_deleted,
        }
    
    def get_file_size_display(self):
        """获取人类可读的文件大小"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def get_file_icon(self):
        """获取文件类型图标"""
        icon_map = {
            "pdf": "file-pdf",
            "doc": "file-word",
            "docx": "file-word",
            "xls": "file-excel",
            "xlsx": "file-excel",
            "jpg": "file-image",
            "jpeg": "file-image",
            "png": "file-image",
        }
        return icon_map.get(self.file_type, "file")
