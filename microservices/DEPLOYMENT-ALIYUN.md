# 极速贷微服务系统 - 阿里云部署方案一

## 📋 方案概述

本方案采用Docker Compose + Nginx + SSL的一键部署方式，适合中小型项目快速上线。通过自动化脚本完成整个部署过程，包括环境准备、服务部署、SSL配置等。

## 🎯 方案特点

- ✅ **一键部署**：自动化脚本完成所有部署步骤
- ✅ **生产就绪**：包含监控、日志、备份等生产环境必需功能
- ✅ **安全加固**：SSL证书、防火墙、安全头配置
- ✅ **高可用**：健康检查、自动重启、负载均衡
- ✅ **易维护**：完整的监控和日志系统

## 🏗️ 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        阿里云ECS                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Nginx (80/443)                      │ │
│  │              SSL终止 + 反向代理 + 负载均衡              │ │
│  └─────────────────┬───────────────────────────────────────┘ │
│                    │                                        │
│  ┌─────────────────┴───────────────────────────────────────┐ │
│  │                  Docker Compose                        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │ │
│  │  │ API网关     │ │ 用户服务    │ │ 贷款服务    │      │ │
│  │  │ :8000       │ │ :8001       │ │ :8002       │      │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘      │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │ │
│  │  │ 还款服务    │ │ 风控服务    │ │ 通知服务    │      │ │
│  │  │ :8003       │ │ :8004       │ │ :8005       │      │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘      │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │ │
│  │  │ 文件服务    │ │ Prometheus  │ │ Grafana     │      │ │
│  │  │ :8006       │ │ :9090       │ │ :3000       │      │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   数据存储层                            │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │ │
│  │  │ PostgreSQL  │ │ Redis       │ │ MinIO       │      │ │
│  │  │ :5432       │ │ :6379       │ │ :9000/9001  │      │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📋 部署清单

### 服务器要求

| 项目 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核 |
| 内存 | 4GB | 8GB |
| 存储 | 40GB | 100GB |
| 网络 | 5Mbps | 10Mbps |
| 操作系统 | CentOS 7.9+ | Ubuntu 20.04 LTS+ |

### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Docker | 20.10+ | 容器运行时 |
| Docker Compose | 2.0+ | 容器编排 |
| Nginx | 1.18+ | 反向代理 |
| Git | 2.0+ | 代码管理 |
| Certbot | 最新 | SSL证书管理 |

## 🚀 快速开始

### 步骤1：准备阿里云服务器

#### 1.1 购买ECS实例

1. 登录阿里云控制台
2. 选择ECS产品
3. 创建实例，配置如下：
   - **实例规格**：ecs.c6.large (2核4GB) 或 ecs.c6.xlarge (4核8GB)
   - **操作系统**：CentOS 7.9 或 Ubuntu 20.04 LTS
   - **存储**：40GB系统盘 + 100GB数据盘
   - **网络**：专有网络VPC
   - **安全组**：开放22(SSH)、80(HTTP)、443(HTTPS)端口

#### 1.2 配置安全组规则

在阿里云控制台配置安全组：

```
入方向规则：
- 端口：22，协议：TCP，授权对象：0.0.0.0/0 (SSH)
- 端口：80，协议：TCP，授权对象：0.0.0.0/0 (HTTP)
- 端口：443，协议：TCP，授权对象：0.0.0.0/0 (HTTPS)

出方向规则：
- 全部允许
```

### 步骤2：连接服务器

```bash
# 使用SSH连接服务器
ssh root@your-server-ip

# 或者使用阿里云控制台的远程连接
```

### 步骤3：下载部署脚本

```bash
# 方法1：直接下载脚本
wget https://raw.githubusercontent.com/your-repo/loan-system/main/deploy-aliyun.sh
chmod +x deploy-aliyun.sh

# 方法2：克隆整个项目
git clone https://github.com/your-repo/loan-system.git
cd loan-system/microservices
```

### 步骤4：配置环境变量

```bash
# 创建生产环境变量文件
cat > .env.prod << 'EOF'
# 数据库配置
POSTGRES_PASSWORD=LoanSystem2024!SecurePass
REDIS_PASSWORD=Redis2024!SecurePass

# JWT密钥（请生成强密钥）
SECRET_KEY=LoanSystemJWTSecretKey2024!VerySecureKey

# 邮件配置
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_app_password

# Twilio配置（短信服务）
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number

# MinIO配置
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123456

# Grafana配置
GRAFANA_PASSWORD=Grafana2024!AdminPass

# 域名配置
DOMAIN=your-domain.com
EOF

# 编辑环境变量文件，填入实际配置
vim .env.prod
```

### 步骤5：执行部署

```bash
# 执行一键部署脚本
./deploy-aliyun.sh
```

### 步骤6：配置域名和SSL

