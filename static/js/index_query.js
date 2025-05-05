// 数据分析页面JS文件(index_query)
$(document).ready(function() {
    // 业务查询页面特定的JS代码
    
    // 模板示例数据
    const sqlTemplates = {
        'template1': 'SELECT * FROM table_name WHERE condition;',
        'template2': 'SELECT column, COUNT(*) as count FROM table_name GROUP BY column;',
        'template3': 'SELECT a.column1, b.column2 FROM table_a a JOIN table_b b ON a.id = b.id;'
    };
    
    // 选择SQL模板时更新SQL显示区域
    $('#sqlTemplate').on('change', function() {
        const templateId = $(this).val();
        if(templateId && sqlTemplates[templateId]) {
            $('#sqlDisplay').text(sqlTemplates[templateId]);
        }
    });
    
    // 生成执行SQL按钮点击事件
    $('#generateSQL').on('click', function() {
        const dbType = $('#dbType').val();
        const templateId = $('#sqlTemplate').val();
        
        if(!templateId) {
            alert('请先选择一个SQL模板');
            return;
        }
        
        // 这里可以根据数据库类型对SQL进行适配，现在只是简单显示
        let sql = sqlTemplates[templateId];
        
        if(dbType === 'mysql') {
            sql = '-- MySQL查询\n' + sql;
        } else if(dbType === 'sqlserver') {
            sql = '-- SQL Server查询\n' + sql;
        } else if(dbType === 'oracle') {
            sql = '-- Oracle查询\n' + sql;
        }
        
        $('#sqlDisplay').text(sql);
    });
    
    // 执行SQL按钮点击事件
    $('#executeSQL').on('click', function() {
        const sql = $('#sqlDisplay').text();
        if(!sql || sql.trim() === '') {
            alert('请先生成SQL语句');
            return;
        }
        
        // 模拟执行SQL
        alert('SQL执行成功！\n实际项目中，这里会发送请求到后端执行SQL并返回结果。');
    });
    
    // 新增SQL模板按钮点击事件
    $('#addTemplate').on('click', function() {
        // 模拟弹出创建模板的对话框
        const templateName = prompt('请输入新模板名称：');
        if(templateName) {
            const templateSQL = prompt('请输入SQL语句：');
            if(templateSQL) {
                // 添加新模板到下拉列表
                const newTemplateId = 'template' + (Object.keys(sqlTemplates).length + 1);
                sqlTemplates[newTemplateId] = templateSQL;
                
                $('#sqlTemplate').append(
                    $('<option></option>').val(newTemplateId).text('模板：' + templateName)
                );
                
                alert('模板添加成功！');
            }
        }
    });
}); 