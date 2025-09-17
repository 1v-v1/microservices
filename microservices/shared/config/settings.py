import os
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_name: str = "极速贷微服务"
    debug: bool = False
    version: str = "1.0.0"
    
    # 数据库配置
    database_url: str = "postgresql+pg8000://postgres:051014ccx@localhost:5432/loanapp"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # RabbitMQ配置
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    # JWT配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 服务配置
    user_service_url: str = "http://localhost:8001"
    loan_service_url: str = "http://localhost:8002"
    repayment_service_url: str = "http://localhost:8003"
    risk_service_url: str = "http://localhost:8004"
    notification_service_url: str = "http://localhost:8005"
    file_service_url: str = "http://localhost:8006"
    
    # 文件存储配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "doc", "docx"}
    
    # 监控配置
    prometheus_port: int = 9090
    grafana_port: int = 3000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

