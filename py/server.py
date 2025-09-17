import csv
import bcrypt
import json
import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import calendar
from io import StringIO
from sqlalchemy.orm import Session

# DB & repositories
from db import SessionLocal
from repositories.users import (
    get_user_by_username,
    verify_password,
    create_user,
    list_users_without_password,
    update_user_profile as repo_update_user_profile,
    update_user_avatar_path,
)
from models import User
from repositories.loans import (
    create_loan,
    list_loans_by_username,
    approve_loan,
    add_repayment,
    stats_totals,
)

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True, methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"], allow_headers=["Content-Type", "Authorization"])

# 获取当前脚本所在目录的绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 存储用户数据的 CSV 文件路径
USERS_CSV = os.path.join(CURRENT_DIR, "users.csv")
LOANS_CSV = os.path.join(CURRENT_DIR, "loans.csv")
REPAYMENTS_CSV = os.path.join(CURRENT_DIR, "repayments.csv")
ADMINS_CSV = os.path.join(CURRENT_DIR, "admins.csv")

# 确保所有CSV文件存在
def ensure_files_exist():
    # 确保users.csv存在并含有正确的字段
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'password', 'realName', 'idCard', 'phone', 
                         'bankCard', 'bankName', 'bankCode', 'monthlyIncome', 
                         'creditScore', 'loanLimit', 'totalBorrowed', 'pendingRepay', 'isProfileCompleted',
                         'education', 'school', 'maritalStatus', 'workStatus', 'company', 'position', 
                         'income', 'hasHouse', 'hasCar', 'contactName', 'contactPhone', 'relation', 'avatar']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    # 确保loans.csv存在并含有正确的字段
    if not os.path.exists(LOANS_CSV):
        with open(LOANS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['loan_id', 'username', 'loan_amount', 'loan_term', 'interest_rate', 
                         'monthly_payment', 'status', 'apply_date', 'approve_date', 
                         'remaining_amount', 'next_payment_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    # 确保repayments.csv存在并含有正确的字段
    if not os.path.exists(REPAYMENTS_CSV):
        with open(REPAYMENTS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['repayment_id', 'loan_id', 'username', 'amount', 'payment_date', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
    # 确保admins.csv存在并含有正确的字段
    if not os.path.exists(ADMINS_CSV):
        with open(ADMINS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'password', 'name', 'role']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # 添加默认管理员账号
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            writer.writerow({
                'username': 'admin',
                'password': hashed_password.decode('utf-8'),
                'name': '系统管理员',
                'role': 'admin'
            })

# 登录验证函数，比对哈希后的密码
def login(username, password):
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                # 验证密码是否以$2b$开头，这是bcrypt哈希的标志
                if row['password'].startswith('$2b$'):
                    stored_password = row['password'].encode('utf-8')
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        # 返回用户信息（不包含密码），并确保所有值都是字符串
                        user_info = {}
                        for k, v in row.items():
                            if k != 'password':
                                user_info[k] = str(v) if v is not None else ''
                        return user_info
                else:
                    # 兼容旧的未哈希密码（不推荐用于生产环境）
                    if row['password'] == password:
                        # 返回用户信息（不包含密码），并确保所有值都是字符串
                        user_info = {}
                        for k, v in row.items():
                            if k != 'password':
                                user_info[k] = str(v) if v is not None else ''
                        return user_info
    return None

# 审核贷款函数(计算等额本息和等额本金)（若三分之二的收入小于还款额，则不通过）
def judge(income, loan_amount, time, repay_method='equal-installment'):
    annual_rate = 0.0412  # 年化利率4.12%
    
    # 根据贷款期限的不同采用不同的计算方式
    if time <= 31:  # 如果是按天计算（短期贷款）
        # 对于短期贷款，使用简单的总利息计算方式
        daily_rate = annual_rate / 365  # 日利率
        total_interest = loan_amount * daily_rate * time  # 总利息
        total_amount = loan_amount + total_interest  # 总还款金额
        monthly_payment = total_amount  # 短期贷款一次性还款
    elif time == 90:  # 3个月
        months = 3
        monthly_rate = annual_rate / 12  # 月利率
        if repay_method == 'equal-principal':  # 等额本金
            # 每月本金
            monthly_principal = loan_amount / months
            # 首月利息
            first_month_interest = loan_amount * monthly_rate
            # 首月还款额（等额本金首月还款额最高）
            monthly_payment = monthly_principal + first_month_interest
        else:  # 等额本息
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    elif time == 180:  # 6个月
        months = 6
        monthly_rate = annual_rate / 12  # 月利率
        if repay_method == 'equal-principal':  # 等额本金
            monthly_principal = loan_amount / months
            first_month_interest = loan_amount * monthly_rate
            monthly_payment = monthly_principal + first_month_interest
        else:  # 等额本息
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    elif time == 365:  # 12个月
        months = 12
        monthly_rate = annual_rate / 12  # 月利率
        if repay_method == 'equal-principal':  # 等额本金
            monthly_principal = loan_amount / months
            first_month_interest = loan_amount * monthly_rate
            monthly_payment = monthly_principal + first_month_interest
        else:  # 等额本息
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:  # 按月计算（长期贷款），time就是月数
        months = time
        monthly_rate = annual_rate / 12  # 月利率
        if repay_method == 'equal-principal':  # 等额本金
            monthly_principal = loan_amount / months
            first_month_interest = loan_amount * monthly_rate
            monthly_payment = monthly_principal + first_month_interest
        else:  # 等额本息
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    
    if float(income) * 2 / 3 < monthly_payment:
        return 0, monthly_payment
    return 1, monthly_payment

# 注册功能函数，对密码哈希处理
def register(username, password):
    ensure_files_exist()
    
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                return False

    # 密码哈希处理
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # 添加新用户
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'password', 'realName', 'idCard', 'phone', 
                     'bankCard', 'bankName', 'bankCode', 'monthlyIncome', 
                     'creditScore', 'loanLimit', 'totalBorrowed', 'pendingRepay', 'isProfileCompleted',
                     'education', 'school', 'maritalStatus', 'workStatus', 'company', 'position', 
                     'income', 'hasHouse', 'hasCar', 'contactName', 'contactPhone', 'relation', 'avatar']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # 如果文件是空的，写入表头
        if os.path.getsize(USERS_CSV) == 0:
            writer.writeheader()
        
        new_user = {
            'username': username, 
            'password': hashed_password.decode('utf-8'),
            'realName': '',
            'idCard': '',
            'phone': '',
            'bankCard': '',
            'bankName': '',
            'bankCode': '',
            'monthlyIncome': '0',
            'creditScore': '700',
            'loanLimit': '50000',
            'totalBorrowed': '0',
            'pendingRepay': '0',
            'isProfileCompleted': 'false',
            'education': '',
            'school': '',
            'maritalStatus': '',
            'workStatus': '',
            'company': '',
            'position': '',
            'income': '',
            'hasHouse': 'false',
            'hasCar': 'false',
            'contactName': '',
            'contactPhone': '',
            'relation': '',
            'avatar': ''
        }
        writer.writerow(new_user)
    return True

# 信用分计算函数
def calculate_credit_score(profile_data, username=None):
    """
    基于用户详细信息计算信用分
    满分750分，及格分550分
    """
    base_score = 480  # 基础分
    
    # 如果没有任何信息，基于用户名生成一个基础的差异化分数
    if not any([profile_data.get('education'), profile_data.get('workStatus'), 
                profile_data.get('income'), profile_data.get('maritalStatus')]):
        if username:
            # 基于用户名生成一个伪随机但固定的分数差异
            import hashlib
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
    marital_score = marital_scores.get(profile_data.get('maritalStatus', ''), 0)
    
    # 工作状态加分 (-30到60分)
    work_scores = {
        '在职员工': 60,
        '个体经营': 40,
        '自由职业': 25,
        '学生': 15,
        '退休': 45,
        '待业': -30
    }
    work_score = work_scores.get(profile_data.get('workStatus', ''), 0)
    
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
    if profile_data.get('hasHouse') == True or profile_data.get('hasHouse') == 'true':
        asset_score += 60  # 有房产
    if profile_data.get('hasCar') == True or profile_data.get('hasCar') == 'true':
        asset_score += 30   # 有车辆
    
    # 联系人信息完整性加分 (0-25分)
    contact_score = 0
    if profile_data.get('contactName') and profile_data.get('contactPhone'):
        contact_score = 25
    
    # 基本信息完整性加分 (0-35分)
    basic_info_score = 0
    if profile_data.get('realName'):
        basic_info_score += 10
    if profile_data.get('idCard'):
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

def get_credit_level(score):
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

# 更新用户资料
def update_profile(username, profile_data):
    if not username:
        return {"success": False, "message": "用户名不能为空"}
    
    # 检查用户是否存在
    user_exists = False
    rows = []
    
    # 定义所有必需的字段
    fieldnames = ['username', 'password', 'realName', 'idCard', 'phone', 
                 'bankCard', 'bankName', 'bankCode', 'monthlyIncome', 
                 'creditScore', 'loanLimit', 'totalBorrowed', 'pendingRepay', 'isProfileCompleted',
                 'education', 'school', 'maritalStatus', 'workStatus', 'company', 'position', 
                 'income', 'hasHouse', 'hasCar', 'contactName', 'contactPhone', 'relation']
    
    try:
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if row['username'] == username:
                    # 合并现有数据和新数据
                    merged_data = {
                        'realName': profile_data.get('realName', row.get('realName', '')),
                        'idCard': profile_data.get('idCard', row.get('idCard', '')),
                        'phone': profile_data.get('phone', row.get('phone', '')),
                        'bankCard': profile_data.get('bankCard', row.get('bankCard', '')),
                        'bankName': profile_data.get('bankName', row.get('bankName', '')),
                        'bankCode': profile_data.get('bankCode', row.get('bankCode', '')),
                        'monthlyIncome': profile_data.get('monthlyIncome', row.get('monthlyIncome', '0')),
                        'education': profile_data.get('education', row.get('education', '')),
                        'school': profile_data.get('school', row.get('school', '')),
                        'maritalStatus': profile_data.get('maritalStatus', row.get('maritalStatus', '')),
                        'workStatus': profile_data.get('workStatus', row.get('workStatus', '')),
                        'company': profile_data.get('company', row.get('company', '')),
                        'position': profile_data.get('position', row.get('position', '')),
                        'income': profile_data.get('income', row.get('income', '')),
                        'hasHouse': str(profile_data.get('hasHouse', row.get('hasHouse', 'false'))).lower(),
                        'hasCar': str(profile_data.get('hasCar', row.get('hasCar', 'false'))).lower(),
                        'contactName': profile_data.get('contactName', row.get('contactName', '')),
                        'contactPhone': profile_data.get('contactPhone', row.get('contactPhone', '')),
                        'relation': profile_data.get('relation', row.get('relation', ''))
                    }
                    
                    # 计算信用分
                    credit_result = calculate_credit_score(merged_data, username)
                    new_credit_score = credit_result['total_score']
                    
                    # 更新用户资料，为每个字段提供默认值
                    updated_row = {
                        'username': username,
                        'password': row.get('password', ''),
                        'realName': merged_data['realName'],
                        'idCard': merged_data['idCard'],
                        'phone': merged_data['phone'],
                        'bankCard': merged_data['bankCard'],
                        'bankName': merged_data['bankName'],
                        'bankCode': merged_data['bankCode'],
                        'monthlyIncome': merged_data['monthlyIncome'],
                        'creditScore': str(new_credit_score),  # 使用计算出的信用分
                        'loanLimit': row.get('loanLimit', '50000'),
                        'totalBorrowed': row.get('totalBorrowed', '0'),
                        'pendingRepay': row.get('pendingRepay', '0'),
                        'isProfileCompleted': 'true',
                        'education': merged_data['education'],
                        'school': merged_data['school'],
                        'maritalStatus': merged_data['maritalStatus'],
                        'workStatus': merged_data['workStatus'],
                        'company': merged_data['company'],
                        'position': merged_data['position'],
                        'income': merged_data['income'],
                        'hasHouse': merged_data['hasHouse'],
                        'hasCar': merged_data['hasCar'],
                        'contactName': merged_data['contactName'],
                        'contactPhone': merged_data['contactPhone'],
                        'relation': merged_data['relation']
                    }
                    rows.append(updated_row)
                    user_exists = True
                else:
                    # 确保其他行的数据也包含所有必需字段
                    current_row = {field: row.get(field, '') for field in fieldnames}
                    rows.append(current_row)
        
        if not user_exists:
            return {"success": False, "message": "用户不存在"}
        
        # 将更新后的数据写回CSV文件
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return {"success": True, "message": "个人资料更新成功"}
        
    except Exception as e:
        return {"success": False, "message": f"更新失败：{str(e)}"}

# 添加贷款记录
def add_loan(username, loan_data):
    try:
        db: Session = SessionLocal()
        user = get_user_by_username(db, username)
        if not user or not (user.isProfileCompleted or False):
            return {"message": "用户资料尚未完善或用户不存在"}, 400

        # 判断贷款审核结果
        monthly_income = float(getattr(user, 'monthlyIncome', 0) or 0)
        loan_amount = float(loan_data['loan_amount'])
        loan_term = int(loan_data['loan_term'])
        # 获取还款方式，默认为等额本息
        repay_method = loan_data.get('repay_method', 'equal-installment')

        approval_result, monthly_payment = judge(monthly_income, loan_amount, loan_term, repay_method)
        if approval_result == 0:
            return {"message": "贷款审核未通过，月收入不足以支付贷款", "approval_result": 0}, 400

        # 检查用户信用分，决定是否需要人工审批
        user_credit_score = int(getattr(user, 'creditScore', 700) or 700)
        need_manual_approval = user_credit_score < 700

        # 生成唯一的贷款ID
        loan_id = str(uuid.uuid4())
        current_date = datetime.now().strftime('%Y-%m-%d')

        # 设置贷款状态
        loan_status = 'pending' if need_manual_approval else 'approved'
        approve_date = current_date if not need_manual_approval else ''

        # 计算到期日 - 根据loan_term计算
        due_date = datetime.now()
        if loan_term <= 31:  # 如果小于等于31，视为天数
            due_date = due_date + timedelta(days=loan_term)
        elif loan_term == 90:  # 3个月，精确到天
            due_date = due_date + timedelta(days=90)
        elif loan_term == 180:  # 6个月，精确到天
            due_date = due_date + timedelta(days=180)
        elif loan_term == 365:  # 12个月，精确到天
            due_date = due_date + timedelta(days=365)
        else:  # 其他情况按月计算（如果是数字3、6、12等）
            # 处理跨月跨年的情况
            new_month = due_date.month + loan_term
            new_year = due_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            # 处理月末日期问题（如从1月31日加一个月，应为2月28/29日）
            last_day = calendar.monthrange(new_year, new_month)[1]
            new_day = min(due_date.day, last_day)
            due_date = due_date.replace(year=new_year, month=new_month, day=new_day)

        next_payment_date = due_date.strftime('%Y-%m-%d')

        # 写入数据库
        create_loan(
            db,
            user,
            loan_id=loan_id,
            amount=loan_amount,
            term_days_or_months=loan_term,
            repay_method=repay_method,
            status=loan_status,
            monthly_payment=round(monthly_payment, 2),
            approve_date=approve_date,
            next_payment_date=next_payment_date if loan_status == 'approved' else None,
            remaining_amount=loan_amount if loan_status == 'approved' else 0,
        )
        db.commit()

        # 只有自动批准的贷款才更新用户借款信息
        if loan_status == 'approved':
            user.totalBorrowed = (user.totalBorrowed or 0) + loan_amount
            user.pendingRepay = (user.pendingRepay or 0) + loan_amount
            db.commit()

        # 构建返回消息
        if need_manual_approval:
            message = f"贷款申请已提交，因您的信用分为{user_credit_score}分（低于700分），需要人工审批。请耐心等待审批结果。"
            approval_result_code = 2  # 2表示需要人工审批
        else:
            message = "贷款申请成功，已自动批准！"
            approval_result_code = 1  # 1表示自动批准

        return {
            "message": message,
            "approval_result": approval_result_code,
            "loan_id": loan_id,
            "monthly_payment": round(monthly_payment, 2),
            "need_manual_approval": need_manual_approval,
            "credit_score": user_credit_score,
            "status": loan_status
        }, 200
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        return {"message": f"申请失败: {str(e)}"}, 500
    finally:
        try:
            db.close()
        except Exception:
            pass


# 获取用户贷款列表
def get_user_loans(username):
    try:
        db: Session = SessionLocal()
        rows = list_loans_by_username(db, username)
        result = []
        for l in rows:
            result.append({
                'loan_id': l.loan_id,
                'username': username,
                'loan_amount': float(l.amount or 0),
                'loan_term': l.term_months or 0,
                'interest_rate': '4.12',
                'monthly_payment': '',
                'status': l.status,
                'apply_date': l.created_at.strftime('%Y-%m-%d') if l.created_at else '',
                'approve_date': l.approved_at.strftime('%Y-%m-%d') if l.approved_at else '',
                'remaining_amount': float(l.remaining_amount or 0),
                'next_payment_date': l.next_payment_date.strftime('%Y-%m-%d') if l.next_payment_date else '',
                'repay_method': l.repay_method,
            })
        return result
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    # CSV fallback
    loans = []
    with open(LOANS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                loans.append(row)
    return loans

# 还款功能
def make_repayment(username, repayment_data):
    loan_id = repayment_data.get('loan_id')
    amount = float(repayment_data.get('amount', 0))

    # DB first
    try:
        db: Session = SessionLocal()
        repayment, loan = add_repayment(db, username, loan_id, amount)
        if not loan:
            return {"message": "找不到对应的贷款记录"}, 400
        # 同步用户的待还金额
        user = get_user_by_username(db, username)
        if user:
            user.pendingRepay = max((user.pendingRepay or 0) - amount, 0)
        db.commit()
        return {
            "message": "还款成功",
            "repayment_id": str(repayment.id) if repayment else '',
            "amount": float(amount),
            "remaining_amount": float(loan.remaining_amount or 0),
            "status": loan.status
        }, 200
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass

    # CSV fallback（保留原实现）
    

# 获取用户还款记录
def get_user_repayments(username):
    repayments = []
    with open(REPAYMENTS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                repayments.append(row)
    return repayments

# 管理员登录验证函数
def admin_login(username, password):
    with open(ADMINS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                # 验证密码是否以$2b$开头，这是bcrypt哈希的标志
                if row['password'].startswith('$2b$'):
                    stored_password = row['password'].encode('utf-8')
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        # 返回管理员信息（不包含密码）
                        admin_info = {}
                        for k, v in row.items():
                            if k != 'password':
                                admin_info[k] = str(v) if v is not None else ''
                        return admin_info
                else:
                    # 兼容旧的未哈希密码（不推荐用于生产环境）
                    if row['password'] == password:
                        # 返回管理员信息（不包含密码）
                        admin_info = {}
                        for k, v in row.items():
                            if k != 'password':
                                admin_info[k] = str(v) if v is not None else ''
                        return admin_info
    return None

# 获取所有用户列表
def get_all_users():
    users = []
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 排除密码字段
            user_info = {k: v for k, v in row.items() if k != 'password'}
            users.append(user_info)
    return users

# 获取所有贷款列表
def get_all_loans():
    loans = []
    with open(LOANS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            loans.append(row)
    return loans

# 获取所有还款记录
def get_all_repayments():
    repayments = []
    with open(REPAYMENTS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repayments.append(row)
    return repayments

# 获取统计数据
def get_statistics_data():
    try:
        db: Session = SessionLocal()
        return stats_totals(db)
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    # CSV fallback
    users = get_all_users()
    user_count = len(users)
    loans = get_all_loans()
    total_loan_amount = sum(float(loan['loan_amount']) for loan in loans)
    pending_repay_amount = sum(float(user['pendingRepay']) for user in users if user['pendingRepay'])
    repayments = get_all_repayments()
    repaid_amount = sum(float(repayment['amount']) for repayment in repayments if repayment['status'] == 'completed')
    return {
        'userCount': user_count,
        'totalLoanAmount': total_loan_amount,
        'pendingRepayAmount': pending_repay_amount,
        'repaidAmount': repaid_amount
    }

# 更新用户信息（管理员接口）
def admin_update_user(username, user_data):
    if not username:
        return {"success": False, "message": "用户名不能为空"}
    
    # 检查用户是否存在
    user_exists = False
    rows = []
    
    # 定义所有必需的字段
    fieldnames = ['username', 'password', 'realName', 'idCard', 'phone', 
                 'bankCard', 'bankName', 'bankCode', 'monthlyIncome', 
                 'creditScore', 'loanLimit', 'totalBorrowed', 'pendingRepay', 'isProfileCompleted']
    
    try:
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if row['username'] == username:
                    # 更新用户资料，保留密码字段不变
                    updated_row = {
                        'username': username,
                        'password': row.get('password', ''),
                        'realName': user_data.get('realName', row.get('realName', '')),
                        'idCard': user_data.get('idCard', row.get('idCard', '')),
                        'phone': user_data.get('phone', row.get('phone', '')),
                        'bankCard': user_data.get('bankCard', row.get('bankCard', '')),
                        'bankName': user_data.get('bankName', row.get('bankName', '')),
                        'bankCode': user_data.get('bankCode', row.get('bankCode', '')),
                        'monthlyIncome': user_data.get('monthlyIncome', row.get('monthlyIncome', '0')),
                        'creditScore': user_data.get('creditScore', row.get('creditScore', '700')),
                        'loanLimit': user_data.get('loanLimit', row.get('loanLimit', '50000')),
                        'totalBorrowed': row.get('totalBorrowed', '0'),
                        'pendingRepay': row.get('pendingRepay', '0'),
                        'isProfileCompleted': 'true'
                    }
                    rows.append(updated_row)
                    user_exists = True
                else:
                    # 确保其他行的数据也包含所有必需字段
                    current_row = {field: row.get(field, '') for field in fieldnames}
                    rows.append(current_row)
        
        if not user_exists:
            return {"success": False, "message": "用户不存在"}
        
        # 将更新后的数据写回CSV文件
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return {"success": True, "message": "用户信息更新成功"}
        
    except Exception as e:
        return {"success": False, "message": f"更新失败：{str(e)}"}

# 删除用户
def admin_delete_user(username):
    if not username:
        return {"success": False, "message": "用户名不能为空"}
    
    # 检查用户是否存在
    user_exists = False
    rows = []
    
    try:
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            
            for row in reader:
                if row['username'] == username:
                    user_exists = True
                else:
                    rows.append(row)
        
        if not user_exists:
            return {"success": False, "message": "用户不存在"}
        
        # 将更新后的数据写回CSV文件
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return {"success": True, "message": "用户删除成功"}
        
    except Exception as e:
        return {"success": False, "message": f"删除失败：{str(e)}"}

# 审批贷款
def admin_approve_loan(loan_id, approval_data):
    if not loan_id:
        return {"success": False, "message": "贷款ID不能为空"}
    approved = approval_data.get('approved', False)

    # DB first
    try:
        db: Session = SessionLocal()
        # 计算下一期还款日与剩余金额
        next_payment_date = None
        remaining_amount = None
        if approved:
            # 无法直接取term，这里仅设置剩余金额在审批时覆盖为正数由前端或后续补算
            remaining_amount = 0.0
        loan = approve_loan(db, loan_id, approved, next_payment_date, remaining_amount)
        if not loan:
            return {"success": False, "message": "贷款不存在"}
        # 若批准，则同步用户聚合
        if approved:
            user = db.get(User, loan.user_id)
            if user:
                user.totalBorrowed = (user.totalBorrowed or 0) + float(loan.amount or 0)
                user.pendingRepay = (user.pendingRepay or 0) + float(loan.amount or 0)
        db.commit()
        return {"success": True, "message": "贷款审批成功", "status": "approved" if approved else "rejected"}
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    
    # CSV fallback（保留原实现）
    try:
        # 原CSV逻辑保留（简化省略）
        return {"success": False, "message": "CSV fallback not executed"}
    except Exception as e:
        return {"success": False, "message": f"审批失败：{str(e)}"}

@app.route('/login', methods=['POST'])
def user_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # DB first
    try:
        db: Session = SessionLocal()
        user = get_user_by_username(db, username)
        if user and verify_password(password, user.password_hash):
            user_info = {
                'username': user.username,
                'realName': user.realName or '',
                'idCard': user.idCard or '',
                'phone': user.phone or '',
                'monthlyIncome': '0',
                'creditScore': str(user.creditScore or 700),
                'loanLimit': str(user.loanLimit or 50000),
                'totalBorrowed': str(user.totalBorrowed or 0),
                'pendingRepay': str(user.pendingRepay or 0),
                'isProfileCompleted': 'true' if (user.isProfileCompleted or False) else 'false',
                'education': user.education or '',
                'school': user.school or '',
                'maritalStatus': user.maritalStatus or '',
                'workStatus': user.workStatus or '',
                'company': user.company or '',
                'position': user.position or '',
                'income': user.income or '',
                'hasHouse': 'true' if (user.hasHouse or False) else 'false',
                'hasCar': 'true' if (user.hasCar or False) else 'false',
                'contactName': user.contactName or '',
                'contactPhone': user.contactPhone or '',
                'relation': user.relation or '',
                'avatar': user.avatar or '',
            }
            return jsonify({
                "message": "登录成功",
                "userInfo": user_info
            })
    except Exception as e:
        # fallback to CSV if DB fails
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass

    # CSV fallback
    user_info = login(username, password)
    if user_info:
        return jsonify({
            "message": "登录成功",
            "userInfo": user_info
        })
    return jsonify({"message": "登录失败"}), 401

@app.route('/register', methods=['POST'])
def user_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # DB first
    try:
        db: Session = SessionLocal()
        if get_user_by_username(db, username):
            return jsonify({"message": "注册失败,该用户名已被使用"}), 400
        create_user(db, username, password)
        db.commit()
        return jsonify({"message": "注册成功，现可进行金融业务服务"})
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass

    # CSV fallback
    if register(username, password):
        return jsonify({"message": "注册成功，现可进行金融业务服务"})
    return jsonify({"message": "注册失败,该用户名已被使用"}), 400

@app.route('/user/profile', methods=['POST'])
def update_user_profile():
    # 这里应该有认证检查
    data = request.get_json()
    username = data.get('username')
    profile_data = {
        'realName': data.get('realName'),
        'idCard': data.get('idCard') or data.get('idNumber'),  # 支持两种字段名
        'phone': data.get('phone'),
        'education': data.get('education'),
        'school': data.get('school'),
        'maritalStatus': data.get('maritalStatus'),
        'workStatus': data.get('workStatus'),
        'company': data.get('company'),
        'position': data.get('position'),
        'income': data.get('income'),
        'hasHouse': data.get('hasHouse'),
        'hasCar': data.get('hasCar'),
        'contactName': data.get('contactName'),
        'contactPhone': data.get('contactPhone'),
        'relation': data.get('relation'),
    }

    # DB first
    try:
        db: Session = SessionLocal()
        ok = update_user_profile(db, username, profile_data)
        if ok:
            db.commit()
            return jsonify({"success": True, "message": "个人资料更新成功"})
        db.rollback()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass

    # CSV fallback
    result = update_profile(username, profile_data)
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 400

@app.route('/user/info', methods=['GET'])
def get_user_info():
    username = request.args.get('username')
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                # 不返回密码，并确保所有值都是字符串
                user_info = {
                    k: (v if v is not None else '') 
                    for k, v in row.items() 
                    if k != 'password'
                }
                return jsonify({"userInfo": user_info})
    return jsonify({"message": "用户不存在"}), 404

@app.route('/loan/apply', methods=['POST'])
def loan_apply():
    # 这里应该有认证检查
    data = request.get_json()
    username = data.get('username')
    loan_data = {
        'loan_amount': data.get('loan_amount'),
        'loan_term': data.get('loan_term'),
        'repay_method': data.get('repay_method', 'equal-installment')  # 添加还款方式参数，默认等额本息
    }
    
    result, status_code = add_loan(username, loan_data)
    return jsonify(result), status_code

@app.route('/loan/list', methods=['GET'])
def loan_list():
    username = request.args.get('username')
    loans = get_user_loans(username)
    return jsonify({"loans": loans})

# 新增API路由 - 前端调用的接口
@app.route('/api/user/loans', methods=['GET'])
def api_user_loans():
    # 从Authorization header获取token，解析用户名
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "需要认证"}), 401
    
    # 简化处理：从query参数获取用户名
    # 在实际应用中，应该从token中解析用户名
    username = request.args.get('username')
    
    # 如果没有用户名参数，尝试从token中获取（简化示例）
    if not username:
        # 为了演示，这里返回一个测试用户的数据
        # 实际应用中应该从token解析用户信息
        token = auth_header.replace('Bearer ', '')
        # 这里可以添加token验证逻辑
        # 为了测试，我们返回一个默认用户
        username = '18727546918'  # 测试用户
        
    if not username:
        return jsonify({"message": "用户未登录或token无效"}), 401
    
    loans = get_user_loans(username)
    return jsonify({"loans": loans})

@app.route('/loan/repay', methods=['POST'])
def loan_repay():
    # 这里应该有认证检查
    data = request.get_json()
    username = data.get('username')
    repayment_data = {
        'loan_id': data.get('loan_id'),
        'amount': data.get('amount'),
        'periods': data.get('periods', 1),
        'payment_method': data.get('paymentMethod', 'alipay')
    }
    
    result, status_code = make_repayment(username, repayment_data)
    return jsonify(result), status_code

@app.route('/repayment/list', methods=['GET'])
def repayment_list():
    username = request.args.get('username')
    repayments = get_user_repayments(username)
    return jsonify({"repayments": repayments})

# 管理员API路由
@app.route('/admin/login', methods=['POST'])
def admin_login_route():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    admin_info = admin_login(username, password)
    if admin_info:
        # 生成简单的token（实际应用中应使用JWT等安全机制）
        token = str(uuid.uuid4())
        return jsonify({
            "message": "登录成功",
            "token": token,
            "adminInfo": admin_info
        })
    return jsonify({"message": "登录失败，用户名或密码错误"}), 401

@app.route('/admin/users', methods=['GET'])
def admin_get_users():
    # 这里应该有认证检查
    try:
        db: Session = SessionLocal()
        users = list_users_without_password(db)
        return jsonify({"users": users})
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    # CSV fallback
    users = get_all_users()
    return jsonify({"users": users})

@app.route('/admin/users/<username>', methods=['GET'])
def admin_get_user(username):
    # 这里应该有认证检查
    users = get_all_users()
    for user in users:
        if user['username'] == username:
            return jsonify({"user": user})
    return jsonify({"message": "用户不存在"}), 404

@app.route('/admin/users/<username>', methods=['PUT'])
def admin_update_user_route(username):
    # 这里应该有认证检查
    data = request.get_json()
    result = admin_update_user(username, data)
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 400

@app.route('/admin/users/<username>', methods=['DELETE'])
def admin_delete_user_route(username):
    # 这里应该有认证检查
    result = admin_delete_user(username)
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 400

@app.route('/admin/loans', methods=['GET'])
def admin_get_loans():
    # 这里应该有认证检查
    loans = get_all_loans()
    return jsonify({"loans": loans})

@app.route('/admin/loans/<loan_id>/approve', methods=['POST'])
def admin_approve_loan_route(loan_id):
    # 这里应该有认证检查
    data = request.get_json()
    result = admin_approve_loan(loan_id, data)
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 400

@app.route('/admin/repayments', methods=['GET'])
def admin_get_repayments():
    # 这里应该有认证检查
    repayments = get_all_repayments()
    return jsonify({"repayments": repayments})

@app.route('/admin/statistics', methods=['GET'])
def admin_get_statistics():
    # 这里应该有认证检查
    statistics = get_statistics_data()
    return jsonify({"data": statistics})

@app.route('/admin/export/users', methods=['GET'])
def admin_export_users():
    # 这里应该有认证检查
    try:
        db: Session = SessionLocal()
        # 从数据库导出
        from models import User
        rows = db.query(User).all()
        output = StringIO()
        fieldnames = ['username','realName','idCard','phone','monthlyIncome','creditScore','loanLimit','totalBorrowed','pendingRepay','isProfileCompleted','education','school','maritalStatus','workStatus','company','position','income','hasHouse','hasCar','contactName','contactPhone','relation','avatar']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for u in rows:
            writer.writerow({
                'username': u.username,
                'realName': u.realName or '',
                'idCard': u.idCard or '',
                'phone': u.phone or '',
                'monthlyIncome': '0',
                'creditScore': str(u.creditScore or 700),
                'loanLimit': str(u.loanLimit or 50000),
                'totalBorrowed': str(u.totalBorrowed or 0),
                'pendingRepay': str(u.pendingRepay or 0),
                'isProfileCompleted': 'true' if (u.isProfileCompleted or False) else 'false',
                'education': u.education or '',
                'school': u.school or '',
                'maritalStatus': u.maritalStatus or '',
                'workStatus': u.workStatus or '',
                'company': u.company or '',
                'position': u.position or '',
                'income': u.income or '',
                'hasHouse': 'true' if (u.hasHouse or False) else 'false',
                'hasCar': 'true' if (u.hasCar or False) else 'false',
                'contactName': u.contactName or '',
                'contactPhone': u.contactPhone or '',
                'relation': u.relation or '',
                'avatar': u.avatar or '',
            })
        return output.getvalue(), 200, {'Content-Type': 'text/csv; charset=utf-8'}
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    # 回退到文件
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        content = csvfile.read()
    return content, 200, {'Content-Type': 'text/csv; charset=utf-8'}

@app.route('/admin/export/loans', methods=['GET'])
def admin_export_loans():
    # 这里应该有认证检查
    try:
        db: Session = SessionLocal()
        from models import Loan, User
        loans = db.query(Loan).join(User, Loan.user_id == User.id).add_columns(User.username).all()
        output = StringIO()
        fieldnames = ['loan_id','username','loan_amount','loan_term','interest_rate','monthly_payment','status','apply_date','approve_date','remaining_amount','next_payment_date','repay_method']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for l, username in loans:
            writer.writerow({
                'loan_id': l.loan_id,
                'username': username,
                'loan_amount': float(l.amount or 0),
                'loan_term': l.term_months or 0,
                'interest_rate': '4.12',
                'monthly_payment': '',
                'status': l.status,
                'apply_date': l.created_at.strftime('%Y-%m-%d') if l.created_at else '',
                'approve_date': l.approved_at.strftime('%Y-%m-%d') if l.approved_at else '',
                'remaining_amount': float(l.remaining_amount or 0),
                'next_payment_date': l.next_payment_date.strftime('%Y-%m-%d') if l.next_payment_date else '',
                'repay_method': l.repay_method,
            })
        return output.getvalue(), 200, {'Content-Type': 'text/csv; charset=utf-8'}
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    with open(LOANS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        content = csvfile.read()
    return content, 200, {'Content-Type': 'text/csv; charset=utf-8'}

@app.route('/admin/export/repayments', methods=['GET'])
def admin_export_repayments():
    # 这里应该有认证检查
    try:
        db: Session = SessionLocal()
        from models import Repayment, Loan, User
        reps = db.query(Repayment, Loan, User).join(Loan, Repayment.loan_id == Loan.id).join(User, Loan.user_id == User.id).all()
        output = StringIO()
        fieldnames = ['repayment_id','loan_id','username','amount','payment_date','status']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for r, l, u in reps:
            writer.writerow({
                'repayment_id': r.id,
                'loan_id': l.loan_id,
                'username': u.username,
                'amount': float(r.paid_amount or 0),
                'payment_date': r.paid_date.strftime('%Y-%m-%d') if r.paid_date else '',
                'status': r.status,
            })
        return output.getvalue(), 200, {'Content-Type': 'text/csv; charset=utf-8'}
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    with open(REPAYMENTS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        content = csvfile.read()
    return content, 200, {'Content-Type': 'text/csv; charset=utf-8'}

# 新增：获取信用分计算详情API
@app.route('/api/credit/calculate', methods=['POST'])
def calculate_credit_score_api():
    try:
        data = request.get_json()
        
        # 计算信用分
        credit_result = calculate_credit_score(data)
        
        return jsonify({
            'success': True,
            'data': credit_result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'计算失败: {str(e)}'}), 500

# 新增：获取信用分计算规则API
@app.route('/api/credit/rules', methods=['GET'])
def get_credit_rules():
    rules = {
        'total_score': 750,
        'pass_score': 550,
        'base_score': 480,
        'rules': {
            'education': {
                'max_score': 120,
                'options': {
                    '初中及以下': 0,
                    '高中/中专': 25,
                    '大专': 50,
                    '本科': 80,
                    '硕士': 100,
                    '博士': 120
                }
            },
            'maritalStatus': {
                'max_score': 40,
                'min_score': -15,
                'options': {
                    '已婚': 40,
                    '未婚': 15,
                    '离异': -15,
                    '丧偶': 5
                }
            },
            'workStatus': {
                'max_score': 60,
                'min_score': -30,
                'options': {
                    '在职员工': 60,
                    '个体经营': 40,
                    '自由职业': 25,
                    '学生': 15,
                    '退休': 45,
                    '待业': -30
                }
            },
            'income': {
                'max_score': 120,
                'options': {
                    '3000以下': 0,
                    '3000-5000': 25,
                    '5000-8000': 50,
                    '8000-12000': 75,
                    '12000-20000': 100,
                    '20000以上': 120
                }
            },
            'assets': {
                'house_score': 60,
                'car_score': 30,
                'max_score': 90
            },
            'contact': {
                'complete_score': 25
            },
            'basic_info': {
                'realName_score': 10,
                'idCard_score': 15,
                'phone_score': 10,
                'max_score': 35
            }
        },
        'levels': {
            '优秀': '700分以上',
            '良好': '650-699分',
            '中等': '600-649分',
            '及格': '550-599分',
            '较差': '550分以下'
        }
    }
    
    return jsonify({
        'success': True,
        'data': rules
    }), 200

# 新增：更新用户信用分API
@app.route('/admin/users/<username>/credit', methods=['PUT'])
def update_user_credit_score(username):
    try:
        data = request.get_json()
        new_credit_score = data.get('creditScore')
        
        if not new_credit_score:
            return jsonify({'success': False, 'message': '信用分不能为空'}), 400
        
        # 更新用户信用分
        if update_user_credit_in_csv(username, new_credit_score):
            return jsonify({
                'success': True,
                'message': '信用分更新成功',
                'data': {'creditScore': new_credit_score}
            }), 200
        else:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

def update_user_credit_in_csv(username, credit_score):
    """更新CSV文件中用户的信用分"""
    try:
        rows = []
        user_found = False
        
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['username'] == username:
                    row['creditScore'] = str(credit_score)
                    user_found = True
                rows.append(row)
        
        if user_found:
            with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                if rows:
                    fieldnames = rows[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            return True
        
        return False
        
    except Exception as e:
        print(f"更新用户信用分失败: {e}")
        return False

# 新增：获取用户信用分详情API
@app.route('/api/user/<username>/credit', methods=['GET'])
def get_user_credit_detail(username):
    try:
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['username'] == username:
                    # 构建用户数据用于计算
                    user_data = {
                        'education': row.get('education', ''),
                        'maritalStatus': row.get('maritalStatus', ''),
                        'workStatus': row.get('workStatus', ''),
                        'income': row.get('income', ''),
                        'hasHouse': row.get('hasHouse', 'false'),
                        'hasCar': row.get('hasCar', 'false'),
                        'contactName': row.get('contactName', ''),
                        'contactPhone': row.get('contactPhone', '')
                    }
                    
                    # 计算信用分详情
                    credit_result = calculate_credit_score(user_data, username)
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'username': username,
                            'current_score': int(row.get('creditScore', 700)),
                            'calculated_score': credit_result['total_score'],
                            'level': credit_result['level'],
                            'details': credit_result['details'],
                            'user_data': user_data
                        }
                    }), 200
        
        return jsonify({'success': False, 'message': '用户不存在'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500

# 新增：用户详细信息更新API
@app.route('/api/user/update-info', methods=['POST'])
def update_user_detailed_info():
    try:
        data = request.get_json()
        print(f"收到的数据: {data}")  # 调试日志
        
        # 这里简化处理，实际应用中需要从token中获取用户名
        # 临时处理：从请求头或数据中获取用户标识
        auth_header = request.headers.get('Authorization')
        print(f"Authorization header: {auth_header}")  # 调试日志
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权访问'}), 401
        
        # 获取最后一个有用户信息的用户（有完整数据的用户）
        username = None
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 查找有真实姓名的用户，这表明是一个活跃用户
                if row['username'] and row.get('realName') and row['realName'].strip():
                    username = row['username']
                # 如果没有找到有真实姓名的用户，使用testuser作为测试
                elif row['username'] == 'testuser':
                    username = 'testuser'
                    
        # 如果还是没有找到，使用第一个非空用户名
        if not username:
            with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['username'] and row['username'].strip():
                        username = row['username']
                        break
        
        print(f"使用的用户名: {username}")  # 调试日志
        
        if not username:
            return jsonify({'success': False, 'message': '系统中没有可用用户'}), 404
        
        # 准备要更新的数据
        profile_data = {
            'realName': data.get('realName'),
            'idCard': data.get('idCard') or data.get('idNumber'),  # 支持两种字段名
            'phone': data.get('phone'),
            'education': data.get('education'),
            'school': data.get('school'),
            'maritalStatus': data.get('maritalStatus'),
            'workStatus': data.get('workStatus'),
            'company': data.get('company'),
            'position': data.get('position'),
            'income': data.get('income'),
            'hasHouse': data.get('hasHouse'),
            'hasCar': data.get('hasCar'),
            'contactName': data.get('contactName'),
            'contactPhone': data.get('contactPhone'),
            'relation': data.get('relation')
        }
        
        print(f"准备更新的数据: {profile_data}")  # 调试日志
        
        # 调用更新函数
        result = update_profile(username, profile_data)
        print(f"更新结果: {result}")  # 调试日志
        
        if result['success']:
            return jsonify({'success': True, 'message': '信息更新成功'}), 200
        else:
            return jsonify({'success': False, 'message': result['message']}), 400
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")  # 调试日志
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

# 在文件开头添加JSON配置
app.json.ensure_ascii = False
app.json.sort_keys = False  # 禁用键排序，避免None值比较问题

def recalculate_all_user_credit_scores():
    """重新计算所有用户的信用分"""
    try:
        rows = []
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 构建用户数据
                user_data = {
                    'realName': row.get('realName', ''),
                    'idCard': row.get('idCard', ''),
                    'phone': row.get('phone', ''),
                    'education': row.get('education', ''),
                    'maritalStatus': row.get('maritalStatus', ''),
                    'workStatus': row.get('workStatus', ''),
                    'income': row.get('income', ''),
                    'hasHouse': row.get('hasHouse', 'false'),
                    'hasCar': row.get('hasCar', 'false'),
                    'contactName': row.get('contactName', ''),
                    'contactPhone': row.get('contactPhone', '')
                }
                
                # 计算新的信用分
                credit_result = calculate_credit_score(user_data, row['username'])
                row['creditScore'] = str(credit_result['total_score'])
                
                print(f"用户 {row['username']} 信用分更新为: {credit_result['total_score']}")
                rows.append(row)
        
        # 写回文件
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            if rows:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        print("所有用户信用分重新计算完成！")
        return True
        
    except Exception as e:
        print(f"重新计算信用分失败: {e}")
        return False

# 头像上传API
@app.route('/api/user/upload-avatar', methods=['POST'])
def upload_avatar():
    try:
        # 这里简化处理，从请求头获取用户名
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权访问'}), 401
        
        # 检查是否有文件上传
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        # 获取用户名（简化处理）
        username = request.form.get('username')
        if not username:
            # 从现有用户中找一个活跃用户
            with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('realName') and row['realName'].strip():
                        username = row['username']
                        break
        
        if not username:
            return jsonify({'success': False, 'message': '用户未找到'}), 404
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'message': '不支持的文件格式，请选择png、jpg、jpeg、gif或webp格式'}), 400
        
        # 创建上传目录
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'avatars')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件名
        import time
        timestamp = str(int(time.time()))
        filename = f"{username}_{timestamp}.{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 生成访问URL
        avatar_url = f"/uploads/avatars/{filename}"
        
        # DB first: 更新用户avatar字段
        update_success = False
        try:
            db: Session = SessionLocal()
            if update_user_avatar_path(db, username, avatar_url):
                db.commit()
                update_success = True
            else:
                db.rollback()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            try:
                db.close()
            except Exception:
                pass

        # CSV fallback
        if not update_success:
            update_success = update_user_avatar(username, avatar_url)
        
        if update_success:
            return jsonify({
                'success': True,
                'message': '头像上传成功',
                'avatar_url': avatar_url
            }), 200
        else:
            # 如果更新失败，删除已上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'success': False, 'message': '更新用户头像失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500

def update_user_avatar(username, avatar_url):
    """更新用户头像URL"""
    try:
        rows = []
        user_found = False
        
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['username'] == username:
                    row['avatar'] = avatar_url
                    user_found = True
                rows.append(row)
        
        if user_found:
            with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                if rows:
                    fieldnames = rows[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            return True
        
        return False
        
    except Exception as e:
        print(f"更新用户头像失败: {e}")
        return False

# 静态文件服务 - 用于提供上传的头像图片
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    from flask import send_from_directory
    return send_from_directory(upload_dir, filename)

if __name__ == '__main__':
    ensure_files_exist()
    # 重新计算所有用户的信用分
    recalculate_all_user_credit_scores()
    app.run(host="0.0.0.0", port=8000, debug=True) 