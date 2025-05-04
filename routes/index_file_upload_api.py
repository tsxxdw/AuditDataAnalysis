"""
文件上传API模块

处理文件上传、获取文件列表和删除文件的API接口
"""

import os
import time
import json
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from werkzeug.utils import secure_filename

# 创建蓝图
file_upload_bp = Blueprint('file_upload', __name__)

# 文件上传目录
UPLOAD_FOLDER = 'static/uploads'

# 确保上传目录存在
def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 获取今天的日期目录
def get_date_dir():
    today = datetime.now().strftime('%Y%m%d')
    date_dir = os.path.join(UPLOAD_FOLDER, today)
    ensure_dir_exists(date_dir)
    return date_dir

# 获取文件的网络访问URL
def get_file_url(folder, filename):
    path = os.path.join(folder, filename)
    relative_path = path.replace('\\', '/') # 兼容Windows路径
    return url_for('static', filename=relative_path.replace('static/', ''), _external=True)

@file_upload_bp.route('/api/files/upload', methods=['POST'])
def upload_file():
    """处理文件上传请求"""
    
    # 检查请求是否包含文件
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': '没有文件被上传'}), 400
    
    # 获取文件
    files = request.files.getlist('files')
    
    uploaded_files = []
    
    for file in files:
        # 检查文件是否存在且有文件名
        if file.filename == '':
            continue
        
        # 获取原始文件名和扩展名
        original_filename = file.filename  # 不使用secure_filename先处理
        
        # 分离文件名和扩展名
        name, ext = os.path.splitext(original_filename)
        
        # 安全处理：只替换明确的危险字符，保留中文和其他字符
        # 替换路径分隔符和一些特殊字符
        filtered_name = name
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            filtered_name = filtered_name.replace(char, '_')
        
        # 替换所有空格为下划线
        filtered_name = filtered_name.replace(' ', '_')
        
        # 移除前导和尾部的空格
        filtered_name = filtered_name.strip()
        
        # 如果过滤后文件名为空，使用default作为文件名
        if not filtered_name:
            filtered_name = 'file'
        
        # 获取当前日期目录
        date_dir = get_date_dir()
        
        # 添加时分秒后缀
        time_suffix = datetime.now().strftime('%H%M%S')
        
        # 最终文件名 = 过滤后文件名 + 时分秒 + 扩展名
        final_filename = f"{filtered_name}_{time_suffix}{ext}"
        
        # 最终安全检查
        # 确保文件名不包含绝对路径或尝试跳出目录
        if os.path.isabs(final_filename) or '..' in final_filename:
            final_filename = secure_filename(final_filename)
            if not final_filename:
                final_filename = f"file_{time_suffix}{ext}"
        
        # 构建文件保存路径
        save_path = os.path.join(date_dir, final_filename)
        
        # 如果同名文件已存在，添加一个随机数
        if os.path.exists(save_path):
            random_suffix = str(int(time.time()))[-4:]
            final_filename = f"{filtered_name}_{time_suffix}_{random_suffix}{ext}"
            save_path = os.path.join(date_dir, final_filename)
        
        # 保存文件
        file.save(save_path)
        
        # 获取文件URL
        file_url = get_file_url(os.path.basename(date_dir), final_filename)
        
        # 添加到已上传文件列表
        uploaded_files.append({
            'name': final_filename,
            'path': save_path,
            'url': file_url
        })
    
    return jsonify({
        'success': True,
        'message': f'成功上传{len(uploaded_files)}个文件',
        'files': uploaded_files
    })

@file_upload_bp.route('/api/files/list', methods=['GET'])
def list_files():
    """获取已上传的文件列表"""
    
    ensure_dir_exists(UPLOAD_FOLDER)
    
    # 要返回的文件列表
    files_list = []
    
    # 遍历上传目录下的所有日期目录
    for date_dir in os.listdir(UPLOAD_FOLDER):
        date_path = os.path.join(UPLOAD_FOLDER, date_dir)
        
        # 跳过非目录
        if not os.path.isdir(date_path):
            continue
        
        # 遍历日期目录下的所有文件
        for filename in os.listdir(date_path):
            file_path = os.path.join(date_path, filename)
            
            # 跳过目录
            if not os.path.isfile(file_path):
                continue
            
            # 获取文件信息
            file_stats = os.stat(file_path)
            
            # 构建文件URL
            file_url = get_file_url(date_dir, filename)
            
            # 添加到文件列表
            files_list.append({
                'name': filename,
                'size': file_stats.st_size,
                'date': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'path': file_path,
                'url': file_url
            })
    
    # 按修改时间倒序排序
    files_list.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify(files_list)

@file_upload_bp.route('/api/files/delete', methods=['POST'])
def delete_file():
    """删除文件"""
    
    # 获取要删除的文件路径
    data = request.get_json()
    
    if not data or 'path' not in data:
        return jsonify({'success': False, 'message': '未指定要删除的文件'}), 400
    
    file_path = data['path']
    
    # 安全检查：确保路径在上传目录内
    if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOAD_FOLDER)):
        return jsonify({'success': False, 'message': '无效的文件路径'}), 403
    
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    try:
        # 删除文件
        os.remove(file_path)
        return jsonify({'success': True, 'message': '文件已成功删除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除文件失败: {str(e)}'}), 500

@file_upload_bp.route('/api/files/delete-all', methods=['POST'])
def delete_all_files():
    """删除全部文件"""
    try:
        # 确保上传目录存在
        ensure_dir_exists(UPLOAD_FOLDER)
        
        # 删除计数器
        deleted_count = 0
        
        # 遍历上传目录下的所有日期目录
        for date_dir in os.listdir(UPLOAD_FOLDER):
            date_path = os.path.join(UPLOAD_FOLDER, date_dir)
            
            # 跳过非目录
            if not os.path.isdir(date_path):
                continue
            
            # 遍历日期目录下的所有文件
            for filename in os.listdir(date_path):
                file_path = os.path.join(date_path, filename)
                
                # 跳过目录
                if not os.path.isfile(file_path):
                    continue
                
                # 删除文件
                os.remove(file_path)
                deleted_count += 1
        
        return jsonify({
            'success': True,
            'message': f'已成功删除全部文件，共{deleted_count}个'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除全部文件失败: {str(e)}'
        }), 500 