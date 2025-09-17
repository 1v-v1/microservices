#!/usr/bin/env python3
"""
微服务数据库初始化脚本
创建所有微服务需要的数据库表
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from shared.config.settings import settings
from shared.models import (
    User, CreditScore, Loan, Repayment,
    Blacklist, RiskAssessment, FraudDetection, RiskRule, RiskEvent,
    Notification, NotificationTemplate, NotificationChannel, NotificationStats,
    FileInfo, FileProcess, FileAccess, FileStorage
)

def create_databases():
    """创建各个微服务的数据库"""
    base_url = settings.database_url.rsplit('/', 1)[0] + '/'
    
    # 数据库列表
    databases = [
        'user_service',
        'loan_service', 
        'repayment_service',
        'risk_service',
        'notification_service',
        'file_service'
    ]
    
    # 创建主数据库引擎
    main_engine = create_engine(base_url + 'postgres', future=True)
    
    for db_name in databases:
        try:
            # 检查数据库是否存在
            with main_engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ), {"db_name": db_name})
                
                if not result.fetchone():
                    # 创建数据库
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"✅ 数据库 {db_name} 创建成功")
                else:
                    print(f"ℹ️  数据库 {db_name} 已存在")
        except Exception as e:
            print(f"❌ 创建数据库 {db_name} 失败: {e}")

def create_tables():
    """创建所有表"""
    databases = {
        'user_service': [User, CreditScore],
        'loan_service': [Loan, Repayment],
        'repayment_service': [Loan, Repayment],
        'risk_service': [Blacklist, RiskAssessment, FraudDetection, RiskRule, RiskEvent],
        'notification_service': [Notification, NotificationTemplate, NotificationChannel, NotificationStats],
        'file_service': [FileInfo, FileProcess, FileAccess, FileStorage]
    }
    
    base_url = settings.database_url.rsplit('/', 1)[0] + '/'
    
    for db_name, models in databases.items():
        try:
            # 创建数据库引擎
            database_url = base_url + db_name
            engine = create_engine(database_url, future=True)
            
            # 创建所有表
            for model in models:
                model.metadata.create_all(engine)
            
            print(f"✅ 数据库 {db_name} 表创建成功")
            
        except Exception as e:
            print(f"❌ 创建数据库 {db_name} 表失败: {e}")

def insert_initial_data():
    """插入初始数据"""
    base_url = settings.database_url.rsplit('/', 1)[0] + '/'
    
    # 为通知服务插入默认模板
    try:
        database_url = base_url + 'notification_service'
        engine = create_engine(database_url, future=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # 检查是否已有模板
            existing_templates = db.query(NotificationTemplate).count()
            if existing_templates == 0:
                # 插入默认模板
                templates = [
                    NotificationTemplate(
                        id="loan_approved",
                        name="贷款批准通知",
                        subject="恭喜！您的贷款申请已批准",
                        content="<h2>贷款申请批准通知</h2><p>尊敬的客户，您的贷款申请已通过审批，贷款金额：{{amount}}元，请及时查看详情。</p>",
                        channel="email",
                        variables=["amount", "loan_id"]
                    ),
                    NotificationTemplate(
                        id="loan_rejected",
                        name="贷款拒绝通知",
                        subject="贷款申请结果通知",
                        content="<h2>贷款申请结果通知</h2><p>很抱歉，您的贷款申请未通过审批。原因：{{reason}}。如有疑问，请联系客服。</p>",
                        channel="email",
                        variables=["reason"]
                    ),
                    NotificationTemplate(
                        id="repayment_reminder",
                        name="还款提醒",
                        subject="还款提醒",
                        content="<h2>还款提醒</h2><p>您有一笔贷款即将到期，请及时还款。还款金额：{{amount}}元，到期日期：{{due_date}}。</p>",
                        channel="all",
                        variables=["amount", "due_date"]
                    ),
                    NotificationTemplate(
                        id="repayment_overdue",
                        name="逾期通知",
                        subject="贷款逾期通知",
                        content="<h2>贷款逾期通知</h2><p>您的贷款已逾期，请尽快还款。逾期金额：{{amount}}元，逾期天数：{{overdue_days}}天。</p>",
                        channel="all",
                        variables=["amount", "overdue_days"]
                    )
                ]
                
                for template in templates:
                    db.add(template)
                
                db.commit()
                print("✅ 通知模板初始化成功")
            else:
                print("ℹ️  通知模板已存在，跳过初始化")
                
    except Exception as e:
        print(f"❌ 初始化通知模板失败: {e}")

def main():
    """主函数"""
    print("🚀 开始初始化微服务数据库...")
    
    # 1. 创建数据库
    print("\n📊 创建数据库...")
    create_databases()
    
    # 2. 创建表
    print("\n📋 创建表结构...")
    create_tables()
    
    # 3. 插入初始数据
    print("\n📝 插入初始数据...")
    insert_initial_data()
    
    print("\n✅ 数据库初始化完成！")
    print("\n📋 数据库列表:")
    print("  - user_service: 用户服务数据库")
    print("  - loan_service: 贷款服务数据库")
    print("  - repayment_service: 还款服务数据库")
    print("  - risk_service: 风控服务数据库")
    print("  - notification_service: 通知服务数据库")
    print("  - file_service: 文件服务数据库")

if __name__ == "__main__":
    main()
