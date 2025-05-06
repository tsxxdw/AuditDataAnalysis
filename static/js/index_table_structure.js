// 数据库表结构管理页面JS文件(index_table_structure)
$(document).ready(function() {
    // 加载表列表
    loadTableList();
    
    // 生成表创建SQL按钮点击事件
    $('#generateTableSql').on('click', function() {
        const tableName = $('#tableName').val();
        const tableComment = $('#tableComment').val();
        
        if(!tableName) {
            alert('请输入表名');
            return;
        }
        
        // 调用后端API生成SQL
        $.ajax({
            url: '/api/table_structure/generate_table_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                tableComment: tableComment
            }),
            success: function(response) {
                if (response.success) {
                    $('#sqlContent').val(response.sql);
                } else {
                    alert(response.message || '生成SQL失败');
                }
            },
            error: function(xhr) {
                console.error('生成SQL请求失败:', xhr);
                alert('生成SQL请求失败，请查看控制台日志');
            }
        });
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
        
        // 调用后端API生成SQL
        $.ajax({
            url: '/api/table_structure/generate_index_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                fieldName: fieldName,
                operationType: operationType
            }),
            success: function(response) {
                if (response.success) {
                    $('#sqlContent').val(response.sql);
                } else {
                    alert(response.message || '生成SQL失败');
                }
            },
            error: function(xhr) {
                console.error('生成SQL请求失败:', xhr);
                alert('生成SQL请求失败，请查看控制台日志');
            }
        });
    });
    
    // 创建表按钮点击事件
    $('#createTable').on('click', function() {
        const tableName = $('#tableName').val();
        const tableComment = $('#tableComment').val();
        const excelPath = $('#excelPath').val();
        const commentRow = $('#commentRow').val();
        
        if(!tableName) {
            alert('请输入表名');
            return;
        }
        
        if(!excelPath) {
            alert('请输入Excel文件路径');
            return;
        }
        
        if(!commentRow) {
            alert('请输入注释行号');
            return;
        }
        
        // 调用后端API创建表
        $.ajax({
            url: '/api/table_structure/create_table',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                tableComment: tableComment,
                excelPath: excelPath,
                commentRow: commentRow
            }),
            success: function(response) {
                if (response.success) {
                    alert('创建表成功');
                    // 显示生成的SQL
                    $('#sqlContent').val(response.sql);
                    // 重新加载表列表
                    loadTableList();
                } else {
                    alert(response.message || '创建表失败');
                }
            },
            error: function(xhr) {
                console.error('创建表请求失败:', xhr);
                alert('创建表请求失败，请查看控制台日志');
            }
        });
    });
    
    // 创建索引按钮点击事件
    $('#createIndex').on('click', function() {
        const tableName = $('#indexTableName').val();
        const fieldName = $('#fieldName').val();
        
        if(!tableName) {
            alert('请选择表名');
            return;
        }
        
        if(!fieldName) {
            alert('请选择字段名');
            return;
        }
        
        // 调用后端API创建索引
        $.ajax({
            url: '/api/table_structure/create_index',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                fieldName: fieldName
            }),
            success: function(response) {
                if (response.success) {
                    alert('创建索引成功');
                    // 显示生成的SQL
                    $('#sqlContent').val(response.sql);
                } else {
                    alert(response.message || '创建索引失败');
                }
            },
            error: function(xhr) {
                console.error('创建索引请求失败:', xhr);
                alert('创建索引请求失败，请查看控制台日志');
            }
        });
    });
    
    // 删除索引按钮点击事件
    $('#deleteIndex').on('click', function() {
        const tableName = $('#indexTableName').val();
        const fieldName = $('#fieldName').val();
        
        if(!tableName) {
            alert('请选择表名');
            return;
        }
        
        if(!fieldName) {
            alert('请选择字段名');
            return;
        }
        
        if(!confirm(`确定要删除表 ${tableName} 中字段 ${fieldName} 的索引吗？`)) {
            return;
        }
        
        // 调用后端API删除索引
        $.ajax({
            url: '/api/table_structure/delete_index',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                fieldName: fieldName
            }),
            success: function(response) {
                if (response.success) {
                    alert('删除索引成功');
                    // 显示生成的SQL
                    $('#sqlContent').val(response.sql);
                } else {
                    alert(response.message || '删除索引失败');
                }
            },
            error: function(xhr) {
                console.error('删除索引请求失败:', xhr);
                alert('删除索引请求失败，请查看控制台日志');
            }
        });
    });
    
    // 执行SQL按钮点击事件
    $('#executeSql').on('click', function() {
        const sql = $('#sqlContent').val();
        
        if(!sql || sql.trim() === '') {
            alert('请先生成或输入SQL语句');
            return;
        }
        
        // 调用后端API执行SQL
        $.ajax({
            url: '/api/table_structure/execute_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sql: sql
            }),
            success: function(response) {
                if (response.success) {
                    if (response.is_query) {
                        alert(`查询成功，返回 ${response.row_count} 条记录`);
                        // 可以进一步处理查询结果，例如显示在表格中
                        displayQueryResults(response.data);
                    } else {
                        alert(`SQL执行成功，影响行数: ${response.affected_rows}`);
                        // 执行成功后，可能需要刷新某些数据
                        loadTableList();
                    }
                } else {
                    alert(response.message || 'SQL执行失败');
                }
            },
            error: function(xhr) {
                console.error('执行SQL请求失败:', xhr);
                alert('执行SQL请求失败，请查看控制台日志');
            }
        });
    });
    
    // 监听索引表名变化，加载字段
    $('#indexTableName').on('change', function() {
        const selectedTable = $(this).val();
        if(selectedTable) {
            loadTableFields(selectedTable);
        } else {
            // 清空字段下拉框
            $('#fieldName').empty();
            $('#fieldName').append('<option value="">请选择字段</option>');
        }
    });
    
    // 加载表列表
    function loadTableList() {
        $.ajax({
            url: '/api/table_structure/tables',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 清空表下拉框
                    $('#indexTableName').empty();
                    $('#indexTableName').append('<option value="">请选择表</option>');
                    
                    // 填充表下拉框
                    response.tables.forEach(table => {
                        $('#indexTableName').append(`<option value="${table.name}">${table.name}</option>`);
                    });
                } else {
                    console.error('获取表列表失败:', response.message);
                }
            },
            error: function(xhr) {
                console.error('获取表列表请求失败:', xhr);
            }
        });
    }
    
    // 加载表字段
    function loadTableFields(tableName) {
        $.ajax({
            url: `/api/table_structure/fields/${tableName}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 清空字段下拉框
                    $('#fieldName').empty();
                    $('#fieldName').append('<option value="">请选择字段</option>');
                    
                    // 填充字段下拉框
                    response.fields.forEach(field => {
                        $('#fieldName').append(`<option value="${field.name}">${field.name} - ${field.comment || '无注释'}</option>`);
                    });
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
    
    // 显示查询结果
    function displayQueryResults(data) {
        if (!data || data.length === 0) {
            alert('查询结果为空');
            return;
        }
        
        // 创建一个临时的结果显示区域
        let resultHtml = '<div class="query-result"><h3>查询结果</h3>';
        resultHtml += '<table class="table table-bordered table-striped"><thead><tr>';
        
        // 创建表头（简单处理，使用第一行数据的索引作为列标题）
        for (let i = 0; i < data[0].length; i++) {
            resultHtml += `<th>Column ${i+1}</th>`;
        }
        resultHtml += '</tr></thead><tbody>';
        
        // 填充数据
        data.forEach(row => {
            resultHtml += '<tr>';
            row.forEach(cell => {
                resultHtml += `<td>${cell === null ? 'NULL' : cell}</td>`;
            });
            resultHtml += '</tr>';
        });
        
        resultHtml += '</tbody></table></div>';
        
        // 显示结果
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-container';
        resultDiv.innerHTML = resultHtml;
        
        // 添加关闭按钮
        const closeBtn = document.createElement('button');
        closeBtn.className = 'btn btn-primary mt-2';
        closeBtn.innerText = '关闭结果';
        closeBtn.onclick = function() {
            document.body.removeChild(resultDiv);
        };
        resultDiv.appendChild(closeBtn);
        
        // 添加到页面
        document.body.appendChild(resultDiv);
        
        // 样式调整
        const style = document.createElement('style');
        style.textContent = `
            .result-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
                max-width: 90%;
                max-height: 80vh;
                overflow: auto;
                z-index: 1000;
            }
            .query-result {
                min-width: 400px;
            }
        `;
        document.head.appendChild(style);
    }
}); 