from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import sys
import os
import uuid
import hashlib
import mimetypes
from datetime import datetime, timedelta
import httpx
from PIL import Image
import cv2
import numpy as np
from minio import Minio
from minio.error import S3Error
import io

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.database import get_db_session
from shared.utils.auth import verify_token
from shared.models.file import FileInfo, FileProcess, FileAccess, FileStorage
from pydantic import BaseModel

app = FastAPI(
    title="文件服务",
    description="文件上传、存储管理、文件处理服务",
    version="1.0.0"
)

security = HTTPBearer()


# Pydantic模型
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    file_type: str
    url: str
    uploaded_at: datetime


class FileInfo(BaseModel):
    file_id: str
    filename: str
    file_size: int
    file_type: str
    url: str
    uploaded_at: datetime
    user_id: int
    category: str
    status: str

    class Config:
        from_attributes = True


class FileProcessRequest(BaseModel):
    file_id: str
    process_type: str  # resize, compress, watermark, convert
    parameters: Dict[str, Any]


# 依赖注入
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload.get("user_id", 0)


# 文件存储接口
class FileStorage:
    def __init__(self):
        self.minio_client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        self.bucket_name = "loan-files"
        self.ensure_bucket_exists()
    
    def ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"创建存储桶失败: {e}")
    
    def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        """上传文件"""
        file_id = str(uuid.uuid4())
        object_name = f"{file_id}/{filename}"
        
        try:
            self.minio_client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(file_data),
                len(file_data),
                content_type=content_type
            )
            return file_id
        except S3Error as e:
            print(f"文件上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件上传失败"
            )
    
    def download_file(self, file_id: str, filename: str) -> bytes:
        """下载文件"""
        object_name = f"{file_id}/{filename}"
        
        try:
            response = self.minio_client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as e:
            print(f"文件下载失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
    
    def delete_file(self, file_id: str, filename: str):
        """删除文件"""
        object_name = f"{file_id}/{filename}"
        
        try:
            self.minio_client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            print(f"文件删除失败: {e}")
    
    def get_file_url(self, file_id: str, filename: str) -> str:
        """获取文件访问URL"""
        object_name = f"{file_id}/{filename}"
        
        try:
            url = self.minio_client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(hours=1)
            )
            return url
        except S3Error as e:
            print(f"获取文件URL失败: {e}")
            return ""


