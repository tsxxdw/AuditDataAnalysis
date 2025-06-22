#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
import logging
from typing import Dict, List
from service.log.logger import app_logger  # 导入app_logger

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelLogService:
    """大模型日志服务类，负责记录大模型调用日志"""
    
    def __init__(self):
        """初始化日志服务"""
        pass
    
    def log_model_call(self, provider_id: str, model_id: str, messages: List[Dict]) -> None:
        """记录大模型调用信息到文件
        
        Args:
            provider_id: 服务提供商ID
            model_id: 模型ID
            messages: 提示词消息列表
        """
        try:
            # 创建时间戳作为文件名 (保持原格式以便于文件排序)
            timestamp_for_filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            
            # 创建格式化的时间戳用于日志内容显示
            formatted_timestamp = datetime.datetime.now().strftime('%Y:%m:%d %H时%M分%S秒')
            
            # 获取当前日期作为目录名
            current_date = datetime.datetime.now().strftime('%Y%m%d')
            
            # 确保日志目录存在
            # 创建根目录的file文件夹
            root_file_dir = os.path.join('file')
            os.makedirs(root_file_dir, exist_ok=True)
            
            # 创建大模型调用记录文件夹
            big_model_dir = os.path.join(root_file_dir, 'big_model_call_record')
            os.makedirs(big_model_dir, exist_ok=True)
            
            # 创建当前日期的文件夹 (格式: YYYYMMDD)
            log_dir = os.path.join(big_model_dir, current_date)
            os.makedirs(log_dir, exist_ok=True)
            
            # 构建日志文件路径
            log_file = os.path.join(log_dir, f"{timestamp_for_filename}.txt")
            
            # 提取系统提示词和用户提示词
            system_prompt = "无系统提示词"
            user_prompt = "无用户提示词"
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    user_prompt = msg['content']
            
            # 组装日志内容 (使用格式化的时间戳)
            log_content = f"调用时间: {formatted_timestamp}\n"
            log_content += f"服务提供商: {provider_id}\n"
            log_content += f"模型: {model_id}\n"
            log_content += f"\n系统提示词:\n{system_prompt}\n"
            log_content += f"\n用户提示词:\n{user_prompt}\n"
            
            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            app_logger.info(f"已记录大模型调用日志到文件: {log_file}")
        except Exception as e:
            app_logger.error(f"记录大模型调用日志失败: {str(e)}")

# 创建全局单例实例
model_log_service = ModelLogService()
