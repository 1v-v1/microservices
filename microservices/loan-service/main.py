from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
import uuid
import calendar
from datetime import datetime, timedelta
import httpx

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.database import get_db_session
from shared.utils.auth import verify_token
from shared.models.loan import Loan
from pydantic import BaseModel

app = FastAPI(
    title="贷款服务",
    description="贷款申请、审批流程、贷款管理服务",
    version="1.0.0"
)

security = HTTPBearer()


# Pydantic模型
class LoanCreate(BaseModel):
    user_id: int
    amount: float
    term_months: int
    repay_method: str = "equal-installment"


class LoanApproval(BaseModel):
    approved: bool
    reason: Optional[str] = None


class LoanResponse(BaseModel):
    id: int
    loan_id: str
    user_id: int
    amount: float
    term_months: int
    interest_rate: float
    repay_method: str
    status: str
    remaining_amount: float
    next_payment_date: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# 依赖注入
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload.get("user_id", 0)


# 贷款计算函数
def calculate_loan_payment(amount: float, term_months: int, repay_method: str = "equal-installment") -> float:
    """计算贷款月供"""
    annual_rate = 0.0412  # 年化利率4.12%
    monthly_rate = annual_rate / 12  # 月利率
    
    if repay_method == "equal-principal":  # 等额本金
        monthly_principal = amount / term_months
        first_month_interest = amount * monthly_rate
        return monthly_principal + first_month_interest
    else:  # 等额本息
        if monthly_rate == 0:
            return amount / term_months
        return (amount * monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)


def calculate_due_date(term_months: int) -> datetime:
    """计算到期日"""
    due_date = datetime.now()
    if term_months <= 31:  # 如果小于等于31，视为天数
        due_date = due_date + timedelta(days=term_months)
    elif term_months == 90:  # 3个月，精确到天
        due_date = due_date + timedelta(days=90)
    elif term_months == 180:  # 6个月，精确到天
        due_date = due_date + timedelta(days=180)
    elif term_months == 365:  # 12个月，精确到天
        due_date = due_date + timedelta(days=365)
    else:  # 其他情况按月计算
        new_month = due_date.month + term_months
        new_year = due_date.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        last_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(due_date.day, last_day)
        due_date = due_date.replace(year=new_year, month=new_month, day=new_day)
    
    return due_date


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


async def call_risk_service(user_id: int, loan_amount: float) -> dict:
    """调用风控服务"""
    async with httpx.AsyncClient() as client:
        try:
            risk_data = {
                "user_id": user_id,
                "loan_amount": loan_amount,
                "timestamp": datetime.utcnow().isoformat()
            }
            response = await client.post(f"{settings.risk_service_url}/assess", json=risk_data)
            if response.status_code == 200:
                return response.json()
            return {"approved": False, "reason": "风控服务不可用"}
        except Exception:
            return {"approved": False, "reason": "风控服务调用失败"}


async def send_notification(user_id: int, message: str, notification_type: str = "loan_status"):
    """发送通知"""
    async with httpx.AsyncClient() as client:
        try:
            notification_data = {
                "user_id": user_id,
                "message": message,
                "type": notification_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            await client.post(f"{settings.notification_service_url}/send", json=notification_data)
        except Exception:
            pass  # 通知发送失败不影响主流程


# API路由
@app.post("/apply", response_model=LoanResponse)
async def apply_loan(
    loan_data: LoanCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("loan_service")))
):
    """申请贷款"""
    # 获取用户信息
    user_info = await get_user_info(loan_data.user_id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户资料是否完整
    if not user_info.get("is_profile_completed", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先完善个人资料"
        )
    
    # 检查用户信用分
    credit_score = user_info.get("credit_score", 0)
    if credit_score < 550:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="信用分不足，无法申请贷款"
        )
    
    # 调用风控服务
    risk_result = await call_risk_service(loan_data.user_id, loan_data.amount)
    if not risk_result.get("approved", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"风控审核未通过：{risk_result.get('reason', '未知原因')}"
        )
    
    # 计算月供
    monthly_payment = calculate_loan_payment(loan_data.amount, loan_data.term_months, loan_data.repay_method)
    
    # 检查月收入是否足够
    monthly_income = user_info.get("monthly_income", 0)
    if monthly_income and monthly_income * 2 / 3 < monthly_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="月收入不足以支付贷款"
        )
    
    # 生成贷款ID
    loan_id = str(uuid.uuid4())
    
    # 判断是否需要人工审批
    need_manual_approval = credit_score < 700
    
    # 创建贷款记录
    loan = Loan(
        loan_id=loan_id,
        user_id=loan_data.user_id,
        amount=loan_data.amount,
        term_months=loan_data.term_months,
        interest_rate=0.0412,
        repay_method=loan_data.repay_method,
        status="pending" if need_manual_approval else "approved",
        remaining_amount=loan_data.amount if not need_manual_approval else 0,
        next_payment_date=calculate_due_date(loan_data.term_months) if not need_manual_approval else None,
        approved_at=datetime.utcnow() if not need_manual_approval else None
    )
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    # 发送通知
    if need_manual_approval:
        await send_notification(
            loan_data.user_id,
            f"您的贷款申请已提交，因信用分为{credit_score}分（低于700分），需要人工审批。请耐心等待审批结果。",
            "loan_pending"
        )
    else:
        await send_notification(
            loan_data.user_id,
            "恭喜！您的贷款申请已自动批准！",
            "loan_approved"
        )
    
    return loan


@app.get("/loans", response_model=List[LoanResponse])
async def get_user_loans(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("loan_service")))
):
    """获取用户贷款列表"""
    loans = db.query(Loan).filter(Loan.user_id == current_user_id).all()
    return loans


@app.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan_detail(
    loan_id: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("loan_service")))
):
    """获取贷款详情"""
    loan = db.query(Loan).filter(
        Loan.loan_id == loan_id,
        Loan.user_id == current_user_id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="贷款不存在"
        )
    
    return loan


@app.post("/loans/{loan_id}/approve", response_model=LoanResponse)
async def approve_loan(
    loan_id: str,
    approval_data: LoanApproval,
    db: Session = Depends(lambda: next(get_db_session("loan_service")))
):
    """审批贷款（管理员接口）"""
    loan = db.query(Loan).filter(Loan.loan_id == loan_id).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="贷款不存在"
        )
    
    if loan.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="贷款状态不允许审批"
        )
    
    if approval_data.approved:
        loan.status = "approved"
        loan.remaining_amount = loan.amount
        loan.next_payment_date = calculate_due_date(loan.term_months)
        loan.approved_at = datetime.utcnow()
        
        # 发送批准通知
        await send_notification(
            loan.user_id,
            "恭喜！您的贷款申请已批准！",
            "loan_approved"
        )
    else:
        loan.status = "rejected"
        
        # 发送拒绝通知
        await send_notification(
            loan.user_id,
            f"很抱歉，您的贷款申请未通过审批。原因：{approval_data.reason or '不符合贷款条件'}",
            "loan_rejected"
        )
    
    db.commit()
    db.refresh(loan)
    
    return loan


@app.get("/admin/loans", response_model=List[LoanResponse])
async def get_all_loans(
    status_filter: Optional[str] = None,
    db: Session = Depends(lambda: next(get_db_session("loan_service")))
):
    """获取所有贷款（管理员接口）"""
    query = db.query(Loan)
    if status_filter:
        query = query.filter(Loan.status == status_filter)
    
    return query.all()


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "loan-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)


