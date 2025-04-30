"""
线程池实现

本模块提供三种不同类型的线程池实现：
1. 日志线程池：固定大小的线程池，用于日志操作
2. 普通业务线程池：动态大小的线程池，用于常规业务操作
3. 紧急业务线程池：优先级线程池，用于紧急操作
"""

import concurrent.futures
import threading
import queue
import time
import logging
from typing import Callable, Any, Dict, Optional
from config.thread_pool_config import thread_pool_config

logger = logging.getLogger(__name__)

class ThreadPoolRejectionError(Exception):
    """当任务提交被拒绝时抛出的异常。"""
    pass

class CustomThreadPoolExecutor:
    """自定义线程池实现，具有额外功能。"""
    
    def __init__(self, pool_name: str):
        """使用配置文件中的设置初始化线程池。"""
        if pool_name not in thread_pool_config:
            raise ValueError(f"未知的池名称: {pool_name}")
        
        self.pool_name = pool_name
        self.config = thread_pool_config[pool_name]
        self.global_config = thread_pool_config['global']
        
        # 初始化线程池
        self._max_workers = self.config.get('max_size', 10)
        self._min_workers = self.config.get('min_size', 5)
        self._thread_name_prefix = self.config.get('thread_name_prefix', f"{pool_name}-worker")
        self._keep_alive_time = self.config.get('keep_alive_time', 60)
        
        # 任务队列
        self._max_queue_size = self.config.get('max_queue_size', 100)
        self._task_queue = queue.Queue(maxsize=self._max_queue_size)
        
        # 线程状态
        self._workers = {}  # 用于跟踪活动工作线程的字典
        self._shutdown = False
        self._shutdown_lock = threading.Lock()
        
        # 拒绝策略
        self._rejection_policy = self.global_config.get('rejection_policy', 'caller_runs')
        
        # 启动监控线程
        self._monitor_interval = self.global_config.get('monitor_interval', 30)
        self._monitor_thread = threading.Thread(target=self._monitor_pool, daemon=True)
        self._monitor_thread.start()
        
        # 启动工作线程
        self._adjust_pool_size(self._min_workers)
        
        logger.info(f"初始化 {pool_name} 线程池，最小线程数={self._min_workers}，最大线程数={self._max_workers}")

    def submit(self, fn: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """提交任务到线程池。"""
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('关闭后无法调度新任务')
                
            future = concurrent.futures.Future()
            
            # 创建任务
            task = {
                'future': future,
                'fn': fn,
                'args': args,
                'kwargs': kwargs
            }
            
            # 尝试提交任务
            try:
                self._task_queue.put_nowait(task)
            except queue.Full:
                # 根据策略处理拒绝
                self._handle_rejection(task)
            
            # 如有需要，调整池大小
            self._adjust_pool_size()
            
            return future
    
    def _handle_rejection(self, task):
        """根据策略处理任务拒绝。"""
        policy = self._rejection_policy
        
        if policy == 'caller_runs':
            # 在调用者的线程中执行任务
            self._execute_task(task)
        elif policy == 'abort':
            # 抛出异常
            raise ThreadPoolRejectionError(f"任务被 {self.pool_name} 线程池拒绝")
        elif policy == 'discard':
            # 静默丢弃任务
            task['future'].set_exception(ThreadPoolRejectionError("任务被丢弃"))
        else:
            # 默认：丢弃最旧的
            try:
                # 从队列中移除最旧的任务
                _ = self._task_queue.get_nowait()
                # 添加新任务
                self._task_queue.put_nowait(task)
            except (queue.Empty, queue.Full):
                # 如果队列操作失败，以异常拒绝
                task['future'].set_exception(ThreadPoolRejectionError("任务被拒绝"))
    
    def _execute_task(self, task):
        """执行任务并在future中设置结果或异常。"""
        future, fn, args, kwargs = task['future'], task['fn'], task['args'], task['kwargs']
        
        if not future.set_running_or_notify_cancel():
            return
        
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
    
    def _worker(self, worker_id):
        """工作线程函数。"""
        thread_name = f"{self._thread_name_prefix}-{worker_id}"
        threading.current_thread().name = thread_name
        
        idle_time = 0
        
        while True:
            try:
                try:
                    # 尝试获取带超时的任务
                    task = self._task_queue.get(timeout=1)
                    # 重置空闲时间
                    idle_time = 0
                    # 执行任务
                    self._execute_task(task)
                    # 标记任务已完成
                    self._task_queue.task_done()
                except queue.Empty:
                    # 没有可用的任务，增加空闲时间
                    idle_time += 1
                    
                    # 检查是否应该因为空闲超时而终止此工作线程
                    # 仅在我们有超过最小工作线程数量时终止
                    if (idle_time >= self._keep_alive_time and 
                        len(self._workers) > self._min_workers):
                        with self._shutdown_lock:
                            if len(self._workers) > self._min_workers:
                                # 从活动工作线程中移除此工作线程
                                self._workers.pop(worker_id, None)
                                logger.debug(f"终止空闲工作线程 {thread_name}")
                                return
                            
                # 检查是否关闭
                with self._shutdown_lock:
                    if self._shutdown:
                        return
                        
            except Exception as e:
                logger.exception(f"工作线程 {thread_name} 中的错误: {e}")
    
    def _adjust_pool_size(self, target_size=None):
        """根据负载或目标大小调整池大小。"""
        with self._shutdown_lock:
            if self._shutdown:
                return
                
            current_size = len(self._workers)
            
            if target_size is None:
                # 根据队列大小计算目标大小
                queue_size = self._task_queue.qsize()
                
                if queue_size > current_size and current_size < self._max_workers:
                    # 扩大池
                    target_size = min(current_size + max(1, queue_size // 2), self._max_workers)
                elif queue_size == 0 and current_size > self._min_workers:
                    # 让工作线程通过空闲超时自然终止
                    return
                else:
                    # 保持当前大小
                    return
            
            # 确保目标大小在界限内
            target_size = max(self._min_workers, min(target_size, self._max_workers))
            
            # 如果需要，添加工作线程
            while current_size < target_size:
                worker_id = id(threading.current_thread()) + len(self._workers) + 1
                worker_thread = threading.Thread(
                    target=self._worker,
                    args=(worker_id,),
                    daemon=self.config.get('daemon', True)
                )
                self._workers[worker_id] = worker_thread
                worker_thread.start()
                current_size += 1
                logger.debug(f"在 {self.pool_name} 中启动新工作线程，总计={current_size}")
    
    def _monitor_pool(self):
        """定期记录池统计信息并调整大小的监控线程。"""
        while True:
            time.sleep(self._monitor_interval)
            
            with self._shutdown_lock:
                if self._shutdown:
                    return
                
                worker_count = len(self._workers)
                queue_size = self._task_queue.qsize()
                
                logger.debug(
                    f"{self.pool_name} 池统计: 活动工作线程={worker_count}, "
                    f"队列大小={queue_size}/{self._max_queue_size}"
                )
    
    def shutdown(self, wait=True):
        """关闭线程池。"""
        with self._shutdown_lock:
            self._shutdown = True
        
        if wait:
            # 等待所有任务完成
            while not self._task_queue.empty():
                time.sleep(0.1)
            
            # 等待所有工作线程终止
            for worker in list(self._workers.values()):
                if worker.is_alive():
                    worker.join(timeout=5)

# 三个线程池的单例实例
_logger_pool = None
_normal_business_pool = None
_emergency_business_pool = None

def get_logger_pool():
    """获取日志线程池实例。"""
    global _logger_pool
    if _logger_pool is None:
        _logger_pool = CustomThreadPoolExecutor('logger_pool')
    return _logger_pool

def get_normal_business_pool():
    """获取普通业务线程池实例。"""
    global _normal_business_pool
    if _normal_business_pool is None:
        _normal_business_pool = CustomThreadPoolExecutor('normal_business_pool')
    return _normal_business_pool

def get_emergency_business_pool():
    """获取紧急业务线程池实例。"""
    global _emergency_business_pool
    if _emergency_business_pool is None:
        _emergency_business_pool = CustomThreadPoolExecutor('emergency_business_pool')
    return _emergency_business_pool

def shutdown_all_pools(wait=True):
    """关闭所有线程池。"""
    global _logger_pool, _normal_business_pool, _emergency_business_pool
    
    for pool in [_logger_pool, _normal_business_pool, _emergency_business_pool]:
        if pool is not None:
            pool.shutdown(wait=wait)
    
    _logger_pool = None
    _normal_business_pool = None
    _emergency_business_pool = None 