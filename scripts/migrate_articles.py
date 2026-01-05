#!/usr/bin/env python3
"""
文章迁移脚本 - 将 news/ 目录中的文章迁移到数据库
"""
import os
import sys
import re

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Article, Category
import markdown
from datetime import datetime


def migrate_articles(news_dir='news'):
    """迁移 news 目录中的文章到数据库"""
    print(f"开始迁移文章从 {news_dir} 目录...")

    # 获取或创建默认管理员
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("未找到管理员账户，正在创建...")
        admin = User(username='admin', email='admin@news.docms.nz', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("管理员账户创建成功: admin / admin123")

    # 获取默认分类
    category = Category.query.first()

    if not os.path.exists(news_dir):
        print(f"目录 {news_dir} 不存在，跳过迁移")
        return 0

    migrated_count = 0
    skipped_count = 0

    for filename in os.listdir(news_dir):
        if not filename.endswith(('.md', '.html')):
            continue

        filepath = os.path.join(news_dir, filename)
        if not os.path.isfile(filepath):
            continue

        # 提取 slug（去掉扩展名）
        slug = os.path.splitext(filename)[0]

        # 检查是否已存在
        if Article.query.filter_by(slug=slug).first():
            print(f"  跳过: {filename} (已存在)")
            skipped_count += 1
            continue

        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取标题
        if filename.endswith('.md'):
            title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else slug
            # 转换为 HTML
            html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        else:
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1) if title_match else slug
            html_content = content

        # 创建文章
        article = Article(
            title=title,
            slug=slug,
            content=content if filename.endswith('.md') else '',
            html_content=html_content,
            excerpt=content[:200] if len(content) > 200 else content,
            status='published',
            user_id=admin.id,
            category_id=category.id if category else None,
            published_at=datetime.utcnow()
        )

        db.session.add(article)
        migrated_count += 1
        print(f"  迁移: {filename} -> {title}")

    db.session.commit()
    print(f"\n迁移完成！")
    print(f"  新增: {migrated_count} 篇")
    print(f"  跳过: {skipped_count} 篇 (已存在)")

    return migrated_count


if __name__ == '__main__':
    with app.app_context():
        migrate_articles()
