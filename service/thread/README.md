# 线程池使用说明

## 概述
线程池模块提供了三种不同类型的线程池实现：
1. **日志线程池（Logger Pool）**：固定大小的线程池，专用于日志操作
2. **普通业务线程池（Normal Business Pool）**：用于标准优先级的常规业务操作
3. **紧急业务线程池（Emergency Business Pool）**：用于高优先级的紧急业务操作

## 使用方法

### 获取线程池实例

```python
from service.thread.thread_pool import get_logger_pool, get_normal_business_pool, get_emergency_business_pool

# 获取日志线程池
logger_pool = get_logger_pool()

# 获取普通业务线程池
normal_pool = get_normal_business_pool()

# 获取紧急业务线程池
emergency_pool = get_emergency_business_pool()
```

### 提交任务

```python
# 定义要执行的函数
def my_task(param1, param2):
    # 任务逻辑
    return result

# 提交任务到线程池
future = normal_pool.submit(my_task, param1, param2)

# 获取任务结果（阻塞直到任务完成）
result = future.result()

# 非阻塞方式处理结果
future.add_done_callback(lambda f: print(f"任务完成，结果: {f.result()}"))
```

### 关闭线程池

```python
# 关闭单个线程池
normal_pool.shutdown(wait=True)  # wait=True 表示等待所有任务完成

# 关闭所有线程池
from service.thread.thread_pool import shutdown_all_pools
shutdown_all_pools(wait=True)
```

## 线程池配置

线程池的配置在 `config/thread_pool_config.py` 文件中定义：

### 日志线程池配置
- 固定大小：5个线程
- 最大队列大小：1000
- 线程为守护线程

### 普通业务线程池配置
- 最小线程数：5
- 最大线程数：20
- 核心线程数：10
- 最大队列大小：500
- 线程保持活跃时间：60秒

### 紧急业务线程池配置
- 最小线程数：3
- 最大线程数：10
- 核心线程数：5
- 最大队列大小：200（较小的队列促使更快创建新线程）
- 线程保持活跃时间：120秒
- 优先级：高

## 拒绝策略

当线程池队列满时，可以采用以下拒绝策略：
- `caller_runs`：在调用者的线程中执行任务（默认）
- `abort`：抛出异常
- `discard`：静默丢弃任务

## 高级用法

### 异常处理

```python
try:
    future = normal_pool.submit(my_task, param1, param2)
    result = future.result(timeout=10)  # 设置超时时间
except concurrent.futures.TimeoutError:
    print("任务执行超时")
except Exception as e:
    print(f"任务执行出错: {e}")
```

### 并行执行多个任务

```python
import concurrent.futures

# 提交多个任务
futures = [normal_pool.submit(my_task, p1, p2) for p1, p2 in parameters]

# 等待所有任务完成
for future in concurrent.futures.as_completed(futures):
    try:
        result = future.result()
        print(f"任务完成: {result}")
    except Exception as e:
        print(f"任务失败: {e}")
```

## 注意事项

1. 对于CPU密集型任务，建议使用普通业务线程池
2. 对于IO密集型任务，可以根据需要使用普通业务线程池或紧急业务线程池
3. 日志线程池仅用于日志记录操作，避免用于其他业务逻辑
4. 在程序退出前，确保调用`shutdown_all_pools()`关闭所有线程池
5. 紧急业务线程池优先级较高，应仅用于真正的紧急任务 