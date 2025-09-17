# 极速贷管理系统

一个完整的贷款管理系统，包含后端API、管理端Web界面和移动端应用。

## 🏗️ 项目架构

本项目采用前后端分离架构，包含三个主要部分：

- **后端服务**（Flask + PostgreSQL + SQLAlchemy）位于 `py/`
- **管理端**（Vue3 + Element-Plus + Pinia）位于 `admin-web/`
- **移动端**（UniApp）位于 `uni-loan-app/`

## 🚀 快速开始

### 环境要求
- Python 3.12+
- Node.js 16+
- PostgreSQL 数据库
- 推荐使用 PowerShell 并启用 UTF-8：`python -X utf8 ...`

### 安装依赖

#### Python 依赖
```powershell
pip install SQLAlchemy==2.0.32 alembic==1.13.2 psycopg2-binary==2.9.9 python-dotenv==1.0.1 pg8000==1.31.2 bcrypt flask flask-cors
```

#### Node.js 依赖（管理端）
```powershell
cd admin-web
npm install
```

### 数据库配置

#### 方法一：环境变量（推荐）
```powershell
$env:DATABASE_URL='postgresql+pg8000://postgres:<你的密码>@localhost:5432/loanapp'
```

#### 方法二：创建 .env 文件
在项目根目录创建 `.env` 文件：
```
DATABASE_URL=postgresql+pg8000://postgres:<你的密码>@localhost:5432/loanapp
```

### 初始化数据库
```powershell
cd py
python -X utf8 init_db.py
```

### 启动服务

#### 启动后端服务
```powershell
cd py
python -X utf8 server.py
```
- 服务地址：`http://localhost:8000`
- 调试模式：已启用，支持热重载
- 功能特性：
  - 用户注册/登录/资料管理
  - 贷款申请/审批/还款管理
  - 信用评分系统
  - 头像上传功能
  - 数据统计与导出
  - 双存储策略：优先使用PostgreSQL，数据库不可用时自动回退到CSV

#### 启动管理端
```powershell
cd admin-web
npm run dev
```
- 管理端地址：`http://localhost:5173`（Vite默认端口）
- 功能模块：
  - 用户管理：查看、编辑、删除用户信息
  - 贷款管理：审批贷款申请、查看贷款记录
  - 还款管理：查看还款记录、统计还款情况
  - 数据统计：用户数量、贷款总额、还款统计
  - 数据导出：支持CSV格式导出

#### 启动移动端
使用 HBuilderX 或 uni-app CLI 运行：
```bash
# 使用 HBuilderX
# 直接打开 uni-loan-app 文件夹

# 或使用 CLI
npm install -g @dcloudio/uvm
uvm ls
uvm install 3.0.0-alpha-3080420230802001
```

## 📁 项目结构

```
loan-management-system/
├── py/                          # 后端服务
│   ├── db.py                    # 数据库连接配置
│   ├── models.py                # ORM 数据模型
│   ├── server.py                # Flask 主服务
│   ├── init_db.py               # 数据库初始化脚本
│   ├── repositories/            # 数据访问层
│   │   ├── users.py             # 用户数据操作
│   │   └── loans.py             # 贷款数据操作
│   ├── uploads/                 # 文件上传目录
│   └── *.csv                    # CSV 备份数据
├── admin-web/                   # 管理端（Vue3）
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   ├── api/                 # API 接口
│   │   ├── router/              # 路由配置
│   │   └── store/               # 状态管理
│   └── package.json
├── uni-loan-app/                # 移动端（UniApp）
│   ├── pages/                   # 页面文件
│   ├── common/                  # 公共模块
│   ├── static/                  # 静态资源
│   └── pages.json               # 页面配置
├── alembic/                     # 数据库迁移
└── README.md                    # 项目说明
```

## 🔧 核心功能

### 后端功能
- **用户管理**：注册、登录、资料完善、头像上传
- **贷款系统**：申请、审批、状态跟踪、自动/人工审批
- **还款管理**：还款计划、还款记录、逾期处理
- **信用评分**：多维度评分算法、信用等级划分
- **数据统计**：用户统计、贷款统计、还款统计
- **文件管理**：头像上传、文件存储

### 管理端功能
- **仪表板**：数据概览、图表展示
- **用户管理**：用户列表、信息编辑、信用分调整
- **贷款管理**：申请审批、状态管理、记录查询
- **还款管理**：还款记录、统计报表
- **数据导出**：CSV格式数据导出

### 移动端功能
- **首页**：贷款信息展示、快捷入口
- **借钱**：贷款申请、额度查询
- **还款**：还款管理、记录查询
- **我的**：个人中心、资料管理

## 🛠️ 技术栈

### 后端技术
- **框架**：Flask
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy 2.0
- **迁移**：Alembic
- **认证**：bcrypt 密码加密
- **文件处理**：Flask 文件上传

### 前端技术
- **管理端**：Vue 3 + Element Plus + Pinia + Vite
- **移动端**：UniApp（支持多端发布）
- **图表**：ECharts
- **HTTP客户端**：Axios

## ⚠️ 常见问题

### 启动问题
1. **模块导入错误**：确保在正确的目录下运行命令
2. **数据库连接失败**：检查PostgreSQL服务是否启动，密码是否正确
3. **端口占用**：确保8000端口未被占用

### 编码问题
- **Windows中文环境**：使用 `python -X utf8` 启动
- **数据库编码**：已使用 `pg8000` 驱动和 `template0` 模板

### 数据库问题
- **首次创建失败**：初始化脚本已处理排序规则问题
- **表结构更新**：使用 Alembic 进行数据库迁移

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 修复模块导入路径问题
- ✅ 完善数据库连接配置
- ✅ 优化信用评分算法
- ✅ 增强错误处理机制
- ✅ 改进文件上传功能
- ✅ 完善API文档

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
