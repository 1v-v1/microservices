from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import User


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalars().first()


def verify_password(plain_password: str, password_hash: str) -> bool:
    import bcrypt
    try:
        if password_hash.startswith("$2b$"):
            return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
        # 兼容老数据（不推荐生产使用）
        return plain_password == password_hash
    except Exception:
        return False


def create_user(db: Session, username: str, password: str) -> User:
    import bcrypt
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(
        username=username,
        password_hash=hashed,
        creditScore=700,
        loanLimit=50000,
        totalBorrowed=0,
        pendingRepay=0,
        isProfileCompleted=False,
    )
    db.add(user)
    db.flush()
    return user


def list_users_without_password(db: Session) -> List[Dict[str, Any]]:
    users = db.execute(select(User)).scalars().all()
    result: List[Dict[str, Any]] = []
    for u in users:
        result.append({
            "username": u.username,
            "realName": u.realName or "",
            "idCard": u.idCard or "",
            "phone": u.phone or "",
            "bankCard": "",  # 未迁移到表结构，保持兼容为空
            "bankName": "",
            "bankCode": "",
            "monthlyIncome": str(u.monthlyIncome) if hasattr(u, 'monthlyIncome') else "0",
            "creditScore": str(u.creditScore or 700),
            "loanLimit": str(u.loanLimit or 50000),
            "totalBorrowed": str(u.totalBorrowed or 0),
            "pendingRepay": str(u.pendingRepay or 0),
            "isProfileCompleted": 'true' if (u.isProfileCompleted or False) else 'false',
            "education": u.education or "",
            "school": u.school or "",
            "maritalStatus": u.maritalStatus or "",
            "workStatus": u.workStatus or "",
            "company": u.company or "",
            "position": u.position or "",
            "income": u.income or "",
            "hasHouse": 'true' if (u.hasHouse or False) else 'false',
            "hasCar": 'true' if (u.hasCar or False) else 'false',
            "contactName": u.contactName or "",
            "contactPhone": u.contactPhone or "",
            "relation": u.relation or "",
            "avatar": u.avatar or "",
        })
    return result


def update_user_profile(db: Session, username: str, payload: Dict[str, Any]) -> bool:
    user = get_user_by_username(db, username)
    if not user:
        return False
    # 基本信息
    user.realName = payload.get('realName', user.realName)
    user.idCard = payload.get('idCard', user.idCard)
    user.phone = payload.get('phone', user.phone)
    # 详细信息
    user.education = payload.get('education', user.education)
    user.school = payload.get('school', user.school)
    user.maritalStatus = payload.get('maritalStatus', user.maritalStatus)
    user.workStatus = payload.get('workStatus', user.workStatus)
    user.company = payload.get('company', user.company)
    user.position = payload.get('position', user.position)
    user.income = payload.get('income', user.income)
    # 资产布尔
    has_house = payload.get('hasHouse')
    has_car = payload.get('hasCar')
    if has_house is not None:
        user.hasHouse = True if str(has_house).lower() == 'true' else False
    if has_car is not None:
        user.hasCar = True if str(has_car).lower() == 'true' else False
    # 联系人
    user.contactName = payload.get('contactName', user.contactName)
    user.contactPhone = payload.get('contactPhone', user.contactPhone)
    user.relation = payload.get('relation', user.relation)
    # 状态
    user.isProfileCompleted = True
    db.flush()
    return True


def update_user_avatar_path(db: Session, username: str, avatar_url: str) -> bool:
    user = get_user_by_username(db, username)
    if not user:
        return False
    user.avatar = avatar_url
    db.flush()
    return True