```bash
# 配置Nginx
cp nginx/loan-system.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/loan-system.conf /etc/nginx/sites-enabled/

# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx

# 申请SSL证书
certbot --nginx -d your-domain.com --non-interactive --agree-tos --email admin@your-domain.com
```

## 📊 服务配置

### 微服务端口分配

| 服务名称 | 内部端口 | 外部端口 | 描述 |
|---------|----------|----------|------|
| API网关 | 8000 | 80/443 | 统一入口 |
| 用户服务 | 8001 | - | 用户管理 |
| 贷款服务 | 8002 | - | 贷款管理 |
| 还款服务 | 8003 | - | 还款管理 |
| 风控服务 | 8004 | - | 风控评估 |
| 通知服务 | 8005 | - | 消息通知 |
| 文件服务 | 8006 | - | 文件管理 |
| Prometheus | 9090 | - | 监控指标 |
| Grafana | 3000 | - | 数据可视化 |

### 数据存储配置

| 服务名称 | 端口 | 数据目录 | 描述 |
|---------|------|----------|------|
| PostgreSQL | 5432 | /opt/loan-system/microservices/data/postgres | 主数据库 |
| Redis | 6379 | /opt/loan-system/microservices/data/redis | 缓存存储 |
| MinIO | 9000/9001 | /opt/loan-system/microservices/data/minio | 对象存储 |

## 🔧 部署后配置

### 访问地址

部署完成后，您可以通过以下地址访问系统：

- **主站**：https://your-domain.com
- **API文档**：https://your-domain.com/docs
- **Grafana监控**：https://your-domain.com/grafana/
- **Prometheus指标**：https://your-domain.com/prometheus/
- **MinIO控制台**：https://your-domain.com/minio/

### 默认账号密码

| 服务 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| Grafana | admin | Grafana2024!AdminPass | 监控面板 |
| MinIO | minioadmin | minioadmin123456 | 对象存储 |
| PostgreSQL | postgres | LoanSystem2024!SecurePass | 数据库 |

⚠️ **重要**：请在生产环境中及时修改所有默认密码！

## 📈 监控和维护

### 查看服务状态

```bash
# 查看所有服务状态
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml ps

# 查看特定服务日志
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml logs -f api-gateway

# 查看所有服务日志
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml logs -f
```

### 服务管理

```bash
# 重启服务
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml restart api-gateway

# 停止服务
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml stop

# 启动服务
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml start

# 更新服务
cd /opt/loan-system/microservices
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

### 健康检查

```bash
# 检查API健康状态
curl http://localhost:8000/health

# 检查外部访问
curl https://your-domain.com/health

# 检查数据库连接
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml exec postgres psql -U postgres -c "SELECT 1;"
```

## 🔒 安全配置

### 防火墙配置

```bash
# CentOS (firewalld)
systemctl start firewalld
systemctl enable firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

# Ubuntu (ufw)
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable
```

### 安全建议

1. **修改默认密码**
   ```bash
   # 修改数据库密码
   vim /opt/loan-system/microservices/.env.prod
   # 修改POSTGRES_PASSWORD和REDIS_PASSWORD
   
   # 重启服务使配置生效
   docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml restart
   ```

2. **定期更新**
   ```bash
   # 更新系统包
   yum update -y  # CentOS
   apt update && apt upgrade -y  # Ubuntu
   
   # 更新Docker镜像
   docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml pull
   docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml up -d
   ```

3. **监控告警**
   - 访问Grafana配置告警规则
   - 设置邮件通知
   - 监控系统资源使用

## 🚨 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 查看服务日志
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml logs service-name

# 检查端口占用
netstat -tulpn | grep :8000

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml exec postgres psql -U postgres -c "SELECT 1;"

# 检查网络连接
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml exec api-gateway ping postgres

# 检查环境变量
docker-compose -f /opt/loan-system/microservices/docker-compose.prod.yml exec api-gateway env | grep DATABASE
```

#### 3. Nginx配置错误

```bash
# 测试Nginx配置
nginx -t

# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 重启Nginx
systemctl restart nginx
```

#### 4. SSL证书问题

```bash
# 检查证书状态
certbot certificates

# 手动续期证书
certbot renew --dry-run

# 强制续期证书
certbot renew --force-renewal
```

## 📞 技术支持

### 获取帮助

1. **查看日志**：`docker-compose logs -f [服务名]`
2. **检查状态**：`docker-compose ps`
3. **健康检查**：`curl http://localhost:8000/health`
4. **监控面板**：访问Grafana和Prometheus

### 联系方式

- **项目仓库**：https://github.com/your-repo/loan-system
- **问题反馈**：https://github.com/your-repo/loan-system/issues
- **技术文档**：https://docs.your-domain.com

---

**注意**: 生产环境部署前，请务必：
- 修改所有默认密码
- 配置SSL证书
- 设置防火墙规则
- 配置监控和告警
- 制定备份策略
- 进行安全测试

**最后更新**: 2024年1月
**版本**: v1.0.0
