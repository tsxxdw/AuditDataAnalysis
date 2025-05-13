// 数据库表结构管理页面JS文件(index_table_structure)
$(document).ready(function() {
    // 初始化文件选择器
    initializeFileSelector();
    
    // 加载表列表
    loadTableList();
    
    // 加载提示词模板列表
    loadPromptTemplates();
    
    // 读取字段备注按钮点击事件
    $('#readFieldComments').on('click', function() {
        // 尝试多种方式获取Excel文件路径
        let excelPath = '';
        
        // 方式1：从隐藏input字段获取
        excelPath = $('#file-select').val();
        
        // 方式2：如果方式1没有获取到，尝试从全局组件实例获取
        if (!excelPath && window.excelDropdown) {
            excelPath = window.excelDropdown.getValue();
            
            // 如果从组件获取到了值，同步更新隐藏字段
            if (excelPath) {
                $('#file-select').val(excelPath);
                console.log('已从组件实例更新文件路径:', excelPath);
            }
        }
        
        console.log('当前选择的Excel文件路径:', excelPath);
        
        const sheetId = $('#sheet-select').val();
        const commentRow = $('#commentRow').val();
        
        if(!excelPath) {
            alert('请选择Excel文件');
            return;
        }
        
        if(!sheetId) {
            alert('请选择工作表');
            return;
        }
        
        if(!commentRow) {
            alert('请输入备注信息所在行号');
            return;
        }
        
        // 显示加载中
        $('#fieldCommentsDisplay').text('加载中...');
        
        // 添加日志信息
        console.log('发送Excel行读取请求，参数：', {
            file_path: excelPath,
            sheet_name: sheetId,
            row_index: commentRow - 1
        });
        
        // 调用API读取Excel文件中的备注行
        $.ajax({
            url: '/api/table_structure/read_excel_row',
            type: 'GET',
            data: {
                file_path: excelPath,
                sheet_name: sheetId,
                row_index: commentRow - 1  // 行号从0开始，需要减1
            },
            success: function(response) {
                if (response.success) {
                    // 将读取到的字段备注用逗号分隔显示
                    const comments = response.data.filter(item => item).join(', ');
                    $('#fieldCommentsDisplay').text(comments || '未找到字段备注');
                    
                    console.log('成功读取Excel行数据:', response.data);
                } else {
                    console.error('读取Excel行失败:', response.message);
                    $('#fieldCommentsDisplay').text('读取失败: ' + response.message);
                    alert(response.message || '读取Excel文件失败');
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('读取Excel文件请求失败:', xhr, errorMsg);
                $('#fieldCommentsDisplay').text('请求失败: ' + errorMsg);
                alert('读取Excel文件请求失败: ' + errorMsg);
            }
        });
    });
    
    // 模态对话框关闭按钮事件
    $('.close-modal').on('click', function() {
        $('#templateDetailsModal').css('display', 'none');
    });
    
    // 点击模态对话框外部关闭
    $(window).on('click', function(event) {
        if ($(event.target).is('#templateDetailsModal')) {
            $('#templateDetailsModal').css('display', 'none');
        }
    });
    
    // 生成表创建SQL按钮点击事件
    $('#generateTableSql').on('click', function() {
        const tableName = $('#tableName').val();
        const tableComment = $('#tableComment').val();
        
        if(!tableName) {
            alert('请输入表名');
            return;
        }

        // 获取Excel文件路径
        let excelPath = $('#file-select').val();
        
        // 如果从隐藏input没获取到，尝试从组件实例获取
        if (!excelPath && window.excelDropdown) {
            excelPath = window.excelDropdown.getValue();
        }

        // 获取工作表ID
        const sheetId = $('#sheet-select').val();
        
        // 获取备注信息所在行
        const commentRow = $('#commentRow').val();
        
        // 获取选择的模板ID
        let templateId = null;
        
        // 先从组件实例获取
        if (window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue();
            console.log('从组件实例获取模板ID:', templateId);
        }
        
        // 如果没有，则从隐藏select获取
        if (!templateId) {
            templateId = $('#promptTemplate').val();
            console.log('从隐藏select获取模板ID:', templateId);
        }
        
        // 验证模板ID是否存在
        if (!templateId) {
            alert('请选择一个提示词模板');
            // 高亮提示模板选择区域
            $('#templateDropdown').addClass('field-required').delay(2000).queue(function(next){
                $(this).removeClass('field-required');
                next();
            });
            return;
        }

        // 显示按钮上的加载动画
        const $button = $(this);
        const $spinner = $button.find('.spinner-border');
        $button.prop('disabled', true);
        $spinner.removeClass('d-none');
        
        // 显示中央加载动画
        $('#loadingOverlay').css('display', 'flex');
        
        // 调用后端API生成SQL
        $.ajax({
            url: '/api/table_structure/generate_table_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                tableComment: tableComment,
                excelPath: excelPath,
                sheetId: sheetId,
                commentRow: commentRow,
                templateId: templateId
            }),
            success: function(response) {
                if (response.success) {
                    $('#sqlContent').val(response.sql);
                    
                    // 如果是从LLM生成的，可以添加一些提示
                    if (response.from_llm) {
                        console.log('SQL由大语言模型生成');
                        // 可以添加一个UI提示，如临时变更按钮颜色等
                        $button.addClass('ai-generated').delay(2000).queue(function(next){
                            $(this).removeClass('ai-generated');
                            next();
                        });
                    }
                } else {
                    alert(response.message || '生成SQL失败');
                }
            },
            error: function(xhr) {
                console.error('生成SQL请求失败:', xhr);
                alert('生成SQL请求失败，请查看控制台日志');
            },
            complete: function() {
                // 隐藏按钮上的加载动画
                $button.prop('disabled', false);
                $spinner.addClass('d-none');
                
                // 隐藏中央加载动画
                $('#loadingOverlay').hide();
            }
        });
    });
    
    // 清空SQL按钮点击事件
    $('#clearSql').on('click', function() {
        $('#sqlContent').val('');
    });
    
    // 查看模板详情按钮点击事件
    $('#viewTemplateDetails').on('click', function() {
        console.log('查看模板详情点击事件触发');
        
        // 优先从组件实例获取值
        let templateId = null;
        
        // 1. 先从按钮的data属性获取
        templateId = $(this).data('template-id');
        console.log('从按钮data属性获取模板ID:', templateId);
        
        // 2. 如果没有，从组件实例获取
        if (!templateId && window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue();
            console.log('从组件实例获取模板ID:', templateId);
        }
        
        // 3. 如果仍然没有，则从隐藏select获取
        if (!templateId) {
            templateId = $('#promptTemplate').val();
            console.log('从隐藏select获取模板ID:', templateId);
        }
        
        if (!templateId) {
            console.log('未选择模板，不执行请求');
            alert('请先选择一个模板');
            return;
        }
        
        // 获取模板详情
        $.ajax({
            url: `/api/prompt_templates/${templateId}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const template = response.template;
                    let templateContent;
                    
                    try {
                        templateContent = JSON.parse(template.content);
                    } catch (e) {
                        console.error('解析模板内容失败:', e);
                        alert('模板内容格式错误');
                        return;
                    }
                    
                    // 清空旧内容
                    $('.template-name-text, .template-description-text, .system-prompt-text, .user-prompt-text').text('');
                    
                    // 显示模板名称
                    $('.template-name-text').text(template.name);
                    
                    // 显示模板描述
                    if (template.description) {
                        $('.template-description-text').text(template.description);
                    } else {
                        $('.template-description-text').text('无描述');
                    }
                    
                    // 显示系统提示词
                    if (templateContent.system) {
                        $('.system-prompt-text').text(templateContent.system);
                    } else {
                        $('.system-prompt-text').text('无系统提示词');
                    }
                    
                    // 显示用户提示词
                    if (templateContent.user) {
                        $('.user-prompt-text').text(templateContent.user);
                    } else {
                        $('.user-prompt-text').text('无用户提示词');
                    }
                    
                    // 显示模态对话框
                    $('#templateDetailsModal').css('display', 'block');
                } else {
                    alert(response.message || '获取模板详情失败');
                }
            },
            error: function(xhr) {
                console.error('获取模板详情失败:', xhr);
                alert('获取模板详情失败，请查看控制台日志');
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
        
        // 获取选择的模板ID
        let templateId = null;
        
        // 先从组件实例获取
        if (window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue();
            console.log('从组件实例获取模板ID:', templateId);
        }
        
        // 如果没有，则从隐藏select获取
        if (!templateId) {
            templateId = $('#promptTemplate').val();
            console.log('从隐藏select获取模板ID:', templateId);
        }
        
        // 验证模板ID是否存在
        if (!templateId) {
            alert('请选择一个提示词模板');
            // 高亮提示模板选择区域
            $('#templateDropdown').addClass('field-required').delay(2000).queue(function(next){
                $(this).removeClass('field-required');
                next();
            });
            return;
        }
        
        // 显示按钮上的加载动画
        const $button = $(this);
        const $spinner = $button.find('.spinner-border');
        $button.prop('disabled', true);
        $spinner.removeClass('d-none');
        
        // 显示中央加载动画
        $('#loadingOverlay').css('display', 'flex');
        
        // 调用后端API生成SQL
        $.ajax({
            url: '/api/table_structure/generate_index_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                fieldName: fieldName,
                operationType: operationType,
                templateId: templateId
            }),
            success: function(response) {
                if (response.success) {
                    $('#sqlContent').val(response.sql);
                    
                    // 如果是从LLM生成的，可以添加一些提示
                    if (response.from_llm) {
                        console.log('SQL由大语言模型生成');
                        // 可以添加一个UI提示，如临时变更按钮颜色等
                        $button.addClass('ai-generated').delay(2000).queue(function(next){
                            $(this).removeClass('ai-generated');
                            next();
                        });
                    }
                } else {
                    alert(response.message || '生成SQL失败');
                }
            },
            error: function(xhr) {
                console.error('生成SQL请求失败:', xhr);
                alert('生成SQL请求失败，请查看控制台日志');
            },
            complete: function() {
                // 隐藏按钮上的加载动画
                $button.prop('disabled', false);
                $spinner.addClass('d-none');
                
                // 隐藏中央加载动画
                $('#loadingOverlay').hide();
            }
        });
    });
    
    // 创建表按钮点击事件
    $('#createTable').on('click', function() {
        const tableName = $('#tableName').val();
        const tableComment = $('#tableComment').val();
        const excelPath = $('#file-select').val();
        const sheetId = $('#sheet-select').val();
        const commentRow = $('#commentRow').val();
        
        if(!tableName) {
            alert('请输入表名');
            return;
        }
        
        if(!excelPath) {
            alert('请选择Excel文件');
            return;
        }
        
        if(!sheetId) {
            alert('请选择工作表');
            return;
        }
        
        if(!commentRow) {
            alert('请输入备注信息所在行号');
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
                sheetId: sheetId,
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
    
    // 初始化文件选择器
    function initializeFileSelector() {
        // 获取Excel文件列表
        $.ajax({
            url: '/api/files/list',
            type: 'GET',
            success: function(data) {
                // 过滤Excel文件
                const excelFiles = data.filter(file => 
                    file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
                ).sort((a, b) => new Date(b.date) - new Date(a.date)); // 按日期降序排序
                
                // 保存文件列表供全局访问
                window.allExcelFiles = excelFiles;
                
                // 使用SearchableDropdown组件初始化Excel文件选择器
                initializeExcelFileDropdown(excelFiles);
            },
            error: function(xhr) {
                console.error('获取文件列表失败:', xhr);
            }
        });
    }
    
    // 使用SearchableDropdown组件初始化Excel文件选择器
    function initializeExcelFileDropdown(files) {
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = files.map(file => ({
            id: file.path,
            text: file.name,
            date: file.date
        }));
        
        // 创建Excel文件下拉选择器
        const excelDropdown = new SearchableDropdown({
            element: '#excelFileDropdown',
            data: dropdownData,
            valueField: 'id',
            textField: 'text',
            searchFields: ['text'],
            placeholder: '输入关键词搜索Excel文件...',
            noResultsText: '没有找到匹配的Excel文件',
            itemTemplate: (item) => `
                <div>
                    <span style="font-weight: bold;">${item.text}</span>
                    <span style="color: #777; margin-left: 10px; font-size: 0.85em;">${item.date}</span>
                </div>
            `,
            onChange: (value, item) => {
                // 设置隐藏下拉框的值
                $('#file-select').val(value);
                console.log('Excel文件已选择，路径已设置:', value);
                
                // 加载工作表
                loadExcelFileSheets(value);
            }
        });
        
        // 保存到全局变量，方便后续访问
        window.excelDropdown = excelDropdown;
    }
    
    // 加载Excel文件的工作表
    function loadExcelFileSheets(filePath) {
        if (!filePath) {
            $('#sheet-select').empty().append('<option value="" disabled selected>请先选择Excel文件</option>');
            return;
        }
        
        // 清空并显示加载中
        $('#sheet-select').empty().append('<option value="" disabled selected>加载中...</option>');
        
        // 从API获取工作表信息
        $.ajax({
            url: '/api/import/excel/sheets',
            method: 'GET',
            data: { file_path: filePath },
            dataType: 'json',
            success: function(response) {
                if (response.success && response.sheets && response.sheets.length > 0) {
                    updateSheetSelect(response.sheets);
                } else {
                    $('#sheet-select').empty().append('<option value="" disabled selected>未找到工作表</option>');
                    console.error('警告: 所选Excel文件中未找到工作表');
                }
            },
            error: function(xhr, status, error) {
                $('#sheet-select').empty().append('<option value="" disabled selected>加载失败</option>');
                console.error('错误: 加载工作表失败 - ' + (xhr.responseJSON?.error || error));
            }
        });
    }
    
    // 更新工作表下拉框
    function updateSheetSelect(sheets) {
        $('#sheet-select').empty().append('<option value="" disabled selected>请选择工作表</option>');
        
        $.each(sheets, function(index, sheet) {
            $('#sheet-select').append(
                $('<option></option>')
                    .attr('value', sheet.id)
                    .text(sheet.name)
            );
        });
        
        if (sheets.length > 0) {
            console.log('成功加载 ' + sheets.length + ' 个工作表');
        }
    }
    
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
                        // 构建表显示名称，包含备注信息
                        var displayName = table.name;
                        if (table.comment && table.comment.trim() !== '') {
                            displayName += ' (' + table.comment + ')';
                        }
                        
                        $('#indexTableName').append(
                            $('<option></option>')
                                .attr('value', table.name)
                                .text(displayName)
                        );
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
    
    // 加载提示词模板列表
    function loadPromptTemplates() {
        // 获取所有模板数据
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 使用SearchableDropdown组件初始化模板选择器
                    initializeTemplateDropdown(response.templates);
                } else {
                    console.error('加载提示词模板失败:', response.message);
                }
            },
            error: function(xhr) {
                console.error('请求提示词模板列表失败:', xhr);
            }
        });
    }
    
    // 使用SearchableDropdown组件初始化模板选择器
    function initializeTemplateDropdown(templates) {
        // 保存模板数据供全局访问
        window.allTemplates = templates;
        
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = templates.map(template => ({
            id: template.id,
            text: template.name,
            description: template.description || ''
        }));
        
        // 创建模板选择下拉框
        const templateDropdown = new SearchableDropdown({
            element: '#templateDropdown',
            data: dropdownData,
            valueField: 'id',
            textField: 'text',
            searchFields: ['text', 'description'],
            placeholder: '输入关键词搜索模板...',
            noResultsText: '没有找到匹配的模板',
            itemTemplate: (item) => `
                <div>
                    <span style="font-weight: bold;">${item.text}</span>
                    ${item.description ? `<span style="color: #777; display: block; font-size: 0.85em;">${item.description}</span>` : ''}
                </div>
            `,
            onChange: (value, item) => {
                // 设置隐藏下拉框的值
                $('#promptTemplate').val(value);
                console.log('已设置隐藏select值:', value, '元素当前值:', $('#promptTemplate').val());
                
                // 保存ID到按钮的data属性中
                $('#viewTemplateDetails').data('template-id', value);
                
                // 启用查看详情按钮
                $('#viewTemplateDetails').prop('disabled', false);
            }
        });
        
        // 保存实例以便后续访问
        window.templateDropdown = templateDropdown;
    }
}); 