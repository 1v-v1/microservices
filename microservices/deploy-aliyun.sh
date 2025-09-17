#!/bin/bash

# 极速贷微服务系统 - 阿里云一键部署脚本
# 支持 CentOS 7.9+ 和 Ubuntu 20.04 LTS+

set -e

# 项目配置
PROJECT_DIR="/opt/loan-system"
SERVICE_USER="loan"
DOMAIN=""
REPO_URL="https://github.com/your-repo/loan-system.git"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "    极速贷微服务系统 - 阿里云部署脚本"
    echo "=========================================="
    echo -e "${NC}"
    echo "本脚本将自动完成以下操作："
    echo "1. 安装Docker和Docker Compose"
    echo "2. 安装Nginx和Certbot"
    echo "3. 克隆项目代码"
    echo "4. 配置环境变量"
    echo "5. 构建和启动微服务"
    echo "6. 配置Nginx反向代理"
    echo "7. 申请SSL证书"
    echo "8. 配置防火墙"
    echo "9. 设置自动备份"
    echo ""
}

# 检查系统
check_system() {
    log_step "检查系统环境..."
    
    # 检查是否为root用户
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    # 检查操作系统
    if [ -f /etc/redhat-release ]; then
        OS="centos"
        log_info "检测到CentOS系统"
    elif [ -f /etc/lsb-release ]; then
        OS="ubuntu"
        log_info "检测到Ubuntu系统"
    else
        log_error "不支持的操作系统，请使用CentOS 7.9+或Ubuntu 20.04 LTS+"
        exit 1
    fi
    
    # 检查内存
    MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ $MEMORY -lt 4000 ]; then
        log_warn "系统内存不足4GB，可能影响服务性能"
    fi
    
    # 检查磁盘空间
    DISK=$(df / | awk 'NR==2{print $4}')
    if [ $DISK -lt 10485760 ]; then  # 10GB in KB
        log_warn "系统磁盘空间不足10GB，可能影响服务运行"
    fi
}

# 安装Docker
install_docker() {
    log_step "安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker已安装，版本: $(docker --version)"
        return
    fi
    
    if [ "$OS" = "centos" ]; then
        # 安装Docker
        yum install -y yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io
    elif [ "$OS" = "ubuntu" ]; then
        # 更新包索引
        apt-get update
        # 安装必要的包
        apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        # 添加Docker官方GPG密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        # 设置稳定版仓库
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        # 安装Docker
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io
    fi
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    log_info "Docker安装完成，版本: $(docker --version)"
}

# 安装Docker Compose
install_docker_compose() {
    log_step "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装，版本: $(docker-compose --version)"
        return
    fi
    
    # 下载Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_info "Docker Compose安装完成，版本: $(docker-compose --version)"
}

# 安装其他依赖
install_dependencies() {
    log_step "安装其他依赖..."
    
    if [ "$OS" = "centos" ]; then
        yum install -y git curl wget vim nginx certbot python3 python3-pip
    elif [ "$OS" = "ubuntu" ]; then
        apt-get update
        apt-get install -y git curl wget vim nginx certbot python3 python3-pip
    fi
    
    # 启动Nginx
    systemctl start nginx
    systemctl enable nginx
    
    log_info "依赖安装完成"
}

# 创建项目目录
create_project_dir() {
    log_step "创建项目目录..."
    
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # 创建服务用户
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false $SERVICE_USER
        log_info "创建服务用户: $SERVICE_USER"
    fi
}

# 克隆代码
clone_code() {
    log_step "克隆项目代码..."
    
    if [ ! -d "microservices" ]; then
        # 克隆代码
        git clone $REPO_URL .
        log_info "代码克隆完成"
    else
        log_info "代码目录已存在，跳过克隆"
    fi
}

