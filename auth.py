"""
JWT 认证模块
"""
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from models import User


# JWT 配置
JWT_SECRET_KEY = None  # 将在 app.py 中初始化
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRY = timedelta(hours=2)
REFRESH_TOKEN_EXPIRY = timedelta(days=7)


def init_app(app):
    """初始化 JWT 配置"""
    global JWT_SECRET_KEY
    JWT_SECRET_KEY = app.config.get('SECRET_KEY') or secrets.token_hex(32)


def generate_tokens(user_id):
    """生成 access token 和 refresh token"""
    now = datetime.now(timezone.utc)

    # Access Token
    access_payload = {
        'user_id': user_id,
        'type': 'access',
        'iat': now,
        'exp': now + ACCESS_TOKEN_EXPIRY
    }
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Refresh Token
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'iat': now,
        'exp': now + REFRESH_TOKEN_EXPIRY
    }
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return access_token, refresh_token


def decode_token(token):
    """解码 token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {'success': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'success': False, 'error': 'Token 已过期'}
    except jwt.InvalidTokenError as e:
        return {'success': False, 'error': f'无效的 Token: {str(e)}'}


def get_token_from_request():
    """从请求中获取 token"""
    # 优先从 Authorization header 获取
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]

    # 其次从 cookie 获取
    return request.cookies.get('access_token')


def get_refresh_token_from_request():
    """从请求中获取 refresh token"""
    return request.cookies.get('refresh_token')


def jwt_required(f):
    """JWT 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({'error': '缺少认证 token', 'code': 'MISSING_TOKEN'}), 401

        result = decode_token(token)
        if not result['success']:
            return jsonify({'error': result['error'], 'code': 'INVALID_TOKEN'}), 401

        payload = result['payload']
        if payload.get('type') != 'access':
            return jsonify({'error': '无效的 token 类型', 'code': 'INVALID_TOKEN_TYPE'}), 401

        # 获取用户
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': '用户不存在', 'code': 'USER_NOT_FOUND'}), 401

        if not user.is_active:
            return jsonify({'error': '用户已被禁用', 'code': 'USER_DISABLED'}), 401

        # 将用户信息注入请求上下文
        request.current_user = user
        request.user_id = user.id

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        if request.current_user.role != 'admin':
            return jsonify({'error': '需要管理员权限', 'code': 'ADMIN_REQUIRED'}), 403
        return f(*args, **kwargs)
    return decorated


def generate_password(length=12):
    """生成随机密码"""
    return secrets.token_urlsafe(length)


def validate_password_strength(password):
    """验证密码强度"""
    errors = []

    if len(password) < 8:
        errors.append('密码长度至少 8 个字符')

    if not any(c.isupper() for c in password):
        errors.append('密码至少包含一个大写字母')

    if not any(c.islower() for c in password):
        errors.append('密码至少包含一个小写字母')

    if not any(c.isdigit() for c in password):
        errors.append('密码至少包含一个数字')

    if not any(c in '!@#$%^&*()_+-=' for c in password):
        errors.append('密码至少包含一个特殊字符 (!@#$%^&*()_+-=)')

    return errors if errors else None
