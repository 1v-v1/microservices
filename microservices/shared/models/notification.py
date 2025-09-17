from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Notification(Base):
    """通知模型"""
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(Text, nullable=False)
    type = Column(String(32), nullable=False, index=True)  # loan_approved, loan_rejected, repayment_reminder, etc.
    channel = Column(String(16), nullable=False)  # email, sms, push, all
    status = Column(String(16), nullable=False, index=True)  # pending, sent, failed
    sent_at = Column(DateTime)
    error_message = Column(Text)
    template_id = Column(String(64))
    template_data = Column(JSON)  # JSON格式的模板数据
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationTemplate(Base):
    """通知模板模型"""
    __tablename__ = 'notification_templates'

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    channel = Column(String(16), nullable=False)  # email, sms, push, all
    variables = Column(JSON)  # JSON格式的变量列表
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(64))


class NotificationChannel(Base):
    """通知渠道配置模型"""
    __tablename__ = 'notification_channels'

    id = Column(Integer, primary_key=True)
    channel_name = Column(String(16), nullable=False, unique=True)  # email, sms, push
    is_enabled = Column(Boolean, default=True)
    config = Column(JSON)  # JSON格式的渠道配置
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationStats(Base):
    """通知统计模型"""
    __tablename__ = 'notification_stats'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, index=True)
    channel = Column(String(16), nullable=False)
    total_sent = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
