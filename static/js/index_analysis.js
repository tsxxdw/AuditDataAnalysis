// 数据分析页面JS文件(index_analysis)
$(document).ready(function() {
    // 全局变量
    let currentTableId = 1;  // 当前表ID计数器
    let currentFieldsTable = null;  // 当前操作的字段表ID
    let selectedFields = {};  // 存储已选择的字段 {tableId: [{field}, {field}...]}
    
    // 初始化页面
    initPage();
    
    // 初始化表下拉选择器
    loadTableList();
    
    // 加载提示词模板列表
    loadPromptTemplates();
    
    // 添加表按钮点击事件
    $('#addTable').on('click', function() {
        addTableSelection();
    });
    
    // 清空表选择按钮点击事件
    $('#clearTables').on('click', function() {
        if (confirm('确定要清空所有表选择吗？')) {
            // 保留第一个表选择，清空其他所有表选择
            $('.table-selection-item:not(:first)').remove();
            
            // 重置第一个表选择
            $('#table-select-1').val('');
            $('#selected-fields-1').empty();
            
            // 重置全局变量
            currentTableId = 1;
            selectedFields = {};
        }
    });
    
    // 监听表选择变化事件（使用事件委托）
    $(document).on('change', '.table-select', function() {
        const tableId = $(this).attr('id').split('-')[2];
        // 清空该表对应的已选字段
        $(`#selected-fields-${tableId}`).empty();
        delete selectedFields[tableId];
    });
    
    // 字段选择按钮点击事件（使用事件委托）
    $(document).on('click', '.btn-add-fields', function() {
        const tableId = $(this).data('table-id');
        const tableName = $(`#table-select-${tableId}`).val();
        
        if (!tableName) {
            alert('请先选择表');
            return;
        }
        
        // 设置当前操作的表ID
        currentFieldsTable = tableId;
        
        // 加载字段列表
        loadTableFields(tableName);
        
        // 显示字段选择模态框
        $('#fieldSelectionModal').css('display', 'block');
    });
    
    // 关闭字段选择模态框
    $('.close-modal-fields').on('click', function() {
        $('#fieldSelectionModal').css('display', 'none');
    });
    
    // 点击模态框外部关闭
    $(window).on('click', function(event) {
        if ($(event.target).is('#fieldSelectionModal')) {
            $('#fieldSelectionModal').css('display', 'none');
        }
        if ($(event.target).is('#templateDetailsModal')) {
            $('#templateDetailsModal').css('display', 'none');
        }
    });
    
    // 字段搜索功能
    $('#fieldSearchInput').on('input', function() {
        const searchText = $(this).val().toLowerCase();
        
        $('.field-item').each(function() {
            const fieldName = $(this).find('.field-item-name').text().toLowerCase();
            const fieldComment = $(this).find('.field-item-comment').text().toLowerCase();
            
            if (fieldName.includes(searchText) || fieldComment.includes(searchText)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // 全选字段按钮
    $('#selectAllFields').on('click', function() {
        $('.field-item input[type="checkbox"]').prop('checked', true);
    });
    
    // 取消全选按钮
    $('#deselectAllFields').on('click', function() {
        $('.field-item input[type="checkbox"]').prop('checked', false);
    });
    
    // 确认字段选择按钮
    $('#confirmFieldSelection').on('click', function() {
        // 获取已选中的字段
        const checkedFields = [];
        
        $('.field-item input[type="checkbox"]:checked').each(function() {
            const $fieldItem = $(this).closest('.field-item');
            checkedFields.push({
                name: $fieldItem.find('.field-item-name').text(),
                type: $fieldItem.find('.field-item-type').text(),
                comment: $fieldItem.find('.field-item-comment').text()
            });
        });
        
        // 更新selectedFields全局变量
        selectedFields[currentFieldsTable] = checkedFields;
        
        // 更新已选字段显示
        updateSelectedFieldsDisplay(currentFieldsTable, checkedFields);
        
        // 关闭模态框
        $('#fieldSelectionModal').css('display', 'none');
    });
    
    // 移除已选字段事件（使用事件委托）
    $(document).on('click', '.remove-field', function() {
        const tableId = $(this).data('table-id');
        const fieldIndex = $(this).data('field-index');
        
        // 从数组中移除
        if (selectedFields[tableId] && selectedFields[tableId][fieldIndex]) {
            selectedFields[tableId].splice(fieldIndex, 1);
            
            // 重新渲染已选字段
            updateSelectedFieldsDisplay(tableId, selectedFields[tableId]);
        }
    });
    
    // 查看模板详情按钮点击事件
    $('#viewTemplateDetails').on('click', function() {
        let templateId = null;
        
        // 从组件实例获取
        if (window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue();
        }
        
        // 如果没获取到，从隐藏select获取
        if (!templateId) {
            templateId = $('#promptTemplate').val();
        }
        
        if (!templateId) {
            alert('请先选择一个模板');
            return;
        }
        
        // 调用API获取模板详情
        $.ajax({
            url: '/api/prompt_templates/detail',
            type: 'GET',
            data: { id: templateId },
            success: function(response) {
                if (response.success) {
                    // 解析模板内容JSON
                    let promptContent = {};
                    try {
                        if (typeof response.data.content === 'string') {
                            promptContent = JSON.parse(response.data.content);
                        } else if (typeof response.data.content === 'object') {
                            promptContent = response.data.content;
                        }
                    } catch (e) {
                        console.error('解析模板内容失败:', e);
                        promptContent = {};
                    }
                    
                    // 填充模板详情
                    $('.template-name-text').text(response.data.name || '');
                    $('.template-description-text').text(response.data.description || '');
                    $('.system-prompt-text').text(promptContent.system || '');
                    $('.user-prompt-text').text(promptContent.user || '');
                    
                    // 显示模态框
                    $('#templateDetailsModal').css('display', 'block');
                } else {
                    alert(response.message || '获取模板详情失败');
                }
            },
            error: function(xhr) {
                console.error('获取模板详情请求失败:', xhr);
                alert('获取模板详情请求失败');
            }
        });
    });
    
    // 生成SQL按钮点击事件
    $('#generateSQL').on('click', function() {
        // 检查是否已选择表和字段
        if (Object.keys(selectedFields).length === 0) {
            alert('请先选择至少一个表和字段');
            return;
        }
        
        // 获取模板ID
        let templateId = null;
        if (window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue();
        }
        if (!templateId) {
            templateId = $('#promptTemplate').val();
        }
        
        if (!templateId) {
            alert('请选择提示词模板');
            return;
        }
        
        // 构建请求数据
        const requestData = {
            template_id: templateId,
            tables: []
        };
        
        // 遍历所有已选表和字段
        for (const tableId in selectedFields) {
            if (selectedFields[tableId] && selectedFields[tableId].length > 0) {
                const tableName = $(`#table-select-${tableId}`).val();
                requestData.tables.push({
                    name: tableName,
                    fields: selectedFields[tableId]
                });
            }
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
            url: '/api/analysis/generate_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
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
    $('#clearSQL').on('click', function() {
        $('#sqlContent').val('');
        
        // 隐藏查询结果区域
        $('#queryResultsContainer').hide();
    });
    
    // 执行SQL按钮点击事件
    $('#executeSQL').on('click', function() {
        const sql = $('#sqlContent').val();
        
        if (!sql || sql.trim() === '') {
            alert('请先生成SQL语句');
            return;
        }
        
        // 显示加载动画
        $('#loadingOverlay').css('display', 'flex');
        
        // 调用后端API执行SQL
        $.ajax({
            url: '/api/analysis/execute_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sql: sql
            }),
            success: function(response) {
                if (response.success) {
                    // 显示查询结果
                    displayQueryResults(response.data);
                } else {
                    alert(response.message || '执行SQL失败');
                }
            },
            error: function(xhr) {
                console.error('执行SQL请求失败:', xhr);
                alert('执行SQL请求失败，请查看控制台日志');
            },
            complete: function() {
                // 隐藏加载动画
                $('#loadingOverlay').hide();
            }
        });
    });
    
    // 初始化页面
    function initPage() {
        // 初始设置模板详情按钮为禁用
        $('#viewTemplateDetails').prop('disabled', true);
        
        // 隐藏查询结果区域
        $('#queryResultsContainer').hide();
    }
    
    // 添加新的表选择行
    function addTableSelection() {
        currentTableId++;
        
        const newTableSelection = `
            <div class="table-selection-item">
                <div class="form-group">
                    <label for="table-select-${currentTableId}">选择表：</label>
                    <select id="table-select-${currentTableId}" class="form-control table-select">
                        <option value="">请选择表</option>
                        <!-- 表选项将动态加载 -->
                    </select>
                    <button type="button" class="btn btn-sm btn-info btn-add-fields" data-table-id="${currentTableId}">选择字段</button>
                </div>
                
                <div class="selected-fields-container" id="selected-fields-${currentTableId}">
                    <!-- 选择的字段将显示在这里 -->
                </div>
            </div>
        `;
        
        $('#tableSelectionContainer').append(newTableSelection);
        
        // 加载新添加的表下拉框选项
        loadTablesForSelect(`#table-select-${currentTableId}`);
    }
    
    // 加载表列表
    function loadTableList() {
        // 调用API获取表列表
        $.ajax({
            url: '/api/table_structure/tables',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 加载第一个表选择器的选项
                    populateTableSelect('#table-select-1', response.tables);
                } else {
                    console.error('获取表列表失败:', response.message);
                    alert(response.message || '获取表列表失败');
                }
            },
            error: function(xhr) {
                console.error('获取表列表请求失败:', xhr);
                alert('获取表列表请求失败');
            }
        });
    }
    
    // 加载表的选择器选项
    function loadTablesForSelect(selectId) {
        // 调用API获取表列表
        $.ajax({
            url: '/api/table_structure/tables',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 加载表选择器的选项
                    populateTableSelect(selectId, response.tables);
                } else {
                    console.error('获取表列表失败:', response.message);
                    alert(response.message || '获取表列表失败');
                }
            },
            error: function(xhr) {
                console.error('获取表列表请求失败:', xhr);
                alert('获取表列表请求失败');
            }
        });
    }
    
    // 填充表下拉选择框
    function populateTableSelect(selectId, tables) {
        const $select = $(selectId);
        // 保留第一个默认选项
        $select.find('option:not(:first)').remove();
        
        // 添加新选项
        tables.forEach(table => {
            $select.append(`<option value="${table.name}">${table.name} (${table.comment || '无备注'})</option>`);
        });
    }
    
    // 加载表的字段列表
    function loadTableFields(tableName) {
        // 清空字段列表和搜索框
        $('#fieldList').empty();
        $('#fieldSearchInput').val('');
        
        // 显示加载提示
        $('#fieldList').html('<div class="loading-fields">加载字段中...</div>');
        
        // 调用API获取字段列表
        $.ajax({
            url: `/api/table_structure/fields/${tableName}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 清空字段列表
                    $('#fieldList').empty();
                    
                    // 填充字段列表
                    if (response.fields && response.fields.length > 0) {
                        response.fields.forEach((field, index) => {
                            const isChecked = isFieldSelected(currentFieldsTable, field.name) ? 'checked' : '';
                            
                            const fieldItem = `
                                <div class="field-item">
                                    <input type="checkbox" id="field-${index}" ${isChecked}>
                                    <span class="field-item-name">${field.name}</span>
                                    <span class="field-item-type">${field.type}</span>
                                    <span class="field-item-comment">${field.comment || ''}</span>
                                </div>
                            `;
                            
                            $('#fieldList').append(fieldItem);
                        });
                    } else {
                        $('#fieldList').html('<div class="no-fields">该表没有字段</div>');
                    }
                } else {
                    console.error('获取字段列表失败:', response.message);
                    $('#fieldList').html(`<div class="load-error">加载失败: ${response.message || '未知错误'}</div>`);
                }
            },
            error: function(xhr) {
                console.error('获取字段列表请求失败:', xhr);
                $('#fieldList').html('<div class="load-error">请求失败，请重试</div>');
            }
        });
    }
    
    // 检查字段是否已被选中
    function isFieldSelected(tableId, fieldName) {
        if (!selectedFields[tableId]) return false;
        
        return selectedFields[tableId].some(field => field.name === fieldName);
    }
    
    // 更新已选字段的显示
    function updateSelectedFieldsDisplay(tableId, fields) {
        const $container = $(`#selected-fields-${tableId}`);
        $container.empty();
        
        if (fields && fields.length > 0) {
            fields.forEach((field, index) => {
                const fieldTag = `
                    <span class="selected-field-tag">
                        ${field.name}
                        <span class="remove-field" data-table-id="${tableId}" data-field-index="${index}">×</span>
                    </span>
                `;
                
                $container.append(fieldTag);
            });
        } else {
            $container.html('<div class="no-fields-selected">未选择字段</div>');
        }
    }
    
    // 加载提示词模板列表
    function loadPromptTemplates() {
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    initializeTemplateDropdown(response.templates);
                } else {
                    console.error('获取模板列表失败:', response.message);
                    alert(response.message || '获取模板列表失败');
                }
            },
            error: function(xhr) {
                console.error('获取模板列表请求失败:', xhr);
                alert('获取模板列表请求失败');
            }
        });
    }
    
    // 初始化模板下拉组件
    function initializeTemplateDropdown(templates) {
        // 清空和准备select元素
        const $select = $('#promptTemplate');
        $select.find('option:not(:first)').remove();
        
        // 保存模板数据供全局访问
        window.allTemplates = templates;
        
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = templates.map(template => ({
            id: template.id,
            text: template.name,
            description: template.description || '无描述'
        }));
        
        // 添加选项到select
        templates.forEach(template => {
            $select.append(`<option value="${template.id}">${template.name}</option>`);
        });
        
        try {
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
                    
                    // 启用查看详情按钮
                    $('#viewTemplateDetails').prop('disabled', false);
                    // 存储模板ID到按钮上，方便后续使用
                    $('#viewTemplateDetails').data('template-id', value);
                }
            });
            
            // 保存实例以便后续访问
            window.templateDropdown = templateDropdown;
        } catch (e) {
            console.error('初始化SearchableDropdown组件失败:', e);
        }
    }
    
    // 显示查询结果
    function displayQueryResults(data) {
        const $container = $('#queryResults');
        $container.empty();
        
        if (!data || !data.columns || !data.rows) {
            $container.html('<div class="no-results">无查询结果</div>');
            $('#queryResultsContainer').show();
            return;
        }
        
        // 创建表格
        let tableHtml = '<table class="result-table">';
        
        // 表头
        tableHtml += '<thead><tr>';
        data.columns.forEach(column => {
            tableHtml += `<th>${column}</th>`;
        });
        tableHtml += '</tr></thead>';
        
        // 表体
        tableHtml += '<tbody>';
        if (data.rows.length > 0) {
            data.rows.forEach(row => {
                tableHtml += '<tr>';
                row.forEach(cell => {
                    tableHtml += `<td>${cell !== null ? cell : 'NULL'}</td>`;
                });
                tableHtml += '</tr>';
            });
        } else {
            // 空结果
            tableHtml += `<tr><td colspan="${data.columns.length}" class="no-data">无数据</td></tr>`;
        }
        tableHtml += '</tbody></table>';
        
        // 显示结果
        $container.html(tableHtml);
        $('#queryResultsContainer').show();
    }
}); 