# 文件处理器
class FileProcessor:
    @staticmethod
    def resize_image(image_data: bytes, width: int, height: int) -> bytes:
        """调整图片大小"""
        try:
            image = Image.open(io.BytesIO(image_data))
            resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            resized_image.save(output, format=image.format)
            return output.getvalue()
        except Exception as e:
            print(f"图片调整大小失败: {e}")
            return image_data
    
    @staticmethod
    def compress_image(image_data: bytes, quality: int = 85) -> bytes:
        """压缩图片"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            output = io.BytesIO()
            if image.format == 'JPEG':
                image.save(output, format='JPEG', quality=quality, optimize=True)
            elif image.format == 'PNG':
                image.save(output, format='PNG', optimize=True)
            else:
                image.save(output, format='JPEG', quality=quality, optimize=True)
            
            return output.getvalue()
        except Exception as e:
            print(f"图片压缩失败: {e}")
            return image_data
    
    @staticmethod
    def add_watermark(image_data: bytes, watermark_text: str) -> bytes:
        """添加水印"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 添加文字水印
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            color = (255, 255, 255)
            thickness = 2
            
            # 获取文字大小
            (text_width, text_height), _ = cv2.getTextSize(watermark_text, font, font_scale, thickness)
            
            # 计算水印位置（右下角）
            x = cv_image.shape[1] - text_width - 10
            y = cv_image.shape[0] - 10
            
            # 添加半透明背景
            overlay = cv_image.copy()
            cv2.rectangle(overlay, (x-5, y-text_height-5), (x+text_width+5, y+5), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, cv_image, 0.5, 0, cv_image)
            
            # 添加文字
            cv2.putText(cv_image, watermark_text, (x, y), font, font_scale, color, thickness)
            
            # 转换回PIL格式
            image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            output = io.BytesIO()
            image.save(output, format=image.format)
            return output.getvalue()
        except Exception as e:
            print(f"添加水印失败: {e}")
            return image_data
    
    @staticmethod
    def convert_image(image_data: bytes, target_format: str) -> bytes:
        """转换图片格式"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            output = io.BytesIO()
            if target_format.upper() == 'JPEG':
                # 转换为RGB模式（JPEG不支持透明度）
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                image.save(output, format='JPEG', quality=95)
            elif target_format.upper() == 'PNG':
                image.save(output, format='PNG')
            elif target_format.upper() == 'WEBP':
                image.save(output, format='WEBP', quality=95)
            else:
                image.save(output, format='JPEG', quality=95)
            
            return output.getvalue()
        except Exception as e:
            print(f"图片格式转换失败: {e}")
            return image_data


# 初始化存储和处理器
file_storage = FileStorage()
file_processor = FileProcessor()


# API路由
@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form("general"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("file_service")))
):
    """上传文件"""
    # 检查文件大小
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({settings.max_file_size / 1024 / 1024:.1f}MB)"
        )
    
    # 检查文件类型
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}"
        )
    
    # 读取文件内容
    file_data = await file.read()
    
    # 生成文件ID和文件名
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{file_ext}"
    
    # 获取MIME类型
    content_type, _ = mimetypes.guess_type(file.filename)
    if not content_type:
        content_type = "application/octet-stream"
    
    # 上传到存储
    try:
        uploaded_file_id = file_storage.upload_file(file_data, filename, content_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )
    
    # 生成访问URL
    file_url = file_storage.get_file_url(uploaded_file_id, filename)
    
    # 保存文件信息到数据库
    file_info = FileInfo(
        file_id=uploaded_file_id,
        user_id=current_user_id,
        filename=file.filename,
        original_filename=file.filename,
        file_size=len(file_data),
        file_type=content_type,
        mime_type=content_type,
        category=category,
        storage_path=f"{uploaded_file_id}/{filename}",
        url=file_url,
        status="active",
        is_public=False,
        metadata={
            "upload_source": "api",
            "file_extension": file_ext,
            "storage_type": "minio"
        }
    )
    
    db.add(file_info)
    db.commit()
    db.refresh(file_info)
    
    return FileUploadResponse(
        file_id=uploaded_file_id,
        filename=file.filename,
        file_size=len(file_data),
        file_type=content_type,
        url=file_url,
        uploaded_at=datetime.utcnow()
    )


@app.get("/download/{file_id}")
async def download_file(
    file_id: str,
    filename: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """下载文件"""
    try:
        file_data = file_storage.download_file(file_id, filename)
        
        # 获取MIME类型
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"
        
        return FileResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )


@app.get("/files", response_model=List[FileInfo])
async def get_user_files(
    current_user_id: int = Depends(get_current_user_id),
    category: Optional[str] = None,
    db: Session = Depends(lambda: next(get_db_session("file_service")))
):
    """获取用户文件列表"""
    query = db.query(FileInfo).filter(
        FileInfo.user_id == current_user_id,
        FileInfo.status == "active"
    )
    
    if category:
        query = query.filter(FileInfo.category == category)
    
    files = query.order_by(FileInfo.created_at.desc()).all()
    
    return files


@app.post("/process/{file_id}")
async def process_file(
    file_id: str,
    process_request: FileProcessRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """处理文件"""
    try:
        # 获取原文件
        # 这里需要从数据库获取文件信息
        filename = f"{file_id}.jpg"  # 简化处理
        
        file_data = file_storage.download_file(file_id, filename)
        
        # 根据处理类型处理文件
        if process_request.process_type == "resize":
            width = process_request.parameters.get("width", 800)
            height = process_request.parameters.get("height", 600)
            processed_data = file_processor.resize_image(file_data, width, height)
        elif process_request.process_type == "compress":
            quality = process_request.parameters.get("quality", 85)
            processed_data = file_processor.compress_image(file_data, quality)
        elif process_request.process_type == "watermark":
            watermark_text = process_request.parameters.get("text", "极速贷")
            processed_data = file_processor.add_watermark(file_data, watermark_text)
        elif process_request.process_type == "convert":
            target_format = process_request.parameters.get("format", "jpeg")
            processed_data = file_processor.convert_image(file_data, target_format)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的处理类型"
            )
        
        # 保存处理后的文件
        processed_filename = f"{file_id}_processed.jpg"
        processed_file_id = file_storage.upload_file(processed_data, processed_filename, "image/jpeg")
        
        return {
            "file_id": processed_file_id,
            "filename": processed_filename,
            "file_size": len(processed_data),
            "url": file_storage.get_file_url(processed_file_id, processed_filename)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件处理失败: {str(e)}"
        )


@app.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    filename: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """删除文件"""
    try:
        file_storage.delete_file(file_id, filename)
        return {"message": "文件删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )


@app.get("/stats")
async def get_file_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("file_service")))
):
    """获取文件统计"""
    # 查询用户文件总数
    total_files = db.query(FileInfo).filter(
        FileInfo.user_id == current_user_id,
        FileInfo.status == "active"
    ).count()
    
    # 查询用户文件总大小
    total_size = db.query(FileInfo).filter(
        FileInfo.user_id == current_user_id,
        FileInfo.status == "active"
    ).with_entities(FileInfo.file_size).all()
    
    total_size = sum(file.file_size for file in total_size) if total_size else 0
    
    # 按文件类型统计
    file_types = {}
    categories = db.query(FileInfo.category).filter(
        FileInfo.user_id == current_user_id,
        FileInfo.status == "active"
    ).distinct().all()
    
    for category in categories:
        count = db.query(FileInfo).filter(
            FileInfo.user_id == current_user_id,
            FileInfo.status == "active",
            FileInfo.category == category[0]
        ).count()
        file_types[category[0]] = count
    
    return {
        "total_files": total_files,
        "total_size": total_size,
        "file_types": file_types
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "file-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)


