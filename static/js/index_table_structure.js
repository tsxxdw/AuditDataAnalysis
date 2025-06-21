// 数据库表结构管理页面JS文件(index_table_structure)
$(document).ready(function() {
    // 确保中央加载动画是隐藏的
    $('#loadingOverlay').hide();
    
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
            } else if (selectedFunction === 'create_index' || selectedFunction === 'drop_index') {
                $('#indexContent').show().removeClass('hidden');
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
    $('#indexContent').hide();
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
            } else if (selectedFunction === 'create_index') {
                // 新增索引功能的SQL生成
                generateIndexSQL(e, 'create');
            } else if (selectedFunction === 'drop_index') {
                // 删除索引功能的SQL生成
                generateIndexSQL(e, 'drop');
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
    function generateIndexSQL(e, operation) {
        const tableName = $('#indexTableName').val();
        const indexName = $('#indexName').val();
        const indexType = $('#indexType').val();
        const indexFields = $('#indexFields').val();
        
        // 验证必填项
        if(!tableName || !indexName || !indexFields) {
            alert('请填写表名、索引名和索引字段');
            return;
        }
        
        // 获取选择的模板ID
        let templateId = null;
        
        if (window.templatePromptsComponent) {
            templateId = window.templatePromptsComponent.getSelectedTemplateId();
        } else {
            alert('模板提示词组件未初始化，请刷新页面重试');
            return;
        }
        
        // 验证模板ID是否存在
        if (!templateId) {
            alert('请选择一个提示词模板');
            return;
        }
        
        // 显示中央加载动画
        $('#loadingOverlay').css('display', 'flex');
        
        // 调用API生成SQL
        $.ajax({
            url: '/api/table_structure/generate_index_sql',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tableName: tableName,
                fieldName: fieldName,
                operationType: operationType,
                templateId: templateId,
                operation: operation
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
                console.error('获取Excel文件列表请求失败:', xhr);
            }
        });
    }
    
    // 初始化Excel文件下拉框
    function initializeExcelFileDropdown(files) {
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = files.map(file => ({
            id: file.path,
            text: file.name,
            date: file.date
        }));
        
        // 使用SearchableDropdown组件（通过模板初始化）
        const excelDropdown = initSearchableDropdownFromTemplate('.searchable-dropdown-container', dropdownData, {
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
            onChange: (value) => {
                // 加载Excel文件的工作表
                if (value) {
                    loadExcelFileSheets(value);
                } else {
                    // 清空工作表选择
                    $('#sheet-select').html('<option value="">请选择工作表</option>');
                }
            }
        });
        
        // 保存实例以便后续访问
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
                    $('#sheet-select').html('<option value="">未找到工作表</option>');
                    console.error('警告: 所选Excel文件中未找到工作表');
                }
            },
            error: function(xhr, status, error) {
                $('#sheet-select').html('<option value="">加载失败</option>');
                console.error('错误: 加载工作表失败 - ' + (xhr.responseJSON?.error || error));
            }
        });
    }
    
    // 更新工作表下拉框
    function updateSheetSelect(sheets) {
        const $sheetSelect = $('#sheet-select');
        
        // 清空下拉框
        $sheetSelect.empty();
        
        // 添加默认选项
        $sheetSelect.append('<option value="">请选择工作表</option>');
        
        // 添加工作表选项
        sheets.forEach(function(sheet) {
            $sheetSelect.append(`<option value="${sheet.id}">${sheet.name}</option>`);
        });
    }
    
    // 加载表列表
    function loadTableList() {
        // 使用通用函数加载表列表
        loadDatabaseTables('#indexTableName');
    }
    
    // 加载表字段
    function loadTableFields(tableName) {
        // 使用通用函数加载表字段
        loadDatabaseTableFields(tableName, '#indexFields');
    }
}); 