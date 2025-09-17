from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import sys
import os
from datetime import datetime, timedelta
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import json

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.database import get_db_session
from shared.utils.auth import verify_token
from shared.models.notification import Notification, NotificationTemplate, NotificationChannel, NotificationStats
from pydantic import BaseModel

app = FastAPI(
    title="通知服务",
    description="消息推送、邮件通知、短信服务",
    version="1.0.0"
)

security = HTTPBearer()


# Pydantic模型
class NotificationRequest(BaseModel):
    user_id: int
    message: str
    type: str = "general"
    channel: str = "all"  # all, email, sms, push
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    timestamp: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    type: str
    channel: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationTemplate(BaseModel):
    id: str
    name: str
    subject: str
    content: str
    channel: str
    variables: List[str]


class NotificationHistory(BaseModel):
    id: int
    user_id: int
    message: str
    type: str
    channel: str
    status: str
    sent_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# 依赖注入
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload.get("user_id", 0)


# 通知渠道接口
class NotificationChannel:
    def send(self, user_id: int, message: str, **kwargs) -> bool:
        """发送通知"""
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.getenv("EMAIL_USERNAME", "")
        self.password = os.getenv("EMAIL_PASSWORD", "")
    
    def send(self, user_id: int, message: str, subject: str = "系统通知", **kwargs) -> bool:
        """发送邮件"""
        try:
            # 获取用户邮箱
            user_email = self.get_user_email(user_id)
            if not user_email:
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = user_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'html', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, user_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def get_user_email(self, user_id: int) -> Optional[str]:
        """获取用户邮箱"""
        # 这里应该从用户服务获取用户邮箱
        # 简化处理，返回默认邮箱
        return f"user{user_id}@example.com"


class SMSChannel(NotificationChannel):
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER", "")
    
    def send(self, user_id: int, message: str, **kwargs) -> bool:
        """发送短信"""
        try:
            # 获取用户手机号
            user_phone = self.get_user_phone(user_id)
            if not user_phone:
                return False
            
            # 这里应该使用Twilio SDK发送短信
            # 简化处理，直接返回成功
            print(f"发送短信到 {user_phone}: {message}")
            return True
        except Exception as e:
            print(f"短信发送失败: {e}")
            return False
    
    def get_user_phone(self, user_id: int) -> Optional[str]:
        """获取用户手机号"""
        # 这里应该从用户服务获取用户手机号
        # 简化处理，返回默认手机号
        return f"+861380000{user_id:04d}"


class PushChannel(NotificationChannel):
    def send(self, user_id: int, message: str, **kwargs) -> bool:
        """发送推送通知"""
        try:
            # 这里应该使用推送服务（如Firebase、极光推送等）
            # 简化处理，直接返回成功
            print(f"发送推送通知到用户 {user_id}: {message}")
            return True
        except Exception as e:
            print(f"推送通知发送失败: {e}")
            return False


# 通知管理器
class NotificationManager:
    def __init__(self, db: Session):
        self.db = db
        self.channels = {
            "email": EmailChannel(),
            "sms": SMSChannel(),
            "push": PushChannel()
        }
    
    def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        """发送通知"""
        # 创建通知记录
        notification = Notification(
            user_id=request.user_id,
            message=request.message,
            type=request.type,
            channel=request.channel,
            status="pending",
            template_id=request.template_id,
            template_data=request.template_data
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # 发送通知
        success = False
        error_message = None
        
        if request.channel == "all":
            # 发送到所有渠道
            for channel_name, channel in self.channels.items():
                try:
                    if channel.send(request.user_id, request.message):
                        success = True
                except Exception as e:
                    error_message = f"渠道 {channel_name} 发送失败: {e}"
                    print(error_message)
        else:
            # 发送到指定渠道
            if request.channel in self.channels:
                try:
                    success = self.channels[request.channel].send(
                        request.user_id, 
                        request.message
                    )
                except Exception as e:
                    error_message = f"渠道 {request.channel} 发送失败: {e}"
                    print(error_message)
        
        # 更新状态
        notification.status = "sent" if success else "failed"
        notification.sent_at = datetime.utcnow() if success else None
        notification.error_message = error_message
        
        self.db.commit()
        
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            message=notification.message,
            type=notification.type,
            channel=notification.channel,
            status=notification.status,
            sent_at=notification.sent_at,
            created_at=notification.created_at
        )
    
    def get_notification_templates(self) -> List[NotificationTemplate]:
        """获取通知模板"""
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
        
        return templates
    
    def render_template(self, template_id: str, data: Dict[str, Any]) -> str:
        """渲染模板"""
        templates = self.get_notification_templates()
        template = next((t for t in templates if t.id == template_id), None)
        
        if not template:
            return f"模板 {template_id} 不存在"
        
        try:
            jinja_template = Template(template.content)
            return jinja_template.render(**data)
        except Exception as e:
            return f"模板渲染失败: {e}"


# API路由
@app.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: NotificationRequest,
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """发送通知"""
    manager = NotificationManager(db)
    
    # 如果提供了模板ID，渲染模板
    if request.template_id and request.template_data:
        rendered_message = manager.render_template(
            request.template_id, 
            request.template_data
        )
        request.message = rendered_message
    
    return manager.send_notification(request)


@app.get("/templates", response_model=List[NotificationTemplate])
async def get_templates(
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """获取通知模板"""
    manager = NotificationManager(db)
    return manager.get_notification_templates()


@app.get("/history/{user_id}", response_model=List[NotificationHistory])
async def get_notification_history(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """获取用户通知历史"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        NotificationHistory(
            id=notification.id,
            user_id=notification.user_id,
            message=notification.message,
            type=notification.type,
            channel=notification.channel,
            status=notification.status,
            sent_at=notification.sent_at,
            error_message=notification.error_message,
            created_at=notification.created_at
        )
        for notification in notifications
    ]


@app.get("/stats")
async def get_notification_stats(
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """获取通知统计"""
    # 查询总发送数
    total_sent = db.query(Notification).count()
    
    # 查询成功发送数
    success_count = db.query(Notification).filter(Notification.status == "sent").count()
    
    # 计算成功率
    success_rate = success_count / total_sent if total_sent > 0 else 0
    
    # 按渠道统计
    channel_stats = {}
    for channel in ["email", "sms", "push", "all"]:
        sent_count = db.query(Notification).filter(Notification.channel == channel).count()
        success_count = db.query(Notification).filter(
            Notification.channel == channel,
            Notification.status == "sent"
        ).count()
        
        channel_stats[channel] = {
            "sent": sent_count,
            "success": success_count
        }
    
    return {
        "total_sent": total_sent,
        "success_rate": round(success_rate, 4),
        "channel_stats": channel_stats
    }


@app.post("/template", response_model=NotificationTemplate)
async def create_template(
    template: NotificationTemplate,
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """创建通知模板"""
    # 这里应该保存到数据库
    # 简化处理，直接返回
    return template


@app.put("/template/{template_id}", response_model=NotificationTemplate)
async def update_template(
    template_id: str,
    template: NotificationTemplate,
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """更新通知模板"""
    # 这里应该更新数据库
    # 简化处理，直接返回
    return template


@app.delete("/template/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(lambda: next(get_db_session("notification_service")))
):
    """删除通知模板"""
    # 这里应该从数据库删除
    return {"message": f"模板 {template_id} 已删除"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "notification-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


