from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Date
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Loan(Base):
    """贷款模型"""
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    loan_id = Column(String(64), unique=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
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


class Repayment(Base):
    """还款模型"""
    __tablename__ = 'repayments'

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, nullable=False, index=True)
    due_date = Column(Date, nullable=False)
    due_amount = Column(Numeric(14, 2), nullable=False)
    paid_date = Column(Date)
    paid_amount = Column(Numeric(14, 2))
    status = Column(String(16), index=True)  # due/paid/overdue

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

