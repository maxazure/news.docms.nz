from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import markdown
import os
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))  # 从环境变量获取密钥，如果不存在则生成随机密钥
# 使用默认的基于cookie的session，确保session能正常工作
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)  # 设置session过期时间为1年
app.config['NEWS_DIR'] = os.getenv('NEWS_DIR', 'news') # 新增：新闻文件存储目录
# 确保新闻目录存在，避免初次运行时因目录缺失导致报错
os.makedirs(app.config['NEWS_DIR'], exist_ok=True)

# 从环境变量获取用户认证信息，如果未设置则使用默认账号
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')
USERS = {
    ADMIN_USERNAME: ADMIN_PASSWORD
}

import re
from flask import send_from_directory
from bs4 import BeautifulSoup

@app.route('/<filename>')
def show_news(filename):
    # 尝试.md文件
    md_path = os.path.join(app.config['NEWS_DIR'], f'{filename}.md')
    html_path = os.path.join(app.config['NEWS_DIR'], f'{filename}.html')

    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            html_content = markdown.markdown(content)
            # 尝试从Markdown中提取标题
            title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else filename
            return render_template('news.html', title=title, content=html_content)
    
    elif os.path.exists(html_path):
        # 对于HTML文件，直接返回其内容
        return send_from_directory(app.config['NEWS_DIR'], f'{filename}.html')

    else:
        return '404 - 新闻未找到', 404

def get_news_title(filepath):
    filename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
    if filepath.endswith('.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
            return title_match.group(1) if title_match else filename_without_ext
    elif filepath.endswith('.html'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.string if title_tag and title_tag.string else filename_without_ext
    return filename_without_ext

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    # 列出所有新闻文件并按时间倒序排序
    news_files = [f for f in os.listdir(app.config['NEWS_DIR']) if f.endswith(('.md', '.html'))]
    # 排序时，优先按文件名（通常是日期）倒序
    news_files.sort(key=lambda x: os.path.splitext(x)[0], reverse=True)
    
    # 获取新闻标题和文件名
    news_items = []
    for f in news_files:
        filepath = os.path.join(app.config['NEWS_DIR'], f)
        title = get_news_title(filepath)
        news_items.append({'filename': os.path.splitext(f)[0], 'title': title})
    
    # 分页处理
    per_page = 5  # 每页显示5条新闻
    total_pages = (len(news_items) + per_page - 1) // per_page  # 计算总页数
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_files = news_items[start_idx:end_idx]
    
    # 添加调试信息，确认session状态
    print(f"首页访问，当前session状态: {session}")
    print(f"logged_in状态: {session.get('logged_in')}")
    return render_template('index.html', news_items=current_page_files, page=page, total_pages=total_pages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session.permanent = True  # 确保session数据被持久化
            session['logged_in'] = True
            session['username'] = username
            print(f"用户登录成功: {username}, session: {session}")
            flash('登录成功！')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('您已成功登出！')
    return redirect(url_for('index'))

@app.route('/editor/<filename>')
def editor(filename):
    # 检查用户是否已登录
    if not session.get('logged_in'):
        flash('请先登录！')
        return redirect(url_for('login'))
        
    # 自动检测文件扩展名
    md_path = os.path.join(app.config['NEWS_DIR'], f'{filename}.md')
    html_path = os.path.join(app.config['NEWS_DIR'], f'{filename}.html')
    news_path = None
    if os.path.exists(md_path):
        news_path = md_path
    elif os.path.exists(html_path):
        news_path = html_path

    content = ''
    if news_path:
        with open(news_path, 'r', encoding='utf-8') as f:
            content = f.read()
    elif filename != 'new':
        # 如果文件不存在且不是创建新文件，则提示
        flash(f'文件 {filename} 不存在，将为您创建新文件。')

    return render_template('editor.html', filename=filename, content=content)

@app.route('/api/save', methods=['POST'])
def save_file():
    # 检查用户是否已登录
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未授权，请先登录'}), 401
        
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    original_filename = data.get('original_filename')
    file_type = data.get('file_type', 'md') # 新增：获取文件类型，默认为md

    if not filename or filename == 'new':
        filename = datetime.now().strftime('%Y%m%d%H%M%S') # 确保新文件名唯一
    
    # 确定文件扩展名
    extension = '.' + file_type
    news_path = os.path.join(app.config['NEWS_DIR'], f'{filename}{extension}')

    # 冲突检测：
    # 如果是新建文件（original_filename为空或'new'）且目标文件已存在
    # 或者，如果是重命名操作（original_filename与filename不同）且目标文件已存在
    if ((not original_filename or original_filename == 'new') and os.path.exists(news_path)) or \
       (original_filename and original_filename != filename and os.path.exists(news_path) and \
        not (os.path.splitext(original_filename)[0] == filename and os.path.splitext(original_filename)[1] == extension)):
        return jsonify({'success': False, 'message': f'文件 {filename}{extension} 已存在，请使用其他文件名'}), 400

    # 如果是重命名操作，在保存新文件前删除原文件
    if original_filename and original_filename != filename and original_filename != 'new':
        original_md_path = os.path.join(app.config['NEWS_DIR'], f'{original_filename}.md')
        original_html_path = os.path.join(app.config['NEWS_DIR'], f'{original_filename}.html')
        
        if os.path.exists(original_md_path):
            os.remove(original_md_path)
        if os.path.exists(original_html_path):
            os.remove(original_html_path)

    with open(news_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return jsonify({'success': True, 'filename': filename, 'file_type': file_type})

@app.route('/api/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # 检查用户是否已登录
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未授权，请先登录'}), 401
    
    md_path = os.path.join(app.config['NEWS_DIR'], f'{filename}.md')
    html_path = os.path.join(app.config['NEWS_DIR'], f'{filename}.html')
    
    deleted = False
    if os.path.exists(md_path):
        try:
            os.remove(md_path)
            deleted = True
        except Exception as e:
            return jsonify({'success': False, 'message': f'删除文件 {filename}.md 时出错: {str(e)}'}), 500
    
    if os.path.exists(html_path):
        try:
            os.remove(html_path)
            deleted = True
        except Exception as e:
            return jsonify({'success': False, 'message': f'删除文件 {filename}.html 时出错: {str(e)}'}), 500

    if not deleted:
        return jsonify({'success': False, 'message': f'文件 {filename}.md 或 {filename}.html 不存在'}), 404
    
    return jsonify({'success': True, 'message': f'文件 {filename} 已成功删除'})

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, port=8080)