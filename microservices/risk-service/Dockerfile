FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    g++ \
    gfortran \
    openblas-dev

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8004

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]


