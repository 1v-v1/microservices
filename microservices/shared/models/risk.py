from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Blacklist(Base):
    """黑名单模型"""
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(String(64))  # 操作员


class RiskAssessment(Base):
    """风险评估记录模型"""
    __tablename__ = 'risk_assessments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    loan_amount = Column(Numeric(14, 2), nullable=False)
    risk_score = Column(Numeric(5, 4), nullable=False)  # 0.0000-1.0000
    risk_level = Column(String(16), nullable=False)  # 极低风险/低风险/中等风险/中高风险/高风险
    approved = Column(Boolean, nullable=False)
    reasons = Column(Text)  # JSON格式的风险原因
    recommendations = Column(Text)  # JSON格式的建议
    assessment_data = Column(Text)  # JSON格式的评估数据
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class FraudDetection(Base):
    """反欺诈检测记录模型"""
    __tablename__ = 'fraud_detections'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    ip_address = Column(String(45))  # 支持IPv6
    device_fingerprint = Column(String(255))
    behavior_data = Column(Text)  # JSON格式的行为数据
    is_fraud = Column(Boolean, nullable=False)
    fraud_score = Column(Numeric(5, 4), nullable=False)  # 0.0000-1.0000
    risk_factors = Column(Text)  # JSON格式的风险因子
    confidence = Column(Numeric(5, 4), nullable=False)  # 0.0000-1.0000
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RiskRule(Base):
    """风控规则模型"""
    __tablename__ = 'risk_rules'

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(128), nullable=False, unique=True)
    rule_type = Column(String(32), nullable=False)  # credit_score, loan_amount, debt_to_income
    rule_config = Column(Text, nullable=False)  # JSON格式的规则配置
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # 优先级，数字越小优先级越高
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(64))


class RiskEvent(Base):
    """风控事件模型"""
    __tablename__ = 'risk_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # application, repayment, login, etc.
    event_data = Column(Text)  # JSON格式的事件数据
    risk_score = Column(Numeric(5, 4))
    is_suspicious = Column(Boolean, default=False)
    action_taken = Column(String(64))  # 采取的行动
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
