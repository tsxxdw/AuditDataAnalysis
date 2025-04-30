// 数据库设置JS文件
// 负责处理数据库设置的加载、保存和表单控制

const DatabaseSettings = {
    // 初始化
    init: function() {
        this.bindEvents();
        this.loadDatabaseSettings();
    },
    
    // 绑定事件
    bindEvents: function() {
        // 数据库类型切换
        $('#db-type').change(function() {
            DatabaseSettings.handleDbTypeChange();
        });
        
        // 默认数据库类型切换
        $('#default-db').change(function() {
            var defaultDbType = $(this).val();
            console.log('默认数据库类型已切换为：' + defaultDbType);
        });
        
        // SQL Server 认证方式切换
        $('#sqlserver-auth').change(function() {
            DatabaseSettings.handleSqlServerAuth();
        });
        
        // 保存数据库设置
        $('.save-db-btn').click(function() {
            DatabaseSettings.saveSettings();
        });
    },
    
    // 加载数据库设置
    loadDatabaseSettings: function() {
        $.ajax({
            url: '/api/settings/database',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                // 设置默认数据库类型
                if (data.defaultDbType) {
                    $('#default-db').val(data.defaultDbType);
                }
                
                // 加载数据库配置
                if (data.databases) {
                    // 默认先显示默认数据库类型的表单
                    var defaultType = data.defaultDbType || 'mysql';
                    $('#db-type').val(defaultType);
                    $('#db-type').trigger('change');
                    
                    // 填充MySQL配置
                    if (data.databases.mysql) {
                        DatabaseSettings.fillMySQLForm(data.databases.mysql);
                    }
                    
                    // 填充SQL Server配置
                    if (data.databases.sqlserver) {
                        DatabaseSettings.fillSQLServerForm(data.databases.sqlserver);
                    }
                    
                    // 填充Oracle配置
                    if (data.databases.oracle) {
                        DatabaseSettings.fillOracleForm(data.databases.oracle);
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('加载数据库设置失败:', error);
            }
        });
    },
    
    // 处理数据库类型切换
    handleDbTypeChange: function() {
        var dbType = $('#db-type').val();
        
        // 隐藏所有数据库连接表单
        $('.db-connection-form').hide();
        
        // 显示对应的数据库连接表单
        $('#' + dbType + '-form').show();
        
        // 特殊处理SQL Server身份验证选项
        if (dbType === 'sqlserver') {
            this.handleSqlServerAuth();
        }
    },
    
    // 处理SQL Server认证方式
    handleSqlServerAuth: function() {
        var authType = $('#sqlserver-auth').val();
        if (authType === 'windows') {
            $('.sql-auth-field').hide();
        } else {
            $('.sql-auth-field').show();
        }
    },
    
    // 保存设置
    saveSettings: function() {
        var defaultDbType = $('#default-db').val();
        
        // 收集所有数据库类型的连接信息
        var mysqlConfig = this.collectMySQLInfo();
        var sqlserverConfig = this.collectSQLServerInfo();
        var oracleConfig = this.collectOracleInfo();
        
        // 构建要保存的数据结构
        var settingsData = {
            defaultDbType: defaultDbType,
            databases: {
                mysql: mysqlConfig,
                sqlserver: sqlserverConfig,
                oracle: oracleConfig
            }
        };
        
        // 发送数据到后端保存
        $.ajax({
            url: '/api/settings/database',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(settingsData),
            success: function(response) {
                alert('数据库设置已保存成功！');
            },
            error: function(xhr, status, error) {
                alert('保存数据库设置失败: ' + error);
                console.error('保存数据库设置失败:', xhr.responseText);
            }
        });
    },
    
    // 填充MySQL表单
    fillMySQLForm: function(config) {
        $('#mysql-host').val(config.host || '');
        $('#mysql-port').val(config.port || '3306');
        $('#mysql-database').val(config.database || '');
        $('#mysql-username').val(config.username || '');
        $('#mysql-password').val(config.password || '');
    },
    
    // 填充SQL Server表单
    fillSQLServerForm: function(config) {
        $('#sqlserver-host').val(config.host || '');
        $('#sqlserver-instance').val(config.instance || '');
        $('#sqlserver-database').val(config.database || '');
        
        if (config.authType) {
            $('#sqlserver-auth').val(config.authType);
            this.handleSqlServerAuth();
        }
        
        if (config.authType === 'sql') {
            $('#sqlserver-username').val(config.username || '');
            $('#sqlserver-password').val(config.password || '');
        }
    },
    
    // 填充Oracle表单
    fillOracleForm: function(config) {
        $('#oracle-host').val(config.host || '');
        $('#oracle-port').val(config.port || '1521');
        $('#oracle-service').val(config.service || '');
        $('#oracle-username').val(config.username || '');
        $('#oracle-password').val(config.password || '');
    },
    
    // 收集MySQL连接信息
    collectMySQLInfo: function() {
        return {
            host: $('#mysql-host').val(),
            port: $('#mysql-port').val(),
            database: $('#mysql-database').val(),
            username: $('#mysql-username').val(),
            password: $('#mysql-password').val()
        };
    },
    
    // 收集SQL Server连接信息
    collectSQLServerInfo: function() {
        var info = {
            host: $('#sqlserver-host').val(),
            instance: $('#sqlserver-instance').val(),
            database: $('#sqlserver-database').val(),
            authType: $('#sqlserver-auth').val()
        };
        
        if ($('#sqlserver-auth').val() === 'sql') {
            info.username = $('#sqlserver-username').val();
            info.password = $('#sqlserver-password').val();
        }
        
        return info;
    },
    
    // 收集Oracle连接信息
    collectOracleInfo: function() {
        return {
            host: $('#oracle-host').val(),
            port: $('#oracle-port').val(),
            service: $('#oracle-service').val(),
            username: $('#oracle-username').val(),
            password: $('#oracle-password').val()
        };
    }
}; 