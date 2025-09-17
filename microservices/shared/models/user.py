from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    real_name = Column(String(64))
    id_card = Column(String(32), index=True)
    phone = Column(String(20), unique=True, index=True)

    # 详细信息
    education = Column(String(32))
    school = Column(String(128))
    marital_status = Column(String(16))
    work_status = Column(String(32))
    company = Column(String(128))
    position = Column(String(64))
    income = Column(String(32))
    has_house = Column(Boolean)
    has_car = Column(Boolean)
    contact_name = Column(String(64))
    contact_phone = Column(String(20))
    relation = Column(String(32))
    avatar = Column(String(256))

    # 聚合与状态
    credit_score = Column(Integer, index=True)
    is_profile_completed = Column(Boolean, default=False, index=True)
    loan_limit = Column(Numeric(14, 2), default=0)
    total_borrowed = Column(Numeric(14, 2), default=0)
    pending_repay = Column(Numeric(14, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreditScore(Base):
    """信用分模型"""
    __tablename__ = 'credit_scores'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    score = Column(Integer, nullable=False)
    details = Column(JSONB)  # 评分构成明细
    level = Column(String(16))
    version = Column(String(16))
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

