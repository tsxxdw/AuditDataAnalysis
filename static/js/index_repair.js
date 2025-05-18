// 数据修复页面JS文件(index_repair)
$(document).ready(function() {
    // 加载表列表
    loadTableList();
    
    // 添加自定义弹框到DOM
    $('body').append(`
        <div id="customModal" class="custom-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="modalTitle">消息提示</h3>
                    <span class="close-button">&times;</span>
                </div>
                <div class="modal-body">
                    <p id="modalMessage"></p>
                </div>
                <div class="modal-footer">
                    <button id="modalConfirmBtn" class="btn btn-primary">确定</button>
                </div>
            </div>
        </div>
    `);
    
    // 添加弹框样式
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .custom-modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                animation: fadeIn 0.3s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideIn {
                from { transform: translateY(-20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            .modal-content {
                background-color: #fff;
                margin: 15% auto;
                padding: 0;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                width: 50%;
                max-width: 500px;
                position: relative;
                animation: slideIn 0.3s ease;
            }
            
            .modal-header {
                padding: 15px 20px;
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                margin: 0;
                color: #333;
            }
            
            .close-button {
                color: #aaa;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            
            .close-button:hover {
                color: #333;
            }
            
            .modal-body {
                padding: 20px;
                color: #212529;
                max-height: 60vh;
                overflow-y: auto;
            }
            
            .modal-footer {
                padding: 15px 20px;
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                text-align: right;
            }
            
            .success-icon, .error-icon, .info-icon {
                font-size: 20px;
                margin-right: 10px;
            }
            
            .success-icon {
                color: #28a745;
            }
            
            .error-icon {
                color: #dc3545;
            }
            
            .info-icon {
                color: #17a2b8;
            }
        `)
        .appendTo('head');
    
    // 自定义弹框显示函数
    window.showModal = function(message, title, type) {
        // 设置标题
        $('#modalTitle').text(title || '消息提示');
        
        // 设置图标和消息
        let icon = '';
        if (type === 'success') {
            icon = '<span class="success-icon">✓</span>';
        } else if (type === 'error') {
            icon = '<span class="error-icon">✗</span>';
        } else {
            icon = '<span class="info-icon">ℹ</span>';
        }
        
        $('#modalMessage').html(icon + message);
        
        // 显示弹框
        $('#customModal').css('display', 'block');
        
        // 处理关闭事件
        $('.close-button, #modalConfirmBtn').off('click').on('click', function() {
            $('#customModal').css('display', 'none');
        });
        
        // 点击弹框外部区域关闭弹框
        $('#customModal').off('click').on('click', function(event) {
            if (event.target === this) {
                $(this).css('display', 'none');
            }
        });
    };
    
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
            // 清空目标字段备注信息
            $('#targetComment').val('');
        }
    });
    
    // 监听参考字段选择变化
    $('#originalField').on('change', function() {
        // 获取选中的参考字段选项
        const selectedOption = $(this).find('option:selected');
        const optionText = selectedOption.text();
        
        // 从选项文本中提取备注信息（格式为：字段名 - 备注信息）
        let comment = '';
        if (optionText && optionText.includes(' - ')) {
            comment = optionText.split(' - ')[1];
            if (comment === '无注释') {
                comment = '';
            }
        }
        
        // 将备注信息 + "(修复后)" 赋值给目标字段备注信息输入框
        if (comment) {
            $('#targetComment').val(comment + '(修复后)');
        } else {
            $('#targetComment').val('');
        }
    });
    
    // 监听操作类型选择变化
    $('#operationType').on('change', function() {
        // 不需要处理，因为字段类型选项已移除
    });
    
    // 配置SQL执行区域组件
    if (window.sqlExecuteArea) {
        // 覆盖生成SQL按钮的点击处理
        window.sqlExecuteArea.options.onGenerateSQL = function(e) {
            // 直接调用生成SQL的逻辑而不是触发按钮点击
            generateSqlLogic();
        };
        
        // 覆盖SQL执行成功的回调
        window.sqlExecuteArea.options.onSuccess = function(response) {
            console.log('SQL执行成功:', response);
            
            if (response.success) {
                // 刷新表列表等操作可以在这里进行
                if (response.error_occurred) {
                    showModal('部分SQL执行成功，但有错误发生', '部分成功', 'info');
                } else {
                    showModal('SQL执行成功！', '执行成功', 'success');
                }
            }
        };
        
        // 覆盖SQL执行错误的回调
        window.sqlExecuteArea.options.onError = function(error) {
            console.error('SQL执行失败:', error);
            showModal('执行SQL失败，请查看控制台日志', '执行失败', 'error');
        };
    }
    
    // 生成SQL按钮点击事件
    $('#generateSql').on('click', function() {
        generateSqlLogic();
    });
    
    // 抽取生成SQL的逻辑到单独的函数中
    function generateSqlLogic() {
        const tableName = $('#tableName').val();
        const originalField = $('#originalField').val();
        const newField = $('#newField').val();
        const operationType = $('#operationType').val();
        const targetComment = $('#targetComment').val() || '';
        
        // 使用组件API获取模板ID - 现在不再需要强制要求
        let templateId = '';
        
        if (window.templatePromptsComponent) {
            templateId = window.templatePromptsComponent.getSelectedTemplateId() || '';
        } else if (window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue() || '';
        } else if ($('#promptTemplate').length) {
            templateId = $('#promptTemplate').val() || '';
        }
        
        // 验证必填项
        if(!tableName || !originalField) {
            // 使用自定义弹框替代alert
            showModal('请至少选择表名和参考字段', '提示', 'info');
            return;
        }
        
        // 显示按钮上的加载动画
        const $button = $('#generateSql');
        const $spinner = $button.find('.spinner-border');
        $button.prop('disabled', true);
        $spinner.removeClass('d-none');
        
        // 显示中央加载动画（如果存在）
        if ($('#loadingOverlay').length) {
            $('#loadingOverlay').css('display', 'flex');
        }
        
        // 判断是否使用API方式生成SQL
        const useApi = true;  // 默认使用API方式
        
        // 调用API生成SQL
        $.ajax({
            url: '/api/repair/generate_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                table_name: tableName,
                reference_field: originalField,
                target_field: newField || '',
                operation_type: operationType || '',
                template_id: templateId,  // 保留此字段以兼容旧代码，但后端不再要求
                target_comment: targetComment,
                use_api: useApi  // 控制是否使用API方式
            }),
            success: function(response) {
                if (response.success) {
                    // 使用SQL执行区域组件设置SQL
                    if (window.sqlExecuteArea) {
                        window.sqlExecuteArea.setSQL(response.sql);
                    } else {
                        $('#sqlContent').val(response.sql);
                    }
                    
                    // 如果是从大模型生成的，显示信息 - 现在不再从大模型生成
                    console.log('SQL由系统生成');
                } else {
                    // 使用自定义弹框替代alert
                    showModal('生成SQL失败: ' + (response.message || '未知错误'), '生成失败', 'error');
                    console.error('生成SQL失败:', response.message);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                console.error('生成SQL请求失败:', xhr, errorMsg);
                // 使用自定义弹框替代alert
                showModal('生成SQL请求失败: ' + errorMsg, '请求错误', 'error');
                
                // 不再使用本地生成SQL作为备选
                $('#sqlContent').val('');
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