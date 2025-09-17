from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import sys
import os
from datetime import datetime, timedelta
import httpx
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import json

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.database import get_db_session
from shared.utils.auth import verify_token
from shared.models.risk import Blacklist, RiskAssessment, FraudDetection, RiskRule, RiskEvent
from pydantic import BaseModel

app = FastAPI(
    title="风控服务",
    description="风险评估、反欺诈、黑名单管理服务",
    version="1.0.0"
)

security = HTTPBearer()


# Pydantic模型
class RiskAssessmentRequest(BaseModel):
    user_id: int
    loan_amount: float
    timestamp: str


class RiskAssessmentResponse(BaseModel):
    approved: bool
    risk_score: float
    risk_level: str
    reasons: List[str]
    recommendations: List[str]


class BlacklistEntry(BaseModel):
    user_id: int
    reason: str
    created_at: datetime
    expires_at: Optional[datetime] = None


class FraudDetectionRequest(BaseModel):
    user_id: int
    ip_address: str
    device_fingerprint: str
    behavior_data: Dict[str, Any]


class FraudDetectionResponse(BaseModel):
    is_fraud: bool
    fraud_score: float
    risk_factors: List[str]
    confidence: float


# 依赖注入
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload.get("user_id", 0)


# 风控模型
class RiskAssessmentModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()
    
    def load_model(self):
        """加载预训练的风控模型"""
        try:
            # 这里应该加载实际的训练好的模型
            # 为了演示，我们创建一个简单的随机森林模型
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            # 在实际应用中，这里应该加载真实的模型文件
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.model = None
    
    def predict_risk(self, features: np.ndarray) -> tuple:
        """预测风险"""
        if self.model is None:
            # 如果没有模型，使用规则引擎
            return self.rule_based_assessment(features)
        
        try:
            # 使用机器学习模型预测
            risk_score = self.model.predict_proba(features)[0][1]
            return risk_score, self.get_risk_level(risk_score)
        except Exception:
            return self.rule_based_assessment(features)
    
    def rule_based_assessment(self, features: np.ndarray) -> tuple:
        """基于规则的评估"""
        # 简化的规则引擎
        risk_score = 0.0
        reasons = []
        
        # 贷款金额风险
        loan_amount = features[0] if len(features) > 0 else 0
        if loan_amount > 100000:
            risk_score += 0.3
            reasons.append("贷款金额过高")
        elif loan_amount > 50000:
            risk_score += 0.1
            reasons.append("贷款金额较高")
        
        # 信用分风险
        credit_score = features[1] if len(features) > 1 else 700
        if credit_score < 550:
            risk_score += 0.4
            reasons.append("信用分过低")
        elif credit_score < 650:
            risk_score += 0.2
            reasons.append("信用分偏低")
        
        # 收入风险
        monthly_income = features[2] if len(features) > 2 else 0
        if monthly_income > 0 and loan_amount > 0:
            debt_to_income = loan_amount / (monthly_income * 12)
            if debt_to_income > 0.5:
                risk_score += 0.3
                reasons.append("负债收入比过高")
            elif debt_to_income > 0.3:
                risk_score += 0.1
                reasons.append("负债收入比偏高")
        
        return min(risk_score, 1.0), self.get_risk_level(risk_score)
    
    def get_risk_level(self, risk_score: float) -> str:
        """获取风险等级"""
        if risk_score >= 0.8:
            return "高风险"
        elif risk_score >= 0.6:
            return "中高风险"
        elif risk_score >= 0.4:
            return "中等风险"
        elif risk_score >= 0.2:
            return "低风险"
        else:
            return "极低风险"


