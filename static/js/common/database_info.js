// 数据库信息显示模块
$(document).ready(function() {
    // 获取当前数据库信息
    function fetchDatabaseInfo() {
        $.ajax({
            url: '/api/common/database_info',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // 显示数据库信息
                    displayDatabaseInfo(response.db_type, response.db_name);
                } else {
                    console.error('获取数据库信息失败:', response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('API请求失败:', error);
            }
        });
    }

    // 显示数据库信息
    function displayDatabaseInfo(dbType, dbName) {
        if (!dbType && !dbName) {
            return;
        }
        
        const dbInfoText = dbType + (dbName ? ': ' + dbName : '');
        
        // 如果数据库信息容器不存在，则创建
        if ($('.db-info-container').length === 0) {
            const dbInfoContainer = $('<div class="db-info-container"></div>');
            const dbInfoElement = $('<span class="db-info"></span>').text(dbInfoText);
            
            dbInfoContainer.append(dbInfoElement);
            
            // 将数据库信息容器添加到页面标题旁边
            $('.page-title').after(dbInfoContainer);
        } else {
            // 如果容器已存在，则更新内容
            $('.db-info').text(dbInfoText);
        }
    }

    // 页面加载时获取数据库信息
    fetchDatabaseInfo();
}); 