# 极速贷微服务系统 - 快速开始指南

## 🚀 5分钟快速部署

### 前置条件

- 阿里云ECS实例（2核4GB或以上）
- 域名已解析到服务器IP
- 服务器已开放80、443、22端口

### 一键部署

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

### 部署完成后

访问以下地址验证部署：

- **主站**: https://your-domain.com
- **API文档**: https://your-domain.com/docs
- **监控面板**: https://your-domain.com/grafana/
- **指标监控**: https://your-domain.com/prometheus/

## 📋 环境变量配置

### 必需配置

```bash
# 域名（必须）
DOMAIN=your-domain.com

# 数据库密码（必须）
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# JWT密钥（必须）
SECRET_KEY=your_jwt_secret_key_32_chars_minimum
```

### 可选配置

```bash
# 邮件服务
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_app_password

# 短信服务
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=your_phone_number

# 监控密码
GRAFANA_PASSWORD=your_grafana_password
```

## 🔧 常用命令

### 服务管理

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f api-gateway

# 重启服务
docker-compose -f docker-compose.prod.yml restart api-gateway

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

### 数据库操作

```bash
# 连接数据库
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres

# 备份数据库
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres user_service > backup.sql

# 恢复数据库
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres user_service < backup.sql
```

### 日志查看

```bash
# 查看Nginx日志
tail -f /var/log/nginx/loan-system.access.log
tail -f /var/log/nginx/loan-system.error.log

# 查看Docker日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 🚨 故障排除

### 服务无法启动

```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 查看详细日志
docker-compose -f docker-compose.prod.yml logs service-name
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -c "SELECT 1;"

# 检查网络连接
docker-compose -f docker-compose.prod.yml exec api-gateway ping postgres
```

### SSL证书问题

```bash
# 检查证书状态
certbot certificates

# 手动续期
certbot renew --force-renewal
```

## 📞 获取帮助

- **详细文档**: [DEPLOYMENT-ALIYUN.md](DEPLOYMENT-ALIYUN.md)
- **问题反馈**: https://github.com/your-repo/loan-system/issues
- **技术交流**: 加入我们的技术交流群

---

**注意**: 请在生产环境中及时修改所有默认密码！
