"""
Flask 应用主文件 - news.docms.nz
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, make_response
from flask_cors import CORS
import os
import markdown
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# 启用 CORS
CORS(app, supports_credentials=True, origins='*')

# 导入模型（使用 models.py 中的 db 实例）
from models import db, User, Article, Category, Setting
db.init_app(app)

# 初始化 JWT 认证
from auth import init_app as init_jwt, generate_tokens, jwt_required, admin_required, get_token_from_request
init_jwt(app)

# 导入模型
from models import User, Article, Category, Setting


# ==================== 模板路由（向后兼容） ====================

@app.route('/')
def index():
    """新闻列表首页"""
    # 检查用户是否已登录（通过 JWT）
    token = get_token_from_request()
    user = None
    if token:
        from auth import decode_token
        result = decode_token(token)
        if result['success']:
            user = User.query.get(result['payload']['user_id'])

    # 获取数据库中的已发布文章
    articles = Article.query.filter_by(status='published')\
        .order_by(Article.published_at.desc()).limit(10).all()

    # 兼容旧版：也读取 news/ 目录的文件
    news_dir = os.getenv('NEWS_DIR', 'news')
    legacy_articles = []
    if os.path.exists(news_dir):
        for f in os.listdir(news_dir):
            if f.endswith(('.md', '.html')):
                filepath = os.path.join(news_dir, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if f.endswith('.md'):
                        title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
                        title = title_match.group(1) if title_match else f
                    else:
                        title_match = re.search(r'<title>(.*?)</title>', content)
                        title = title_match.group(1) if title_match else f
                legacy_articles.append({
                    'filename': f.replace('.md', '').replace('.html', ''),
                    'title': title
                })

    return render_template('index.html',
                           articles=[a.to_dict() for a in articles],
                           legacy_articles=legacy_articles,
                           user=user.to_dict() if user else None,
                           page=1)


@app.route('/article/<slug>')
def show_article(slug):
    """查看数据库文章"""
    article = Article.query.filter_by(slug=slug).first()
    if article:
        # 增加阅读量
        article.view_count += 1
        db.session.commit()
        # 返回 Vue SPA，由前端渲染
        return render_template('index.html')

    return '404 - 文章未找到', 404


@app.route('/<filename>')
def show_news(filename):
    """查看新闻文章（兼容文件版本和直接访问）"""
    # 尝试从数据库获取
    article = Article.query.filter_by(slug=filename).first()
    if article:
        # 增加阅读量
        article.view_count += 1
        db.session.commit()
        return render_template('news.html', article=article.to_detail_dict())

    # 兼容旧版：从文件读取
    news_dir = os.getenv('NEWS_DIR', 'news')
    md_path = os.path.join(news_dir, f'{filename}.md')
    html_path = os.path.join(news_dir, f'{filename}.html')

    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            html_content = markdown.markdown(content)
            title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else filename
            return render_template('news.html', article={
                'title': title,
                'content': content,
                'html_content': html_content,
                'filename': filename
            })

    elif os.path.exists(html_path):
        return send_from_directory(news_dir, f'{filename}.html')

    return '404 - 文章未找到', 404


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """登录页面 - 返回 Vue SPA"""
    return render_template('index.html')


@app.route('/logout')
def logout_page():
    """登出页面"""
    response = make_response(redirect('/'))
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    return response


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """注册页面 - 返回 Vue SPA"""
    return render_template('index.html')


@app.route('/profile')
def profile_page():
    """个人中心 - 返回 Vue SPA"""
    return render_template('index.html')


@app.route('/admin')
def admin_page():
    """管理后台 - 返回 Vue SPA"""
    return render_template('index.html')


@app.route('/editor/<path:filename>')
def editor_page(filename):
    """编辑器页面"""
    return render_template('index.html')


# ==================== API 路由 ====================

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


# ==================== 认证 API ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # 验证必填字段
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码都是必填项'}), 400

    # 检查用户名是否存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400

    # 检查邮箱是否存在
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400

    # 创建用户
    user = User(username=username, email=email)
    user.set_password(password)

    # 如果是第一个用户，设为管理员
    if User.query.count() == 0:
        user.role = 'admin'

    db.session.add(user)
    db.session.commit()

    # 生成 token
    access_token, refresh_token = generate_tokens(user.id)

    response = make_response(jsonify({
        'message': '注册成功',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }))

    # 设置 cookie（HttpOnly）
    response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax')

    return response, 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')

    # 查找用户
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(email=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401

    if not user.is_active:
        return jsonify({'error': '账户已被禁用'}), 403

    # 生成 token
    access_token, refresh_token = generate_tokens(user.id)

    response = make_response(jsonify({
        'message': '登录成功',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }))

    # 设置 cookie
    if data.get('remember', False):
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', max_age=7200)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', max_age=604800)
    else:
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax')

    return response


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """登出"""
    response = make_response(jsonify({'message': '登出成功'}))
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    return response


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """刷新 token"""
    refresh_token_val = request.cookies.get('refresh_token')
    if not refresh_token_val:
        return jsonify({'error': '缺少 refresh token'}), 401

    from auth import decode_token
    result = decode_token(refresh_token_val)
    if not result['success']:
        return jsonify({'error': result['error']}), 401

    payload = result['payload']
    if payload.get('type') != 'refresh':
        return jsonify({'error': '无效的 token 类型'}), 401

    user = User.query.get(payload['user_id'])
    if not user or not user.is_active:
        return jsonify({'error': '用户不存在或已被禁用'}), 401

    # 生成新 token
    access_token, new_refresh_token = generate_tokens(user.id)

    response = make_response(jsonify({
        'access_token': access_token,
        'refresh_token': new_refresh_token
    }))

    response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', new_refresh_token, httponly=True, samesite='Lax')

    return response


@app.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    """获取当前用户信息"""
    return jsonify({'user': request.current_user.to_dict()})


@app.route('/api/auth/password', methods=['PUT'])
@jwt_required
def change_password():
    """修改密码"""
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not request.current_user.check_password(old_password):
        return jsonify({'error': '原密码错误'}), 400

    request.current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': '密码修改成功'})


# ==================== 文章 API ====================

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """获取文章列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')

    query = Article.query

    # 筛选已发布或需要认证
    # status='null' 字符串表示获取所有文章（管理后台使用）
    if status and status != 'null':
        query = query.filter_by(status=status)
    elif not status:
        # 默认只返回已发布的
        query = query.filter_by(status='published')
    # status='null' 时不筛选，返回所有文章

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search:
        query = query.filter(
            (Article.title.contains(search)) |
            (Article.content.contains(search))
        )

    # 排序
    query = query.order_by(Article.published_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    articles = [a.to_dict() for a in pagination.items]

    return jsonify({
        'articles': articles,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    })


@app.route('/api/articles/<slug>', methods=['GET'])
def get_article(slug):
    """获取文章详情"""
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    # 未发布文章需要登录
    if article.status != 'published':
        token = get_token_from_request()
        if not token:
            return jsonify({'error': '需要登录才能查看此文章'}), 401

        from auth import decode_token
        result = decode_token(token)
        if not result['success']:
            return jsonify({'error': '无效的 token'}), 401

        user_id = result['payload']['user_id']
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': '无权查看此文章'}), 403

    # 增加阅读量
    article.view_count += 1
    db.session.commit()

    return jsonify({'article': article.to_detail_dict()})


@app.route('/api/articles', methods=['POST'])
@jwt_required
def create_article():
    """创建文章"""
    data = request.get_json()

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    slug = data.get('slug', '').strip()
    excerpt = data.get('excerpt', '').strip()
    category_id = data.get('category_id', type=int)
    status = data.get('status', 'draft')

    if not title or not content:
        return jsonify({'error': '标题和内容都是必填项'}), 400

    # 生成 slug
    if not slug:
        slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '-', title.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')

    # 检查 slug 是否存在
    if Article.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Slug 已存在，请使用其他标题'}), 400

    # 生成 HTML 内容
    html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])

    # 创建文章
    article = Article(
        title=title,
        slug=slug,
        content=content,
        html_content=html_content,
        excerpt=excerpt or content[:200],
        user_id=request.current_user.id,
        category_id=category_id,
        status=status
    )

    if status == 'published':
        article.published_at = datetime.now(timezone.utc)

    db.session.add(article)
    db.session.commit()

    return jsonify({
        'message': '创建成功',
        'article': article.to_dict()
    }), 201


