# 新闻展示系统

## 项目简介

这是一个基于Flask的新闻展示系统，支持Markdown格式的新闻内容管理和展示。系统采用Docker容器化部署，具有良好的可移植性和可维护性。

## 功能特点

- 支持Markdown格式新闻内容
- 响应式网页设计，适配多种设备
- Docker容器化部署
- Nginx反向代理支持
- 简单高效的文件管理机制

## 技术架构

- 后端框架：Flask
- 前端技术：HTML5, CSS3
- 容器化：Docker & Docker Compose
- 服务器：Gunicorn
- 反向代理：Nginx（可选）

## 本地开发环境配置

1. 克隆项目
```bash
git clone <repository_url>
cd news.docms.nz
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行开发服务器
```bash
flask run
```

## Docker部署

1. 确保安装了Docker和Docker Compose

2. 构建并启动容器
```bash
docker-compose up -d --build
```

3. 访问服务
- 本地访问：http://localhost:8009
- 如果配置了Nginx，可通过域名访问

## 新闻内容管理

### 新闻文件格式
- 新闻文件使用Markdown格式
- 文件名格式：YYYYMMDD.md（例如：20250302.md）
- 存放位置：/news目录

### 添加新闻
1. 在news目录下创建新的Markdown文件
2. 按照日期格式命名（YYYYMMDD.md）
3. 编写新闻内容，使用Markdown格式

### 修改新闻
1. 直接编辑对应的Markdown文件
2. 保存后自动生效，无需重启服务

## 系统维护

### 日常维护
- 定期备份news目录
- 监控服务器资源使用情况
- 检查日志文件

### 故障排除
- 查看容器状态：`docker-compose ps`
- 查看容器日志：`docker logs news-docms`
- 重启服务：`docker-compose restart`

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 发起 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。