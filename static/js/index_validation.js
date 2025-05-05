// 数据校验页面JS文件(index_validation)
$(document).ready(function() {
    // 监听表名选择变化
    $('#tableName').on('change', function() {
        const selectedTable = $(this).val();
        if(selectedTable) {
            // 模拟加载字段
            loadFields(selectedTable);
        } else {
            // 清空字段下拉框
            $('#fieldName').empty().append('<option value="">请选择字段</option>');
        }
    });
    
    // 生成SQL按钮点击事件
    $('#generateSql').on('click', function() {
        const tableName = $('#tableName').val();
        const fieldName = $('#fieldName').val();
        const validationType = $('#validationType').val();
        
        // 验证必填项
        if(!tableName || !fieldName || !validationType) {
            alert('请选择表名、字段名和校验类型');
            return;
        }
        
        // 根据校验类型生成不同的SQL
        let sql = '';
        
        if(validationType === 'idcard') {
            sql = `-- 身份证号码校验SQL\n`;
            sql += `SELECT * FROM ${tableName} WHERE ${fieldName} IS NOT NULL AND (\n`;
            sql += `  -- 长度不是15位或18位\n`;
            sql += `  LENGTH(${fieldName}) NOT IN (15, 18)\n`;
            sql += `  -- 或者18位身份证格式不正确（最后一位校验码错误）\n`;
            sql += `  OR (LENGTH(${fieldName}) = 18 AND \n`;
            sql += `      NOT REGEXP_LIKE(${fieldName}, '^[1-9]\\d{5}(19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{3}[0-9X]$')\n`;
            sql += `     )\n`;
            sql += `  -- 或者15位身份证格式不正确\n`;
            sql += `  OR (LENGTH(${fieldName}) = 15 AND \n`;
            sql += `      NOT REGEXP_LIKE(${fieldName}, '^[1-9]\\d{5}\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{3}$')\n`;
            sql += `     )\n`;
            sql += `);`;
        } 
        else if(validationType === 'date') {
            sql = `-- 日期格式校验SQL\n`;
            sql += `SELECT * FROM ${tableName} WHERE ${fieldName} IS NOT NULL AND (\n`;
            sql += `  -- 不符合YYYY-MM-DD格式\n`;
            sql += `  NOT REGEXP_LIKE(${fieldName}, '^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$')\n`;
            sql += `  -- 或者不符合YYYY/MM/DD格式\n`;
            sql += `  AND NOT REGEXP_LIKE(${fieldName}, '^\\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12]\\d|3[01])$')\n`;
            sql += `  -- 或者不符合YYYYMMDD格式\n`;
            sql += `  AND NOT REGEXP_LIKE(${fieldName}, '^\\d{4}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])$')\n`;
            sql += `);`;
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
        
        // 显示加载提示
        $('.empty-result').text('执行中，请稍候...');
        $('.validation-results').hide();
        
        // 模拟SQL执行过程
        setTimeout(function() {
            // 隐藏提示文字，显示校验结果
            $('.empty-result').hide();
            
            const tableName = $('#tableName').val();
            const fieldName = $('#fieldName').val();
            const validationType = $('#validationType').val();
            
            // 生成模拟校验结果
            let resultsHtml = '<div class="validation-summary">';
            resultsHtml += '<h3>校验完成</h3>';
            resultsHtml += '<p>表名: ' + tableName + '</p>';
            resultsHtml += '<p>字段名: ' + fieldName + '</p>';
            resultsHtml += '<p>校验类型: ' + (validationType === 'idcard' ? '身份证校验' : '日期格式错误校验') + '</p>';
            resultsHtml += '<p>校验时间: ' + new Date().toLocaleString() + '</p>';
            resultsHtml += '</div>';
            
            resultsHtml += '<div class="validation-details">';
            resultsHtml += '<h3>校验详情</h3>';
            
            if(validationType === 'idcard') {
                resultsHtml += '<table class="validation-table">';
                resultsHtml += '<thead><tr><th>错误类型</th><th>记录数</th><th>错误率</th><th>示例值</th></tr></thead>';
                resultsHtml += '<tbody>';
                resultsHtml += '<tr><td>长度不为15位或18位</td><td>5</td><td>0.5%</td><td>123456, 12345678901234567</td></tr>';
                resultsHtml += '<tr><td>格式不正确</td><td>12</td><td>1.2%</td><td>440121198X0218XXXX</td></tr>';
                resultsHtml += '<tr><td>校验码错误</td><td>3</td><td>0.3%</td><td>440121198901011234</td></tr>';
                resultsHtml += '</tbody></table>';
            } else if(validationType === 'date') {
                resultsHtml += '<table class="validation-table">';
                resultsHtml += '<thead><tr><th>错误类型</th><th>记录数</th><th>错误率</th><th>示例值</th></tr></thead>';
                resultsHtml += '<tbody>';
                resultsHtml += '<tr><td>格式错误</td><td>8</td><td>0.8%</td><td>2021.01.01, 01-01-2021</td></tr>';
                resultsHtml += '<tr><td>无效日期</td><td>7</td><td>0.7%</td><td>2021-02-30, 2021-13-01</td></tr>';
                resultsHtml += '</tbody></table>';
            }
            
            resultsHtml += '</div>';
            
            // 显示校验结果
            $('.validation-results').html(resultsHtml).show();
        }, 1000);
    });
    
    // 模拟加载字段
    function loadFields(tableName) {
        $('#fieldName').empty().append('<option value="">请选择字段</option>');
        
        // 根据表名添加不同的字段选项
        const fields = [];
        if(tableName === 'table1') {
            fields.push('id', 'name', 'id_card', 'birth_date', 'create_time');
        } else if(tableName === 'table2') {
            fields.push('order_id', 'customer_id', 'order_date', 'ship_date', 'status');
        } else if(tableName === 'table3') {
            fields.push('product_id', 'product_name', 'launch_date', 'producer_code', 'price');
        }
        
        // 添加字段选项
        fields.forEach(field => {
            $('#fieldName').append(`<option value="${field}">${field}</option>`);
        });
    }
}); 