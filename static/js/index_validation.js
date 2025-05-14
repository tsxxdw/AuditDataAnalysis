// 数据校验页面JS文件(index_validation)
$(document).ready(function() {
    // 加载表列表
    loadTableList();
    
    // 加载提示词模板列表
    loadPromptTemplates();

    // 监听表名选择变化
    $('#tableName').on('change', function() {
        const selectedTable = $(this).val();
        if(selectedTable) {
            // 加载表字段
            loadTableFields(selectedTable);
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
        
        // 调用API生成SQL
        $.ajax({
            url: '/api/validation/generate_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                fieldName: fieldName,
                validationType: validationType,
                templateId: templateId
            }),
            success: function(response) {
                if (response.success) {
        // 显示生成的SQL
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
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('生成SQL请求失败:', xhr, errorMsg);
                alert('生成SQL请求失败: ' + errorMsg);
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
        
        // 调用API执行SQL
        $.ajax({
            url: '/api/validation/execute_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sql: sql
            }),
            success: function(response) {
                // 隐藏提示文字
            $('.empty-result').hide();
            
                if (response.success) {
                    const results = response.results;
            const tableName = $('#tableName').val();
            const fieldName = $('#fieldName').val();
            const validationType = $('#validationType').val();
            
                    // 生成校验结果HTML
            let resultsHtml = '<div class="validation-summary">';
            resultsHtml += '<h3>校验完成</h3>';
            resultsHtml += '<p>表名: ' + tableName + '</p>';
            resultsHtml += '<p>字段名: ' + fieldName + '</p>';
            resultsHtml += '<p>校验类型: ' + (validationType === 'idcard' ? '身份证校验' : '日期格式错误校验') + '</p>';
                    resultsHtml += '<p>校验时间: ' + (results.execution_time || new Date().toLocaleString()) + '</p>';
            resultsHtml += '</div>';
            
            resultsHtml += '<div class="validation-details">';
            resultsHtml += '<h3>校验详情</h3>';
            
                    // 如果有详情数据
                    if (results.details && results.details.length > 0) {
                resultsHtml += '<table class="validation-table">';
                resultsHtml += '<thead><tr><th>错误类型</th><th>记录数</th><th>错误率</th><th>示例值</th></tr></thead>';
                resultsHtml += '<tbody>';
                        
                        results.details.forEach(function(detail) {
                            resultsHtml += '<tr>';
                            resultsHtml += '<td>' + detail.error_type + '</td>';
                            resultsHtml += '<td>' + detail.count + '</td>';
                            resultsHtml += '<td>' + detail.error_rate + '</td>';
                            resultsHtml += '<td>' + detail.examples + '</td>';
                            resultsHtml += '</tr>';
                        });
                        
                resultsHtml += '</tbody></table>';
                    } else {
                        resultsHtml += '<p>未发现错误数据</p>';
            }
            
            resultsHtml += '</div>';
            
            // 显示校验结果
            $('.validation-results').html(resultsHtml).show();
                } else {
                    $('.empty-result').text(response.message || '执行SQL失败').show();
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('执行SQL请求失败:', xhr, errorMsg);
                $('.empty-result').text('执行SQL请求失败: ' + errorMsg).show();
            }
        });
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
    
    // 加载表列表的函数
    function loadTableList() {
        // 清空下拉框并添加提示选项
        $('#tableName').empty().append('<option value="">请选择表</option>');
        
        // 调用API获取表列表
        $.ajax({
            url: '/api/table_structure/tables',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 填充表下拉框
                    response.tables.forEach(table => {
                        // 构建表显示名称，包含备注信息
                        var displayName = table.name;
                        if (table.comment && table.comment.trim() !== '') {
                            displayName += ' (' + table.comment + ')';
                        }
                        
                        $('#tableName').append(
                            $('<option></option>')
                                .attr('value', table.name)
                                .text(displayName)
                        );
                    });
                } else {
                    console.error('获取表列表失败:', response.message);
                    // 添加备用表
                    addDefaultTables();
                }
            },
            error: function(xhr) {
                console.error('获取表列表请求失败:', xhr);
                // 添加备用表
                addDefaultTables();
            }
        });
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
    
    // 加载表字段的函数
    function loadTableFields(tableName) {
        // 清空字段下拉框并添加提示选项
        $('#fieldName').empty().append('<option value="">请选择字段</option>');
        
        // 调用API获取表字段
        $.ajax({
            url: `/api/table_structure/fields/${tableName}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 填充字段下拉框
                    response.fields.forEach(field => {
                        $('#fieldName').append(`<option value="${field.name}">${field.name} - ${field.comment || '无注释'}</option>`);
                    });
                } else {
                    console.error('获取表字段失败:', response.message);
                    // 添加备用字段
                    addDefaultFields(tableName);
                }
            },
            error: function(xhr) {
                console.error(`获取表 ${tableName} 字段失败:`, xhr);
                // 添加备用字段
                addDefaultFields(tableName);
            }
        });
    }
    
    // 添加默认字段选项的函数
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
        
        // 添加默认字段选项
        defaultFields.forEach(field => {
            $('#fieldName').append(`<option value="${field.name}">${field.name} - ${field.comment || '无注释'}</option>`);
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
}); 