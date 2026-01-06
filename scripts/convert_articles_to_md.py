#!/usr/bin/env python3
"""
将现有 HTML 文章转换为 Markdown 格式
使用正则表达式解析，不依赖外部库
"""

import re
import os
import subprocess

# 服务器配置
SERVER = "maxazure@192.168.31.205"
NEWS_DIR = "~/projects/news.docms.nz/news"


def extract_article_data(html_content):
    """从HTML内容中提取文章数据"""
    # 提取标题
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "未命名文章"

    # 提取内容区域
    content_match = re.search(r'<div class="content">(.*?)</div>', html_content, re.DOTALL)
    if not content_match:
        content_match = re.search(r'<article>(.*?)</article>', html_content, re.DOTALL)
    if not content_match:
        # 提取body内容
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
        content = body_match.group(1) if body_match else html_content
    else:
        content = content_match.group(1)

    # 提取元数据
    meta = {}
    meta_match = re.search(r'<div class="meta"[^>]*>(.*?)</div>', html_content, re.DOTALL)
    if meta_match:
        meta_text = re.sub(r'<[^>]+>', '', meta_match.group(1)).strip()
        # 尝试提取日期
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', meta_text)
        if date_match:
            year, month, day = date_match.groups()
            meta['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # 尝试提取分类
        cat_match = re.search(r'分类[：:]\s*([^\s|]+)', meta_text)
        if cat_match:
            meta['category'] = cat_match.group(1)

    # 转换为Markdown
    markdown = convert_html_to_markdown(content, title, meta)
    return markdown, title, meta


def convert_html_to_markdown(html_content, title, meta):
    """将HTML内容转换为Markdown"""
    lines = []

    # 添加元数据头部
    lines.append("---")
    lines.append(f"title: {title}")
    if 'date' in meta:
        lines.append(f"date: {meta['date']}")
    if 'category' in meta:
        lines.append(f"category: {meta['category']}")
    lines.append("---")
    lines.append("")

    # 移除script和style标签
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)

    # 移除注释
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

    # 逐个处理元素
    pos = 0
    in_list = False
    list_type = None
    list_items = []

    # 定义所有标签的正则模式
    patterns = [
        (r'<h2[^>]*>(.*?)</h2>', 'h2'),
        (r'<h3[^>]*>(.*?)</h3>', 'h3'),
        (r'<h4[^>]*>(.*?)</h4>', 'h4'),
        (r'<h5[^>]*>(.*?)</h5>', 'h5'),
        (r'<p[^>]*>(.*?)</p>', 'p'),
        (r'<ul[^>]*>', 'ul_start'),
        (r'</ul>', 'ul_end'),
        (r'<ol[^>]*>', 'ol_start'),
        (r'</ol>', 'ol_end'),
        (r'<li[^>]*>(.*?)</li>', 'li'),
        (r'<blockquote[^>]*>(.*?)</blockquote>', 'blockquote'),
        (r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', 'pre_code'),
        (r'<pre[^>]*>(.*?)</pre>', 'pre'),
        (r'<hr\s*/?>', 'hr'),
    ]

    while pos < len(html_content):
        # 找到下一个标签
        match = None
        min_pos = len(html_content)

        for pattern, tag_type in patterns:
            m = re.search(pattern, html_content[pos:], re.DOTALL)
            if m and m.start() < min_pos:
                min_pos = m.start()
                match = (m, tag_type)

        if match:
            m, tag_type = match
            # 处理标签前的文本
            before_text = html_content[pos:pos + m.start()].strip()
            if before_text and not in_list:
                # 纯文本段落
                cleaned = clean_text(before_text)
                if cleaned:
                    lines.append("")
                    lines.append(cleaned)
                    lines.append("")

            # 处理标签
            if tag_type == 'h2':
                text = clean_text(m.group(1))
                if text:
                    lines.append("")
                    lines.append(f"## {text}")
                    lines.append("")
            elif tag_type == 'h3':
                text = clean_text(m.group(1))
                if text:
                    lines.append("")
                    lines.append(f"### {text}")
                    lines.append("")
            elif tag_type == 'h4':
                text = clean_text(m.group(1))
                if text:
                    lines.append("")
                    lines.append(f"#### {text}")
                    lines.append("")
            elif tag_type == 'p':
                text = clean_text(m.group(1))
                if text:
                    lines.append("")
                    lines.append(text)
                    lines.append("")
            elif tag_type == 'ul_start':
                in_list = True
                list_type = 'ul'
            elif tag_type == 'ol_start':
                in_list = True
                list_type = 'ol'
            elif tag_type in ['ul_end', 'ol_end']:
                # 输出列表
                if list_items:
                    for idx, item in enumerate(list_items, 1):
                        prefix = f"{idx}." if list_type == 'ol' else "-"
                        lines.append(prefix + " " + item)
                    if list_items:
                        lines.append("")
                in_list = False
                list_type = None
                list_items = []
            elif tag_type == 'li':
                text = clean_text(m.group(1))
                if text:
                    list_items.append(text)
            elif tag_type == 'blockquote':
                text = clean_text(m.group(1))
                if text:
                    lines.append("")
                    lines.append(f"> {text}")
                    lines.append("")
            elif tag_type == 'pre_code':
                code = m.group(1).strip()
                lines.append("")
                lines.append("```")
                lines.append(code)
                lines.append("```")
                lines.append("")
            elif tag_type == 'pre':
                code = m.group(1).strip()
                code = re.sub(r'<code[^>]*>', '', code)
                code = re.sub(r'</code>', '', code)
                lines.append("")
                lines.append("```")
                lines.append(code.strip())
                lines.append("```")
                lines.append("")
            elif tag_type == 'hr':
                lines.append("")
                lines.append("---")
                lines.append("")

            pos += m.end()
        else:
            # 没有更多标签了
            remaining = html_content[pos:].strip()
            if remaining:
                # 检查是否是表格
                table_match = re.search(r'<table[^>]*>(.*?)</table>', remaining, re.DOTALL)
                if table_match:
                    table_md = convert_table(table_match.group(1))
                    lines.append("")
                    lines.extend(table_md)
                    lines.append("")
                    pos += table_match.end()
                else:
                    # 处理特殊框
                    highlight_match = re.search(r'<div class="highlight-box"[^>]*>(.*?)</div>', remaining, re.DOTALL)
                    if highlight_match:
                        text = clean_text(highlight_match.group(1))
                        if text:
                            lines.append("")
                            lines.append(f"> **{text}**")
                            lines.append("")
                        pos += highlight_match.end()
                        continue

                    info_match = re.search(r'<div class="info-box"[^>]*>(.*?)</div>', remaining, re.DOTALL)
                    if info_match:
                        text = clean_text(info_match.group(1))
                        if text:
                            lines.append("")
                            lines.append(f"> 💡 {text}")
                            lines.append("")
                        pos += info_match.end()
                        continue

                    warning_match = re.search(r'<div class="warning-box"[^>]*>(.*?)</div>', remaining, re.DOTALL)
                    if warning_match:
                        text = clean_text(warning_match.group(1))
                        if text:
                            lines.append("")
                            lines.append(f"> ⚠️ {text}")
                            lines.append("")
                        pos += warning_match.end()
                        continue

                    # 其他文本
                    cleaned = clean_text(remaining)
                    if cleaned:
                        lines.append("")
                        lines.append(cleaned)
                        lines.append("")
                    break
            else:
                break

    # 后处理：清理空行
    result = '\n'.join(lines)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    result = result.strip()

    return result


def convert_table(table_html):
    """转换表格为Markdown"""
    lines = []

    # 提取表头
    thead_match = re.search(r'<thead[^>]*>(.*?)</thead>', table_html, re.DOTALL)
    tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_html, re.DOTALL)
    tbody = tbody_match.group(1) if tbody_match else table_html

    # 处理所有行
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

    for idx, row in enumerate(rows):
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        if cells:
            cleaned_cells = [clean_text(c).strip() for c in cells]
            lines.append('| ' + ' | '.join(cleaned_cells) + ' |')
            if idx == 0:
                # 表头分隔线
                lines.append('| ' + ' | '.join(['---'] * len(cleaned_cells)) + ' |')

    return lines


