# 共享数据模型

from .user import User, CreditScore
from .loan import Loan, Repayment
from .risk import Blacklist, RiskAssessment, FraudDetection, RiskRule, RiskEvent
from .notification import Notification, NotificationTemplate, NotificationChannel, NotificationStats
from .file import FileInfo, FileProcess, FileAccess, FileStorage

__all__ = [
    # User models
    'User', 'CreditScore',
    # Loan models
    'Loan', 'Repayment',
    # Risk models
    'Blacklist', 'RiskAssessment', 'FraudDetection', 'RiskRule', 'RiskEvent',
    # Notification models
    'Notification', 'NotificationTemplate', 'NotificationChannel', 'NotificationStats',
    # File models
    'FileInfo', 'FileProcess', 'FileAccess', 'FileStorage'
]