# 反欺诈检测
class FraudDetectionModel:
    def __init__(self):
        self.suspicious_patterns = {
            "rapid_applications": 0.3,  # 快速申请
            "unusual_ip": 0.2,  # 异常IP
            "device_mismatch": 0.4,  # 设备不匹配
            "behavior_anomaly": 0.5,  # 行为异常
        }
    
    def detect_fraud(self, request: FraudDetectionRequest) -> FraudDetectionResponse:
        """检测欺诈"""
        fraud_score = 0.0
        risk_factors = []
        
        # 检查IP地址
        if self.is_suspicious_ip(request.ip_address):
            fraud_score += self.suspicious_patterns["unusual_ip"]
            risk_factors.append("异常IP地址")
        
        # 检查设备指纹
        if self.is_device_suspicious(request.device_fingerprint):
            fraud_score += self.suspicious_patterns["device_mismatch"]
            risk_factors.append("设备指纹异常")
        
        # 检查行为数据
        behavior_score = self.analyze_behavior(request.behavior_data)
        if behavior_score > 0.5:
            fraud_score += self.suspicious_patterns["behavior_anomaly"]
            risk_factors.append("行为模式异常")
        
        # 检查申请频率
        if self.check_application_frequency(request.user_id):
            fraud_score += self.suspicious_patterns["rapid_applications"]
            risk_factors.append("申请频率过高")
        
        is_fraud = fraud_score > 0.6
        confidence = min(fraud_score, 1.0)
        
        return FraudDetectionResponse(
            is_fraud=is_fraud,
            fraud_score=fraud_score,
            risk_factors=risk_factors,
            confidence=confidence
        )
    
    def is_suspicious_ip(self, ip_address: str) -> bool:
        """检查IP是否可疑"""
        # 简化的IP检查逻辑
        suspicious_ips = ["192.168.1.100", "10.0.0.1"]  # 示例
        return ip_address in suspicious_ips
    
    def is_device_suspicious(self, device_fingerprint: str) -> bool:
        """检查设备是否可疑"""
        # 简化的设备检查逻辑
        return len(device_fingerprint) < 10  # 设备指纹过短
    
    def analyze_behavior(self, behavior_data: Dict[str, Any]) -> float:
        """分析行为数据"""
        # 简化的行为分析
        score = 0.0
        
        # 检查操作时间
        if "operation_time" in behavior_data:
            hour = datetime.fromisoformat(behavior_data["operation_time"]).hour
            if hour < 6 or hour > 23:  # 非正常时间操作
                score += 0.3
        
        # 检查操作频率
        if "operation_count" in behavior_data:
            if behavior_data["operation_count"] > 100:  # 操作过于频繁
                score += 0.4
        
        return min(score, 1.0)
    
    def check_application_frequency(self, user_id: int) -> bool:
        """检查申请频率"""
        # 这里应该查询数据库检查用户的申请频率
        # 简化处理，返回False
        return False


# 黑名单管理
class BlacklistManager:
    def __init__(self, db: Session):
        self.db = db
    
    def add_to_blacklist(self, user_id: int, reason: str, expires_at: Optional[datetime] = None, created_by: str = "system"):
        """添加到黑名单"""
        # 检查是否已在黑名单中
        existing = self.db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.is_active == True
        ).first()
        
        if existing:
            return existing
        
        # 创建新的黑名单记录
        blacklist_entry = Blacklist(
            user_id=user_id,
            reason=reason,
            expires_at=expires_at,
            created_by=created_by
        )
        
        self.db.add(blacklist_entry)
        self.db.commit()
        self.db.refresh(blacklist_entry)
        
        return blacklist_entry
    
    def is_blacklisted(self, user_id: int) -> bool:
        """检查是否在黑名单中"""
        now = datetime.utcnow()
        blacklist_entry = self.db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.is_active == True,
            (Blacklist.expires_at.is_(None)) | (Blacklist.expires_at > now)
        ).first()
        
        return blacklist_entry is not None
    
    def remove_from_blacklist(self, user_id: int):
        """从黑名单移除"""
        blacklist_entries = self.db.query(Blacklist).filter(
            Blacklist.user_id == user_id,
            Blacklist.is_active == True
        ).all()
        
        for entry in blacklist_entries:
            entry.is_active = False
        
        self.db.commit()
    
    def get_blacklist_entries(self, limit: int = 100, offset: int = 0):
        """获取黑名单条目"""
        return self.db.query(Blacklist).filter(
            Blacklist.is_active == True
        ).offset(offset).limit(limit).all()


# 初始化模型
risk_model = RiskAssessmentModel()
fraud_model = FraudDetectionModel()