def clean_text(text):
    """清理HTML标签和实体"""
    if not text:
        return ""

    # 处理加粗
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)

    # 处理斜体
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)

    # 处理代码
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)

    # 处理链接
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # 处理换行
    text = text.replace('<br/>', '\n').replace('<br>', '\n')

    # 去除其他标签
    text = re.sub(r'<[^>]+>', '', text)

    # 解码HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")

    # 清理多余空白
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()

    return text


def get_output_filename(input_filename, index=0):
    """生成输出文件名，避免冲突"""
    base_match = re.match(r'(\d{8})', input_filename)
    if base_match:
        base = base_match.group(1)
        # 如果原文件名包含序号或时间后缀，保留它
        suffix_match = re.match(r'\d{8}-(\d{2})', input_filename)
        time_match = re.match(r'\d{8}(\d{4})', input_filename)
        if suffix_match:
            return f"{base}-{suffix_match.group(1)}.md"
        elif time_match:
            return f"{base}{time_match.group(1)}.md"
        elif index > 0:
            return f"{base}-{str(index+1).zfill(2)}.md"
        else:
            return f"{base}.md"
    return input_filename.replace('.html', '.md')


def main():
    """主函数"""
    print("📰 开始转换文章...")

    # 获取远程文件列表
    result = subprocess.run(
        f"ssh {SERVER} 'ls {NEWS_DIR}/*.html 2>/dev/null'",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ 无法获取文章列表")
        return

    html_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip() and f.endswith('.html')]

    if not html_files:
        print("📭 没有找到HTML文章")
        return

    print(f"📄 找到 {len(html_files)} 篇文章")

    # 按日期分组
    date_groups = {}
    for html_path in html_files:
        filename = os.path.basename(html_path)
        date_match = re.match(r'(\d{8})', filename)
        if date_match:
            date = date_match.group(1)
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(filename)
        else:
            # 无日期文件
            if '_other' not in date_groups:
                date_groups['_other'] = []
            date_groups['_other'].append(filename)

    # 转换每篇文章
    converted = []
    for date, files in sorted(date_groups.items()):
        for idx, filename in enumerate(sorted(files)):
            print(f"\n🔄 处理: {filename}")

            # 下载HTML内容
            result = subprocess.run(
                f"ssh {SERVER} 'cat {NEWS_DIR}/{filename}'",
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"  ❌ 下载失败")
                continue

            html_content = result.stdout

            # 转换
            try:
                md_content, title, meta = extract_article_data(html_content)
                if not md_content:
                    print(f"  ❌ 解析失败")
                    continue

                # 如果同一天有多篇文章，使用原文件名中的后缀或添加序号
                output_filename = get_output_filename(filename, idx if len(files) > 1 else -1)

                # 写入到服务器（使用cat命令）
                # 创建临时文件
                local_tmp = f"/tmp/{output_filename}"
                with open(local_tmp, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                # 上传到服务器
                subprocess.run(
                    f"scp {local_tmp} {SERVER}:{NEWS_DIR}/{output_filename}",
                    shell=True,
                    capture_output=True
                )
                os.remove(local_tmp)

                print(f"  ✅ 已转换: {output_filename}")
                if title:
                    print(f"     标题: {title}")
                converted.append(output_filename)

            except Exception as e:
                print(f"  ❌ 转换失败: {e}")

    print(f"\n\n📊 转换完成!")
    print(f"✅ 成功: {len(converted)} 篇")
    print(f"\n转换的文件:")
    for f in converted:
        print(f"  - {f}")

    # 备份原HTML文件
    print(f"\n💾 备份原HTML文件到 _html 目录...")
    subprocess.run(
        f"ssh {SERVER} 'mkdir -p {NEWS_DIR}/_html && mv {NEWS_DIR}/*.html {NEWS_DIR}/_html/ 2>/dev/null || true'",
        shell=True
    )
    print("✅ 备份完成")


if __name__ == "__main__":
    main()
