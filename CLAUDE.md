# CLAUDE.md - news.docms.nz 项目指南

本文件为 Claude Code 提供项目开发、内容管理和部署的完整指南。

---

## 项目概述

这是一个基于 Flask 的新闻展示系统，支持 Markdown 和 HTML 两种格式的新闻内容，提供 Web 浏览界面和管理员编辑器。

**技术栈：** Flask + Python-Markdown + Jinja2 + Gunicorn + Docker

**访问地址：** https://news.docms.nz / http://192.168.31.205:8009

---

## 服务器信息

| 项目 | 信息 |
|------|------|
| **服务器** | maxazure@192.168.31.205 |
| **项目路径** | ~/projects/news.docms.nz |
| **容器名称** | news-docms |
| **端口** | 8009 |

---

## 新闻发布完整流程

### 推荐工作流程

```
1. 内容调研 → 2. 撰写文章 → 3. 本地预览 → 4. 上传服务器 → 5. 在线验证
```

### 方法一：使用 askall 搜索 + HTML 模板（推荐）

**适用于：** 技术研究、产品分析、行业报告

```bash
# 1. 使用 askall 搜索相关信息
askall run --prompt "搜索主题" --providers perplexity,chatgpt

# 2. 查看搜索结果
cat askall-output/*/perplexity.md
cat askall-output/*/chatgpt.md

# 3. 使用 HTML 模板撰写文章（参考下方"HTML 样式规范"）
nano /tmp/YYYYMMDD.html

# 4. 上传到服务器
scp /tmp/YYYYMMDD.html maxazure@192.168.31.205:~/projects/news.docms.nz/news/

# 5. 验证访问
curl -s https://news.docms.nz/YYYYMMDD | grep -o '<title>[^<]*</title>'
```

### 方法二：通过 Web 编辑器

**适用于：** 简单新闻、快速更新

1. 访问 https://news.docms.nz/login
2. 使用管理员账号登录
3. 访问 https://news.docms.nz/editor/new
4. 编写内容并保存

### 方法三：直接在服务器创建

```bash
# SSH 连接
ssh maxazure@192.168.31.205

# 创建文件
cd ~/projects/news.docms.nz/news
nano YYYYMMDD.html  # 推荐 HTML 格式
```

---

## HTML 样式规范（重要！）

### 必须包含的元素

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <!-- 移动端响应式必须 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文章标题</title>
    <style>
        /* 样式代码 */
    </style>
</head>
<body>
    <div class="container">
        <!-- 内容 -->
    </div>
</body>
</html>
```

### 完整样式模板

复制以下模板作为新闻文章的基础：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文章标题</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 10px;
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 1.8em;
            font-weight: 300;
            margin-bottom: 10px;
        }
        .header .meta {
            font-size: 0.85em;
            opacity: 0.9;
        }
        .content {
            padding: 25px 50px;
        }
        h2 {
            color: #2c3e50;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        h3 {
            color: #667eea;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        h4 {
            color: #7f8c8d;
            font-size: 1.1em;
            margin-top: 15px;
        }
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        ul, ol {
            margin: 12px 0;
            padding-left: 25px;
        }
        li {
            margin: 6px 0;
        }
        strong, b {
            color: #667eea;
            font-weight: 600;
        }

        /* 表格样式 - 重要！需要 data-label 属性 */
        .table-wrapper {
            overflow-x: auto;
            margin: 20px 0;
            -webkit-overflow-scrolling: touch;
        }
        table {
            width: 100%;
            min-width: 500px;
            border-collapse: collapse;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        tbody tr:hover {
            background-color: #f8f9fa;
        }
        tbody tr:nth-child(even) {
            background-color: #fafbfc;
        }

        /* 代码块 */
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            color: #ecf0f1;
        }

        /* 特殊框 */
        .highlight-box {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .info-box {
            background: #e8f4fd;
            border-left: 5px solid #2196F3;
            padding: 15px;
            margin: 15px 0;
        }
        .warning-box {
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
        }

        /* 链接 */
        a {
            color: #667eea;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }

        /* 页脚 */
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.85em;
        }

        /* 移动端响应式 - 必须！ */
        @media screen and (max-width: 768px) {
            body { padding: 0; }
            .container { border-radius: 0; }
            .header { padding: 20px 15px; }
            .header h1 { font-size: 1.3em; }
            .content { padding: 15px; }
            h2 { font-size: 1.3em; }
            h3 { font-size: 1.1em; }

            /* 移动端表格：卡片式布局 */
            .table-wrapper { margin: 15px -15px; }
            table { display: block; overflow-x: auto; }
            thead tr { position: absolute; top: -9999px; }
            tr { display: block; margin-bottom: 10px; border: 1px solid #ecf0f1; }
            td {
                display: block;
                border: none;
                border-bottom: 1px solid #ecf0f1;
                padding: 8px 10px;
                padding-left: 50%;
                position: relative;
                text-align: left;
            }
            td:before {
                position: absolute;
                top: 8px;
                left: 10px;
                width: 45%;
                padding-right: 10px;
                white-space: nowrap;
                font-weight: bold;
                content: attr(data-label);
                color: #667eea;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>文章标题</h1>
            <div class="meta">发布日期：YYYY年MM月DD日 | 分类：xxx</div>
        </div>

        <div class="content">
            <h2>章节标题</h2>
            <p>段落内容...</p>

            <h3>小节标题</h3>
            <ul>
                <li>列表项</li>
            </ul>

            <!-- 表格示例：注意 td 的 data-label 属性 -->
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>列1</th>
                            <th>列2</th>
                            <th>列3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td data-label="列1">内容1</td>
                            <td data-label="列2">内容2</td>
                            <td data-label="列3">内容3</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <p>生成时间：YYYY年MM月DD日</p>
        </div>
    </div>
</body>
</html>
```

