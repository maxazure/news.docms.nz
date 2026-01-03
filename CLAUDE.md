# CLAUDE.md - news.docms.nz 项目指南

本文件为 Claude Code 提供项目开发、内容管理和部署的完整指南。

---

## 项目概述

这是一个基于 Flask 的新闻展示系统，支持 Markdown 和 HTML 两种格式的新闻内容，提供 Web 浏览界面和管理员编辑器。

**技术栈：** Flask + Python-Markdown + Jinja2 + Gunicorn + Docker

**访问地址：** http://192.168.31.205:8009

---

## 服务器信息

| 项目 | 信息 |
|------|------|
| **服务器** | maxazure@192.168.31.205 |
| **项目路径** | ~/projects/news.docms.nz |
| **容器名称** | news-docms |
| **端口** | 8009 |

---

## 添加新新闻的完整流程

### 方法一：通过 Web 编辑器添加（推荐）

1. 访问登录页面：http://192.168.31.205:8009/login
2. 使用管理员账号登录
3. 点击"编辑新文章"或访问 http://192.168.31.205:8009/editor/new
4. 在编辑器中编写新闻内容
5. 点击"保存"按钮

### 方法二：直接在服务器上添加文件

```bash
# SSH 连接到服务器
ssh maxazure@192.168.31.205

# 进入新闻目录
cd ~/projects/news.docms.nz/news

# 创建新的 Markdown 文件（按日期命名）
nano 20250105.md

# 或创建 HTML 文件
nano 20250105.html
```

---

## 新闻格式规范

### 文件命名规范

| 格式 | 命名规则 | 示例 |
|------|----------|------|
| **日期型** | `YYYYMMDD.md` 或 `YYYYMMDD.html` | `20250105.md` |
| **日期+序号** | `YYYYMMDDNN.md` (当天多篇文章) | `2025010501.md` |
| **描述型** | 有意义的英文/拼音名称 | `ai-news-report.html` |

### Markdown 格式规范

**基本结构：**

```markdown
# 主标题（文章标题，必须以 # 开头）

## 二级标题（章节标题）

这里是段落内容，支持**加粗**、*斜体*等 Markdown 语法。

### 三级标题（小节）

- 列表项 1
- 列表项 2
- 列表项 3

### 代码块

\```python
def hello():
    print("Hello, World!")
\```

### 引用

> 这是一段引用文字
```

**格式要求：**
- 第一行必须是 `# 主标题`，用于提取文章标题
- 使用 `##` 表示二级标题
- 使用 `###` 表示三级标题
- 空行分隔段落
- 使用 `-` 或 `*` 创建无序列表
- 使用 `**文本**` 加粗，`*文本*` 斜体

**参考示例：** `news/20250302.md`（科技新闻解读）

### HTML 格式规范

**基本结构：**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文章标题</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        h3 {
            color: #2980b9;
            margin-top: 25px;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>文章标题</h1>

        <h2>二级标题</h2>
        <p>段落内容...</p>

        <h3>三级标题</h3>
        <p>更多内容...</p>
    </div>
</body>
</html>
```

**格式要求：**
- 必须包含完整的 HTML 结构（DOCTYPE, html, head, body）
- `<title>` 标签内容将作为文章标题
- 建议内嵌 CSS 样式以保持独立性
- 使用语义化标签（h1, h2, h3, p, code, pre 等）

**参考示例：** `news/20250628012742.html`（Claude Code 研究报告）

---

## 部署到服务器

### 部署流程

```bash
# 1. 本地确保代码已同步到 GitHub
cd ~/projects/news.docms.nz
git status
git push

# 2. SSH 连接到服务器
ssh maxazure@192.168.31.205

# 3. 进入项目目录
cd ~/projects/news.docms.nz

# 4. 拉取最新代码
git pull

# 5. 停止并删除旧容器
docker-compose down

# 6. 重新构建并启动容器
docker-compose up -d --build

# 7. 查看容器状态
docker ps | grep news-docms

# 8. 查看日志（如有问题）
docker logs news-docms
```

### 快速部署脚本

```bash
# 一键部署命令
ssh maxazure@192.168.31.205 "cd ~/projects/news.docms.nz && git pull && docker-compose down && docker-compose up -d --build"
```

---

## 重要注意事项

### news 目录不受 Git 管理

`news/` 目录已被 `.gitignore` 排除，原因：
- 服务器上新增的文章不会被 Git 追踪
- 部署时不会覆盖服务器上的现有文章
- 避免版本冲突和数据丢失

**因此：**
- 新增文章直接在服务器上操作，或通过 Web 编辑器
- 如需备份，使用 `rsync` 或其他方式单独处理

### 服务器文章备份

```bash
# 从服务器备份文章到本地
rsync -avz maxazure@192.168.31.205:~/projects/news.docms.nz/news/ ~/projects/news.docms.nz/news/
```

---

## 项目结构

```
news.docms.nz/
├── app.py              # Flask 应用主文件
├── requirements.txt    # Python 依赖
├── Dockerfile          # Docker 镜像构建
├── docker-compose.yml  # Docker Compose 配置
├── .env                # 环境变量（不提交到 Git）
├── .gitignore          # Git 忽略规则
├── news/               # 新闻内容目录（不受 Git 管理）
│   ├── *.md           # Markdown 格式文章
│   └── *.html         # HTML 格式文章
├── templates/          # Jinja2 模板
│   ├── index.html     # 新闻列表页
│   ├── news.html      # 新闻详情页
│   ├── editor.html    # 编辑器页面
│   └── login.html     # 登录页面
└── static/             # 静态资源
    └── images/        # 图片资源
```

---

## API 端点

### 公开访问

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 新闻列表（首页） |
| `/page/<n>` | GET | 分页新闻列表 |
| `/<filename>` | GET | 查看特定新闻 |
| `/login` | GET/POST | 登录页面 |
| `/logout` | GET | 退出登录 |

### 需要认证

| 端点 | 方法 | 说明 |
|------|------|------|
| `/editor/<filename>` | GET | 编辑文章 |
| `/api/save` | POST | 保存文章 |
| `/api/delete/<filename>` | POST | 删除文章 |

---

## 开发与测试

### 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
flask run --port=8080
# 或
python app.py
```

### 运行测试

```bash
pip install pytest
pytest tests/
```

---

## 故障排除

### 容器无法启动

```bash
# 查看容器日志
docker logs news-docms

# 查看容器状态
docker ps -a | grep news-docms

# 重启容器
docker-compose restart
```

### 文章未显示

1. 检查文件名格式是否正确
2. 确认文件在 `news/` 目录下
3. Markdown 文件首行必须是 `# 标题`
4. HTML 文件必须包含 `<title>` 标签

### 无法登录

1. 检查 `.env` 文件中的用户名和密码
2. 确认容器已正确读取环境变量
3. 清除浏览器 Cookie 后重试

---

## 更新历史

| 日期 | 提交 | 说明 |
|------|------|------|
| 2025-01-04 | 9f2b097 | 将 news 目录从 git 仓库排除 |
| 2025-01-04 | 3724735 | 备份服务器文章到本地 |