@app.route('/api/articles/<slug>', methods=['PUT'])
@jwt_required
def update_article(slug):
    """更新文章"""
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    # 检查权限
    if request.current_user.role != 'admin' and article.user_id != request.current_user.id:
        return jsonify({'error': '无权修改此文章'}), 403

    data = request.get_json()

    if 'title' in data:
        article.title = data['title'].strip()

    if 'content' in data:
        article.content = data['content'].strip()
        article.html_content = markdown.markdown(article.content, extensions=['fenced_code', 'tables'])

    if 'excerpt' in data:
        article.excerpt = data['excerpt'].strip()

    if 'category_id' in data:
        article.category_id = data['category_id']

    if 'status' in data:
        old_status = article.status
        article.status = data['status']
        if data['status'] == 'published' and old_status != 'published':
            article.published_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        'message': '更新成功',
        'article': article.to_dict()
    })


@app.route('/api/articles/<slug>', methods=['DELETE'])
@jwt_required
def delete_article(slug):
    """删除文章"""
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    # 检查权限
    if request.current_user.role != 'admin' and article.user_id != request.current_user.id:
        return jsonify({'error': '无权删除此文章'}), 403

    db.session.delete(article)
    db.session.commit()

    return jsonify({'message': '删除成功'})


@app.route('/api/articles/<slug>/publish', methods=['POST'])
@jwt_required
def publish_article(slug):
    """发布文章"""
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    if request.current_user.role != 'admin' and article.user_id != request.current_user.id:
        return jsonify({'error': '无权操作此文章'}), 403

    article.status = 'published'
    article.published_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({'message': '发布成功', 'article': article.to_dict()})


