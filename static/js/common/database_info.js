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
            
            // 将数据库信息容器添加到容器中的顶部位置
            $('.container').append(dbInfoContainer);
        } else {
            // 如果容器已存在，则更新内容
            $('.db-info').text(dbInfoText);
        }
    }

    // 页面加载时获取数据库信息
    fetchDatabaseInfo();
});

// 公共数据库表和字段操作函数
/**
 * 加载数据库表列表
 * @param {string} targetSelector - 目标下拉框选择器
 * @param {function} callback - 可选的回调函数，用于在加载完成后执行
 */
function loadDatabaseTables(targetSelector, callback) {
    $.ajax({
        url: '/api/common/tables',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                // 清空表下拉框
                $(targetSelector).empty();
                $(targetSelector).append('<option value="">请选择表</option>');
                
                // 填充表下拉框
                response.tables.forEach(table => {
                    // 构建表显示名称，包含备注信息
                    var displayName = table.name;
                    if (table.comment && table.comment.trim() !== '') {
                        displayName += ' (' + table.comment + ')';
                    }
                    
                    $(targetSelector).append(
                        $('<option></option>')
                            .attr('value', table.name)
                            .text(displayName)
                    );
                });
                
                // 如果提供了回调函数，则执行
                if (typeof callback === 'function') {
                    callback(response.tables);
                }
            } else {
                console.error('获取表列表失败:', response.message);
            }
        },
        error: function(xhr) {
            console.error('获取表列表请求失败:', xhr);
        }
    });
}

/**
 * 加载表字段
 * @param {string} tableName - 表名
 * @param {string} targetSelector - 目标下拉框选择器
 * @param {function} callback - 可选的回调函数，用于在加载完成后执行
 */
function loadDatabaseTableFields(tableName, targetSelector, callback) {
    if (!tableName) {
        // 清空字段下拉框
        $(targetSelector).empty();
        $(targetSelector).append('<option value="">请选择字段</option>');
        return;
    }
    
    $.ajax({
        url: `/api/common/fields/${tableName}`,
        type: 'GET',
        success: function(response) {
            if (response.success) {
                // 清空字段下拉框
                $(targetSelector).empty();
                $(targetSelector).append('<option value="">请选择字段</option>');
                
                // 填充字段下拉框
                response.fields.forEach(field => {
                    $(targetSelector).append(
                        `<option value="${field.name}">${field.name} - ${field.comment || '无注释'}</option>`
                    );
                });
                
                // 如果提供了回调函数，则执行
                if (typeof callback === 'function') {
                    callback(response.fields);
                }
            } else {
                console.error('获取表字段失败:', response.message);
                alert(response.message || '获取表字段失败');
            }
        },
        error: function(xhr) {
            console.error('获取表字段请求失败:', xhr);
            alert('获取表字段请求失败，请查看控制台日志');
        }
    });
} 