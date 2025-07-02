// 数据导入页面JS文件(index_import)
$(document).ready(function() {
    // 存储表字段信息的全局变量
    window.tableFields = null;
    // 是否为本地环境的标志
    window.isLocalEnvironment = null;
    // 存储原始预览表格的HTML
    window.originalTableHtml = '';
    // 存储已选文件的数组
    window.selectedFiles = [];
    
    // 初始化时保存原始表格HTML
    window.originalTableHtml = $('.preview-table').html();
    
    // 初始化文件选择器
    initializeFileSelector();
    
    // 初始化数据库类型下拉框
    initializeDatabaseTypes();
    
    // 检查是否在本地环境
    checkLocalEnvironment();
    
    // 初始化Excel列选择下拉框（A到CZ）
    initializeColumnSelect();
    
    // 记录初始化完成
    addLog('页面初始化完成，等待用户操作...');
    
    // 全选按钮点击事件
    $('#select-all-btn').click(function() {
        addLog('用户点击: 全选文件');
        selectAllFiles();
    });
    
    // 加载数据按钮点击事件
    $('#load-tables-btn').click(function() {
        addLog('用户点击: 加载数据');
        loadDatabaseTables();
    });
    
    // 加载Excel文件按钮点击事件
    $('#load-excel-btn').click(function() {
        addLog('用户点击: 加载选择的excel文件');
        loadSelectedExcelFiles();
    });
    
    // Excel文件选择事件
    $('#excel-file-select').change(function() {
        var selectedValue = $(this).val();
        var selectedText = $(this).find('option:selected').text();
        addLog('用户选择Excel文件: ' + selectedText);
        loadExcelFileSheets(selectedValue);
    });
    
    // sheet选择事件
    $('#sheet-select').change(function() {
        var selectedValue = $(this).val();
        var selectedText = $(this).find('option:selected').text();
        addLog('用户选择工作表: ' + selectedText);
    });
    
    // 数据库选择事件
    $('#db-select').change(function() {
        var selectedValue = $(this).val();
        var selectedText = $(this).find('option:selected').text();
        addLog('用户选择数据库: ' + selectedText);
    });
    
    // 表选择事件
    $('#table-select').change(function() {
        var selectedValue = $(this).val();
        var selectedText = $(this).find('option:selected').text();
        if (selectedValue) {
            addLog('用户选择目标表: ' + selectedText);
        }
    });
    
    // 起始行输入变化事件
    $('#start-row').change(function() {
        addLog('用户设置预览起始行: ' + $(this).val());
    });
    
    // 预览按钮点击事件
    $('#preview-btn').click(function() {
        addLog('用户点击: 预览数据');
        previewData();
    });
    
    // 取消预览按钮点击事件
    $('#cancel-preview-btn').click(function() {
        addLog('用户点击: 取消预览');
        cancelPreview();
    });
    
    // 打开Excel按钮点击事件
    $('#open-excel-btn').click(function() {
        addLog('用户点击: 下载EXCEL');
        openExcelFile();
    });
    
    // 导入按钮点击事件
    $('#import-btn').click(function() {
        addLog('用户点击: 开始导入');
        showImportConfirmation();
    });
    
    // 确认导入按钮点击事件
    $('#confirm-import-btn').click(function() {
        addLog('用户点击: 确认导入');
        hideImportConfirmation();
        executeImport();
    });
    
    // 取消导入按钮点击事件
    $('#cancel-import-btn, .close-modal').click(function() {
        addLog('用户点击: 取消导入');
        hideImportConfirmation();
    });
    
    // 点击模态框背景关闭
    $(window).click(function(event) {
        if ($(event.target).hasClass('modal')) {
            hideImportConfirmation();
        }
    });
    
    // 清空日志按钮点击事件
    $('#clear-log-btn').click(function() {
        addLog('用户点击: 清空日志');
        $('#import-log').html('<div class="log-entry">日志已清空</div>');
    });
    
    // 导出日志按钮点击事件
    $('#export-log-btn').click(function() {
        addLog('用户点击: 导出日志');
        exportLogs();
    });
    
    // 列选择变化事件
    $('#column-select').change(function() {
        var selectedColumn = $(this).find('option:selected').text();
        addLog('用户选择导入条件列: ' + selectedColumn);
    });
    
    // 条件选择变化事件
    $('#condition-select').change(function() {
        var selectedValue = $(this).val();
        var selectedText = $(this).find('option:selected').text();
        addLog('用户选择导入条件: ' + selectedText);
    });
    
    // 开始导入行选择变化事件
    $('#import-start-row').change(function() {
        var selectedRow = $(this).val();
        addLog('用户设置开始导入行: ' + selectedRow);
    });
    
    // 补充列选择变化事件
    $('#supplement-column-select-1').change(function() {
        var selectedColumn = $(this).find('option:selected').text();
        addLog('用户选择补充列1: ' + selectedColumn);
    });
    
    // 补充值输入变化事件
    $('#supplement-value-1').change(function() {
        var value = $(this).val();
        addLog('用户设置补充值1: ' + value);
    });
    
    // 补充列2选择变化事件
    $('#supplement-column-select-2').change(function() {
        var selectedColumn = $(this).find('option:selected').text();
        addLog('用户选择补充列2: ' + selectedColumn);
    });
    
    // 补充值2输入变化事件
    $('#supplement-value-2').change(function() {
        var value = $(this).val();
        addLog('用户设置补充值2: ' + value);
    });
    
    // 补充列3选择变化事件
    $('#supplement-column-select-3').change(function() {
        var selectedColumn = $(this).find('option:selected').text();
        addLog('用户选择补充列3: ' + selectedColumn);
    });
    
    // 补充值3输入变化事件
    $('#supplement-value-3').change(function() {
        var value = $(this).val();
        addLog('用户设置补充值3: ' + value);
    });
    
    // 补充字段启用复选框事件
    $('#supplement-enable-1').change(function() {
        var isChecked = $(this).is(':checked');
        addLog('用户' + (isChecked ? '启用' : '禁用') + '补充字段1');
    });
    
    $('#supplement-enable-2').change(function() {
        var isChecked = $(this).is(':checked');
        addLog('用户' + (isChecked ? '启用' : '禁用') + '补充字段2');
    });
    
    $('#supplement-enable-3').change(function() {
        var isChecked = $(this).is(':checked');
        addLog('用户' + (isChecked ? '启用' : '禁用') + '补充字段3');
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
                
                // 使用SearchableDropdown组件初始化文件选择器
                initializeExcelFilesDropdown(excelFiles);
            },
            error: function(xhr) {
                console.error('获取文件列表失败:', xhr);
                addLog('错误: 获取文件列表失败 - ' + (xhr.responseJSON?.error || xhr.statusText));
            }
        });
    }
    
    // 使用SearchableDropdown组件初始化Excel文件选择器
    function initializeExcelFilesDropdown(files) {
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = files.map(file => ({
            id: file.path,
            text: file.name,
            date: file.date,
            size: file.size,
            type: file.name.split('.').pop().toUpperCase()
        }));
        
        // 使用SearchableDropdown模板组件
        const fileDropdown = initSearchableDropdownFromTemplate('.searchable-dropdown-container', dropdownData, {
            valueField: 'id',
            textField: 'text',
            searchFields: ['text'],
            placeholder: '输入关键词搜索Excel文件...',
            noResultsText: '没有找到匹配的Excel文件',
            itemTemplate: (item) => `
                <div>
                    <span style="font-weight: bold;">${item.text}</span>
                    <span style="color: #777; margin-left: 10px; font-size: 0.85em;">${item.date || ''}</span>
                    <span style="color: #555; margin-left: 10px; font-size: 0.85em;">${item.size || ''}</span>
                    <span class="file-type-badge">${item.type}</span>
                </div>
            `,
            onChange: (value, item) => {
                // 记录选择的文件
                if (!window.selectedFiles.includes(value)) {
                    window.selectedFiles.push(value);
                    
                    // 更新UI显示
                    updateSelectedFiles();
                    
                    // 记录日志
                    addLog('用户选择文件: ' + item.text);
                }
            }
        });
        
        // 在组件上存储所有文件数据，以便后续使用
        window.allExcelFiles = dropdownData;
    }
    
    // 初始化数据库类型下拉框
    function initializeDatabaseTypes() {
        $('#db-select').empty().append('<option value="" disabled selected>加载中...</option>');
        
        // 从后端API获取数据库类型
        $.ajax({
            url: '/api/import/db_types',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                $('#db-select').empty().append('<option value="" disabled selected>请选择数据库</option>');
                
                // 添加所有数据库类型选项
                $.each(data, function(index, db) {
                    var option = $('<option></option>')
                        .attr('value', db.id)
                        .text(db.name);
                    
                    // 如果是默认数据库类型，设置为选中
                    if (db.isDefault) {
                        option.attr('selected', true);
                    }
                    
                    $('#db-select').append(option);
                });
                
                // 触发change事件以便可以根据需要执行其他初始化
                if (data.length > 0) {
                    $('#db-select').trigger('change');
                }
            },
            error: function(xhr, status, error) {
                $('#db-select').empty().append('<option value="" disabled selected>加载失败</option>');
                addLog('错误: 加载数据库类型失败 - ' + (xhr.responseJSON?.error || error));
            }
        });
    }
    
    // 检查是否在本地环境
    function checkLocalEnvironment() {
        // 从URL中获取主机名
        var hostname = window.location.hostname.toLowerCase();
        
        // 检查是否为localhost或127.0.0.1
        var isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
        
        // 设置全局变量，可能用于其他功能
        window.isLocalEnvironment = isLocal;
        
        // 不再限制"打开EXCEL"功能只能在本地环境使用
        // 因为我们现在通过浏览器查看Excel文件，而不是通过本地Excel程序
        
        return isLocal;
    }
    
    // 更新打开Excel按钮的状态
    function updateOpenExcelButtonState() {
        var $btn = $('#open-excel-btn');
        var hasFile = $('#excel-file-select').val() !== null && $('#excel-file-select').val() !== '';
        var hasSheet = $('#sheet-select').val() !== null && $('#sheet-select').val() !== '';
        
        // 只需要检查是否选择了文件和工作表
        var canOpen = hasFile && hasSheet;
        
        // 启用/禁用按钮
        $btn.prop('disabled', !canOpen);
        
        // 更新提示信息
        if (!hasFile || !hasSheet) {
            $btn.attr('title', '请先选择Excel文件和工作表');
        } else {
            $btn.attr('title', '下载Excel文件');
        }
    }
    
    // 打开Excel文件
    function openExcelFile() {
        // 获取选择的Excel文件和工作表ID
        const filePath = $('#excel-file-select').val();
        const sheetId = $('#sheet-select').val();
        
        if (!filePath) {
            addLog('错误: 请先选择Excel文件');
            return;
        }
        
        if (!sheetId) {
            addLog('错误: 请先选择工作表');
            return;
        }
        
        addLog('正在请求打开Excel文件...');
        
        // 调用API获取Excel文件的URL
        $.ajax({
            url: '/api/import/excel/view',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                file_path: filePath,
                sheet_id: sheetId
            }),
            success: function(response) {
                if (response.success) {
                    addLog('成功: ' + response.message);
                    
                    // 在新标签页打开Excel文件
                    if (response.view_url) {
                        window.open(response.view_url, '_blank');
                    }
                } else {
                    addLog('错误: ' + response.message);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                addLog('错误: 打开Excel文件失败 - ' + errorMsg);
                console.error('打开Excel文件请求失败:', xhr);
            }
        });
    }
    
    // 监听Excel文件和工作表选择变化，更新打开Excel按钮状态
    $('#excel-file-select, #sheet-select').change(function() {
        updateOpenExcelButtonState();
    });
    
    // 加载数据库表
    function loadDatabaseTables() {
        var selectedDb = $('#db-select').val();
        
        if (!selectedDb) {
            addLog('错误: 请先选择数据库');
            return;
        }
        
        // 禁用按钮，防止重复点击
        $('#load-tables-btn').prop('disabled', true).text('加载中...');
        
        // 清空并重新加载表下拉框
        $('#table-select').empty().append('<option value="" disabled selected>加载中...</option>');
        
        addLog('正在加载数据库表列表...');
        
        // 注意：这里我们可以选择使用通用函数或保持使用导入模块特定API
        // 此实现使用导入模块特定的API，保持原有逻辑
        $.ajax({
            url: '/api/import/tables',
            method: 'GET',
            data: { db_type: selectedDb },
            dataType: 'json',
            success: function(data) {
                $('#table-select').empty().append('<option value="" disabled selected>请选择表</option>');
                
                // 添加所有表选项
                if (data.length > 0) {
                    $.each(data, function(index, table) {
                        // 构建表显示名称，包含备注信息
                        var displayName = table.name;
                        if (table.comment && table.comment.trim() !== '') {
                            displayName += ' (' + table.comment + ')';
                        }
                        
                        $('#table-select').append($('<option></option>')
                            .attr('value', table.id)
                            .text(displayName));
                    });
                    addLog('成功加载 ' + data.length + ' 个表');
                } else {
                    $('#table-select').append('<option value="" disabled>没有可用的表</option>');
                    addLog('警告: 没有找到任何表');
                }
            },
            error: function(xhr, status, error) {
                $('#table-select').empty().append('<option value="" disabled selected>加载失败</option>');
                addLog('错误: 加载表列表失败 - ' + (xhr.responseJSON?.error || error));
            },
            complete: function() {
                // 恢复按钮状态
                $('#load-tables-btn').prop('disabled', false).text('加载数据');
            }
        });
    }
    
    // 可选的通用表加载函数版本（如果需要切换到通用API）
    function loadDatabaseTablesFromCommon() {
        var selectedDb = $('#db-select').val();
        
        if (!selectedDb) {
            addLog('错误: 请先选择数据库');
            return;
        }
        
        // 禁用按钮，防止重复点击
        $('#load-tables-btn').prop('disabled', true).text('加载中...');
        
        addLog('正在加载数据库表列表...');
        
        // 使用公共函数加载表
        loadDatabaseTables('#table-select', function(tables) {
            if (tables && tables.length > 0) {
                addLog('成功加载 ' + tables.length + ' 个表');
            } else {
                addLog('警告: 没有找到任何表');
            }
            
            // 恢复按钮状态
            $('#load-tables-btn').prop('disabled', false).text('加载数据');
        });
    }
    
    // 加载选择的Excel文件
    function loadSelectedExcelFiles() {
        if (window.selectedFiles.length === 0) {
            addLog('错误: 请先选择Excel文件');
            return;
        }
        
        // 禁用按钮，防止重复点击
        $('#load-excel-btn').prop('disabled', true).text('加载中...');
        
        addLog('正在加载Excel文件内容，共' + window.selectedFiles.length + '个文件...');
        
        // 调用API处理选择的Excel文件
        $.ajax({
            url: '/api/import/excel/selected-files',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ file_paths: window.selectedFiles }),
            dataType: 'json',
            success: function(response) {
                if (response.success && response.files && response.files.length > 0) {
                    // 清空并重新填充Excel文件下拉框
                    $('#excel-file-select').empty().append('<option value="" disabled selected>请选择Excel文件</option>');
                    
                    // 存储文件和工作表信息到全局变量
                    window.excelFiles = response.files;
                    
                    // 添加Excel文件选项，并标记文件类型
                    $.each(response.files, function(index, file) {
                        var fileLabel = file.name;
                        // 如果有扩展名属性，显示格式类型
                        if (file.extension) {
                            var ext = file.extension.toLowerCase();
                            var formatBadge = ext === '.xlsx' ? '[xlsx]' : '[xls]';
                            fileLabel = fileLabel + ' ' + formatBadge;
                        }
                        
                        $('#excel-file-select').append(
                            $('<option></option>')
                                .attr('value', file.path)
                                .text(fileLabel)
                        );
                    });
                    
                    addLog('成功加载 ' + response.files.length + ' 个Excel文件');
                    
                    // 如果有跳过的文件，显示警告
                    if (response.skipped_files && response.skipped_files.length > 0) {
                        addLog('警告: ' + response.skipped_files.length + ' 个文件被跳过');
                        $.each(response.skipped_files, function(index, file) {
                            var fileName = file.path.split('/').pop().split('\\').pop();
                            addLog('- 跳过文件: ' + fileName + ' (' + file.reason + ')');
                        });
                    }
                    
                    // 如果有错误的文件，显示错误
                    if (response.error_files && response.error_files.length > 0) {
                        addLog('错误: ' + response.error_files.length + ' 个文件无法处理');
                        $.each(response.error_files, function(index, file) {
                            addLog('- 处理失败: ' + file.name + ' (' + file.error + ')');
                        });
                    }
                } else {
                    addLog('警告: 没有找到有效的Excel文件');
                    $('#excel-file-select').empty().append('<option value="" disabled selected>没有有效的Excel文件</option>');
                    
                    // 如果有详细错误消息，显示它们
                    if (response.skipped_files && response.skipped_files.length > 0) {
                        addLog('以下文件被跳过:');
                        $.each(response.skipped_files, function(index, file) {
                            var fileName = file.path.split('/').pop().split('\\').pop();
                            addLog('- ' + fileName + ' (' + file.reason + ')');
                        });
                    }
                    
                    if (response.error_files && response.error_files.length > 0) {
                        addLog('以下文件处理失败:');
                        $.each(response.error_files, function(index, file) {
                            addLog('- ' + file.name + ' (' + file.error + ')');
                        });
                    }
                }
            },
            error: function(xhr, status, error) {
                $('#excel-file-select').empty().append('<option value="" disabled selected>加载失败</option>');
                
                var errorMessage = '加载Excel文件失败';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage += ' - ' + xhr.responseJSON.error;
                } else if (error) {
                    errorMessage += ' - ' + error;
                }
                
                addLog('错误: ' + errorMessage);
                console.error('加载Excel文件失败:', {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    response: xhr.responseText,
                    error: error
                });
            },
            complete: function() {
                // 恢复按钮状态
                $('#load-excel-btn').prop('disabled', false).text('加载选择的excel文件');
            }
        });
    }
    
    // 加载Excel文件的工作表
    function loadExcelFileSheets(filePath) {
        if (!filePath) {
            $('#sheet-select').empty().append('<option value="" disabled selected>请先选择Excel文件</option>');
            return;
        }
        
        // 从缓存中查找文件信息
        var fileInfo = null;
        if (window.excelFiles) {
            fileInfo = window.excelFiles.find(function(file) {
                return file.path === filePath;
            });
        }
        
        if (fileInfo && fileInfo.sheets && fileInfo.sheets.length > 0) {
            // 使用缓存的工作表信息
            updateSheetSelect(fileInfo.sheets);
        } else {
            // 如果没有缓存，从API获取工作表信息
            $('#sheet-select').empty().append('<option value="" disabled selected>加载中...</option>');
            
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
                        addLog('警告: 所选Excel文件中未找到工作表');
                    }
                },
                error: function(xhr, status, error) {
                    $('#sheet-select').empty().append('<option value="" disabled selected>加载失败</option>');
                    addLog('错误: 加载工作表失败 - ' + (xhr.responseJSON?.error || error));
                }
            });
        }
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
            addLog('成功加载 ' + sheets.length + ' 个工作表');
        }
    }
    
    // 预览数据
    function previewData() {
        var filePaths = $('#file-select').data('file-paths') || $('#file-path').val();
        var selectedDb = $('#db-select').val();
        var selectedTable = $('#table-select').val();
        var selectedExcel = $('#excel-file-select').val();
        var selectedSheet = $('#sheet-select').val();
        var startRow = $('#start-row').val();
        
        // 验证输入
        if (!filePaths) {
            addLog('错误: 请选择文件');
            return;
        }
        
        if (!selectedDb) {
            addLog('错误: 请选择数据库');
            return;
        }
        
        if (!selectedTable) {
            addLog('错误: 请选择目标表');
            return;
        }
        
        if (!selectedExcel) {
            addLog('错误: 请选择要导入的Excel文件');
            return;
        }
        
        if (!selectedSheet) {
            addLog('错误: 请选择要导入的工作表');
            return;
        }
        
        // 显示加载中
        $('.preview-table tbody').html('<tr><td colspan="5" class="no-data-message">加载数据中...</td></tr>');
        
        // 首先加载表字段信息，然后加载Excel数据
        loadTableFields(selectedDb, selectedTable, function() {
            loadExcelPreview(selectedExcel, selectedSheet, startRow);
        });
    }
    
    // 加载表字段信息
    function loadTableFields(dbType, tableName, callback) {
        $.ajax({
            url: '/api/import/tables/fields',
            method: 'GET',
            data: {
                db_type: dbType,
                table_name: tableName
            },
            dataType: 'json',
            success: function(response) {
                if (response.success && response.fields && response.fields.length > 0) {
                    // 存储表字段信息
                    window.tableFields = response.fields;
                    
                    // 更新表头
                    updateTableHeader(response.fields);
                    
                    addLog(`成功加载 ${response.table} 表的 ${response.fields.length} 个字段`);
                    
                    // 如果有回调函数，执行它
                    if (typeof callback === 'function') {
                        callback();
                    }
                } else {
                    $('.preview-table tbody').html('<tr><td colspan="5" class="no-data-message">获取表字段失败</td></tr>');
                    addLog('警告: 未找到表字段信息');
                }
            },
            error: function(xhr, status, error) {
                $('.preview-table tbody').html('<tr><td colspan="5" class="no-data-message">获取表字段失败</td></tr>');
                addLog('错误: 获取表字段失败 - ' + (xhr.responseJSON?.error || error));
            }
        });
    }
    
    // 更新表头
    function updateTableHeader(fields) {
        // 创建Excel列字母行
        var excelLetterRow = '<tr class="excel-column-header">';
        
        // 为每个字段添加对应的Excel列字母
        for (var i = 0; i < fields.length; i++) {
            var columnLetter = getExcelColumnName(i);
            excelLetterRow += `<th title="Excel列${columnLetter}" class="excel-column-letter">${columnLetter}</th>`;
        }
        
        excelLetterRow += '</tr>';
        
        // 创建表字段行
        var fieldHeaderRow = '<tr class="field-header-row">';
        
        // 使用表字段作为表头
        $.each(fields, function(index, field) {
            var displayName = field.name;
            if (field.comment && field.comment.trim() !== '') {
                displayName += ' (' + field.comment + ')';
            }
            fieldHeaderRow += `<th title="${field.type}">${displayName}</th>`;
        });
        
        fieldHeaderRow += '</tr>';
        
        // 组合两行表头
        var headerHtml = excelLetterRow + fieldHeaderRow;
        
        // 更新表头
        $('.preview-table thead').html(headerHtml);
    }
    
    // 加载Excel预览数据
    function loadExcelPreview(filePath, sheetId, startRow) {
        addLog('正在加载Excel预览数据');
        
        // 获取Excel文件路径、工作表ID和起始行
        var filePath = $('#excel-file-select').val();
        var sheetId = $('#sheet-select').val();
        var startRow = $('#start-row').val();
        
        // 清除之前显示的总行数
        $('#excel-total-rows').text('-');
        
        // 验证参数
        if (!filePath) {
            addLog('警告: 未选择Excel文件', true, 'warning');
            return;
        }
        
        if (!sheetId) {
            addLog('警告: 未选择工作表', true, 'warning');
            return;
        }
        
        // 设置隐藏字段，用于后续处理
        $('#excel-file-path').val(filePath);
        $('#excel-worksheet').val(sheetId);
        $('#preview-start-row').val(startRow);
        
        // 正在加载数据的信息
        addLog(`加载Excel数据 (文件: ${filePath}, 工作表: ${sheetId}, 起始行: ${startRow})`, false);
        
        // 构建请求数据
        var requestData = {
            file_path: filePath,
            sheet_id: sheetId,
            start_row: startRow,
            row_limit: 10, // 最多显示10行
            get_total_rows: true // 请求获取总行数
        };
        
        // 发送AJAX请求
        $.ajax({
            url: '/api/import/excel/preview',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    // 更新表格数据
                    updateTableData(response.data.rows);
                    addLog(`成功加载Excel数据预览，从第${response.start_row}行开始，共${response.data.rows.length}条记录`);
                    
                    // 显示取消预览按钮
                    $('#cancel-preview-btn').show();
                    
                    // 显示Excel总行数（如果有）
                    if (response.total_rows !== undefined) {
                        $('.total-rows-container').show(); // 显示总行数容器
                        $('#excel-total-rows').text(response.total_rows);
                        addLog(`该Excel工作表实际有效行数为 ${response.total_rows} 行`);
                    }
                } else {
                    $('.preview-table tbody').html('<tr><td colspan="' + (window.tableFields ? window.tableFields.length : 5) + '" class="no-data-message">未找到Excel数据</td></tr>');
                    addLog('警告: 未找到Excel数据', true, 'warning');
                    
                    // 隐藏取消预览按钮
                    $('#cancel-preview-btn').hide();
                }
            },
            error: function(xhr, status, error) {
                var errorMsg = '';
                try {
                    // 尝试解析错误响应
                    if (xhr.responseJSON && xhr.responseJSON.error) {
                        errorMsg = xhr.responseJSON.error;
                    } else if (xhr.responseText) {
                        errorMsg = xhr.responseText;
                    } else {
                        errorMsg = error || 'Unknown error';
                    }
                } catch (e) {
                    errorMsg = '解析错误响应失败：' + e.message;
                }
                
                $('.preview-table tbody').html('<tr><td colspan="' + (window.tableFields ? window.tableFields.length : 5) + '" class="no-data-message">加载Excel数据失败</td></tr>');
                addLog('错误: 加载Excel数据失败 - ' + errorMsg, true, 'error');
                console.error('Excel预览错误:', {
                    status: status,
                    error: error,
                    response: xhr.responseText,
                    requestData: requestData
                });
                
                // 隐藏取消预览按钮
                $('#cancel-preview-btn').hide();
            }
        });
    }
    
    // 取消预览，恢复到默认状态
    function cancelPreview() {
        // 恢复预览表格的原始HTML
        $('.preview-table').html(window.originalTableHtml);
        
        // 隐藏取消预览按钮和总行数显示
        $('#cancel-preview-btn').hide();
        $('.total-rows-container').hide();
        
        // 更新日志
        addLog('已取消预览，恢复默认状态');
    }
    
    // 更新表格数据
    function updateTableData(rows) {
        if (!rows || rows.length === 0) {
            var colCount = window.tableFields ? window.tableFields.length : 5;
            $('.preview-table tbody').html('<tr><td colspan="' + colCount + '" class="no-data-message">没有数据</td></tr>');
            return;
        }
        
        var tableHtml = '';
        
        // 遍历数据行
        $.each(rows, function(rowIndex, row) {
            tableHtml += '<tr>';
            
            // 如果有表字段信息，使用它来限制列数
            var columnCount = window.tableFields ? window.tableFields.length : row.length;
            
            // 遍历列
            for (var colIndex = 0; colIndex < columnCount; colIndex++) {
                var cellValue = colIndex < row.length ? row[colIndex] : '';
                
                // 如果单元格值为null或undefined，显示空字符串
                if (cellValue === null || cellValue === undefined) {
                    cellValue = '';
                }
                
                tableHtml += '<td>' + cellValue + '</td>';
            }
            
            tableHtml += '</tr>';
        });
        
        $('.preview-table tbody').html(tableHtml);
        
        // 更新列选择下拉框
        updateColumnSelect();
    }
    
    // 更新列选择下拉框（预览数据后强调当前实际使用的列）
    function updateColumnSelect() {
        // 获取当前表格的列数
        var columnCount = $('.preview-table thead th').length;
        
        // 高亮显示当前使用的列
        var $columnSelect = $('#column-select');
        $columnSelect.find('option').each(function() {
            var index = parseInt($(this).val());
            if (!isNaN(index) && index < columnCount) {
                $(this).css('font-weight', 'bold');
            } else if (!isNaN(index)) {
                $(this).css('font-weight', 'normal');
            }
        });
        
        // 同样更新补充列下拉框1-3
        updateSupplementColumnSelect('#supplement-column-select-1', columnCount);
        updateSupplementColumnSelect('#supplement-column-select-2', columnCount);
        updateSupplementColumnSelect('#supplement-column-select-3', columnCount);
        
        addLog('已更新列选择下拉框，当前表格共' + columnCount + '列（A到' + getExcelColumnName(columnCount-1) + '）');
    }
    
    // 更新补充列下拉框辅助函数
    function updateSupplementColumnSelect(selectId, columnCount) {
        var $select = $(selectId);
        $select.find('option').each(function() {
            var index = parseInt($(this).val());
            if (!isNaN(index) && index < columnCount) {
                $(this).css('font-weight', 'bold');
            } else if (!isNaN(index)) {
                $(this).css('font-weight', 'normal');
            }
        });
    }
    
    // 获取Excel列名格式（A, B, C, ..., Z, AA, AB, ..., CZ）
    function getExcelColumnName(index) {
        var columnName = '';
        var dividend = index + 1;
        var modulo;
        
        while (dividend > 0) {
            modulo = (dividend - 1) % 26;
            columnName = String.fromCharCode(65 + modulo) + columnName;
            dividend = Math.floor((dividend - modulo) / 26);
        }
        
        return columnName;
    }
    
    // 显示导入确认对话框
    function showImportConfirmation() {
        // 收集导入参数
        var selectedDb = $('#db-select option:selected').text();
        var selectedTable = $('#table-select option:selected').text();
        var selectedExcel = $('#excel-file-select option:selected').text();
        var selectedSheet = $('#sheet-select option:selected').text();
        var importStartRow = $('#import-start-row').val();
        
        // 获取导入条件
        var selectedColumn = $('#column-select').val();
        var selectedCondition = $('#condition-select').val();
        var conditionText = '';
        
        if (selectedColumn && selectedCondition) {
            var columnName = $('#column-select option:selected').text();
            var conditionName = $('#condition-select option:selected').text();
            conditionText = columnName + ' ' + conditionName;
            $('#confirm-condition').text(conditionText);
            $('#confirm-condition-container').show();
        } else {
            $('#confirm-condition-container').hide();
        }
        
        // 设置基本信息
        $('#confirm-db').text(selectedDb);
        $('#confirm-table').text(selectedTable);
        $('#confirm-excel').text(selectedExcel);
        $('#confirm-sheet').text(selectedSheet);
        $('#confirm-start-row').text(importStartRow);
        
        // 处理补充字段
        var $supplementsContainer = $('#confirm-supplements');
        $supplementsContainer.empty();
        
        // 补充字段1
        addSupplementToConfirmation(1, $supplementsContainer);
        
        // 补充字段2
        addSupplementToConfirmation(2, $supplementsContainer);
        
        // 补充字段3
        addSupplementToConfirmation(3, $supplementsContainer);
        
        // 显示对话框
        $('#import-confirm-modal').css('display', 'block');
    }
    
    // 添加补充字段到确认对话框
    function addSupplementToConfirmation(index, container) {
        var supplementColumn = $(`#supplement-column-select-${index}`).val();
        var supplementValue = $(`#supplement-value-${index}`).val();
        var supplementEnabled = $(`#supplement-enable-${index}`).is(':checked');
        
        if (supplementEnabled && supplementColumn && supplementValue) {
            var columnName = $(`#supplement-column-select-${index} option:selected`).text();
            var supplementHtml = `
                <div class="confirm-info-item">
                    <span class="confirm-label">补充字段${index}:</span>
                    <span class="confirm-value">${columnName} = ${supplementValue} (已启用)</span>
                </div>
            `;
            container.append(supplementHtml);
        } else if (supplementColumn && supplementValue) {
            var columnName = $(`#supplement-column-select-${index} option:selected`).text();
            var supplementHtml = `
                <div class="confirm-info-item">
                    <span class="confirm-label">补充字段${index}:</span>
                    <span class="confirm-value">${columnName} = ${supplementValue} (未启用)</span>
                </div>
            `;
            container.append(supplementHtml);
        }
    }
    
    // 隐藏导入确认对话框
    function hideImportConfirmation() {
        $('#import-confirm-modal').css('display', 'none');
    }
    
    // 执行导入操作
    function executeImport() {
        var filePaths = $('#file-select').data('file-paths') || $('#file-path').val();
        var selectedDb = $('#db-select').val();
        var selectedTable = $('#table-select').val();
        var selectedExcel = $('#excel-file-select').val();
        var selectedSheet = $('#sheet-select').val();
        var startRow = $('#start-row').val();
        var importStartRow = $('#import-start-row').val();
        
        // 获取导入条件
        var selectedColumn = $('#column-select').val();
        var selectedCondition = $('#condition-select').val();
        
        // 获取补充字段
        var supplementColumn1 = $('#supplement-column-select-1').val();
        var supplementValue1 = $('#supplement-value-1').val();
        var supplementEnabled1 = $('#supplement-enable-1').is(':checked');
        
        var supplementColumn2 = $('#supplement-column-select-2').val();
        var supplementValue2 = $('#supplement-value-2').val();
        var supplementEnabled2 = $('#supplement-enable-2').is(':checked');
        
        var supplementColumn3 = $('#supplement-column-select-3').val();
        var supplementValue3 = $('#supplement-value-3').val();
        var supplementEnabled3 = $('#supplement-enable-3').is(':checked');
        
        // 记录详细导入参数
        addLog('导入参数:');
        addLog('- 数据库: ' + $('#db-select option:selected').text());
        addLog('- 目标表: ' + $('#table-select option:selected').text());
        addLog('- Excel文件: ' + $('#excel-file-select option:selected').text());
        addLog('- 工作表: ' + $('#sheet-select option:selected').text());
        addLog('- 起始行: ' + startRow);
        addLog('- 开始导入行: ' + importStartRow);
        
        // 记录导入条件
        if (selectedColumn && selectedCondition) {
            var columnName = $('#column-select option:selected').text();
            var conditionName = $('#condition-select option:selected').text();
            addLog('- 导入条件: ' + columnName + ' ' + conditionName);
        }
        
        // 记录补充字段
        if (supplementEnabled1 && supplementColumn1 && supplementValue1) {
            var columnName = $('#supplement-column-select-1 option:selected').text();
            addLog('- 补充字段1: ' + columnName + ' = ' + supplementValue1 + ' (已启用)');
        } else if (supplementColumn1 && supplementValue1) {
            var columnName = $('#supplement-column-select-1 option:selected').text();
            addLog('- 补充字段1: ' + columnName + ' = ' + supplementValue1 + ' (未启用)');
        }
        
        if (supplementEnabled2 && supplementColumn2 && supplementValue2) {
            var columnName = $('#supplement-column-select-2 option:selected').text();
            addLog('- 补充字段2: ' + columnName + ' = ' + supplementValue2 + ' (已启用)');
        } else if (supplementColumn2 && supplementValue2) {
            var columnName = $('#supplement-column-select-2 option:selected').text();
            addLog('- 补充字段2: ' + columnName + ' = ' + supplementValue2 + ' (未启用)');
        }
        
        if (supplementEnabled3 && supplementColumn3 && supplementValue3) {
            var columnName = $('#supplement-column-select-3 option:selected').text();
            addLog('- 补充字段3: ' + columnName + ' = ' + supplementValue3 + ' (已启用)');
        } else if (supplementColumn3 && supplementValue3) {
            var columnName = $('#supplement-column-select-3 option:selected').text();
            addLog('- 补充字段3: ' + columnName + ' = ' + supplementValue3 + ' (未启用)');
        }
        
        // 验证输入
        if (!validateImportParams()) {
            return;
        }
        
        // 禁用导入按钮，防止重复点击
        $('#import-btn').prop('disabled', true).text('导入中...');
        
        // 隐藏进度区域（我们不需要它了）
        $('.import-status').hide();
        
        // 添加开始导入的日志记录
        addLog('开始导入数据...', true);
        addLog('正在读取Excel文件数据...');
        
        // 准备补充字段数组
        var supplements = [];
        
        if (supplementEnabled1 && supplementColumn1 && supplementValue1) {
            supplements.push({
                enabled: true,
                column: supplementColumn1,
                column_name: $('#supplement-column-select-1 option:selected').text(),
                value: supplementValue1
            });
        }
        
        if (supplementEnabled2 && supplementColumn2 && supplementValue2) {
            supplements.push({
                enabled: true,
                column: supplementColumn2,
                column_name: $('#supplement-column-select-2 option:selected').text(),
                value: supplementValue2
            });
        }
        
        if (supplementEnabled3 && supplementColumn3 && supplementValue3) {
            supplements.push({
                enabled: true,
                column: supplementColumn3,
                column_name: $('#supplement-column-select-3 option:selected').text(),
                value: supplementValue3
            });
        }
        
        // 准备导入条件
        var condition = null;
        if (selectedColumn && selectedCondition) {
            condition = {
                column: selectedColumn,
                column_name: $('#column-select option:selected').text(),
                type: selectedCondition,
                type_name: $('#condition-select option:selected').text()
            };
        }
        
        // 构建请求数据
        var requestData = {
            file_path: selectedExcel,
            sheet_id: selectedSheet,
            database_id: selectedDb,
            table_id: selectedTable,
            start_row: parseInt(importStartRow) || 2,
            condition: condition,
            supplements: supplements
        };
        
        // 显示结果区域并初始化
        $('.import-result').show();
        $('#files-count').text('1');
        $('#records-count').text('0');
        $('#success-count').text('0');
        $('#failed-count').text('0');
        
        // 生成一个任务ID (可以使用时间戳+随机数简单模拟)
        var taskId = 'import_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
        
        // 存储任务ID，用于后续轮询
        window.currentImportTaskId = taskId;
        
        // 启动一个任务轮询器
        startImportTaskPoller(taskId, requestData);
    }
    
    // 启动导入任务并开始轮询进度
    function startImportTaskPoller(taskId, requestData) {
        // 记录轮询开始时间
        var startTime = new Date().getTime();
        
        // 发送导入请求
        $.ajax({
            url: '/api/import/excel/import',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            dataType: 'json',
            timeout: 300000, // 5分钟超时
            success: function(response) {
                if (response.success) {
                    // 更新最终结果
                    updateFinalImportResult(response);
                } else {
                    // 处理导入失败
                    handleImportError(response);
                }
                
                // 停止轮询
                clearInterval(window.importProgressPoller);
                
                // 启用导入按钮
                $('#import-btn').prop('disabled', false).text('开始导入');
            },
            error: function(xhr, status, error) {
                // 处理AJAX错误
                handleAjaxError(xhr, status, error);
                
                // 停止轮询
                clearInterval(window.importProgressPoller);
                
                // 启用导入按钮
                $('#import-btn').prop('disabled', false).text('开始导入');
            }
        });
        
        // 清除已有的轮询器
        if (window.importProgressPoller) {
            clearInterval(window.importProgressPoller);
        }
        
        // 初始化进度轮询请求计数
        window.pollCounter = 0;
        
        // 开始轮询，每1秒查询一次进度
        window.importProgressPoller = setInterval(function() {
            // 增加轮询计数
            window.pollCounter++;
            
            // 模拟进度查询 (这里模拟了后端的进度回复)
            simulateProgressCheck(startTime, window.pollCounter);
            
        }, 1000);
    }
    
    // 模拟进度查询 (这里模拟了后端的进度回复)
    function simulateProgressCheck(startTime, counter) {
        // 实际项目中，这里应该发送AJAX请求到后端API获取真实进度
        // 由于当前后端没有专门的进度查询API，暂时只能使用模拟方式
        
        // 计算模拟进度百分比（基于时间和计数器）
        var elapsedTime = (new Date().getTime() - startTime) / 1000; // 经过的秒数
        
        // 计算模拟的行数和进度
        var estimatedRowsPerSecond = 80; // 假设每秒处理80行
        var processedRows = Math.floor(elapsedTime * estimatedRowsPerSecond);
        var progressPercent = Math.min(99, Math.floor(counter * 5)); // 不超过99%
        
        if (counter % 5 === 0) { // 每5秒更新一次日志
            // 模拟不同阶段的日志
            if (counter <= 5) {
                addLog('正在读取Excel数据...', false, 'info');
            } else if (counter <= 10) {
                addLog('正在验证数据格式...', false, 'info');
            } else if (counter <= 15) {
                addLog('正在初始化数据库连接...', false, 'info');
            } else {
                // 更新进度日志
                addLog(`已处理约 ${processedRows} 行数据 (${progressPercent}%)`, false, 'info');
                
                // 更新结果计数
                $('#records-count').text(processedRows);
                $('#success-count').text(processedRows);
            }
        }
        
        // 超过30秒没有完成，显示提示
        if (elapsedTime > 30 && counter % 10 === 0) {
            addLog('导入正在进行中，请耐心等待...', false, 'info');
        }
    }
    
    // 更新最终导入结果
    function updateFinalImportResult(response) {
        // 设置结果数据
        $('#files-count').text('1');
        $('#records-count').text(response.total_rows || 0);
        $('#success-count').text(response.success_count || 0);
        $('#failed-count').text(response.error_count || 0);
        
        // 获取Excel文件名
        var excelFileName = $('#excel-file-select option:selected').text();
        // 检查是否获取到有效的文件名
        if (!excelFileName || excelFileName.trim() === '' || excelFileName.includes('请选择')) {
            // 尝试从路径中提取文件名
            var filePath = $('#excel-file-select').val();
            if (filePath) {
                // 提取路径中的文件名部分
                var pathParts = filePath.split(/[\/\\]/);
                excelFileName = pathParts[pathParts.length - 1];
            } else {
                // 如果仍然无法获取，使用默认文本
                excelFileName = "所选Excel文件";
            }
        }
        
        // 添加完成日志
        var completionMessage = `导入完成！文件"${excelFileName}"成功导入${response.success_count || 0}条记录`;
        if (response.error_count && response.error_count > 0) {
            completionMessage += `，失败${response.error_count}条`;
        }
        addLog(completionMessage, true);
        
        // 如果有详细信息，显示它
        if (response.details) {
            addLog('耗时: ' + (response.details.duration || '未知') + ' 秒');
        }
        
        // 如果服务器返回了详细日志，添加到日志区域
        if (response.logs && response.logs.length > 0) {
            response.logs.forEach(function(log) {
                addLog(log.message, false, log.type || "info");
            });
        }
    }
    
    // 处理导入错误
    function handleImportError(response) {
        // 处理导入失败的情况
        addLog('导入失败: ' + (response.message || '未知错误'), false, "error");
        
        // 如果有错误信息，显示它
        if (response.error) {
            if (response.error.row) {
                addLog(`错误发生在第 ${response.error.row} 行`, false, "error");
            }
            if (response.error.message) {
                addLog('错误详情: ' + response.error.message, false, "error");
            }
            if (response.error.details) {
                addLog('技术详情: ' + response.error.details);
            }
        }
        
        // 如果有已处理的行信息，显示它
        if (response.processed_rows) {
            addLog(`已成功导入第 1 行至第 ${response.processed_rows} 行的数据`, false, "info");
        }
        
        // 如果服务器返回了详细日志，添加到日志区域
        if (response.logs && response.logs.length > 0) {
            response.logs.forEach(function(log) {
                addLog(log.message, false, log.type || "info");
            });
        }
    }
    
    // 处理AJAX错误
    function handleAjaxError(xhr, status, error) {
        // 处理AJAX错误
        var errorMessage = '';
        try {
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            } else if (xhr.responseText) {
                var response = JSON.parse(xhr.responseText);
                errorMessage = response.message || response.error || xhr.statusText;
            } else {
                errorMessage = error || '未知错误';
            }
        } catch (e) {
            errorMessage = '无法解析错误信息: ' + (error || '未知错误');
        }
        
        addLog('导入过程中发生错误: ' + errorMessage, false, "error");
        
        if (status === 'timeout') {
            addLog('请求超时，请稍后重试或减少导入数据量', false, "error");
        }
        
        // 如果响应中包含日志，显示它们
        try {
            if (xhr.responseJSON && xhr.responseJSON.logs) {
                xhr.responseJSON.logs.forEach(function(log) {
                    addLog(log.message, false, log.type || "info");
                });
            }
        } catch (e) {
            console.error('处理错误日志时出错:', e);
        }
        
        console.error('导入错误:', {
            status: xhr.status,
            statusText: xhr.statusText,
            error: error,
            response: xhr.responseText
        });
    }
    
    // 验证导入参数
    function validateImportParams() {
        var filePaths = $('#file-select').data('file-paths') || $('#file-path').val();
        var selectedDb = $('#db-select').val();
        var selectedTable = $('#table-select').val();
        var selectedExcel = $('#excel-file-select').val();
        var selectedSheet = $('#sheet-select').val();
        
        // 验证输入
        if (!filePaths) {
            addLog('错误: 请选择文件', true);
            return false;
        }
        
        if (!selectedDb) {
            addLog('错误: 请选择数据库', true);
            return false;
        }
        
        if (!selectedTable) {
            addLog('错误: 请选择目标表', true);
            return false;
        }
        
        if (!selectedExcel) {
            addLog('错误: 请选择要导入的Excel文件', true);
            return false;
        }
        
        if (!selectedSheet) {
            addLog('错误: 请选择要导入的工作表', true);
            return false;
        }
        
        // 验证条件完整性
        var selectedColumn = $('#column-select').val();
        var selectedCondition = $('#condition-select').val();
        
        if ((selectedColumn && !selectedCondition) || (!selectedColumn && selectedCondition)) {
            addLog('错误: 导入条件不完整，请同时选择条件列和条件类型', true);
            return false;
        }
        
        return true;
    }
    
    // 导出日志功能
    function exportLogs() {
        // 获取所有日志内容
        var logEntries = [];
        $('#import-log .log-entry').each(function() {
            logEntries.push($(this).text());
        });
        
        if (logEntries.length === 0) {
            alert('没有可导出的日志内容');
            return;
        }
        
        // 显示导出中状态
        var $btn = $('#export-log-btn');
        var originalText = $btn.text();
        $btn.prop('disabled', true).text('导出中...');
        
        // 发送日志内容到后端
        $.ajax({
            url: '/api/import/export-logs',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                logs: logEntries,
                title: '数据导入操作日志'
            }),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // 触发下载
                    if (response.download_url) {
                        addLog('成功: 日志已导出，正在下载文件...');
                        
                        // 如果服务器返回了文件路径，显示它
                        if (response.file_path) {
                            addLog('服务器文件位置: ' + response.file_path, true);
                        }
                        
                        // 创建隐藏的下载链接并点击
                        var $downloadLink = $('<a></a>')
                            .attr('href', response.download_url)
                            .attr('download', response.filename || 'import_logs.txt')
                            .css('display', 'none');
                        
                        $('body').append($downloadLink);
                        $downloadLink[0].click();
                        $downloadLink.remove();
                    } else {
                        addLog('成功: 日志已导出，但无法自动下载');
                    }
                } else {
                    addLog('错误: 导出日志失败 - ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                var errorMsg = '';
                try {
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMsg = xhr.responseJSON.message;
                    } else {
                        errorMsg = error || '未知错误';
                    }
                } catch (e) {
                    errorMsg = '无法解析错误信息';
                }
                
                addLog('错误: 导出日志失败 - ' + errorMsg);
            },
            complete: function() {
                // 恢复按钮状态
                $btn.prop('disabled', false).text(originalText);
            }
        });
    }
    
    // 添加日志函数
    function addLog(message, highlight = false, type = "info") {
        var now = new Date();
        var timeString = now.getHours().toString().padStart(2, '0') + ':' + 
                         now.getMinutes().toString().padStart(2, '0') + ':' + 
                         now.getSeconds().toString().padStart(2, '0');
        
        var cssClass = 'log-entry';
        
        // 根据类型添加样式
        if (type === "error" || highlight === true) {
            cssClass += ' log-entry-error';
        } else if (type === "warning") {
            cssClass += ' log-entry-warning';
        } else if (highlight) {
            cssClass += ' log-entry-highlight';
        }
        
        var logEntry = '<div class="' + cssClass + '">[' + timeString + '] ' + message + '</div>';
        $('#import-log').append(logEntry);
        
        // 自动滚动到底部
        var logContainer = document.getElementById('import-log');
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    // 全选所有Excel文件
    function selectAllFiles() {
        if (!window.allExcelFiles || window.allExcelFiles.length === 0) {
            addLog('警告: 没有可选择的Excel文件');
            return;
        }
        
        // 获取所有文件的ID
        window.selectedFiles = window.allExcelFiles.map(file => file.id);
        
        // 更新UI显示
        updateSelectedFiles();
        
        // 记录日志
        addLog('用户选择了所有Excel文件: ' + window.selectedFiles.length + '个文件');
    }

    // 初始化Excel列选择下拉框，填充A到CZ的列选项
    function initializeColumnSelect() {
        // 初始化条件列下拉框
        var $columnSelect = $('#column-select');
        $columnSelect.empty().append('<option value="" disabled selected>请选择列（如A、B、C）</option>');
        
        // 初始化补充列下拉框（1-3）
        var $supplementColumnSelect1 = $('#supplement-column-select-1');
        var $supplementColumnSelect2 = $('#supplement-column-select-2');
        var $supplementColumnSelect3 = $('#supplement-column-select-3');
        
        $supplementColumnSelect1.empty().append('<option value="" disabled selected>请选择列（如A、B、C）</option>');
        $supplementColumnSelect2.empty().append('<option value="" disabled selected>请选择列（如A、B、C）</option>');
        $supplementColumnSelect3.empty().append('<option value="" disabled selected>请选择列（如A、B、C）</option>');
        
        // 生成A到CZ的列选项
        for (var i = 0; i < 78; i++) { // A-Z (26) + AA-AZ (26) + BA-BZ (26) = 78
            var columnName = getExcelColumnName(i);
            
            // 添加到条件列下拉框
            $columnSelect.append(
                $('<option></option>')
                    .attr('value', i)
                    .text(columnName)
            );
            
            // 添加到补充列下拉框1
            $supplementColumnSelect1.append(
                $('<option></option>')
                    .attr('value', i)
                    .text(columnName)
            );
            
            // 添加到补充列下拉框2
            $supplementColumnSelect2.append(
                $('<option></option>')
                    .attr('value', i)
                    .text(columnName)
            );
            
            // 添加到补充列下拉框3
            $supplementColumnSelect3.append(
                $('<option></option>')
                    .attr('value', i)
                    .text(columnName)
            );
        }
        
        addLog('已初始化列选择下拉框，共78列（A到CZ）');
    }

    // 初始化打开Excel按钮状态
    updateOpenExcelButtonState();

    // 更新已选文件显示
    function updateSelectedFiles() {
        var $container = $('#selected-files-container');
        
        console.log("更新已选文件:", window.selectedFiles.length, "个文件");
        
        $container.empty();
        
        if (window.selectedFiles.length === 0) {
            return;
        }
        
        // 如果选择的文件太多，只显示一部分
        var maxDisplay = 20; // 最多显示20个文件标签
        var displayCount = Math.min(window.selectedFiles.length, maxDisplay);
        
        // 添加已选文件标签
        for (var i = 0; i < displayCount; i++) {
            var fileId = window.selectedFiles[i];
            var fileInfo = window.allExcelFiles.find(f => f.id === fileId);
            
            if (fileInfo) {
                var $tag = $(
                    '<div class="selected-file-tag" data-id="' + fileId + '">' +
                        fileInfo.text +
                        '<span class="remove-file" title="移除">&times;</span>' +
                    '</div>'
                );
                
                // 点击X移除文件
                $tag.find('.remove-file').on('click', function() {
                    var fileId = $(this).parent().data('id');
                    window.selectedFiles = window.selectedFiles.filter(id => id !== fileId);
                    updateSelectedFiles();
                });
                
                $container.append($tag);
            }
        }
        
        // 如果有更多文件，显示计数
        if (window.selectedFiles.length > maxDisplay) {
            var moreCount = window.selectedFiles.length - maxDisplay;
            var $moreTag = $(
                '<div class="selected-file-tag more-files">' +
                    '还有' + moreCount + '个文件...' +
                '</div>'
            );
            $container.append($moreTag);
        }
        
        // 显示已选文件数量
        if (window.selectedFiles.length > 0) {
            var $countTag = $(
                '<div class="selected-file-count">' +
                    '共选择了 ' + window.selectedFiles.length + ' 个文件' +
                '</div>'
            );
            $container.append($countTag);
        }
        
        // 将选择的文件ID写入隐藏的select元素，保持兼容性
        $('#file-select').val(window.selectedFiles);
        
        // 更新文件路径到按钮数据中
        updateFilePathForButtons(window.selectedFiles);
    }
    
    // 更新文件路径到按钮数据中
    function updateFilePathForButtons(selectedFiles) {
        if (selectedFiles.length === 0) {
            return;
        }
        
        var filePaths = selectedFiles.join(',');
        
        // 将文件路径存储在按钮的data属性中
        $('#preview-btn').data('file-paths', filePaths);
        $('#import-btn').data('file-paths', filePaths);
        
        // 兼容原有代码，更新隐藏的文件路径输入框
        $('#file-path').val(filePaths);
    }

    // 移除文件
    function removeFile(fileId) {
        // 从已选文件中移除
        window.selectedFiles = window.selectedFiles.filter(file => file.id !== fileId);
        
        // 更新UI显示
        updateSelectedFiles();
        
        // 更新按钮状态
        updateButtonStates();
        
        // 记录日志
        logAction('移除文件', `文件ID: ${fileId}`);
    }

    // 更新按钮状态
    function updateButtonStates() {
        const hasSelectedFiles = window.selectedFiles.length > 0;
        const hasSelectedTable = $('#table-select').val() !== '';
        const hasSelectedSheet = $('#sheet-select').val() !== '';
        
        // 更新预览按钮状态
        $('#preview-btn').prop('disabled', !(hasSelectedFiles && hasSelectedTable && hasSelectedSheet));
        
        // 更新导入按钮状态
        $('#import-btn').prop('disabled', !(hasSelectedFiles && hasSelectedTable && hasSelectedSheet));
    }
}); 