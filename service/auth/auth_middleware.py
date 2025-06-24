"""
身份验证中间件

用于验证用户登录状态和权限
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from service.log.logger import app_logger

def init_auth_middleware(app):
    """初始化身份验证中间件"""
    @app.before_request
    def check_auth():
        # 需要登录的路径列表
        protected_paths = [
            '/',  # 首页
            '/index_table_structure',
            '/index_import',
            '/index_one_to_one_import',
            '/index_file_upload',
            '/index_repair',
            '/index_validation',
            '/index_excel_validation',
            '/index_analysis',
            '/index_sql',
            '/index_prompt_templates',
            '/excel_repair',
            '/settings',
            '/index_knowledge_base',
            '/user_management'
        ]
        
        # 不需要登录的API路径前缀
        public_api_prefixes = [
            '/api/user/login',
            '/api/user/logout',
            '/static/'
        ]
        
        # 当前请求路径
        path = request.path
        
        # 检查是否是公开API
        for prefix in public_api_prefixes:
            if path.startswith(prefix):
                return  # 允许访问公开API
        
        # 检查是否是受保护的页面
        is_protected_page = path in protected_paths
        is_api = path.startswith('/api/')
        
        # 检查登录状态
        user_info = session.get('user_info')
        
        # 如果是受保护的页面或API，且用户未登录
        if (is_protected_page or is_api) and not user_info:
            if is_api:
                # 对于API请求，返回401错误
                return jsonify({
                    'code': 401,
                    'message': '用户未登录或登录已过期',
                    'data': None
                }), 401
            else:
                # 对于页面请求，重定向到登录页
                return redirect(url_for('pages.login'))
        
        # 对于已登录用户，检查页面访问权限
        if user_info and is_protected_page and path != '/':
            # 管理员可以访问所有页面
            if user_info.get('role') == '管理员':
                return
            
            # 检查普通用户的权限
            permissions = user_info.get('permissions', [])
            
            # 将页面路径转换为权限标识
            # 例如：/user_management -> user_management.html
            page_identifier = path[1:] + '.html' if path != '/' else 'index.html'
            
            # 检查是否有权限访问
            has_permission = False
            for perm in permissions:
                # 权限可能是字符串类型
                if isinstance(perm, str):
                    if perm == page_identifier or perm == page_identifier.replace('index_', ''):
                        has_permission = True
                        break
                # 或者是字典类型
                elif isinstance(perm, dict) and 'path' in perm:
                    if perm['path'] == page_identifier or perm['path'] == page_identifier.replace('index_', ''):
                        has_permission = True
                        break
            
            if not has_permission:
                app_logger.warning(f"用户 {user_info.get('username')} 尝试访问无权限页面: {path}")
                return redirect(url_for('pages.index'))  # 无权限则重定向到首页

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_info' not in session:
            if request.path.startswith('/api/'):
                return jsonify({
                    'code': 401,
                    'message': '用户未登录或登录已过期',
                    'data': None
                }), 401
            else:
                return redirect(url_for('pages.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_info = session.get('user_info')
        if not user_info or user_info.get('role') != '管理员':
            if request.path.startswith('/api/'):
                return jsonify({
                    'code': 403,
                    'message': '需要管理员权限',
                    'data': None
                }), 403
            else:
                return redirect(url_for('pages.index'))
        return f(*args, **kwargs)
    return decorated_function

def has_permission(permission_path):
    """检查是否有特定页面的访问权限"""
    user_info = session.get('user_info')
    
    # 未登录
    if not user_info:
        return False
    
    # 管理员有所有权限
    if user_info.get('role') == '管理员':
        return True
    
    # 检查普通用户权限
    permissions = user_info.get('permissions', [])
    for perm in permissions:
        # 权限可能是字符串类型
        if isinstance(perm, str):
            if perm == permission_path:
                return True
        # 或者是字典类型
        elif isinstance(perm, dict) and 'path' in perm:
            if perm['path'] == permission_path:
                return True
    
    return False 