async def get_user_info(user_id: int) -> dict:
    """获取用户信息"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.user_service_url}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


# API路由
@app.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(lambda: next(get_db_session("risk_service")))
):
    """风险评估"""
    # 获取用户信息
    user_info = await get_user_info(request.user_id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查黑名单
    blacklist_manager = BlacklistManager(db)
    if blacklist_manager.is_blacklisted(request.user_id):
        return RiskAssessmentResponse(
            approved=False,
            risk_score=1.0,
            risk_level="高风险",
            reasons=["用户在黑名单中"],
            recommendations=["联系客服了解详情"]
        )
    
    # 准备特征数据
    features = np.array([
        request.loan_amount,
        user_info.get("credit_score", 700),
        user_info.get("monthly_income", 0),
        user_info.get("total_borrowed", 0),
        user_info.get("pending_repay", 0)
    ]).reshape(1, -1)
    
    # 风险评估
    risk_score, risk_level = risk_model.predict_risk(features)
    
    # 生成建议
    reasons = []
    recommendations = []
    
    if risk_score > 0.7:
        reasons.append("综合风险评分过高")
        recommendations.append("建议降低贷款金额或提供更多担保")
    elif risk_score > 0.5:
        reasons.append("风险评分较高")
        recommendations.append("建议谨慎审批")
    else:
        reasons.append("风险评分在可接受范围内")
        recommendations.append("可以正常审批")
    
    approved = risk_score < 0.6
    
    # 保存风险评估记录到数据库
    assessment_record = RiskAssessment(
        user_id=request.user_id,
        loan_amount=request.loan_amount,
        risk_score=risk_score,
        risk_level=risk_level,
        approved=approved,
        reasons=json.dumps(reasons, ensure_ascii=False),
        recommendations=json.dumps(recommendations, ensure_ascii=False),
        assessment_data=json.dumps({
            "credit_score": user_info.get("credit_score", 700),
            "monthly_income": user_info.get("monthly_income", 0),
            "total_borrowed": user_info.get("total_borrowed", 0),
            "pending_repay": user_info.get("pending_repay", 0)
        }, ensure_ascii=False)
    )
    
    db.add(assessment_record)
    db.commit()
    
    return RiskAssessmentResponse(
        approved=approved,
        risk_score=risk_score,
        risk_level=risk_level,
        reasons=reasons,
        recommendations=recommendations
    )


@app.post("/fraud-detect", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest,
    db: Session = Depends(lambda: next(get_db_session("risk_service")))
):
    """反欺诈检测"""
    result = fraud_model.detect_fraud(request)
    
    # 保存反欺诈检测记录到数据库
    fraud_record = FraudDetection(
        user_id=request.user_id,
        ip_address=request.ip_address,
        device_fingerprint=request.device_fingerprint,
        behavior_data=json.dumps(request.behavior_data, ensure_ascii=False),
        is_fraud=result.is_fraud,
        fraud_score=result.fraud_score,
        risk_factors=json.dumps(result.risk_factors, ensure_ascii=False),
        confidence=result.confidence
    )
    
    db.add(fraud_record)
    db.commit()
    
    return result


@app.post("/blacklist/add")
async def add_to_blacklist(
    entry: BlacklistEntry,
    db: Session = Depends(lambda: next(get_db_session("risk_service")))
):
    """添加到黑名单"""
    blacklist_manager = BlacklistManager(db)
    blacklist_manager.add_to_blacklist(
        entry.user_id,
        entry.reason,
        entry.expires_at
    )
    
    return {"message": "已添加到黑名单"}


@app.get("/blacklist/check/{user_id}")
async def check_blacklist(
    user_id: int,
    db: Session = Depends(lambda: next(get_db_session("risk_service")))
):
    """检查黑名单状态"""
    blacklist_manager = BlacklistManager(db)
    is_blacklisted = blacklist_manager.is_blacklisted(user_id)
    
    return {"is_blacklisted": is_blacklisted}


@app.delete("/blacklist/remove/{user_id}")
async def remove_from_blacklist(
    user_id: int,
    db: Session = Depends(lambda: next(get_db_session("risk_service")))
):
    """从黑名单移除"""
    blacklist_manager = BlacklistManager(db)
    blacklist_manager.remove_from_blacklist(user_id)
    
    return {"message": "已从黑名单移除"}


@app.get("/risk-rules")
async def get_risk_rules():
    """获取风控规则"""
    rules = {
        "credit_score_rules": {
            "excellent": {"min": 700, "max": 750, "risk_multiplier": 0.5},
            "good": {"min": 650, "max": 699, "risk_multiplier": 0.7},
            "fair": {"min": 600, "max": 649, "risk_multiplier": 0.9},
            "poor": {"min": 550, "max": 599, "risk_multiplier": 1.2},
            "bad": {"min": 0, "max": 549, "risk_multiplier": 1.5}
        },
        "loan_amount_rules": {
            "low": {"min": 0, "max": 10000, "risk_multiplier": 0.8},
            "medium": {"min": 10001, "max": 50000, "risk_multiplier": 1.0},
            "high": {"min": 50001, "max": 100000, "risk_multiplier": 1.2},
            "very_high": {"min": 100001, "max": 999999, "risk_multiplier": 1.5}
        },
        "debt_to_income_rules": {
            "low": {"min": 0, "max": 0.2, "risk_multiplier": 0.8},
            "medium": {"min": 0.21, "max": 0.4, "risk_multiplier": 1.0},
            "high": {"min": 0.41, "max": 0.6, "risk_multiplier": 1.3},
            "very_high": {"min": 0.61, "max": 1.0, "risk_multiplier": 1.8}
        }
    }
    
    return rules


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "risk-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)


