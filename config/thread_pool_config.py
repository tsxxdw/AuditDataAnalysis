"""
线程池配置

本模块定义了三种不同的线程池配置：
1. 日志线程池 - 固定大小池（5个线程）用于日志操作
2. 普通业务线程池 - 用于标准优先级的常规业务操作
3. 紧急业务线程池 - 用于高优先级的紧急操作
"""

# 日志线程池配置
LOGGER_POOL = {
    "name": "logger_pool",
    "size": 5,  # 固定池大小
    "max_queue_size": 1000,
    "thread_name_prefix": "logger_worker",
    "daemon": True
}

# 普通业务线程池配置
NORMAL_BUSINESS_POOL = {
    "name": "normal_business_pool",
    "min_size": 5,
    "max_size": 20,
    "core_size": 10,
    "max_queue_size": 500,
    "keep_alive_time": 60,  # 秒
    "thread_name_prefix": "normal_worker",
    "daemon": False
}

# 紧急业务线程池配置
EMERGENCY_BUSINESS_POOL = {
    "name": "emergency_business_pool",
    "min_size": 3,
    "max_size": 10,
    "core_size": 5,
    "max_queue_size": 200,  # 较小的队列，以促使为紧急情况创建线程
    "keep_alive_time": 120,  # 秒
    "thread_name_prefix": "emergency_worker",
    "daemon": False,
    "priority": "high"
}

# 全局线程池设置
GLOBAL_SETTINGS = {
    "monitor_interval": 30,  # 秒
    "rejection_policy": "caller_runs",  # 选项：caller_runs, abort, discard
    "thread_factory": "default"
} 

# 将所有配置整合到一个字典中，供thread_pool.py使用
thread_pool_config = {
    "logger_pool": LOGGER_POOL,
    "normal_business_pool": NORMAL_BUSINESS_POOL,
    "emergency_business_pool": EMERGENCY_BUSINESS_POOL,
    "global": GLOBAL_SETTINGS
} 