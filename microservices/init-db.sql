-- 创建数据库
CREATE DATABASE user_service;
CREATE DATABASE loan_service;
CREATE DATABASE repayment_service;
CREATE DATABASE risk_service;
CREATE DATABASE notification_service;
CREATE DATABASE file_service;

-- 创建用户
CREATE USER loan_user WITH PASSWORD 'loan_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE user_service TO loan_user;
GRANT ALL PRIVILEGES ON DATABASE loan_service TO loan_user;
GRANT ALL PRIVILEGES ON DATABASE repayment_service TO loan_user;
GRANT ALL PRIVILEGES ON DATABASE risk_service TO loan_user;
GRANT ALL PRIVILEGES ON DATABASE notification_service TO loan_user;
GRANT ALL PRIVILEGES ON DATABASE file_service TO loan_user;


