"""
线程池使用示例

本模块演示了如何使用线程池来处理不同类型的任务。
"""

import time
import random
from service.log.logger import app_logger
from service.log.tools import log_with_context, handle_exceptions
from service.thread.thread_pool import (
    get_logger_pool,
    get_normal_business_pool,
    get_emergency_business_pool,
    shutdown_all_pools
)

# 模拟日志任务
def log_task(message, level="info"):
    """模拟日志记录任务"""
    time.sleep(0.1)  # 模拟I/O操作
    if level == "info":
        app_logger.info(f"日志消息: {message}")
    elif level == "error":
        app_logger.error(f"错误日志: {message}")
    return f"已记录日志: {message}"

# 模拟普通业务任务
@log_with_context(level="INFO", with_args=True)
def normal_task(task_id, duration=1):
    """模拟普通业务处理任务"""
    app_logger.info(f"开始处理普通任务 #{task_id}, 预计耗时 {duration}s")
    time.sleep(duration)  # 模拟处理时间
    result = f"普通任务 #{task_id} 已完成"
    app_logger.info(result)
    return result

# 模拟紧急业务任务
@log_with_context(level="INFO", with_args=True)
def emergency_task(task_id, duration=0.5):
    """模拟紧急业务处理任务"""
    app_logger.info(f"开始处理紧急任务 #{task_id}, 预计耗时 {duration}s")
    time.sleep(duration)  # 模拟处理时间
    result = f"紧急任务 #{task_id} 已完成"
    app_logger.info(result)
    return result

# 任务完成回调
def task_done_callback(future):
    """任务完成时的回调函数"""
    try:
        result = future.result()
        app_logger.info(f"任务回调: {result}")
    except Exception as e:
        app_logger.error(f"任务执行出错: {e}")

@handle_exceptions(reraise=True)
def main():
    """主函数，演示线程池的使用"""
    try:
        # 获取线程池实例
        logger_pool = get_logger_pool()
        normal_pool = get_normal_business_pool()
        emergency_pool = get_emergency_business_pool()
        
        app_logger.info("开始提交任务到线程池")
        
        # 提交日志任务
        log_futures = []
        for i in range(10):
            level = "error" if i % 3 == 0 else "info"
            future = logger_pool.submit(log_task, f"测试日志消息 #{i}", level)
            future.add_done_callback(task_done_callback)
            log_futures.append(future)
        
        # 提交普通业务任务
        normal_futures = []
        for i in range(15):
            duration = random.uniform(0.5, 2.0)
            future = normal_pool.submit(normal_task, i, duration)
            future.add_done_callback(task_done_callback)
            normal_futures.append(future)
        
        # 提交紧急业务任务
        emergency_futures = []
        for i in range(5):
            duration = random.uniform(0.2, 1.0)
            future = emergency_pool.submit(emergency_task, i, duration)
            future.add_done_callback(task_done_callback)
            emergency_futures.append(future)
        
        # 等待所有日志任务完成
        app_logger.info("等待日志任务完成...")
        for future in log_futures:
            app_logger.info(f"日志任务结果: {future.result()}")
        
        # 等待所有普通业务任务完成
        app_logger.info("等待普通业务任务完成...")
        for future in normal_futures:
            app_logger.info(f"普通业务任务结果: {future.result()}")
        
        # 等待所有紧急业务任务完成
        app_logger.info("等待紧急业务任务完成...")
        for future in emergency_futures:
            app_logger.info(f"紧急业务任务结果: {future.result()}")
        
        app_logger.info("所有任务已完成")
    
    finally:
        # 关闭所有线程池
        app_logger.info("关闭所有线程池")
        shutdown_all_pools(wait=True)

if __name__ == "__main__":
    main() 