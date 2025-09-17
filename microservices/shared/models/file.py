from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class FileInfo(Base):
    """文件信息模型"""
    __tablename__ = 'file_info'

    id = Column(Integer, primary_key=True)
    file_id = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(64), nullable=False)
    mime_type = Column(String(128))
    category = Column(String(32), default='general')  # avatar, document, image, etc.
    storage_path = Column(String(512), nullable=False)  # 存储路径
    url = Column(String(512))  # 访问URL
    status = Column(String(16), default='active')  # active, deleted, processing
    is_public = Column(Boolean, default=False)  # 是否公开访问
    metadata = Column(JSON)  # JSON格式的文件元数据
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)


class FileProcess(Base):
    """文件处理记录模型"""
    __tablename__ = 'file_processes'

    id = Column(Integer, primary_key=True)
    file_id = Column(String(64), nullable=False, index=True)
    process_type = Column(String(32), nullable=False)  # resize, compress, watermark, convert
    parameters = Column(JSON)  # JSON格式的处理参数
    status = Column(String(16), default='pending')  # pending, processing, completed, failed
    result_file_id = Column(String(64))  # 处理结果文件ID
    error_message = Column(Text)
    processing_time = Column(Integer)  # 处理耗时（毫秒）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)


class FileAccess(Base):
    """文件访问记录模型"""
    __tablename__ = 'file_access'

    id = Column(Integer, primary_key=True)
    file_id = Column(String(64), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    access_type = Column(String(16), nullable=False)  # download, view, share
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class FileStorage(Base):
    """文件存储配置模型"""
    __tablename__ = 'file_storage'

    id = Column(Integer, primary_key=True)
    storage_name = Column(String(64), nullable=False, unique=True)  # minio, local, s3, etc.
    storage_type = Column(String(32), nullable=False)
    config = Column(JSON, nullable=False)  # JSON格式的存储配置
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