@app.route('/api/articles/<slug>/unpublish', methods=['POST'])
@jwt_required
def unpublish_article(slug):
    """下架文章"""
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': '文章不存在'}), 404

    if request.current_user.role != 'admin' and article.user_id != request.current_user.id:
        return jsonify({'error': '无权操作此文章'}), 403

    article.status = 'draft'
    db.session.commit()

    return jsonify({'message': '下架成功', 'article': article.to_dict()})


# ==================== 分类 API ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    categories = Category.query.order_by(Category.sort_order.asc()).all()
    return jsonify({'categories': [c.to_dict() for c in categories]})


@app.route('/api/categories', methods=['POST'])
@admin_required
def create_category():
    """创建分类"""
    data = request.get_json()

    name = data.get('name', '').strip()
    slug = data.get('slug', '').strip() or re.sub(r'[^a-zA-Z0-9]', '-', name.lower())
    description = data.get('description', '').strip()
    sort_order = data.get('sort_order', 0, type=int)

    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'error': '分类名称已存在'}), 400

    if Category.query.filter_by(slug=slug).first():
        return jsonify({'error': '分类 Slug 已存在'}), 400

    category = Category(name=name, slug=slug, description=description, sort_order=sort_order)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'message': '创建成功',
        'category': category.to_dict()
    }), 201


@app.route('/api/categories/<int:id>', methods=['PUT'])
@admin_required
def update_category(id):
    """更新分类"""
    category = Category.query.get(id)
    if not category:
        return jsonify({'error': '分类不存在'}), 404

    data = request.get_json()

    if 'name' in data:
        category.name = data['name'].strip()

    if 'slug' in data:
        category.slug = data['slug'].strip()

    if 'description' in data:
        category.description = data['description'].strip()

    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    db.session.commit()

    return jsonify({
        'message': '更新成功',
        'category': category.to_dict()
    })


@app.route('/api/categories/<int:id>', methods=['DELETE'])
@admin_required
def delete_category(id):
    """删除分类"""
    category = Category.query.get(id)
    if not category:
        return jsonify({'error': '分类不存在'}), 404

    # 检查是否有文章使用此分类
    if category.articles.count() > 0:
        return jsonify({'error': '该分类下有文章，无法删除'}), 400

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': '删除成功'})


# ==================== 用户管理 API ====================

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """获取用户列表"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]})


@app.route('/api/admin/users/<int:id>', methods=['GET'])
@admin_required
def get_user(id):
    """获取用户详情"""
    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'user': user.to_dict()})


@app.route('/api/admin/users/<int:id>', methods=['PUT'])
@admin_required
def update_user(id):
    """更新用户"""
    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()

    if 'role' in data:
        user.role = data['role']

    if 'is_active' in data:
        user.is_active = data['is_active']

    db.session.commit()

    return jsonify({
        'message': '更新成功',
        'user': user.to_dict()
    })


@app.route('/api/admin/users/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    """删除用户"""
    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    if user.id == request.current_user.id:
        return jsonify({'error': '不能删除自己'}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': '删除成功'})


@app.route('/api/admin/users/<int:id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(id):
    """切换用户激活状态"""
    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    if user.id == request.current_user.id:
        return jsonify({'error': '不能禁用自己'}), 400

    user.is_active = not user.is_active
    db.session.commit()

    status = '已启用' if user.is_active else '已禁用'
    return jsonify({'message': status, 'user': user.to_dict()})


# ==================== 统计 API ====================

@app.route('/api/admin/dashboard')
@admin_required
def dashboard_stats():
    """仪表盘统计"""
    total_users = User.query.count()
    total_articles = Article.query.count()
    published_articles = Article.query.filter_by(status='published').count()
    draft_articles = Article.query.filter_by(status='draft').count()

    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()

    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_articles': total_articles,
            'published_articles': published_articles,
            'draft_articles': draft_articles,
        },
        'recent_articles': [a.to_dict() for a in recent_articles]
    })


# ==================== 静态文件 ====================

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


# ==================== 数据库初始化 ====================

def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()

        # 创建默认分类
        if Category.query.count() == 0:
            default_categories = [
                {'name': '技术资讯', 'slug': 'tech', 'description': '技术新闻和动态'},
                {'name': '产品分析', 'slug': 'product', 'description': '产品评测和分析'},
                {'name': '行业报告', 'slug': 'industry', 'description': '行业研究报告'},
            ]
            for cat in default_categories:
                category = Category(**cat)
                db.session.add(category)
            db.session.commit()

        # 创建默认管理员（如果不存在）
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@news.docms.nz')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

        if not User.query.filter_by(username=admin_username).first():
            admin = User(
                username=admin_username,
                email=admin_email,
                role='admin'
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f'默认管理员创建成功: {admin_username}')


# ==================== 启动入口 ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)
