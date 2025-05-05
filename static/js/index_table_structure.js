// 数据库表结构管理页面JS文件(index_table_structure)
$(document).ready(function() {
    // 生成表创建SQL按钮点击事件
    $('#generateTableSql').on('click', function() {
        const tableName = $('#tableName').val();
        const tableComment = $('#tableComment').val();
        const dataSource = $('#dataSource').val();
        
        if(!tableName) {
            alert('请输入表名');
            return;
        }
        
        // 根据数据源类型生成不同的SQL
        let sql = '';
        if(dataSource === 'mysql') {
            sql = `CREATE TABLE ${tableName} (\n`;
            sql += `  id INT NOT NULL AUTO_INCREMENT,\n`;
            sql += `  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,\n`;
            sql += `  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n`;
            sql += `  PRIMARY KEY (id)\n`;
            sql += `) COMMENT='${tableComment}';`;
        } else if(dataSource === 'sqlserver') {
            sql = `CREATE TABLE ${tableName} (\n`;
            sql += `  id INT IDENTITY(1,1) NOT NULL,\n`;
            sql += `  create_time DATETIME DEFAULT GETDATE(),\n`;
            sql += `  update_time DATETIME DEFAULT GETDATE(),\n`;
            sql += `  PRIMARY KEY (id)\n`;
            sql += `);`;
            sql += `\nEXEC sp_addextendedproperty 'MS_Description', '${tableComment}', 'schema', 'dbo', 'table', '${tableName}';`;
        } else if(dataSource === 'oracle') {
            sql = `CREATE TABLE ${tableName} (\n`;
            sql += `  id NUMBER GENERATED ALWAYS AS IDENTITY,\n`;
            sql += `  create_time TIMESTAMP DEFAULT SYSTIMESTAMP,\n`;
            sql += `  update_time TIMESTAMP DEFAULT SYSTIMESTAMP,\n`;
            sql += `  CONSTRAINT ${tableName}_pk PRIMARY KEY (id)\n`;
            sql += `);`;
            sql += `\nCOMMENT ON TABLE ${tableName} IS '${tableComment}';`;
        } else {
            sql = `-- 请选择数据源类型以生成相应SQL`;
        }
        
        $('#sqlContent').val(sql);
    });
    
    // 生成索引SQL按钮点击事件
    $('#generateIndexSql').on('click', function() {
        const tableName = $('#indexTableName').val();
        const fieldName = $('#fieldName').val();
        const operationType = $('#indexOperationType').val();
        
        if(!tableName) {
            alert('请选择表名');
            return;
        }
        
        if(!fieldName) {
            alert('请选择字段名');
            return;
        }
        
        // 根据操作类型生成不同的SQL
        let sql = '';
        if(operationType === 'create') {
            sql = `CREATE INDEX idx_${tableName}_${fieldName} ON ${tableName}(${fieldName});`;
        } else if(operationType === 'delete') {
            sql = `DROP INDEX idx_${tableName}_${fieldName};`;
        }
        
        $('#sqlContent').val(sql);
    });
    
    // 执行SQL按钮点击事件
    $('#executeSql').on('click', function() {
        const sql = $('#sqlContent').val();
        
        if(!sql || sql.trim() === '') {
            alert('请先生成或输入SQL语句');
            return;
        }
        
        // 模拟执行SQL
        alert('SQL执行成功！\n实际项目中，这里会将SQL发送到后端执行。');
    });
    
    // 监听数据源选择变化
    $('#dataSource').on('change', function() {
        // 如果生成表创建SQL按钮已被点击过，则自动更新SQL
        if($('#sqlContent').val().includes('CREATE TABLE')) {
            $('#generateTableSql').click();
        }
    });
    
    // 监听索引表名变化，模拟加载字段
    $('#indexTableName').on('change', function() {
        const selectedTable = $(this).val();
        if(selectedTable) {
            // 这里模拟加载字段信息，实际项目中应该从后端获取
            $('#fieldName').empty();
            $('#fieldName').append('<option value="">请选择字段</option>');
            
            // 添加模拟字段
            const fields = ['id', 'name', 'code', 'status', 'create_time', 'update_time'];
            fields.forEach(field => {
                $('#fieldName').append(`<option value="${field}">${field}</option>`);
            });
        }
    });
}); 