// 数据校验页面JS文件(index_validation)
$(document).ready(function() {
    // 确保加载动画是隐藏的
    $('#loadingOverlay').hide();
    
    // 加载表列表
    loadTableList();
    
    // 加载提示词模板列表
    // loadPromptTemplates();

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
    
    // 配置SQL执行区域组件
    if (window.sqlExecuteArea) {
        // 确保使用通用API
        window.sqlExecuteArea.options.apiEndpoint = '/api/common/execute_sql';
        
        // 覆盖生成SQL按钮的点击处理
        window.sqlExecuteArea.options.onGenerateSQL = function(e) {
            // 直接调用生成SQL的逻辑函数
            generateSqlLogic();
        };
        
        // 覆盖SQL执行成功的回调
        window.sqlExecuteArea.options.onSuccess = function(response) {
            console.log('SQL执行成功:', response);
            
            // 不再处理校验结果显示
            if (response.error_occurred) {
                alert('部分SQL执行成功，但有错误发生');
            } else {
                console.log('SQL执行成功:', response);
            }
        };
        
        // 覆盖SQL执行错误的回调
        window.sqlExecuteArea.options.onError = function(error) {
            console.error('SQL执行失败:', error);
            alert('执行SQL失败: ' + (error.message || '未知错误'));
        };
    }
    
    // 生成SQL按钮点击事件
    $('#generateSql').on('click', function() {
        generateSqlLogic();
    });
    
    // 抽取生成SQL的逻辑到单独的函数中
    function generateSqlLogic() {
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
        
        if (window.templatePromptsComponent) {
            templateId = window.templatePromptsComponent.getSelectedTemplateId();
        } else {
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
        const $button = $('#generateSql');
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
                    // 使用SQL执行区域组件设置SQL
                    if (window.sqlExecuteArea) {
                        window.sqlExecuteArea.setSQL(response.sql);
                    } else {
                        $('#sqlContent').val(response.sql);
                    }
                    
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
    }
    
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
        // 使用通用函数加载表列表
        loadDatabaseTables('#tableName', function(tables) {
            // 加载成功后的回调，如果需要可以在这里添加自定义逻辑
            console.log('成功加载了', tables.length, '个表');
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
        // 使用通用函数加载表字段
        loadDatabaseTableFields(tableName, '#fieldName', function(fields) {
            // 加载成功后的回调，如果需要可以在这里添加自定义逻辑
            console.log('成功加载了', fields.length, '个字段');
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
    // function loadPromptTemplates() {...}
    
    // 初始化提示词模板下拉框
    // function initializeTemplateDropdown(templates) {...}
}); 