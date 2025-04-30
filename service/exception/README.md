# 统一异常处理机制

## 简介

本系统实现了统一的异常处理机制，主要特点：

- 单一的异常基类 `AppException`，用于系统中所有异常
- 全局异常处理，自动捕获并处理所有未捕获的异常
- 统一的错误响应格式，包含错误码、消息、时间戳、请求ID
- 基于请求类型自动选择响应格式（API请求返回JSON，页面请求返回错误页面）

## 使用方法

### 抛出异常

```python
from service.exception import AppException

# 简单使用
raise AppException("数据库连接失败")

# 指定HTTP状态码
raise AppException("无权限访问", code=403)

# 包含详细信息
raise AppException("输入参数无效", code=400, details={"field": "username", "reason": "长度不足"})
```

### 全局处理器

在应用初始化时，已经注册了全局异常处理器，无需额外操作：

```python
# main.py 中已经注册
from service.exception import register_error_handlers
register_error_handlers(app)
```

### 响应格式

1. **API请求**（路径以/api开头或Accept头为application/json）
   
   ```json
   {
     "code": 500,
     "message": "数据库连接失败",
     "details": {},
     "timestamp": "2023-04-30T15:57:33.123456",
     "request_id": "1234-5678-9abc-def0"
   }
   ```

2. **页面请求**
   
   将渲染`templates/log/error.html`模板，显示友好的错误页面。

## 最佳实践

1. **总是使用 AppException**：确保系统内所有自定义异常都使用 AppException

2. **合理设置状态码**：
   - 400: 客户端错误（如参数验证失败）
   - 401/403: 认证/授权错误
   - 404: 资源不存在
   - 500: 服务器内部错误（如数据库操作失败）

3. **提供有用的错误消息**：错误消息应该简洁明了，说明问题所在

4. **记录详细信息**：可以通过details参数提供更详细的错误信息，便于调试 