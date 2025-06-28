"""
身份验证中间件

用于验证用户登录状态和权限
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from service.log.logger import app_logger
from service.session_service import session_service

def init_auth_middleware(app):
    """
    注册全局权限验证中间件
    """
    @app.before_request
    def check_auth():
        """
        请求拦截器：在每次请求前执行，判断用户是否有权限访问
        
        判断逻辑：
        1. 公开路径（登录页、静态资源等）无需验证直接放行
        2. 用户未登录时，API请求返回401错误，页面请求重定向到登录页
        3. 已登录用户访问页面时，检查是否有该页面的权限
        4. 管理员拥有所有页面权限，普通用户只能访问其权限列表中的页面
        """
        # 不需要登录的API路径前缀
        public_api_prefixes = [
            '/api/login',  # 新的登录API路径
            '/api/login/logout',  # 新的退出登录API路径
            '/api/user/login',  # 旧的登录API路径（保留兼容性）
            '/api/user/logout',  # 旧的退出登录API路径（保留兼容性）
            '/static/',
            '/login'  # 登录页面
        ]
        
        # 当前请求路径
        path = request.path
        
        # 检查是否是公开API
        for prefix in public_api_prefixes:
            if path.startswith(prefix):
                return  # 允许访问公开API
        
        # 检查登录状态
        # 使用 SessionService 实例方法
        user_info = session_service.get_user_info()
        
        # 用户未登录时的处理
        if not user_info:
            if path.startswith('/api/'):
                # 对于API请求，返回401错误
                return jsonify({
                    'code': 401,
                    'message': '用户未登录或登录已过期',
                    'data': None
                }), 401
            else:
                # 对于页面请求，重定向到登录页
                return redirect(url_for('pages.login'))
        
        # 对于已登录用户，检查页面访问权限（除了首页外）
        if path != '/' and not path.startswith('/api/'):
            # 管理员可以访问所有页面
            if user_info.get('role') == '管理员':
                return
            
            # 检查普通用户的权限
            permissions = user_info.get('permissions', [])
            
            # 将页面路径转换为权限标识
            # 例如：/user_management -> user_management
            page_identifier = path[1:] if path != '/' else 'index'
            
            # 检查是否有权限访问
            has_permission = False
            for perm in permissions:
                # 权限可能是字符串类型
                if isinstance(perm, str):
                    # 移除可能的.html后缀进行比较
                    perm_clean = perm.replace('.html', '')
                    if perm_clean == page_identifier or perm_clean == page_identifier.replace('index_', ''):
                        has_permission = True
                        break
                # 或者是字典类型
                elif isinstance(perm, dict) and 'path' in perm:
                    # 移除可能的.html后缀进行比较
                    perm_path_clean = perm['path'].replace('.html', '')
                    if perm_path_clean == page_identifier or perm_path_clean == page_identifier.replace('index_', ''):
                        has_permission = True
                        break
            
            if not has_permission:
                app_logger.warning(f"用户 {user_info.get('username')} 尝试访问无权限页面: {path}")
                return redirect(url_for('pages.index'))  # 无权限则重定向到首页

def login_required(f):
    """
    登录验证装饰器：确保用户必须登录才能访问某个路由
    
    验证逻辑：检查session中是否存在user_info，不存在则拒绝访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 使用 SessionService 实例方法
        if not session_service.is_logged_in():
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
    """
    管理员验证装饰器：确保只有管理员角色才能访问某个路由
    
    验证逻辑：检查用户是否登录且角色为"管理员"，不符合则拒绝访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 使用 SessionService 实例方法
        user_info = session_service.get_user_info()
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
    """
    权限检查函数：判断当前用户是否有访问指定功能的权限
    
    判断逻辑：
    1. 未登录用户没有任何权限
    2. 管理员拥有所有权限
    3. 普通用户检查权限列表中是否包含指定的路径标识符
    """
    # 使用 SessionService 实例方法
    user_info = session_service.get_user_info()
    
    # 未登录
    if not user_info:
        return False
    
    # 管理员有所有权限
    if user_info.get('role') == '管理员':
        return True
    
    # 移除可能的.html后缀
    permission_path_clean = permission_path.replace('.html', '')
    
    # 检查普通用户权限
    permissions = user_info.get('permissions', [])
    for perm in permissions:
        # 权限可能是字符串类型
        if isinstance(perm, str):
            # 移除可能的.html后缀进行比较
            perm_clean = perm.replace('.html', '')
            if perm_clean == permission_path_clean:
                return True
        # 或者是字典类型
        elif isinstance(perm, dict) and 'path' in perm:
            # 移除可能的.html后缀进行比较
            perm_path_clean = perm['path'].replace('.html', '')
            if perm_path_clean == permission_path_clean:
                return True
    
    return False 