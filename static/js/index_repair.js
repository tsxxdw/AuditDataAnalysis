// 数据修复页面JS文件(index_repair)
$(document).ready(function() {
    // 监听表名选择变化
    $('#tableName').on('change', function() {
        const selectedTable = $(this).val();
        if(selectedTable) {
            // 模拟加载原字段
            loadOriginalFields(selectedTable);
            // 清空新字段下拉框
            $('#newField').empty().append('<option value="">请选择新字段</option>');
        }
    });
    
    // 监听原字段选择变化
    $('#originalField').on('change', function() {
        const selectedField = $(this).val();
        if(selectedField) {
            // 模拟加载新字段选项
            loadNewFields(selectedField);
        }
    });
    
    // 监听操作类型选择变化
    $('#operationType').on('change', function() {
        const operationType = $(this).val();
        // 根据操作类型决定是否启用字段类型选择
        if(operationType === 'repair_date' || operationType === 'repair_idcard') {
            $('#fieldType').prop('disabled', true);
            
            // 根据操作类型自动选择对应的字段类型
            if(operationType === 'repair_date') {
                $('#fieldType').val('date');
            } else if(operationType === 'repair_idcard') {
                $('#fieldType').val('idCard');
            }
        } else {
            $('#fieldType').prop('disabled', false);
        }
    });
    
    // 生成SQL按钮点击事件
    $('#generateSql').on('click', function() {
        const tableName = $('#tableName').val();
        const originalField = $('#originalField').val();
        const newField = $('#newField').val();
        const fieldType = $('#fieldType').val();
        const operationType = $('#operationType').val();
        
        // 验证必填项
        if(!tableName || !originalField || !operationType) {
            alert('请至少选择表名、原字段和操作类型');
            return;
        }
        
        // 根据操作类型生成不同的SQL
        let sql = '';
        
        if(operationType === 'rename') {
            if(!newField) {
                alert('修改字段名需要选择新字段');
                return;
            }
            sql = `ALTER TABLE ${tableName} RENAME COLUMN ${originalField} TO ${newField};`;
        } 
        else if(operationType === 'repair_date') {
            sql = `-- 日期类型修复\n`;
            sql += `UPDATE ${tableName} SET ${originalField} = \n`;
            sql += `  CASE \n`;
            sql += `    WHEN LENGTH(${originalField}) = 8 THEN \n`;
            sql += `      SUBSTR(${originalField}, 1, 4) || '-' || SUBSTR(${originalField}, 5, 2) || '-' || SUBSTR(${originalField}, 7, 2) \n`;
            sql += `    WHEN LENGTH(${originalField}) = 10 AND INSTR(${originalField}, '/') > 0 THEN \n`;
            sql += `      REPLACE(${originalField}, '/', '-') \n`;
            sql += `    ELSE ${originalField} \n`;
            sql += `  END \n`;
            sql += `WHERE ${originalField} IS NOT NULL;`;
        } 
        else if(operationType === 'repair_idcard') {
            sql = `-- 身份证修复\n`;
            sql += `UPDATE ${tableName} SET ${originalField} = \n`;
            sql += `  CASE \n`;
            sql += `    WHEN LENGTH(${originalField}) = 15 THEN \n`;
            sql += `      -- 15位转18位身份证算法\n`;
            sql += `      CONCAT(SUBSTR(${originalField}, 1, 6), '19', SUBSTR(${originalField}, 7, 9)) \n`;
            sql += `    WHEN LENGTH(${originalField}) = 18 THEN ${originalField} \n`;
            sql += `    ELSE ${originalField} \n`;
            sql += `  END \n`;
            sql += `WHERE ${originalField} IS NOT NULL;`;
        }
        
        // 显示生成的SQL
        $('#sqlContent').val(sql);
    });
    
    // 执行SQL按钮点击事件
    $('#executeSql').on('click', function() {
        const sql = $('#sqlContent').val();
        
        if(!sql || sql.trim() === '') {
            alert('请先生成SQL语句');
            return;
        }
        
        // 模拟执行SQL
        alert('SQL执行成功！\n实际项目中，这里会将SQL发送到后端执行。');
    });
    
    // 模拟加载原字段
    function loadOriginalFields(tableName) {
        $('#originalField').empty().append('<option value="">请选择原字段</option>');
        
        // 根据表名添加不同的字段选项
        const fields = [];
        if(tableName === 'table1') {
            fields.push('id', 'name', 'id_card', 'birthday', 'create_time');
        } else if(tableName === 'table2') {
            fields.push('id', 'code', 'birth_date', 'person_id', 'update_time');
        } else if(tableName === 'table3') {
            fields.push('id', 'title', 'date_field', 'id_number', 'status');
        }
        
        // 添加字段选项
        fields.forEach(field => {
            $('#originalField').append(`<option value="${field}">${field}</option>`);
        });
    }
    
    // 模拟加载新字段
    function loadNewFields(originalField) {
        $('#newField').empty().append('<option value="">请选择新字段</option>');
        
        // 根据原字段添加建议的新字段名
        let suggestedFields = [];
        
        if(originalField.includes('id_card') || originalField.includes('id_number')) {
            suggestedFields = ['id_card_no', 'identity_card', 'id_number_fixed'];
        } 
        else if(originalField.includes('birth') || originalField.includes('date')) {
            suggestedFields = ['birth_date', 'birthday_fixed', 'date_formatted'];
        }
        else {
            suggestedFields = [`${originalField}_new`, `${originalField}_fixed`, `new_${originalField}`];
        }
        
        // 添加新字段选项
        suggestedFields.forEach(field => {
            $('#newField').append(`<option value="${field}">${field}</option>`);
        });
    }
}); 