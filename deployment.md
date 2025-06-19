# 新闻网站Docker部署指南

## 环境要求

- Docker Engine
- Docker Compose
- Nginx（可选，用于反向代理）

## Docker部署步骤

### 1. 安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 克隆项目代码

```bash
git clone <repository_url>
cd news.docms.nz
```

### 3. 配置环境

项目使用 Docker Compose 进行容器编排，主要配置文件包括：

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

EXPOSE 8009

CMD ["gunicorn", "--bind", "0.0.0.0:8009", "app:app"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  news-app:
    build: .
    container_name: news-docms
    ports:
      - "8009:8009"
    volumes:
      - /home/maxazure/projects/news.docms.nz/news:/app/news
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
```

### 4. 构建和启动容器

```bash
# 构建镜像并启动容器
docker-compose up -d --build

# 查看容器状态
docker-compose ps
```

### 5. Nginx反向代理配置（可选）

如果需要使用Nginx作为反向代理，创建以下配置文件 `/etc/nginx/sites-available/news.docms.nz`：

```nginx
server {
    listen 80;
    server_name news.docms.nz;

    access_log /var/log/nginx/news.docms.nz.access.log;
    error_log /var/log/nginx/news.docms.nz.error.log;

    location / {
        proxy_pass http://localhost:8009;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用Nginx配置：
```bash
sudo ln -s /etc/nginx/sites-available/news.docms.nz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 性能优化建议

1. **Docker优化**
   - 使用多阶段构建减小镜像大小
   - 配置适当的容器资源限制
   - 使用Docker Volume提高I/O性能

2. **应用优化**
   - 配置Gunicorn工作进程数
   - 使用Redis容器作为缓存层
   - 实现容器健康检查

3. **监控方案**
   - 使用Docker Stats监控容器资源
   - 集成Prometheus和Grafana
   - 配置容器日志聚合

## 维护建议

1. **容器维护**
   - 定期更新基础镜像
   - 监控容器日志和资源使用
   - 配置容器自动重启策略

2. **数据维护**
   - 定期备份挂载的新闻文件
   - 管理Docker Volume
   - 清理未使用的镜像和容器

3. **安全维护**
   - 定期更新依赖包
   - 使用非root用户运行容器
   - 限制容器网络访问

## 故障排除

1. 检查容器状态：
   ```bash
   docker-compose ps
   docker logs news-docms
   ```

2. 检查容器资源使用：
   ```bash
   docker stats news-docms
   ```

3. 重启服务：
   ```bash
   docker-compose restart
   ```

4. 完全重建服务：
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

5. 检查挂载卷：
   ```bash
   docker volume ls
   docker-compose config
   ```