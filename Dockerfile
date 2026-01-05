FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/news /app/static/lib /app/scripts

# 设置环境变量
ENV FLASK_ENV=production
ENV PORT=8009

# 暴露端口
EXPOSE 8009

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8009", "--workers", "2", "--timeout", "120", "app:app"]
