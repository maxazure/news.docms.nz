#!/usr/bin/env python3
"""
更新现有文章的摘要字段
将存储的 HTML/Markdown 摘要转换为纯文本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, generate_excerpt_from_markdown
from models import db, Article


def update_article_excerpts():
    """更新所有文章的摘要"""
    with app.app_context():
        articles = Article.query.all()
        updated_count = 0

        for article in articles:
            # 检查摘要是否包含 HTML 标签
            if article.excerpt and ('<!DOCTYPE' in article.excerpt or '<html' in article.excerpt or '<div' in article.excerpt):
                # 重新生成摘要
                new_excerpt = generate_excerpt_from_markdown(article.content)
                article.excerpt = new_excerpt
                updated_count += 1
                print(f"更新文章: {article.title}")
            elif not article.excerpt:
                # 如果摘要为空，也生成一个
                new_excerpt = generate_excerpt_from_markdown(article.content)
                article.excerpt = new_excerpt
                updated_count += 1
                print(f"生成摘要: {article.title}")

        if updated_count > 0:
            db.session.commit()
            print(f"\n成功更新 {updated_count} 篇文章的摘要")
        else:
            print("\n没有需要更新的文章")


if __name__ == '__main__':
    update_article_excerpts()
