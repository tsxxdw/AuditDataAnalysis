#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import logging
import datetime
from typing import Dict
from service.log.logger import app_logger
from service.session_service import session_service

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DifyService:
    """DIFY服务类，负责与Dify API交互"""
    
    # 基础API地址
    BASE_URL = 'http://127.0.0.1/v1/workflows/run'
    
    # 操作类型到对应API密钥的映射
    OPERATION_KEYS = {
        'repair_date':   'app-lAMRAZF7U5J8O2E6NOMYWG9m',  # 日期修复密钥
        'repair_idcard': 'app-lAMRAZF7U5J8O2E6NOMYWG9m',  # 身份证修复密钥
        # 可以根据需要添加更多操作类型及对应的密钥
    }
    
    def __init__(self):
        """初始化Dify服务"""
        # 不在初始化时调用_ensure_log_directories，避免在没有请求上下文时访问session
        pass
    
    def _ensure_log_directories(self):
        """确保日志目录存在"""
        try:
            # 从session获取用户信息
            user_info = session_service.get_user_info()
            # 获取用户名，如果没有则使用'anonymous'作为默认值
            username = user_info.get('username', 'anonymous')
            
            # 创建根目录的file文件夹
            root_file_dir = os.path.join('file')
            os.makedirs(root_file_dir, exist_ok=True)
            
            # 创建用户目录
            user_dir = os.path.join(root_file_dir, username)
            os.makedirs(user_dir, exist_ok=True)
            
            # 创建logfile目录
            logfile_dir = os.path.join(user_dir, 'logfile')
            os.makedirs(logfile_dir, exist_ok=True)
            
            # 创建Dify调用记录文件夹
            dify_dir = os.path.join(logfile_dir, 'dify_call_record')
            os.makedirs(dify_dir, exist_ok=True)
            app_logger.info(f"确保Dify调用记录目录存在: {dify_dir}")
            
            # 创建当前日期的文件夹 (格式: YYYYMMDD)
            current_date = datetime.datetime.now().strftime('%Y%m%d')
            date_dir = os.path.join(dify_dir, current_date)
            os.makedirs(date_dir, exist_ok=True)
            app_logger.info(f"确保日期目录存在: {date_dir}")
            
            return username, current_date
        except Exception as e:
            app_logger.error(f"创建日志目录时出错: {str(e)}")
            return 'anonymous', datetime.datetime.now().strftime('%Y%m%d')
    
    def _log_dify_call(self, operation_type: str, params: Dict) -> None:
        """记录Dify调用信息到文件
        
        Args:
            operation_type: 操作类型
            params: 调用参数
        """
        try:
            # 创建时间戳作为文件名
            timestamp_for_filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            
            # 创建格式化的时间戳用于日志内容显示
            formatted_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 确保日志目录存在并获取用户名和当前日期
            username, current_date = self._ensure_log_directories()
            
            # 构建日志文件路径
            log_dir = os.path.join('file', username, 'logfile', 'dify_call_record', current_date)
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{timestamp_for_filename}.txt")
            
            # 组装日志内容
            log_content = f"调用时间: {formatted_timestamp}\n"
            log_content += f"操作类型: {operation_type}\n"
            log_content += f"调用参数:\n{json.dumps(params, indent=2, ensure_ascii=False)}\n"
            
            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            app_logger.info(f"已记录Dify调用日志到文件: {log_file}")
        except Exception as e:
            app_logger.error(f"记录Dify调用日志失败: {str(e)}")
    
    def call_dify_api(self, operation_type: str, inputs: Dict) -> Dict:
        """
        调用Dify API
        
        Args:
            operation_type: 操作类型(repair_date/repair_idcard)
            inputs: API输入参数
            
        Returns:
            Dict: API响应结果
        """
        try:
            # 获取API密钥
            api_key = self.OPERATION_KEYS.get(operation_type)
            if not api_key:
                app_logger.error(f"未找到操作类型 {operation_type} 对应的API密钥")
                return {
                    "success": False,
                    "message": f"未找到操作类型 {operation_type} 对应的API密钥"
                }
            
            # 准备请求头
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 准备请求体
            payload = {
                'inputs': inputs,
                'response_mode': 'blocking',
                'user': 'audit-data-analysis'
            }
            
            # 记录API调用日志
            self._log_dify_call(operation_type, {
                'url': self.BASE_URL,
                'headers': {
                    'Authorization': f'Bearer {api_key.replace(api_key[4:-4], "****")}',  # 隐藏部分API Key
                    'Content-Type': 'application/json'
                },
                'payload': payload
            })
            
            # 调用API
            app_logger.info(f"正在调用Dify API: {operation_type}")
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=180  # 120秒超时
            )
            
            # 解析响应
            if response.status_code == 200:
                # 尝试解析响应内容
                try:
                    # 解析响应内容
                    content = response.text
                    app_logger.info(f"Dify API原始响应: {content[:200]}...")
                    
                    # 解析JSON响应
                    result = json.loads(content)
                    app_logger.info(f"Dify API调用成功: {operation_type}")
                    return {
                        "success": True,
                        "data": result,
                        "message": "API调用成功"
                    }
                except Exception as e:
                    app_logger.error(f"解析Dify API响应失败: {str(e)}")
                    return {
                        "success": False,
                        "message": f"解析API响应失败: {str(e)}",
                        "error": response.text
                    }
            else:
                error_detail = response.text
                app_logger.error(f"Dify API调用失败: 状态码 {response.status_code}, 错误: {error_detail}")
                return {
                    "success": False,
                    "message": f"API调用失败，状态码: {response.status_code}",
                    "error": error_detail
                }
                
        except requests.exceptions.Timeout:
            app_logger.error(f"Dify API调用超时: {operation_type}")
            return {
                "success": False,
                "message": "API调用超时"
            }
        except requests.exceptions.ConnectionError:
            app_logger.error(f"Dify API连接错误: {operation_type}")
            return {
                "success": False,
                "message": "API连接错误，请检查网络或API服务是否可用"
            }
        except Exception as e:
            app_logger.error(f"调用Dify API时发生错误: {str(e)}")
            return {
                "success": False,
                "message": f"调用API时发生错误: {str(e)}"
            }
    
    def generate_repair_sql(self, params: Dict) -> Dict:
        """
        生成修复SQL语句
        
        Args:
            params: 包含以下字段的字典
                operation_type: 操作类型(repair_date/repair_idcard)
                table_name: 表名
                reference_field: 参考字段
                target_field: 目标字段
                database_type: 数据库类型
                target_field_remark: 目标字段备注信息
                
        Returns:
            Dict: 包含生成的SQL语句和状态信息
        """
        try:
            # 获取操作类型
            operation_type = params.get('operation_type', '')
            
            # 验证必填参数
            if not operation_type:
                app_logger.error("操作类型不能为空")
                return {
                    "success": False,
                    "message": "操作类型不能为空",
                    "sql": ""
                }
            
            if not params.get('table_name'):
                app_logger.error("表名不能为空")
                return {
                    "success": False,
                    "message": "表名不能为空",
                    "sql": ""
                }
            
            if not params.get('reference_field'):
                app_logger.error("参考字段不能为空")
                return {
                    "success": False,
                    "message": "参考字段不能为空",
                    "sql": ""
                }
            
            # 获取对应的API密钥
            api_key = self.OPERATION_KEYS.get(operation_type)
            if not api_key:
                app_logger.error(f"未找到操作类型 {operation_type} 对应的API密钥")
                return {
                    "success": False,
                    "message": f"未找到操作类型 {operation_type} 对应的API密钥",
                    "sql": ""
                }
            
            # 记录调用日志
            self._log_dify_call(operation_type, params)
            
            # 直接生成SQL语句，不调用Dify API
            sql = self._generate_sql_directly(params)
            
            return {
                "success": True,
                "message": "SQL生成成功",
                "sql": sql
            }
            
        except Exception as e:
            app_logger.error(f"生成修复SQL失败: {str(e)}")
            return {
                "success": False,
                "message": f"生成修复SQL失败: {str(e)}",
                "sql": ""
            }
    
    def generate_repair_sql_via_api(self, params: Dict) -> Dict:
        """
        通过调用Dify API生成修复SQL语句
        
        Args:
            params: 包含以下字段的字典
                operation_type: 操作类型(repair_date/repair_idcard)
                table_name: 表名
                reference_field: 参考字段
                target_field: 目标字段
                database_type: 数据库类型
                target_field_remark: 目标字段备注信息
                
        Returns:
            Dict: 包含生成的SQL语句和状态信息
        """
        try:
            # 获取操作类型
            operation_type = params.get('operation_type', '')
            
            # 验证必填参数
            if not operation_type:
                app_logger.error("操作类型不能为空")
                return {
                    "success": False,
                    "message": "操作类型不能为空",
                    "sql": ""
                }
            
            if not params.get('table_name'):
                app_logger.error("表名不能为空")
                return {
                    "success": False,
                    "message": "表名不能为空",
                    "sql": ""
                }
            
            if not params.get('reference_field'):
                app_logger.error("参考字段不能为空")
                return {
                    "success": False,
                    "message": "参考字段不能为空",
                    "sql": ""
                }
            
            # 准备API输入参数
            api_inputs = {
                'operation_type': operation_type,
                'table_name': params.get('table_name', ''),
                'reference_field': params.get('reference_field', ''),
                'target_field': params.get('target_field', ''),
                'database_type': params.get('database_type', 'mysql'),
                'target_field_remark': params.get('target_field_remark', '')
            }
            
            # 调用Dify API
            api_result = self.call_dify_api(operation_type, api_inputs)
            
            # 处理API响应
            if api_result.get('success'):
                # 从API响应中提取SQL
                api_data = api_result.get('data', {})
                
                # 根据实际的Dify API响应格式提取SQL
                if 'data' in api_data and 'outputs' in api_data['data'] and 'output' in api_data['data']['outputs']:
                    raw_output = api_data['data']['outputs']['output']
                    app_logger.info(f"从Dify API获取到原始输出: {raw_output[:200]}...")
                    
                    # 从输出中提取SQL语句，去除<think>标签及其内容
                    sql = self._extract_sql_from_output(raw_output)
                    
                    if not sql:
                        app_logger.error("无法从Dify API输出中提取有效的SQL语句")
                        return {
                            "success": False,
                            "message": "无法从Dify API输出中提取有效的SQL语句",
                            "sql": ""
                        }
                    
                    app_logger.info(f"提取到的SQL语句: {sql}")
                    return {
                        "success": True,
                        "message": "通过API生成SQL成功",
                        "sql": sql
                    }
                else:
                    app_logger.error(f"Dify API响应格式不正确，找不到outputs.output字段: {api_data}")
                    return {
                        "success": False,
                        "message": "Dify API响应格式不正确，找不到outputs.output字段",
                        "sql": ""
                    }
            else:
                # API调用失败，直接返回错误
                error_msg = api_result.get('message', 'API调用失败')
                app_logger.error(f"Dify API调用失败: {error_msg}")
                return {
                    "success": False,
                    "message": f"Dify API调用失败: {error_msg}",
                    "sql": ""
                }
            
        except Exception as e:
            app_logger.error(f"通过API生成修复SQL失败: {str(e)}")
            return {
                "success": False,
                "message": f"通过API生成修复SQL失败: {str(e)}",
                "sql": ""
            }
    
    def _generate_sql_directly(self, params: Dict) -> str:
        """
        直接生成SQL语句而不调用Dify API
        
        Args:
            params: 包含SQL生成所需参数的字典
            
        Returns:
            str: 生成的SQL语句
        """
        operation_type = params.get('operation_type', '')
        table_name = params.get('table_name', '')
        reference_field = params.get('reference_field', '')
        target_field = params.get('target_field', '')
        database_type = params.get('database_type', 'mysql')  # 默认为mysql
        
        # 如果未提供目标字段，则使用参考字段
        if not target_field:
            target_field = reference_field
        
        # 根据操作类型生成不同的SQL
        if operation_type == 'repair_date':
            sql = f"""-- 日期类型修复SQL
UPDATE {table_name} SET {target_field} = 
  CASE 
    WHEN LENGTH({reference_field}) = 8 AND {reference_field} REGEXP '^[0-9]+$' THEN
      -- 处理格式为YYYYMMDD的日期
      CONCAT(SUBSTR({reference_field}, 1, 4), '-', SUBSTR({reference_field}, 5, 2), '-', SUBSTR({reference_field}, 7, 2))
    WHEN LENGTH({reference_field}) = 10 AND INSTR({reference_field}, '/') > 0 THEN
      -- 处理格式为YYYY/MM/DD的日期
      REPLACE({reference_field}, '/', '-')
    WHEN {reference_field} REGEXP '^[0-9]{{4}}年[0-9]{{1,2}}月[0-9]{{1,2}}日$' THEN
      -- 处理格式为YYYY年MM月DD日的日期
      CONCAT(
        SUBSTR({reference_field}, 1, 4), '-',
        LPAD(SUBSTR({reference_field}, 6, INSTR({reference_field}, '月') - 6), 2, '0'), '-',
        LPAD(SUBSTR({reference_field}, INSTR({reference_field}, '月') + 1, INSTR({reference_field}, '日') - INSTR({reference_field}, '月') - 1), 2, '0')
      )
    ELSE {reference_field}
  END
WHERE {reference_field} IS NOT NULL AND {reference_field} != '';"""
            
        elif operation_type == 'repair_idcard':
            sql = f"""-- 身份证号码修复SQL
UPDATE {table_name} SET {target_field} = 
  CASE 
    WHEN LENGTH({reference_field}) = 15 AND {reference_field} REGEXP '^[0-9]+$' THEN
      -- 15位身份证转18位算法
      CONCAT(
        SUBSTR({reference_field}, 1, 6),
        '19',
        SUBSTR({reference_field}, 7, 9),
        -- 校验码计算较复杂，这里简化为'X'
        'X'
      )
    WHEN LENGTH({reference_field}) = 18 AND {reference_field} REGEXP '^[0-9X]+$' THEN
      -- 已经是18位，保持不变
      {reference_field}
    ELSE 
      -- 其他情况保持原样
      {reference_field}
  END
WHERE {reference_field} IS NOT NULL AND LENGTH({reference_field}) IN (15, 18);"""
            
        else:
            # 未知操作类型，生成查询SQL
            sql = f"""-- 查询数据SQL
SELECT * FROM {table_name} WHERE {reference_field} IS NOT NULL LIMIT 100;"""
            
        return sql
    
    def _extract_sql_from_output(self, output: str) -> str:
        """
        从原始输出中提取SQL语句，去除<think>标签及其内容
        
        Args:
            output: 原始输出文本
            
        Returns:
            str: 提取的SQL语句
        """
        try:
            # 记录原始输出长度
            app_logger.info(f"原始输出长度: {len(output)}")
            
            # 移除<think>标签及其内容
            import re
            output_without_think = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)
            
            # 去除前后空白字符
            sql = output_without_think.strip()
            
            # 如果有多个语句（以None分隔），只取第一个有效语句

            
            app_logger.info(f"提取后的SQL长度: {len(sql)}")
            
            return sql
        except Exception as e:
            app_logger.error(f"提取SQL语句时发生错误: {str(e)}")
            return ""


# 创建服务实例
dify_service = DifyService() 