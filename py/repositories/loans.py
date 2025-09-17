from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models import User, Loan, Repayment


def create_loan(
    db: Session,
    user: User,
    loan_id: str,
    amount: float,
    term_days_or_months: int,
    repay_method: str,
    status: str,
    monthly_payment: float,
    approve_date: Optional[str],
    next_payment_date: Optional[str],
    remaining_amount: float,
) -> Loan:
    loan = Loan(
        loan_id=loan_id,
        user_id=user.id,
        amount=Decimal(str(amount)),
        term_months=term_days_or_months if term_days_or_months > 31 else term_days_or_months,
        interest_rate=Decimal("0.0412"),
        repay_method=repay_method,
        status=status,
        remaining_amount=Decimal(str(remaining_amount)),
        next_payment_date=datetime.strptime(next_payment_date, "%Y-%m-%d").date() if next_payment_date else None,
        approved_at=datetime.strptime(approve_date, "%Y-%m-%d") if approve_date else None,
    )
    db.add(loan)
    db.flush()
    return loan


def list_loans_by_username(db: Session, username: str) -> List[Loan]:
    stmt = select(Loan).join(User, Loan.user_id == User.id).where(User.username == username)
    return db.execute(stmt).scalars().all()


def approve_loan(db: Session, loan_id: str, approved: bool, next_payment_date: Optional[str], remaining_amount: Optional[float]) -> Optional[Loan]:
    stmt = select(Loan).where(Loan.loan_id == loan_id)
    loan = db.execute(stmt).scalars().first()
    if not loan:
        return None
    loan.status = 'approved' if approved else 'rejected'
    loan.approved_at = datetime.utcnow()
    if approved:
        if next_payment_date:
            loan.next_payment_date = datetime.strptime(next_payment_date, "%Y-%m-%d").date()
        if remaining_amount is not None:
            loan.remaining_amount = Decimal(str(remaining_amount))
    db.flush()
    return loan


def add_repayment(db: Session, username: str, loan_id: str, amount: float) -> Tuple[Optional[Repayment], Optional[Loan]]:
    loan_stmt = select(Loan).join(User, Loan.user_id == User.id).where(Loan.loan_id == loan_id, User.username == username)
    loan = db.execute(loan_stmt).scalars().first()
    if not loan:
        return None, None
    pay_amount = Decimal(str(amount))
    remaining = (loan.remaining_amount or Decimal('0')) - pay_amount
    if remaining < 0:
        pay_amount = (loan.remaining_amount or Decimal('0'))
        remaining = Decimal('0')
    loan.remaining_amount = remaining
    if remaining <= 0:
        loan.status = 'completed'
    repayment = Repayment(
        loan_id=loan.id,
        due_date=loan.next_payment_date or date.today(),
        due_amount=pay_amount,
        paid_date=date.today(),
        paid_amount=pay_amount,
        status='completed',
    )
    db.add(repayment)
    db.flush()
    return repayment, loan


def stats_totals(db: Session) -> dict:
    # 用户数
    user_count = db.execute(select(func.count(User.id))).scalar() or 0
    # 贷款总额
    total_loan_amount = db.execute(select(func.coalesce(func.sum(Loan.amount), 0))).scalar() or 0
    # 待还总额
    pending_total = db.execute(select(func.coalesce(func.sum(Loan.remaining_amount), 0))).scalar() or 0
    # 已还总额（以还款表累计）
    repaid_total = db.execute(select(func.coalesce(func.sum(Repayment.paid_amount), 0))).scalar() or 0
    return {
        'userCount': int(user_count),
        'totalLoanAmount': float(total_loan_amount),
        'pendingRepayAmount': float(pending_total),
        'repaidAmount': float(repaid_total),
    }




