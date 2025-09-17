# 极速贷微服务架构

## 📋 项目结构

```
microservices/
├── api-gateway/                 # API网关服务
├── user-service/               # 用户服务
├── loan-service/               # 贷款服务
├── repayment-service/          # 还款服务
├── risk-service/               # 风控服务
├── notification-service/       # 通知服务
├── file-service/               # 文件服务
├── shared/                     # 共享组件
│   ├── models/                 # 数据模型
│   ├── utils/                  # 工具函数
│   └── config/                 # 配置管理
├── monitoring/                 # 监控配置
├── nginx/                      # Nginx配置
├── docker-compose.yml          # 本地开发环境
├── docker-compose.prod.yml     # 生产环境配置
├── deploy-aliyun.sh           # 阿里云一键部署脚本
├── env.prod.template          # 生产环境变量模板
├── init_database.py           # 数据库初始化脚本
├── DEPLOYMENT-ALIYUN.md       # 阿里云部署详细文档
├── QUICK-START.md             # 快速开始指南
└── README.md                  # 项目说明
```

## 服务职责

### 用户服务 (user-service)
- 用户注册、登录、认证
- 用户信息管理
- 用户画像计算
- 信用分管理

### 贷款服务 (loan-service)
- 贷款申请处理
- 贷款审批流程
- 贷款状态管理
- 贷款额度计算

### 还款服务 (repayment-service)
- 还款计划生成
- 还款记录管理
- 逾期处理
- 催收管理

### 风控服务 (risk-service)
- 风险评估
- 反欺诈检测
- 黑名单管理
- 信用评分

### 通知服务 (notification-service)
- 消息推送
- 邮件通知
- 短信服务
- 模板管理

### 文件服务 (file-service)
- 文件上传
- 文件存储
- 文件处理
- 访问控制

### API网关 (api-gateway)
- 统一入口
- 路由转发
- 负载均衡
- 认证授权
- 限流熔断

## 技术栈

- **后端框架**: Python + FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **消息队列**: RabbitMQ
- **容器化**: Docker + Docker Compose
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack
- **反向代理**: Nginx
- **对象存储**: MinIO

## 🚀 快速部署

### 阿里云一键部署

```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/loan-system/main/microservices/deploy-aliyun.sh
chmod +x deploy-aliyun.sh

# 3. 配置环境变量
cp env.prod.template .env.prod
vim .env.prod  # 编辑域名和密码

# 4. 执行部署
./deploy-aliyun.sh
```

### 本地开发环境

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/loan-system.git
cd loan-system/microservices

# 2. 启动服务
docker-compose up -d

# 3. 初始化数据库
python3 init_database.py
```

## 📚 文档

- [快速开始指南](QUICK-START.md) - 5分钟快速部署
- [阿里云部署文档](DEPLOYMENT-ALIYUN.md) - 详细部署说明
- [API文档](http://localhost:8000/docs) - 接口文档（部署后访问）

## 🔧 管理命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f api-gateway

# 重启服务
docker-compose -f docker-compose.prod.yml restart api-gateway

# 更新服务
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📞 技术支持

- **问题反馈**: https://github.com/your-repo/loan-system/issues
- **技术交流**: 加入我们的技术交流群
- **文档中心**: https://docs.your-domain.com

