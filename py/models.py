from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    realName = Column(String(64))
    idCard = Column(String(32), index=True)
    phone = Column(String(20), unique=True, index=True)

    # 详细信息
    education = Column(String(32))
    school = Column(String(128))
    maritalStatus = Column(String(16))
    workStatus = Column(String(32))
    company = Column(String(128))
    position = Column(String(64))
    income = Column(String(32))
    hasHouse = Column(Boolean)
    hasCar = Column(Boolean)
    contactName = Column(String(64))
    contactPhone = Column(String(20))
    relation = Column(String(32))
    avatar = Column(String(256))

    # 聚合与状态
    creditScore = Column(Integer, index=True)
    isProfileCompleted = Column(Boolean, default=False, index=True)
    loanLimit = Column(Numeric(14, 2), default=0)
    totalBorrowed = Column(Numeric(14, 2), default=0)
    pendingRepay = Column(Numeric(14, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    loans = relationship('Loan', back_populates='user')


class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    loan_id = Column(String(64), unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    term_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(7, 4), default=0)
    repay_method = Column(String(32), default='equal-installment')
    status = Column(String(32), index=True)  # pending/approved/rejected/settled
    remaining_amount = Column(Numeric(14, 2), default=0)
    next_payment_date = Column(Date)
    approved_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='loans')
    repayments = relationship('Repayment', back_populates='loan')


class Repayment(Base):
    __tablename__ = 'repayments'

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey('loans.id'), nullable=False, index=True)
    due_date = Column(Date, nullable=False)
    due_amount = Column(Numeric(14, 2), nullable=False)
    paid_date = Column(Date)
    paid_amount = Column(Numeric(14, 2))
    status = Column(String(16), index=True)  # due/paid/overdue

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    loan = relationship('Loan', back_populates='repayments')


class CreditScore(Base):
    __tablename__ = 'credit_scores'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    details = Column(JSONB)  # 评分构成明细
    level = Column(String(16))
    version = Column(String(16))
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


