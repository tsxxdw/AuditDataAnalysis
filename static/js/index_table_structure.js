// 数据库表结构管理页面JS文件(index_table_structure)
$(document).ready(function() {
    // 功能切换逻辑
    $('#functionType').on('change', function() {
        const selectedFunction = $(this).val();
        
        // 添加平滑过渡效果
        $('.function-content').addClass('hidden');
        
        setTimeout(function() {
            // 隐藏所有内容
            $('.function-content').hide();
            
            // 根据选择显示对应内容
            if (selectedFunction === 'table') {
                $('#tableCreateContent').show().removeClass('hidden');
                // 隐藏模板提示词区域
                if (window.templatePromptsComponent) {
                    window.templatePromptsComponent.hide();
                } else {
                    $('.template-prompts').hide();
                }
            } else if (selectedFunction === 'index') {
                $('#indexManageContent').show().removeClass('hidden');
                // 显示模板提示词区域
                if (window.templatePromptsComponent) {
                    window.templatePromptsComponent.show();
                } else {
                    $('.template-prompts').show();
                }
            }
        }, 300); // 等待淡出动画完成
    });
    
    // 初始化功能选择（默认显示表创建）
    // 首次加载无需动画
    $('#functionType').val('table');
    $('#tableCreateContent').show().removeClass('hidden');
    $('#indexManageContent').hide();
    // 初始状态隐藏模板提示词区域（因为默认是表创建）
    if (window.templatePromptsComponent) {
        window.templatePromptsComponent.hide();
    } else {
        $('.template-prompts').hide();
    }
    
    // 初始化文件选择器
    initializeFileSelector();
    
    // 加载表列表
    loadTableList();
    
    // 加载提示词模板列表
    loadPromptTemplates();
    
    // 确保模板组件已经存在
    let checkTemplateComponentInterval = setInterval(function() {
        if (window.templatePromptsComponent) {
            clearInterval(checkTemplateComponentInterval);
            console.log('模板提示词组件已加载');
        } else {
            console.log('等待模板提示词组件加载...');
            // 尝试初始化模板组件
            if (typeof TemplatePrompts !== 'undefined') {
                window.templatePromptsComponent = new TemplatePrompts({
                    onSelect: function(templateId, item) {
                        console.log('已选择模板:', templateId, item);
                    }
                });
                
                // 根据当前选择的功能类型设置显示状态
                if ($('#functionType').val() === 'table') {
                    window.templatePromptsComponent.hide();
                } else {
                    window.templatePromptsComponent.show();
                }
                
                clearInterval(checkTemplateComponentInterval);
            }
        }
    }, 500);
    
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
    
    // 配置SQL执行区域组件
    if (window.sqlExecuteArea) {
        // 覆盖生成SQL按钮的点击处理
        window.sqlExecuteArea.options.onGenerateSQL = function(e) {
            // 获取当前选择的功能类型
            const selectedFunction = $('#functionType').val();
            
            if (selectedFunction === 'table') {
                // 表创建功能的SQL生成
                generateTableSQL(e);
            } else if (selectedFunction === 'index') {
                // 索引管理功能的SQL生成
                generateIndexSQL(e);
            }
        };
        
        // 覆盖SQL执行成功的回调
        window.sqlExecuteArea.options.onSuccess = function(response) {
            console.log('SQL执行成功:', response);
            // 执行成功后刷新表列表
            loadTableList();
        };
    }
    
    // 生成表SQL
    function generateTableSQL(e) {
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
        
        // 显示中央加载动画
        $('#loadingOverlay').css('display', 'flex');
        
        // 调用后端API生成表SQL
        $.ajax({
            url: '/api/table_structure/generate_table_sql',
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
                    // 设置SQL内容到组件
                    if (window.sqlExecuteArea) {
                        window.sqlExecuteArea.setSQL(response.sql);
                    } else {
                        $('#sqlContent').val(response.sql);
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
                // 隐藏中央加载动画
                $('#loadingOverlay').hide();
            }
        });
    }
    
    // 生成索引SQL
    function generateIndexSQL(e) {
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
        
        // 首先检查组件是否存在
        if (window.templatePromptsComponent) {
            // 尝试从组件获取模板ID
            templateId = window.templatePromptsComponent.getSelectedTemplateId();
            console.log('从templatePromptsComponent获取的模板ID:', templateId);
        }
        
        // 如果组件不存在或未选择模板，尝试从隐藏select获取
        if (!templateId) {
            templateId = $('#promptTemplate').val();
            console.log('从promptTemplate隐藏选择框获取的模板ID:', templateId);
        }
        
        // 如果还是没有，尝试从模板下拉框组件获取
        if (!templateId && window.templateDropdown && window.templateDropdown.getValue) {
            templateId = window.templateDropdown.getValue();
            console.log('从templateDropdown组件获取的模板ID:', templateId);
        }
        
        // 验证模板ID是否存在
        if (!templateId) {
            alert('请选择一个提示词模板');
            // 确保模板提示词区域可见
            $('.template-prompts').show();
            if (window.templatePromptsComponent) {
                window.templatePromptsComponent.show();
            }
            
            // 高亮提示模板选择区域
            $('#templateDropdown').addClass('field-required').delay(2000).queue(function(next){
                $(this).removeClass('field-required');
                next();
            });
            return;
        }
        
        // 显示中央加载动画
        $('#loadingOverlay').css('display', 'flex');
        
        // 调用后端API生成索引SQL
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
                    // 设置SQL内容到组件
                    if (window.sqlExecuteArea) {
                        window.sqlExecuteArea.setSQL(response.sql);
                    } else {
                        $('#sqlContent').val(response.sql);
                    }
                    
                    // 如果是从LLM生成的，可以添加一些提示
                    if (response.from_llm) {
                        console.log('SQL由大语言模型生成');
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
                // 隐藏中央加载动画
                $('#loadingOverlay').hide();
            }
        });
    }
    
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
        // 使用通用函数加载表列表
        loadDatabaseTables('#indexTableName', function(tables) {
            if (!tables || tables.length === 0) {
                console.error('获取表列表失败');
            }
        });
    }
    
    // 加载表字段
    function loadTableFields(tableName) {
        // 使用通用函数加载表字段
        loadDatabaseTableFields(tableName, '#fieldName', function(fields) {
            if (!fields || fields.length === 0) {
                console.error('获取表字段失败');
                alert('获取表字段失败');
            }
        });
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