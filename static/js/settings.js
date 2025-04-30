// 设置页面JS文件
$(document).ready(function() {
    // 初始化数据库设置表单
    initDbSettingsForm();

    // 导航菜单切换
    $('.nav-item').click(function() {
        // 移除所有导航项的active类
        $('.nav-item').removeClass('active');
        // 给当前点击的导航项添加active类
        $(this).addClass('active');
        
        // 获取目标内容区域的ID
        var targetId = $(this).data('target');
        
        // 隐藏所有内容区域
        $('.settings-section').removeClass('active');
        // 显示目标内容区域
        $('#' + targetId).addClass('active');
    });

    // 初始化数据库设置表单状态
    function initDbSettingsForm() {
        // 默认显示MySQL表单
        $('.db-connection-form').hide();
        $('#mysql-form').show();
        
        // 初始化SQL Server认证字段
        handleSqlServerAuth();
    }

    // 默认数据库类型切换
    $('#default-db').change(function() {
        var defaultDbType = $(this).val();
        
        // 可以在这里添加加载默认数据库配置的逻辑
        console.log('默认数据库类型已切换为：' + defaultDbType);
    });

    // 数据库类型切换
    $('#db-type').change(function() {
        var dbType = $(this).val();
        
        // 隐藏所有数据库连接表单
        $('.db-connection-form').hide();
        
        // 显示对应的数据库连接表单
        $('#' + dbType + '-form').show();
        
        // 特殊处理SQL Server身份验证选项
        if (dbType === 'sqlserver') {
            handleSqlServerAuth();
        }
    });
    
    // SQL Server 认证方式切换
    $('#sqlserver-auth').change(function() {
        handleSqlServerAuth();
    });
    
    function handleSqlServerAuth() {
        var authType = $('#sqlserver-auth').val();
        if (authType === 'windows') {
            $('.sql-auth-field').hide();
        } else {
            $('.sql-auth-field').show();
        }
    }

    // 保存数据库设置
    $('.save-db-btn').click(function() {
        var defaultDbType = $('#default-db').val();
        var dbType = $('#db-type').val();
        var formData = {};
        
        // 添加默认数据库类型
        formData.defaultDbType = defaultDbType;
        formData.type = dbType;
        
        // 根据数据库类型收集表单数据
        if (dbType === 'mysql') {
            formData.connection = {
                host: $('#mysql-host').val(),
                port: $('#mysql-port').val(),
                database: $('#mysql-database').val(),
                username: $('#mysql-username').val(),
                password: $('#mysql-password').val()
            };
        } else if (dbType === 'sqlserver') {
            formData.connection = {
                host: $('#sqlserver-host').val(),
                instance: $('#sqlserver-instance').val(),
                database: $('#sqlserver-database').val(),
                authType: $('#sqlserver-auth').val()
            };
            
            if ($('#sqlserver-auth').val() === 'sql') {
                formData.connection.username = $('#sqlserver-username').val();
                formData.connection.password = $('#sqlserver-password').val();
            }
        } else if (dbType === 'oracle') {
            formData.connection = {
                host: $('#oracle-host').val(),
                port: $('#oracle-port').val(),
                service: $('#oracle-service').val(),
                username: $('#oracle-username').val(),
                password: $('#oracle-password').val()
            };
        }
        
        // 这里仅做演示，实际操作需要后端支持
        alert('数据库设置已保存!\n默认数据库类型: ' + defaultDbType + '\n当前配置数据库类型: ' + dbType + '\n连接信息已收集');
        console.log('保存的设置:', formData);
    });

    // 编辑数据库连接
    $('.edit-btn').click(function() {
        var connectionName = $(this).closest('.connection-item').find('.connection-name').text();
        alert('编辑连接: ' + connectionName + '\n这里将显示编辑数据库连接的弹窗');
    });

    // 删除数据库连接
    $('.delete-btn').click(function() {
        var connectionName = $(this).closest('.connection-item').find('.connection-name').text();
        if (confirm('确定要删除连接 "' + connectionName + '" 吗？')) {
            // 这里仅做演示，实际操作需要后端支持
            $(this).closest('.connection-item').fadeOut(300);
        }
    });

    // 添加新连接
    $('.add-connection-btn').click(function() {
        alert('添加新连接\n这里将显示添加数据库连接的弹窗');
    });

    // 浏览按钮 - 选择日志路径
    $('.browse-btn').click(function() {
        alert('选择目录\n实际应用中会打开文件夹选择对话框');
    });

    // 保存日志设置
    $('.save-logs-btn').click(function() {
        var logPath = $('#log-path').val();
        var logLevel = $('#log-level').val();
        
        // 这里仅做演示，实际操作需要后端支持
        alert('日志设置已保存!\n路径: ' + logPath + '\n日志级别: ' + logLevel);
    });
}); 