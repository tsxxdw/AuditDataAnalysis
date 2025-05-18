/**
 * SQL执行区域组件初始化
 */
$(document).ready(function() {
    // 检查是否存在SQL执行区域组件
    if ($('.sql-execute-section').length > 0) {
        // 创建组件实例
        window.sqlExecuteArea = new SqlExecuteArea({
            // 可以在这里传入自定义配置
            apiEndpoint: '/api/common/execute_sql',
            onGenerateSQL: function(e) {
                // 这个回调函数会被各页面覆盖
                console.log('生成SQL按钮被点击');
            },
            onSuccess: function(response) {
                console.log('SQL执行成功:', response);
                // 如果需要刷新表列表等操作，在各页面中覆盖此函数
            },
            onError: function(error) {
                console.error('SQL执行失败:', error);
            }
        });
        
        console.log('SQL执行区域组件已初始化');
    }
}); 