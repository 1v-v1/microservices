# 极速贷管理员后台系统

这是一个基于Vue 3、Element Plus和Pinia构建的极速贷管理员后台系统。

## 功能特点

- 管理员登录认证
- 用户管理：查看、编辑、删除用户信息
- 贷款管理：查看、审批贷款申请
- 还款管理：查看还款记录
- 数据统计：用户数量、贷款总额、待还款总额等统计信息
- 数据导出：导出用户、贷款、还款数据

## 技术栈

- Vue 3
- Vue Router
- Pinia (状态管理)
- Element Plus (UI组件库)
- Axios (HTTP请求)
- Vite (构建工具)

## 安装与运行

1. 安装依赖

```bash
npm install
```

2. 启动开发服务器

```bash
npm run dev
```

3. 构建生产版本

```bash
npm run build
```

## 管理员账号

默认管理员账号：
- 用户名：admin
- 密码：admin123

## 后端API

后端API基于Flask构建，位于`py/server.py`文件中。 