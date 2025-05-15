// 数据修复页面JS文件(index_repair)
$(document).ready(function() {
    // 加载表列表
    loadTableList();
    
    // 加载提示词模板列表
    loadPromptTemplates();
    
    // 监听表名选择变化
    $('#tableName').on('change', function() {
        const selectedTable = $(this).val();
        if(selectedTable) {
            // 加载表字段（同时更新参考字段和目标字段）
            loadTableFields(selectedTable);
        } else {
            // 清空参考字段下拉框
            $('#originalField').empty().append('<option value="">请选择参考字段</option>');
            // 清空目标字段下拉框
            $('#newField').empty().append('<option value="">请选择目标字段</option>');
        }
    });
    
    // 监听参考字段选择变化
    $('#originalField').on('change', function() {
        // 不需要任何处理，目标字段已经在选择表时加载
    });
    
    // 监听操作类型选择变化
    $('#operationType').on('change', function() {
        // 不需要处理，因为字段类型选项已移除
    });
    
    // 模板详情按钮点击事件
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
                    console.error('获取模板详情失败:', response.message);
                    alert(response.message || '获取模板详情失败');
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('获取模板详情请求失败:', xhr, errorMsg);
                alert('获取模板详情请求失败: ' + errorMsg);
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
    
    // 生成SQL按钮点击事件
    $('#generateSql').on('click', function() {
        const tableName = $('#tableName').val();
        const originalField = $('#originalField').val();
        const newField = $('#newField').val();
        const operationType = $('#operationType').val();
        
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
        
        // 验证必填项
        if(!tableName || !originalField) {
            alert('请至少选择表名和参考字段');
            return;
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
        
        // 显示中央加载动画（如果存在）
        if ($('#loadingOverlay').length) {
            $('#loadingOverlay').css('display', 'flex');
        }
        
        // 使用模板调用API生成SQL
        $.ajax({
            url: '/api/repair/generate_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                table_name: tableName,
                reference_field: originalField,
                target_field: newField || '',
                operation_type: operationType || '',
                template_id: templateId
            }),
            success: function(response) {
                if (response.success) {
                    // 显示生成的SQL
                    $('#sqlContent').val(response.sql);
                    
                    // 如果是从大模型生成的，显示信息
                    if (response.from_llm) {
                        console.log('SQL由大模型生成');
                        // 添加一个UI提示，如临时变更按钮颜色等
                        $button.addClass('ai-generated').delay(2000).queue(function(next){
                            $(this).removeClass('ai-generated');
                            next();
                        });
                    } else {
                        console.log('SQL由系统默认逻辑生成');
                    }
                } else {
                    alert('生成SQL失败: ' + (response.message || '未知错误'));
                    console.error('生成SQL失败:', response.message);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('生成SQL请求失败:', xhr, errorMsg);
                alert('生成SQL请求失败: ' + errorMsg);
                
                // 如果API调用失败，使用本地逻辑生成基本SQL
                generateLocalSql(tableName, originalField, newField, operationType);
            },
            complete: function() {
                // 恢复按钮状态
                $button.prop('disabled', false);
                $spinner.addClass('d-none');
                
                // 隐藏中央加载动画（如果存在）
                if ($('#loadingOverlay').length) {
                    $('#loadingOverlay').hide();
                }
            }
        });
    });
    
    // 备用的本地SQL生成函数
    function generateLocalSql(tableName, originalField, newField, operationType) {
        let sql = '';
        
        if(operationType === 'repair_date') {
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
        else {
            // 默认生成一个查询sql
            sql = `SELECT * FROM ${tableName} WHERE ${originalField} IS NOT NULL LIMIT 10;`;
        }
        
        // 显示生成的SQL
        $('#sqlContent').val(sql);
    }
    
    // 执行SQL按钮点击事件
    $('#executeSql').on('click', function() {
        const sql = $('#sqlContent').val();
        
        if(!sql || sql.trim() === '') {
            alert('请先生成SQL语句');
            return;
        }
        
        // 显示按钮上的加载动画
        const $button = $(this);
        $button.prop('disabled', true);
        
        // 调用API执行SQL
        $.ajax({
            url: '/api/repair/execute_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sql: sql
            }),
            success: function(response) {
                if (response.success) {
                    // 清空结果区域
                    $('#resultContainer').empty();
                    
                    if (response.is_query) {
                        // 查询类语句的结果显示
                        displayQueryResults(response);
                    } else {
                        // 非查询类语句的结果显示
                        displayNonQueryResults(response);
                    }
                } else {
                    alert('执行SQL失败: ' + (response.message || '未知错误'));
                    $('#resultContainer').html(`
                        <div class="validation-error">
                            <h3>执行错误</h3>
                            <p>${response.message || '发生未知错误'}</p>
                        </div>
                    `);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('执行SQL请求失败:', xhr, errorMsg);
                alert('执行SQL请求失败: ' + errorMsg);
                $('#resultContainer').html(`
                    <div class="validation-error">
                        <h3>执行错误</h3>
                        <p>${errorMsg}</p>
                    </div>
                `);
            },
            complete: function() {
                // 恢复按钮状态
                $button.prop('disabled', false);
            }
        });
    });
    
    // 显示查询类语句的结果
    function displayQueryResults(response) {
        const headers = response.headers || [];
        const rows = response.rows || [];
        const rowCount = response.row_count || 0;
        
        let html = `
            <div class="validation-summary">
                <h3>查询结果</h3>
                <p>返回了 ${rowCount} 条记录</p>
            </div>
        `;
        
        // 如果有数据，显示表格
        if (rowCount > 0) {
            html += `
                <div class="validation-details">
                    <h3>数据详情</h3>
                    <div class="table-responsive">
                        <table class="validation-table">
                            <thead>
                                <tr>
            `;
            
            // 表头
            headers.forEach(header => {
                html += `<th>${header}</th>`;
            });
            
            html += `
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            // 表格数据
            rows.forEach(row => {
                html += `<tr>`;
                row.forEach(cell => {
                    html += `<td>${cell !== null ? cell : '<em>NULL</em>'}</td>`;
                });
                html += `</tr>`;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } else {
            html += `<p>查询没有返回任何记录</p>`;
        }
        
        $('#resultContainer').html(html);
    }
    
    // 显示非查询类语句的结果
    function displayNonQueryResults(response) {
        const affectedRows = response.affected_rows || 0;
        
        let html = `
            <div class="validation-summary">
                <h3>执行结果</h3>
                <p>操作成功完成，影响了 ${affectedRows} 行记录</p>
            </div>
        `;
        
        $('#resultContainer').html(html);
    }
    
    // 加载表列表的函数
    function loadTableList() {
        // 使用通用函数加载表列表
        loadDatabaseTables('#tableName', function(tables) {
            if (!tables || tables.length === 0) {
                // 如果没有表或加载失败，添加默认表
                addDefaultTables();
            }
        });
    }
    
    // 加载提示词模板列表
    function loadPromptTemplates() {
        // 调用API获取提示词模板列表
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success && response.templates) {
                    initializeTemplateDropdown(response.templates);
                } else {
                    console.error('获取提示词模板列表失败:', response.message);
                }
            },
            error: function(xhr) {
                console.error('获取提示词模板请求失败:', xhr);
            }
        });
    }
    
    // 初始化提示词模板下拉框
    function initializeTemplateDropdown(templates) {
        // 准备模板数据
        const templateOptions = templates.map(template => ({
            id: template.id,
            text: template.name,
            description: template.description || '无描述'
        }));
        
        // 如果存在SearchableDropdown组件
        if(window.SearchableDropdown) {
            // 初始化模板下拉框
            window.templateDropdown = new SearchableDropdown({
                element: '#templateDropdown',
                data: templateOptions,
                valueField: 'id',
                textField: 'text',
                searchFields: ['text', 'description'],
                placeholder: '请选择提示词模板',
                noResultsText: '没有找到匹配的模板',
                itemTemplate: (item) => `
                    <div>
                        <span style="font-weight: bold;">${item.text}</span>
                        ${item.description ? `<span style="color: #777; display: block; font-size: 0.85em;">${item.description}</span>` : ''}
                    </div>
                `,
                onChange: function(value, item) {
                    // 更新隐藏的select值
                    $('#promptTemplate').val(value);
                    
                    // 设置查看详情按钮上的data属性，并启用按钮
                    $('#viewTemplateDetails').data('template-id', value);
                    $('#viewTemplateDetails').prop('disabled', !value);
                }
            });
        } else {
            console.error('SearchableDropdown组件未找到');
            
            // 如果无法使用组件，则回退到标准select
            const $select = $('#promptTemplate');
            $select.empty().append('<option value="">请选择提示词模板</option>').show();
            
            templates.forEach(template => {
                $select.append(`<option value="${template.id}">${template.name}</option>`);
            });
            
            // 为标准select添加change事件
            $select.on('change', function() {
                const value = $(this).val();
                $('#viewTemplateDetails').data('template-id', value);
                $('#viewTemplateDetails').prop('disabled', !value);
            });
        }
    }
    
    // 添加默认表选项的函数
    function addDefaultTables() {
        const defaultTables = [
            {name: 'table1', comment: '用户表'},
            {name: 'table2', comment: '订单表'},
            {name: 'table3', comment: '产品表'}
        ];
        
        defaultTables.forEach(function(table) {
            var displayName = table.name;
            if (table.comment) {
                displayName += ' (' + table.comment + ')';
            }
            
            $('#tableName').append(
                $('<option></option>')
                    .attr('value', table.name)
                    .text(displayName)
            );
        });
    }
    
    // 加载表字段的函数 - 同时填充参考字段和目标字段下拉框
    function loadTableFields(tableName) {
        // 清空两个字段下拉框并添加提示选项
        $('#originalField').empty().append('<option value="">请选择参考字段</option>');
        $('#newField').empty().append('<option value="">请选择目标字段</option>');
        
        // 使用自定义回调处理两个下拉框的更新
        loadDatabaseTableFields(tableName, null, function(fields) {
            if (fields && fields.length > 0) {
                // 填充两个字段下拉框
                fields.forEach(field => {
                    const optionText = `${field.name} - ${field.comment || '无注释'}`;
                    
                    // 添加到参考字段下拉框
                    $('#originalField').append(
                        $('<option></option>')
                            .attr('value', field.name)
                            .text(optionText)
                    );
                    
                    // 添加到目标字段下拉框
                    $('#newField').append(
                        $('<option></option>')
                            .attr('value', field.name)
                            .text(optionText)
                    );
                });
            } else {
                // 添加备用字段
                addDefaultFields(tableName);
            }
        });
    }
    
    // 添加默认字段选项的函数 - 同时填充参考字段和目标字段下拉框
    function addDefaultFields(tableName) {
        // 根据表名准备默认字段数据
        let defaultFields = [];
        
        if(tableName === 'table1') {
            defaultFields = [
                {name: 'id', comment: 'ID'},
                {name: 'name', comment: '姓名'},
                {name: 'id_card', comment: '身份证号'},
                {name: 'birth_date', comment: '出生日期'},
                {name: 'create_time', comment: '创建时间'}
            ];
        } else if(tableName === 'table2') {
            defaultFields = [
                {name: 'order_id', comment: '订单ID'},
                {name: 'customer_id', comment: '客户ID'},
                {name: 'order_date', comment: '下单日期'},
                {name: 'ship_date', comment: '发货日期'},
                {name: 'status', comment: '订单状态'}
            ];
        } else if(tableName === 'table3') {
            defaultFields = [
                {name: 'product_id', comment: '产品ID'},
                {name: 'product_name', comment: '产品名称'},
                {name: 'launch_date', comment: '上市日期'},
                {name: 'producer_code', comment: '生产商代码'},
                {name: 'price', comment: '价格'}
            ];
        }
        
        // 添加默认字段选项到两个下拉框
        defaultFields.forEach(field => {
            const optionText = `${field.name} - ${field.comment || '无注释'}`;
            
            // 添加到参考字段下拉框
            $('#originalField').append(
                $('<option></option>')
                    .attr('value', field.name)
                    .text(optionText)
            );
            
            // 添加到目标字段下拉框
            $('#newField').append(
                $('<option></option>')
                    .attr('value', field.name)
                    .text(optionText)
            );
        });
    }
}); 