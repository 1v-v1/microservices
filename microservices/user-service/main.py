from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.database import get_db_session
from shared.utils.auth import verify_token, verify_password, get_password_hash, create_access_token
from shared.models.user import User, CreditScore
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib

app = FastAPI(
    title="用户服务",
    description="用户管理、认证授权、用户画像服务",
    version="1.0.0"
)

security = HTTPBearer()


# Pydantic模型
class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    school: Optional[str] = None
    marital_status: Optional[str] = None
    work_status: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    income: Optional[str] = None
    has_house: Optional[bool] = None
    has_car: Optional[bool] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    relation: Optional[str] = None
    avatar: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: Optional[str]
    phone: Optional[str]
    credit_score: Optional[int]
    is_profile_completed: bool
    loan_limit: float
    total_borrowed: float
    pending_repay: float
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# 依赖注入
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(lambda: next(get_db_session("user_service")))
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    return user


# 信用分计算函数
def calculate_credit_score(profile_data: dict, username: str = None) -> dict:
    """计算信用分"""
    base_score = 480  # 基础分
    
    # 如果没有任何信息，基于用户名生成一个基础的差异化分数
    if not any([profile_data.get('education'), profile_data.get('work_status'), 
                profile_data.get('income'), profile_data.get('marital_status')]):
        if username:
            # 基于用户名生成一个伪随机但固定的分数差异
            hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
            variation = (hash_value % 200) - 100  # -100到+100的变化
            base_score += variation
    
    # 学历加分 (0-120分)
    education_scores = {
        '初中及以下': 0,
        '高中/中专': 25,
        '大专': 50,
        '本科': 80,
        '硕士': 100,
        '博士': 120
    }
    education_score = education_scores.get(profile_data.get('education', ''), 0)
    
    # 婚姻状况加分 (-15到40分)
    marital_scores = {
        '已婚': 40,
        '未婚': 15,
        '离异': -15,
        '丧偶': 5
    }
    marital_score = marital_scores.get(profile_data.get('marital_status', ''), 0)
    
    # 工作状态加分 (-30到60分)
    work_scores = {
        '在职员工': 60,
        '个体经营': 40,
        '自由职业': 25,
        '学生': 15,
        '退休': 45,
        '待业': -30
    }
    work_score = work_scores.get(profile_data.get('work_status', ''), 0)
    
    # 收入水平加分 (0-120分)
    income_scores = {
        '3000以下': 0,
        '3000-5000': 25,
        '5000-8000': 50,
        '8000-12000': 75,
        '12000-20000': 100,
        '20000以上': 120
    }
    income_score = income_scores.get(profile_data.get('income', ''), 0)
    
    # 资产状况加分 (0-90分)
    asset_score = 0
    if profile_data.get('has_house'):
        asset_score += 60  # 有房产
    if profile_data.get('has_car'):
        asset_score += 30   # 有车辆
    
    # 联系人信息完整性加分 (0-25分)
    contact_score = 0
    if profile_data.get('contact_name') and profile_data.get('contact_phone'):
        contact_score = 25
    
    # 基本信息完整性加分 (0-35分)
    basic_info_score = 0
    if profile_data.get('real_name'):
        basic_info_score += 10
    if profile_data.get('id_card'):
        basic_info_score += 15
    if profile_data.get('phone'):
        basic_info_score += 10
    
    # 计算总分
    total_score = (base_score + education_score + marital_score + 
                  work_score + income_score + asset_score + contact_score + basic_info_score)
    
    # 确保分数在350-750之间
    total_score = max(350, min(750, total_score))
    
    # 返回计算详情
    return {
        'total_score': total_score,
        'details': {
            'base_score': base_score,
            'education_score': education_score,
            'marital_score': marital_score,
            'work_score': work_score,
            'income_score': income_score,
            'asset_score': asset_score,
            'contact_score': contact_score,
            'basic_info_score': basic_info_score
        },
        'level': get_credit_level(total_score)
    }


def get_credit_level(score: int) -> str:
    """根据信用分获取信用等级"""
    if score >= 700:
        return '优秀'
    elif score >= 650:
        return '良好'
    elif score >= 600:
        return '中等'
    elif score >= 550:
        return '及格'
    else:
        return '较差'


# API路由
@app.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(lambda: next(get_db_session("user_service")))):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        password_hash=hashed_password,
        real_name=user_data.real_name,
        phone=user_data.phone,
        credit_score=700,  # 默认信用分
        loan_limit=50000,  # 默认贷款额度
        is_profile_completed=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@app.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(lambda: next(get_db_session("user_service")))):
    """用户登录"""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@app.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """获取用户资料"""
    return current_user


@app.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(lambda: next(get_db_session("user_service")))
):
    """更新用户资料"""
    # 更新用户信息
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    # 计算新的信用分
    profile_data = {
        'real_name': current_user.real_name,
        'id_card': current_user.id_card,
        'phone': current_user.phone,
        'education': current_user.education,
        'marital_status': current_user.marital_status,
        'work_status': current_user.work_status,
        'income': current_user.income,
        'has_house': current_user.has_house,
        'has_car': current_user.has_car,
        'contact_name': current_user.contact_name,
        'contact_phone': current_user.contact_phone
    }
    
    credit_result = calculate_credit_score(profile_data, current_user.username)
    current_user.credit_score = credit_result['total_score']
    current_user.is_profile_completed = True
    
    # 保存信用分记录
    credit_score_record = CreditScore(
        user_id=current_user.id,
        score=credit_result['total_score'],
        details=credit_result['details'],
        level=credit_result['level'],
        version="1.0"
    )
    db.add(credit_score_record)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@app.get("/credit/calculate")
async def calculate_credit_score_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(lambda: next(get_db_session("user_service")))
):
    """计算信用分详情"""
    profile_data = {
        'real_name': current_user.real_name,
        'id_card': current_user.id_card,
        'phone': current_user.phone,
        'education': current_user.education,
        'marital_status': current_user.marital_status,
        'work_status': current_user.work_status,
        'income': current_user.income,
        'has_house': current_user.has_house,
        'has_car': current_user.has_car,
        'contact_name': current_user.contact_name,
        'contact_phone': current_user.contact_phone
    }
    
    credit_result = calculate_credit_score(profile_data, current_user.username)
    
    return {
        "success": True,
        "data": credit_result
    }


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(lambda: next(get_db_session("user_service")))
):
    """根据ID获取用户信息（内部服务调用）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@app.get("/users/username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(lambda: next(get_db_session("user_service")))
):
    """根据用户名获取用户信息（内部服务调用）"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "user-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

