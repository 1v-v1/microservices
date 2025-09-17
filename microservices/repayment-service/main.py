from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
from datetime import datetime, timedelta, date
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.database import get_db_session
from shared.utils.auth import verify_token
from shared.models.loan import Loan, Repayment
from pydantic import BaseModel

app = FastAPI(
    title="还款服务",
    description="还款计划、还款记录、逾期处理服务",
    version="1.0.0"
)

security = HTTPBearer()

# 调度器
scheduler = BackgroundScheduler()


# Pydantic模型
class RepaymentCreate(BaseModel):
    loan_id: int
    amount: float
    payment_method: str = "alipay"


class RepaymentResponse(BaseModel):
    id: int
    loan_id: int
    due_date: date
    due_amount: float
    paid_date: Optional[date]
    paid_amount: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RepaymentPlanResponse(BaseModel):
    loan_id: int
    total_amount: float
    remaining_amount: float
    next_payment_date: Optional[date]
    next_payment_amount: float
    overdue_amount: float
    repayments: List[RepaymentResponse]

    class Config:
        from_attributes = True


# 依赖注入
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload.get("user_id", 0)


async def get_loan_info(loan_id: int) -> dict:
    """获取贷款信息"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.loan_service_url}/loans/{loan_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


async def send_notification(user_id: int, message: str, notification_type: str = "repayment"):
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
            pass


def calculate_repayment_schedule(loan: Loan) -> List[Repayment]:
    """计算还款计划"""
    repayments = []
    monthly_rate = loan.interest_rate / 12
    remaining_principal = float(loan.amount)
    
    for i in range(loan.term_months):
        if loan.repay_method == "equal-principal":
            # 等额本金
            monthly_principal = float(loan.amount) / loan.term_months
            monthly_interest = remaining_principal * monthly_rate
            monthly_payment = monthly_principal + monthly_interest
            remaining_principal -= monthly_principal
        else:
            # 等额本息
            if monthly_rate == 0:
                monthly_payment = float(loan.amount) / loan.term_months
            else:
                monthly_payment = (float(loan.amount) * monthly_rate * (1 + monthly_rate)**loan.term_months) / ((1 + monthly_rate)**loan.term_months - 1)
            monthly_principal = monthly_payment - remaining_principal * monthly_rate
            remaining_principal -= monthly_principal
        
        due_date = loan.created_at.date() + timedelta(days=30 * (i + 1))
        
        repayment = Repayment(
            loan_id=loan.id,
            due_date=due_date,
            due_amount=monthly_payment,
            status="due"
        )
        repayments.append(repayment)
    
    return repayments


def check_overdue_repayments(db: Session):
    """检查逾期还款"""
    today = date.today()
    overdue_repayments = db.query(Repayment).filter(
        Repayment.status == "due",
        Repayment.due_date < today
    ).all()
    
    for repayment in overdue_repayments:
        repayment.status = "overdue"
        db.commit()
        
        # 发送逾期通知
        # 这里需要获取用户ID，简化处理
        loan = db.query(Loan).filter(Loan.id == repayment.loan_id).first()
        if loan:
            # 异步发送通知
            import asyncio
            asyncio.create_task(send_notification(
                loan.user_id,
                f"您的贷款还款已逾期，请尽快还款。逾期金额：{repayment.due_amount}元",
                "repayment_overdue"
            ))


# 定时任务
@scheduler.scheduled_job(CronTrigger(hour=0, minute=0))  # 每天凌晨执行
def daily_overdue_check():
    """每日逾期检查"""
    db = next(get_db_session("repayment_service"))
    try:
        check_overdue_repayments(db)
    finally:
        db.close()


# 启动调度器
scheduler.start()


# API路由
@app.post("/repay", response_model=RepaymentResponse)
async def make_repayment(
    repayment_data: RepaymentCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("repayment_service")))
):
    """执行还款"""
    # 获取贷款信息
    loan = db.query(Loan).filter(
        Loan.id == repayment_data.loan_id,
        Loan.user_id == current_user_id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="贷款不存在"
        )
    
    if loan.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="贷款状态不允许还款"
        )
    
    # 查找待还款记录
    repayment = db.query(Repayment).filter(
        Repayment.loan_id == repayment_data.loan_id,
        Repayment.status.in_(["due", "overdue"])
    ).order_by(Repayment.due_date).first()
    
    if not repayment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有待还款记录"
        )
    
    # 更新还款记录
    repayment.paid_date = date.today()
    repayment.paid_amount = repayment_data.amount
    repayment.status = "paid"
    
    # 更新贷款剩余金额
    loan.remaining_amount = max(0, float(loan.remaining_amount) - repayment_data.amount)
    
    # 检查是否全部还清
    if loan.remaining_amount <= 0:
        loan.status = "settled"
        loan.remaining_amount = 0
    
    db.commit()
    db.refresh(repayment)
    
    # 发送还款成功通知
    await send_notification(
        current_user_id,
        f"还款成功！还款金额：{repayment_data.amount}元",
        "repayment_success"
    )
    
    return repayment


@app.get("/repayments", response_model=List[RepaymentResponse])
async def get_user_repayments(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("repayment_service")))
):
    """获取用户还款记录"""
    # 获取用户的所有贷款ID
    user_loans = db.query(Loan).filter(Loan.user_id == current_user_id).all()
    loan_ids = [loan.id for loan in user_loans]
    
    # 获取还款记录
    repayments = db.query(Repayment).filter(
        Repayment.loan_id.in_(loan_ids)
    ).order_by(Repayment.created_at.desc()).all()
    
    return repayments


@app.get("/repayment-plan/{loan_id}", response_model=RepaymentPlanResponse)
async def get_repayment_plan(
    loan_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(lambda: next(get_db_session("repayment_service")))
):
    """获取还款计划"""
    # 获取贷款信息
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.user_id == current_user_id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="贷款不存在"
        )
    
    # 获取还款记录
    repayments = db.query(Repayment).filter(
        Repayment.loan_id == loan_id
    ).order_by(Repayment.due_date).all()
    
    # 计算逾期金额
    overdue_amount = sum(
        float(repayment.due_amount) for repayment in repayments 
        if repayment.status == "overdue"
    )
    
    # 计算下次还款
    next_repayment = db.query(Repayment).filter(
        Repayment.loan_id == loan_id,
        Repayment.status.in_(["due", "overdue"])
    ).order_by(Repayment.due_date).first()
    
    next_payment_date = next_repayment.due_date if next_repayment else None
    next_payment_amount = float(next_repayment.due_amount) if next_repayment else 0
    
    return RepaymentPlanResponse(
        loan_id=loan_id,
        total_amount=float(loan.amount),
        remaining_amount=float(loan.remaining_amount),
        next_payment_date=next_payment_date,
        next_payment_amount=next_payment_amount,
        overdue_amount=overdue_amount,
        repayments=repayments
    )


@app.post("/generate-plan/{loan_id}")
async def generate_repayment_plan(
    loan_id: int,
    db: Session = Depends(lambda: next(get_db_session("repayment_service")))
):
    """生成还款计划（内部接口）"""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="贷款不存在"
        )
    
    # 检查是否已有还款计划
    existing_repayments = db.query(Repayment).filter(Repayment.loan_id == loan_id).count()
    if existing_repayments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="还款计划已存在"
        )
    
    # 生成还款计划
    repayments = calculate_repayment_schedule(loan)
    
    for repayment in repayments:
        db.add(repayment)
    
    db.commit()
    
    return {"message": "还款计划生成成功", "count": len(repayments)}


@app.get("/overdue")
async def get_overdue_repayments(
    db: Session = Depends(lambda: next(get_db_session("repayment_service")))
):
    """获取逾期还款列表（管理员接口）"""
    overdue_repayments = db.query(Repayment).filter(
        Repayment.status == "overdue"
    ).all()
    
    return overdue_repayments


@app.post("/repayments/{repayment_id}/mark-overdue")
async def mark_repayment_overdue(
    repayment_id: int,
    db: Session = Depends(lambda: next(get_db_session("repayment_service")))
):
    """标记还款为逾期（管理员接口）"""
    repayment = db.query(Repayment).filter(Repayment.id == repayment_id).first()
    
    if not repayment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="还款记录不存在"
        )
    
    repayment.status = "overdue"
    db.commit()
    
    return {"message": "已标记为逾期"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "repayment-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)


