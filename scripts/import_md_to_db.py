#!/usr/bin/env python3
"""
将 news/ 目录中的 Markdown 和 HTML 文件导入数据库
"""
import os
import sys
import re
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, Article, db, markdown, init_db


def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    title = None
    category = None
    date = None

    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end != -1:
            frontmatter = content[3:frontmatter_end]
            content = content[frontmatter_end + 3:].strip()

            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == 'title':
                        title = value
                    elif key == 'category':
                        category = value
                    elif key == 'date':
                        date = value

    # 如果没有标题，尝试从第一个 # 标题获取
    if not title:
        match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        if match:
            title = match.group(1)

    # 如果还是没有标题，使用文件名
    if not title:
        title = "未命名文章"

    return title, category, date, content


def parse_html_file(filepath):
    """解析 HTML 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else None

    # 提取分类（从 meta 或内容中）
    category = None
    category_match = re.search(r'分类：([^<|]+)', content)
    if category_match:
        category = category_match.group(1).strip()

    # 提取日期
    date = None
    date_match = re.search(r'(\d{4}年\d{2}月\d{2}日)', content)
    if date_match:
        date_str = date_match.group(1)
        # 转换为 ISO 格式
        try:
            date = datetime.strptime(date_str, '%Y年%m月%d日').strftime('%Y-%m-%d')
        except:
            pass

    # 提取正文内容（container 内部）
    body_match = re.search(r'<div class="content">(.*?)</div>\s*<div class="footer">', content, re.DOTALL)
    body = body_match.group(1) if body_match else ""

    # 清理 HTML 标签，转换为纯文本用于摘要
    clean_body = re.sub(r'<[^>]+>', '', body)
    clean_body = re.sub(r'\s+', ' ', clean_body).strip()

    # 如果没有标题，尝试从 h1 获取
    if not title:
        h1_match = re.search(r'<h1>(.*?)</h1>', content)
        title = h1_match.group(1) if h1_match else None

    if not title:
        title = "未命名文章"

    return title, category, date, clean_body, body


def generate_excerpt(content, max_length=200):
    """从 Markdown 内容生成摘要"""
    # 移除代码块
    clean_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # 移除标题标记
    clean_content = re.sub(r'^#+\s*', '', clean_content, flags=re.MULTILINE)
    # 移除加粗和斜体
    clean_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_content)
    clean_content = re.sub(r'\*([^*]+)\*', r'\1', clean_content)
    # 清理多余空格
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()

    if len(clean_content) > max_length:
        return clean_content[:max_length] + '...'
    return clean_content


def import_md_files(news_dir='news'):
    """导入 MD 和 HTML 文件到数据库"""
    # 初始化数据库
    init_db()

    with app.app_context():
        # MD 文件
        md_files = [f for f in os.listdir(news_dir) if f.endswith('.md') and not f.startswith('_')]
        # HTML 文件
        html_files = [f for f in os.listdir(news_dir) if f.endswith('.html')]

        print(f"找到 {len(md_files)} 个 MD 文件")
        print(f"找到 {len(html_files)} 个 HTML 文件")

        imported = 0
        skipped = 0

        # 导入 MD 文件
        for filename in sorted(md_files, reverse=True):
            filepath = os.path.join(news_dir, filename)
            slug = filename[:-3]  # 移除 .md 扩展名

            # 检查是否已存在
            existing = Article.query.filter_by(slug=slug).first()
            if existing:
                print(f"  跳过: {slug} (已存在)")
                skipped += 1
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            title, category, date_str, body = parse_frontmatter(content)

            # 生成 slug
            slug_clean = re.sub(r'[^\w\u4e00-\u9fff-]', '-', slug.lower())
            slug_clean = re.sub(r'-+', '-', slug_clean).strip('-')

            # 生成 HTML
            html_content = markdown.markdown(body, extensions=['fenced_code', 'tables'])

            # 生成摘要
            excerpt = generate_excerpt(body)

            # 解析日期
            published_at = datetime.now()
            if date_str:
                try:
                    published_at = datetime.fromisoformat(date_str)
                except:
                    pass

            # 创建文章
            article = Article(
                title=title,
                slug=slug_clean,
                content=body,
                html_content=html_content,
                excerpt=excerpt,
                status='published',
                published_at=published_at,
                user_id=1,  # 默认管理员
                view_count=0
            )

            db.session.add(article)
            print(f"  导入 MD: {slug_clean} - {title}")
            imported += 1

        # 导入 HTML 文件
        for filename in sorted(html_files, reverse=True):
            filepath = os.path.join(news_dir, filename)
            slug = filename[:-5]  # 移除 .html 扩展名

            # 检查是否已存在
            existing = Article.query.filter_by(slug=slug).first()
            if existing:
                print(f"  跳过: {slug} (已存在)")
                skipped += 1
                continue

            title, category, date_str, clean_body, body_html = parse_html_file(filepath)

            # 生成 slug
            slug_clean = re.sub(r'[^\w\u4e00-\u9fff-]', '-', slug.lower())
            slug_clean = re.sub(r'-+', '-', slug_clean).strip('-')

            # 使用原始 HTML 作为 content（保留样式）
            html_content = body_html

            # 生成摘要
            excerpt = generate_excerpt(clean_body) if clean_body else title[:200]

            # 解析日期
            published_at = datetime.now()
            if date_str:
                try:
                    published_at = datetime.fromisoformat(date_str)
                except:
                    pass

            # 创建文章
            article = Article(
                title=title,
                slug=slug_clean,
                content=html_content,  # HTML 内容存储在 content 字段
                html_content=html_content,
                excerpt=excerpt,
                status='published',
                published_at=published_at,
                user_id=1,  # 默认管理员
                view_count=0
            )

            db.session.add(article)
            print(f"  导入 HTML: {slug_clean} - {title}")
            imported += 1

        db.session.commit()
        print(f"\n完成! 导入 {imported} 篇，跳过 {skipped} 篇")


if __name__ == '__main__':
    import_md_files()
