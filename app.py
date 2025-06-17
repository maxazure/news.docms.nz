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

# 从环境变量获取用户认证信息
USERS = {
    os.getenv('ADMIN_USERNAME'): os.getenv('ADMIN_PASSWORD')
}

@app.route('/<filename>')
def show_news(filename):
    news_path = os.path.join('news', f'{filename}.md')
    if not os.path.exists(news_path):
        return '404 - 新闻未找到', 404
    
    with open(news_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 将Markdown转换为HTML
        html_content = markdown.markdown(content)
        return render_template('news.html', content=html_content)

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    # 列出所有新闻文件并按时间倒序排序
    news_files = [f.replace('.md', '') for f in os.listdir('news') if f.endswith('.md')]
    news_files.sort(reverse=True)
    
    # 分页处理
    per_page = 5  # 每页显示5条新闻
    total_pages = (len(news_files) + per_page - 1) // per_page  # 计算总页数
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_files = news_files[start_idx:end_idx]
    
    # 添加调试信息，确认session状态
    print(f"首页访问，当前session状态: {session}")
    print(f"logged_in状态: {session.get('logged_in')}")
    return render_template('index.html', news_files=current_page_files, page=page, total_pages=total_pages)

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
        
    news_path = os.path.join('news', f'{filename}.md')
    content = ''
    if os.path.exists(news_path):
        with open(news_path, 'r', encoding='utf-8') as f:
            content = f.read()
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
    
    if not filename or filename == 'new':
        filename = datetime.now().strftime('%Y%m%d')
    
    news_path = os.path.join('news', f'{filename}.md')

    # 如果目标文件已存在且不是编辑当前文件，则返回错误，避免覆盖已有内容
    if os.path.exists(news_path) and original_filename != filename:
        return jsonify({'success': False, 'message': f'文件 {filename}.md 已存在，请使用其他文件名'}), 400

    # 检查文件名是否有变更，如果有则需要处理文件重命名
    if original_filename and original_filename != filename and original_filename != 'new':
        original_path = os.path.join('news', f'{original_filename}.md')
    with open(news_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 如果是重命名操作，在保存新文件后删除原文件
    if original_filename and original_filename != filename and original_filename != 'new':
        original_path = os.path.join('news', f'{original_filename}.md')
        if os.path.exists(original_path):
            os.remove(original_path)
    
    return jsonify({'success': True, 'filename': filename})

@app.route('/api/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # 检查用户是否已登录
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未授权，请先登录'}), 401
    
    news_path = os.path.join('news', f'{filename}.md')
    if not os.path.exists(news_path):
        return jsonify({'success': False, 'message': f'文件 {filename}.md 不存在'}), 404
    
    try:
        os.remove(news_path)
        return jsonify({'success': True, 'message': f'文件 {filename}.md 已成功删除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除文件时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