### 样式检查清单

发布前必须确认：

- [ ] 包含 `viewport` meta 标签
- [ ] 包含移动端媒体查询 `@media screen and (max-width: 768px)`
- [ ] 表格使用 `.table-wrapper` 包裹
- [ ] 表格单元格 `td` 添加 `data-label` 属性
- [ ] 渐变色使用项目主题色 `#667eea` → `#764ba2`
- [ ] 所有颜色使用 CSS 变量或固定值
- [ ] 代码块使用深色背景 `#2c3e50`
- [ ] 链接颜色为紫色 `#667eea`
- [ ] 测试移动端显示效果

---

## 文件命名规范

| 格式 | 命名规则 | 示例 | 说明 |
|------|----------|------|------|
| **日期型** | `YYYYMMDD.html` | `20260104.html` | 推荐使用 |
| **日期+序号** | `YYYYMMDDNN.html` | `2026010401.html` | 当天多篇文章 |
| **描述型** | 英文/拼音名称 | `ai-news-report.html` | 特殊主题 |

**注意：** 使用当前年份，如 2026 年应使用 `2026` 开头。

---

## 部署到服务器

### 代码部署（修改 app.py 时）

```bash
# 1. 本地提交
git add .
git commit -m "描述"
git push

# 2. 服务器部署
ssh maxazure@192.168.31.205 "cd ~/projects/news.docms.nz && git pull && docker-compose down && docker-compose up -d --build"
```

### 文章部署（仅添加文章时）

```bash
# 直接上传，无需重新部署
scp /tmp/YYYYMMDD.html maxazure@192.168.31.205:~/projects/news.docms.nz/news/

# 或使用 rsync
rsync -avz /tmp/YYYYMMDD.html maxazure@192.168.31.205:~/projects/news.docms.nz/news/
```

### 验证文章

```bash
# 检查标题
curl -s https://news.docms.nz/YYYYMMDD | grep -o '<title>[^<]*</title>'

# 检查首页是否显示
curl -s https://news.docms.nz/ | grep -o "YYYYMMDD"
```

---

## 重要注意事项

### news 目录不受 Git 管理

`news/` 目录已被 `.gitignore` 排除：
- 服务器上新增的文章不会被 Git 追踪
- 部署代码时不会覆盖服务器上的现有文章
- 避免版本冲突和数据丢失

### 文章备份

```bash
# 从服务器备份到本地
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
├── .env                # 环境变量（不提交）
├── .gitignore          # Git 忽略规则
├── news/               # 新闻内容（不受 Git 管理）
│   ├── *.html         # HTML 格式文章（推荐）
│   └── *.md           # Markdown 格式文章
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

## 故障排除

### 文章未显示

1. 检查文件名格式是否正确
2. 确认文件在 `news/` 目录下
3. HTML 文件必须包含 `<title>` 标签
4. 检查文件权限：`ls -la ~/projects/news.docms.nz/news/`

### 表格在移动端显示异常

1. 确认使用了 `.table-wrapper` 包裹
2. 检查 `td` 标签是否有 `data-label` 属性
3. 确认包含移动端媒体查询

### 无法登录

1. 检查 `.env` 文件中的用户名和密码
2. 清除浏览器 Cookie 后重试

---

## 更新历史

| 日期 | 提交 | 说明 |
|------|------|------|
| 2026-01-04 | 最新 | 添加完整新闻发布流程和 HTML 样式规范 |
| 2025-01-04 | 9f2b097 | 将 news 目录从 git 仓库排除 |
| 2025-01-04 | 3724735 | 备份服务器文章到本地 |