# 配置环境
setup_environment() {
    log_step "配置环境变量..."
    
    cd microservices
    
    # 检查环境变量文件
    if [ ! -f "env.prod.template" ]; then
        log_error "环境变量模板文件不存在"
        exit 1
    fi
    
    # 复制环境变量文件
    if [ ! -f ".env.prod" ]; then
        cp env.prod.template .env.prod
        log_warn "已创建环境变量文件 .env.prod，请编辑后重新运行脚本"
        log_info "编辑命令: vim .env.prod"
        exit 1
    fi
    
    # 复制环境变量文件
    cp .env.prod .env
    
    # 创建必要的目录
    mkdir -p data/{postgres,redis,minio,prometheus,grafana}
    chmod 755 data/*
    chown -R $SERVICE_USER:$SERVICE_USER data/
    
    # 获取域名
    DOMAIN=$(grep "^DOMAIN=" .env | cut -d'=' -f2)
    if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
        log_error "请在 .env.prod 文件中设置正确的域名"
        exit 1
    fi
    
    log_info "环境配置完成，域名: $DOMAIN"
}

# 构建和启动服务
deploy_services() {
    log_step "构建和启动微服务..."
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose -f docker-compose.prod.yml build
    
    # 启动服务
    log_info "启动微服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 60
    
    # 初始化数据库
    log_info "初始化数据库..."
    python3 init_database.py
    
    log_info "微服务部署完成"
}

# 配置Nginx
setup_nginx() {
    log_step "配置Nginx反向代理..."
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/loan-system << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL配置
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # 日志配置
    access_log /var/log/nginx/loan-system.access.log;
    error_log /var/log/nginx/loan-system.error.log;

    # 客户端最大请求体大小
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # API网关
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # 监控面板
    location /grafana/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
    }

    location /prometheus/ {
        proxy_pass http://127.0.0.1:9090/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # MinIO控制台
    location /minio/ {
        proxy_pass http://127.0.0.1:9001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/loan-system /etc/nginx/sites-enabled/
    
    # 删除默认站点
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    
    # 重启Nginx
    systemctl restart nginx
    
    log_info "Nginx配置完成"
}

# 配置SSL证书
setup_ssl() {
    log_step "配置SSL证书..."
    
    # 安装certbot
    if [ "$OS" = "centos" ]; then
        yum install -y epel-release
        yum install -y certbot python3-certbot-nginx
    elif [ "$OS" = "ubuntu" ]; then
        apt-get install -y certbot python3-certbot-nginx
    fi
    
    # 申请SSL证书
    log_info "申请SSL证书..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    
    # 设置自动续期
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
    
    log_info "SSL证书配置完成"
}

# 配置防火墙
setup_firewall() {
    log_step "配置防火墙..."
    
    if [ "$OS" = "centos" ]; then
        # 配置firewalld
        systemctl start firewalld
        systemctl enable firewalld
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --reload
    elif [ "$OS" = "ubuntu" ]; then
        # 配置ufw
        ufw allow ssh
        ufw allow http
        ufw allow https
        ufw --force enable
    fi
    
    log_info "防火墙配置完成"
}

# 创建备份脚本
create_backup_script() {
    log_step "创建备份脚本..."
    
    cat > /opt/loan-system/backup.sh << 'EOF'
#!/bin/bash
# 极速贷微服务系统 - 自动备份脚本

BACKUP_DIR="/backup/loan-system"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/opt/loan-system/microservices"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "开始备份..."

# 备份数据库
echo "备份数据库..."
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T postgres pg_dump -U postgres user_service > $BACKUP_DIR/user_service_$DATE.sql
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T postgres pg_dump -U postgres loan_service > $BACKUP_DIR/loan_service_$DATE.sql
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T postgres pg_dump -U postgres repayment_service > $BACKUP_DIR/repayment_service_$DATE.sql
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T postgres pg_dump -U postgres risk_service > $BACKUP_DIR/risk_service_$DATE.sql
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T postgres pg_dump -U postgres notification_service > $BACKUP_DIR/notification_service_$DATE.sql
docker-compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T postgres pg_dump -U postgres file_service > $BACKUP_DIR/file_service_$DATE.sql

# 备份文件
echo "备份文件..."
tar -czf $BACKUP_DIR/files_$DATE.tar.gz $PROJECT_DIR/data/

# 备份配置文件
echo "备份配置文件..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz $PROJECT_DIR/.env.prod $PROJECT_DIR/docker-compose.prod.yml

# 清理旧备份（保留30天）
echo "清理旧备份..."
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR"
EOF
    
    chmod +x /opt/loan-system/backup.sh
    
    # 设置定时备份
    echo "0 2 * * * /opt/loan-system/backup.sh" | crontab -
    
    log_info "备份脚本创建完成"
}

# 检查服务状态
check_services() {
    log_step "检查服务状态..."
    
    # 检查Docker服务
    log_info "Docker服务状态:"
    docker-compose -f docker-compose.prod.yml ps
    
    # 检查API健康状态
    sleep 10
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ API网关健康检查通过"
    else
        log_warn "⚠️  API网关健康检查失败"
    fi
    
    # 检查Nginx状态
    if systemctl is-active --quiet nginx; then
        log_info "✅ Nginx服务运行正常"
    else
        log_error "❌ Nginx服务异常"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_step "部署完成！"
    echo ""
    echo -e "${GREEN}🎉 极速贷微服务系统部署成功！${NC}"
    echo ""
    echo -e "${BLUE}📋 服务访问地址：${NC}"
    echo "  🌐 主站: https://$DOMAIN"
    echo "  📊 Grafana: https://$DOMAIN/grafana/"
    echo "  📈 Prometheus: https://$DOMAIN/prometheus/"
    echo "  💾 MinIO控制台: https://$DOMAIN/minio/"
    echo ""
    echo -e "${BLUE}🔧 管理命令：${NC}"
    echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f [服务名]"
    echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
    echo "  重启服务: docker-compose -f docker-compose.prod.yml restart [服务名]"
    echo "  更新服务: docker-compose -f docker-compose.prod.yml up -d --build"
    echo ""
    echo -e "${BLUE}📁 项目目录：${NC}"
    echo "  项目路径: $PROJECT_DIR"
    echo "  日志目录: /var/log/nginx/"
    echo "  备份目录: /backup/loan-system/"
    echo ""
    echo -e "${YELLOW}🔐 默认密码：${NC}"
    echo "  Grafana: admin / $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"
    echo "  MinIO: $(grep MINIO_ACCESS_KEY .env | cut -d'=' -f2) / $(grep MINIO_SECRET_KEY .env | cut -d'=' -f2)"
    echo ""
    echo -e "${RED}⚠️  请及时修改默认密码！${NC}"
    echo ""
    echo -e "${GREEN}部署完成时间: $(date)${NC}"
}

# 主函数
main() {
    show_welcome
    check_system
    install_docker
    install_docker_compose
    install_dependencies
    create_project_dir
    clone_code
    setup_environment
    deploy_services
    setup_nginx
    setup_ssl
    setup_firewall
    create_backup_script
    check_services
    show_deployment_info
}

# 执行主函数
main "$@"
