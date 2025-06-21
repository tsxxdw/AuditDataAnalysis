// EXCEL修复页面JS文件
$(document).ready(function() {
    // 存储已选列的数组
    window.selectedColumns = [];
    // 是否为本地环境的标志
    window.isLocalEnvironment = null;
    // 存储Excel列信息
    window.excelColumns = [];
    // 存储下载链接
    window.downloadUrl = null;
    
    // 初始化文件选择器
    initializeFileSelector();
    
    // 检查是否为本地环境
    checkLocalEnvironment();
    
    // 记录初始化完成
    addLog('系统准备就绪，等待修复操作...');
    
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
        
        // 如果选择了文件和工作表，加载Excel的列信息（用于字段去重）
        var excelFile = $('#excel-file-select').val();
        if (excelFile && selectedValue) {
            loadExcelColumns(excelFile, selectedValue);
        }
    });
    
    // 数据开始行选择事件
    $('#start-row-select').change(function() {
        var selectedValue = $(this).val();
        addLog('用户选择数据开始行: 第' + selectedValue + '行');
        
        // 如果已经选择了文件和工作表，重新加载Excel的列信息
        var excelFile = $('#excel-file-select').val();
        var sheetId = $('#sheet-select').val();
        if (excelFile && sheetId) {
            addLog('重新加载Excel列信息...');
            loadExcelColumns(excelFile, sheetId);
        }
    });
    
    // 操作类型选择事件
    $('#operation-type').change(function() {
        var selectedValue = $(this).val();
        var selectedText = $(this).find('option:selected').text();
        addLog('用户选择操作类型: ' + selectedText);
        
        // 如果选择了"字段去重"，显示字段列选择区域
        if (selectedValue === 'remove_duplicates') {
            $('#columns-selection-section').show();
        } else {
            $('#columns-selection-section').hide();
        }
    });
    
    // 打开Excel按钮点击事件
    $('#open-excel-btn').click(function() {
        addLog('用户点击: 打开EXCEL');
        openExcelFile();
    });
    
    // 修复按钮点击事件
    $('#repair-btn').click(function() {
        addLog('用户点击: 开始修复');
        showRepairConfirmation();
    });
    
    // 确认修复按钮点击事件
    $('#confirm-repair-btn').click(function() {
        addLog('用户点击: 确认修复');
        hideRepairConfirmation();
        executeRepair();
    });
    
    // 取消修复按钮点击事件
    $('#cancel-repair-btn, .close-modal').click(function() {
        addLog('用户点击: 取消修复');
        hideRepairConfirmation();
    });
    
    // 点击模态框背景关闭
    $(window).click(function(event) {
        if ($(event.target).hasClass('modal')) {
            hideRepairConfirmation();
        }
    });
    
    // 清空日志按钮点击事件
    $('#clear-log-btn').click(function() {
        addLog('用户点击: 清空日志');
        $('#repair-log').html('<div class="log-entry">系统准备就绪，等待修复操作...</div>');
    });
    
    // 导出日志按钮点击事件
    $('#export-log-btn').click(function() {
        addLog('用户点击: 导出日志');
        exportLogs();
    });
    
    // 下载按钮点击事件
    $('#download-btn').click(function() {
        addLog('用户点击: 下载修复后的文件');
        if (window.downloadUrl) {
            window.open(window.downloadUrl, '_blank');
        } else {
            addLog('错误: 没有可下载的文件', false, 'error');
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
                
                // 更新Excel文件下拉列表
                updateExcelFileSelect(excelFiles);
            },
            error: function(xhr) {
                console.error('获取文件列表失败:', xhr);
                addLog('错误: 获取文件列表失败 - ' + (xhr.responseJSON?.error || xhr.statusText), false, 'error');
            }
        });
    }
    
    // 更新Excel文件选择下拉框
    function updateExcelFileSelect(files) {
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = files.map(file => ({
            id: file.path,
            text: file.name,
            date: file.date,
            size: file.size,
            type: file.name.split('.').pop().toUpperCase()
        }));
        
        // 使用模板初始化下拉框组件
        const excelDropdown = initSearchableDropdownFromTemplate('.searchable-dropdown-container', dropdownData, {
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
            onChange: function(value, item) {
                if (value) {
                    // 触发Excel文件选择事件
                    $('#excel-file-select').val(value).trigger('change');
                }
            }
        });
        
        // 如果有文件，添加日志
        if (files.length > 0) {
            addLog('已加载 ' + files.length + ' 个Excel文件');
        } else {
            addLog('没有找到Excel文件', false, 'error');
        }
    }
    
    // 检查是否为本地环境（localhost或127.0.0.1）
    function checkLocalEnvironment() {
        // 获取当前主机名
        var host = window.location.hostname.toLowerCase();
        window.isLocalEnvironment = (host === 'localhost' || host === '127.0.0.1');
        
        // 设置按钮初始状态
        updateOpenExcelButtonState();
        
        // 添加提示信息
        if (!window.isLocalEnvironment) {
            $('#open-excel-btn').attr('title', '此功能仅在本地环境下可用');
        } else {
            $('#open-excel-btn').attr('title', '在Windows中打开所选的Excel文件');
        }
    }
    
    // 更新打开Excel按钮的状态
    function updateOpenExcelButtonState() {
        var $btn = $('#open-excel-btn');
        var selectedExcel = $('#excel-file-select').val();
        var selectedSheet = $('#sheet-select').val();
        
        // 禁用条件：非本地环境或未选择Excel文件或工作表
        var shouldDisable = !window.isLocalEnvironment || !selectedExcel || !selectedSheet;
        
        $btn.prop('disabled', shouldDisable);
    }
    
    // 打开Excel文件
    function openExcelFile() {
        // 获取选择的Excel文件和工作表ID
        const filePath = $('#excel-file-select').val();
        const sheetId = $('#sheet-select').val();
        
        if (!filePath) {
            addLog('错误: 请先选择Excel文件', false, 'error');
            return;
        }
        
        if (!sheetId) {
            addLog('错误: 请先选择工作表', false, 'error');
            return;
        }
        
        // 检查是否在本地环境
        if (!window.isLocalEnvironment) {
            addLog('错误: 此功能仅支持在本地环境使用', false, 'error');
            return;
        }
        
        addLog('正在请求打开Excel文件...');
        
        // 调用API打开Excel文件
        $.ajax({
            url: '/api/import/excel/open',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                file_path: filePath,
                sheet_id: sheetId
            }),
            success: function(response) {
                if (response.success) {
                    addLog('成功: ' + response.message, true, 'success');
                } else {
                    addLog('错误: ' + response.message, false, 'error');
                    if (!response.is_local) {
                        addLog('注意: 此功能仅支持在本地环境使用', false, 'error');
                    }
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                addLog('错误: 打开Excel文件失败 - ' + errorMsg, false, 'error');
                console.error('打开Excel文件请求失败:', xhr);
            }
        });
    }
    
    // 监听Excel文件和工作表选择变化，更新打开Excel按钮状态
    $('#excel-file-select, #sheet-select').change(function() {
        updateOpenExcelButtonState();
    });
    
    // 加载Excel文件的工作表
    function loadExcelFileSheets(filePath) {
        if (!filePath) {
            return;
        }
        
        // 清空工作表选择框并显示加载中
        $('#sheet-select').empty().append('<option value="" disabled selected>加载中...</option>');
        
        // 调用API获取工作表列表 - 将POST改为GET，并通过URL参数传递file_path
        $.ajax({
            url: '/api/import/excel/sheets',
            type: 'GET',
            data: { file_path: filePath },
            success: function(response) {
                if (response.success) {
                    // 更新工作表下拉框
                    updateSheetSelect(response.sheets);
                    addLog('成功加载工作表列表');
                } else {
                    addLog('错误: ' + response.message, false, 'error');
                    $('#sheet-select').empty().append('<option value="" disabled selected>加载失败</option>');
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                addLog('错误: 加载工作表失败 - ' + errorMsg, false, 'error');
                $('#sheet-select').empty().append('<option value="" disabled selected>加载失败</option>');
            }
        });
    }
    
    // 更新工作表选择下拉框
    function updateSheetSelect(sheets) {
        var $select = $('#sheet-select');
        $select.empty().append('<option value="" disabled selected>请选择工作表</option>');
        
        // 添加所有工作表
        sheets.forEach(function(sheet) {
            $select.append(`<option value="${sheet.id}">${sheet.name}</option>`);
        });
    }
    
    // 加载Excel文件的列信息
    function loadExcelColumns(filePath, sheetId) {
        if (!filePath || !sheetId) {
            return;
        }
        
        // 无论是否成功获取列信息，先初始化列选择下拉框
        initializeColumnsDropdown([]);
        
        // 获取用户选择的数据开始行
        const startRow = parseInt($('#start-row-select').val()) || 1;
        
        // 显示加载提示
        addLog(`正在加载Excel列信息(从第${startRow}行开始)...`);
        
        // 调用API获取Excel文件的列信息
        $.ajax({
            url: '/api/import/excel/preview',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                file_path: filePath,
                sheet_id: sheetId,
                start_row: startRow,
                row_count: 1
            }),
            success: function(response) {
                if (response.success && response.data && response.data.rows && response.data.rows.length > 0) {
                    // 保存列信息 - 使用第一行数据的列名
                    window.excelColumns = Object.values(response.data.rows[0]);
                    addLog(`成功加载Excel列信息: ${window.excelColumns.length}列，从第${startRow}行`, true, 'success');
                    
                    // 显示每列的名称
                    window.excelColumns.forEach((colName, index) => {
                        const colLetter = getExcelColumnName(index + 1);
                        addLog(`${colLetter}: ${colName}`);
                    });
                } else {
                    window.excelColumns = [];
                    addLog('警告: 无法加载Excel列信息，将使用列名代替', false, 'error');
                }
            },
            error: function(xhr) {
                window.excelColumns = [];
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                addLog('警告: 加载Excel列信息失败 - ' + errorMsg + '，将使用列名代替', false, 'error');
            }
        });
    }
    
    // 初始化列选择下拉框
    function initializeColumnsDropdown(columns) {
        // 清空已选列
        window.selectedColumns = [];
        $('#selected-columns-container').empty();
        
        // 转换数据结构以适应下拉框
        var $select = $('#columns-select');
        $select.empty().append('<option value="" disabled selected>请选择列</option>');
        
        // 创建Excel列名列表（A-Z, AA-BZ）
        const excelColumns = [];
        
        // 添加A-Z
        for (let i = 1; i <= 26; i++) {
            excelColumns.push(getExcelColumnName(i));
        }
        
        // 添加AA-BZ
        for (let i = 27; i <= 78; i++) {
            excelColumns.push(getExcelColumnName(i));
        }
        
        // 添加所有Excel列名到下拉框
        excelColumns.forEach(function(colName) {
            $select.append(`<option value="${colName}">${colName}</option>`);
        });
        
        // 列选择事件
        $select.off('change').on('change', function() {
            var selectedColumn = $(this).val();
            if (selectedColumn && !window.selectedColumns.includes(selectedColumn)) {
                window.selectedColumns.push(selectedColumn);
                updateSelectedColumns();
                
                // 如果有Excel列信息，显示更有意义的日志
                if (window.excelColumns && window.excelColumns.length > 0) {
                    const index = excelColumnToIndex(selectedColumn);
                    if (index >= 0 && index < window.excelColumns.length) {
                        addLog(`用户选择列: ${selectedColumn} (${window.excelColumns[index]})`);
                    } else {
                        addLog('用户选择列: ' + selectedColumn);
                    }
                } else {
                    addLog('用户选择列: ' + selectedColumn);
                }
                
                $(this).val(''); // 重置下拉框
            }
        });
    }
    
    // 更新已选列显示
    function updateSelectedColumns() {
        var $container = $('#selected-columns-container');
        $container.empty();
        
        // 添加已选列标签
        window.selectedColumns.forEach(function(column) {
            var $tag = $('<div class="selected-column-tag"></div>');
            $tag.append('<span>' + column + '</span>');
            $tag.append('<span class="remove-column" data-column="' + column + '">×</span>');
            $container.append($tag);
        });
        
        // 绑定移除列事件
        $('.remove-column').click(function() {
            var column = $(this).data('column');
            removeColumn(column);
        });
    }
    
    // 移除列
    function removeColumn(column) {
        // 从数组中移除
        window.selectedColumns = window.selectedColumns.filter(c => c !== column);
        
        // 更新UI
        updateSelectedColumns();
        
        // 如果有Excel列信息，显示更有意义的日志
        if (window.excelColumns && window.excelColumns.length > 0) {
            const index = excelColumnToIndex(column);
            if (index >= 0 && index < window.excelColumns.length) {
                addLog(`用户移除列: ${column} (${window.excelColumns[index]})`);
            } else {
                addLog('用户移除列: ' + column);
            }
        } else {
            addLog('用户移除列: ' + column);
        }
    }
    
    // 获取Excel列名（例如：1->A, 2->B, 27->AA）
    function getExcelColumnName(index) {
        let colName = '';
        while (index > 0) {
            let modulo = (index - 1) % 26;
            colName = String.fromCharCode(65 + modulo) + colName;
            index = Math.floor((index - modulo) / 26);
        }
        return colName;
    }
    
    // 将Excel列名转换为索引（例如：A->0, B->1, AA->26）
    function excelColumnToIndex(colName) {
        let result = 0;
        for (let i = 0; i < colName.length; i++) {
            result = result * 26 + (colName.charCodeAt(i) - 'A'.charCodeAt(0) + 1);
        }
        return result - 1; // 转为0-based索引
    }
    
    // 显示修复确认对话框
    function showRepairConfirmation() {
        // 验证参数
        const validationResult = validateRepairParams();
        if (!validationResult.valid) {
            addLog('错误: ' + validationResult.message, false, 'error');
            return;
        }
        
        // 获取参数
        const filePath = $('#excel-file-select').val();
        const sheetName = $('#sheet-select option:selected').text();
        const operationType = $('#operation-type').val();
        const operationText = $('#operation-type option:selected').text();
        const startRow = $('#start-row-select').val();
        
        // 填充确认对话框
        $('#confirm-excel').text(filePath.split('/').pop());
        $('#confirm-sheet').text(sheetName);
        $('#confirm-start-row').text('第' + startRow + '行');
        $('#confirm-operation').text(operationText);
        
        // 如果是字段去重，显示字段列信息
        if (operationType === 'remove_duplicates') {
            $('#confirm-columns-container').show();
            
            // 如果有Excel列信息，显示更有意义的信息
            if (window.excelColumns && window.excelColumns.length > 0) {
                // 将Excel列名（A, B, C等）转换为更有意义的描述
                const columnsInfo = window.selectedColumns.map(colName => {
                    const index = excelColumnToIndex(colName);
                    // 确保索引有效
                    if (index >= 0 && index < window.excelColumns.length) {
                        return `${colName} (${window.excelColumns[index]})`;
                    }
                    return colName;
                });
                
                $('#confirm-columns').text(columnsInfo.join(', '));
            } else {
                // 如果没有列信息，只显示列名
                $('#confirm-columns').text(window.selectedColumns.join(', '));
            }
        } else {
            $('#confirm-columns-container').hide();
        }
        
        // 显示对话框
        $('#repair-confirm-modal').css('display', 'block');
    }
    
    // 隐藏修复确认对话框
    function hideRepairConfirmation() {
        $('#repair-confirm-modal').css('display', 'none');
    }
    
    // 验证修复参数
    function validateRepairParams() {
        const filePath = $('#excel-file-select').val();
        if (!filePath) {
            return { valid: false, message: '请选择要修复的Excel文件' };
        }
        
        const sheetId = $('#sheet-select').val();
        if (!sheetId) {
            return { valid: false, message: '请选择要修复的工作表' };
        }
        
        const operationType = $('#operation-type').val();
        if (!operationType) {
            return { valid: false, message: '请选择修复操作类型' };
        }
        
        const startRow = parseInt($('#start-row-select').val());
        if (isNaN(startRow) || startRow < 1 || startRow > 10) {
            return { valid: false, message: '请选择有效的数据开始行（1-10行）' };
        }
        
        // 如果是字段去重，需要选择至少一个字段列
        if (operationType === 'remove_duplicates' && window.selectedColumns.length === 0) {
            return { valid: false, message: '请选择至少一个用于去重的字段列' };
        }
        
        return { valid: true };
    }
    
    // 执行修复操作
    function executeRepair() {
        // 获取参数
        const filePath = $('#excel-file-select').val();
        const sheetName = $('#sheet-select option:selected').text();
        const operationType = $('#operation-type').val();
        const startRow = parseInt($('#start-row-select').val()) || 1;
        
        // 显示进度区域
        $('.repair-status').show();
        $('.repair-result').hide();
        
        // 更新进度
        updateProgressBar(50);
        $('.status-text').text('正在处理Excel文件...');
        
        let apiEndpoint = '';
        let requestData = {};
        
        // 根据操作类型设置API端点和请求数据
        if (operationType === 'remove_blank_rows') {
            apiEndpoint = '/api/excel_repair/remove_blank_rows';
            requestData = {
                file_path: filePath,
                sheet_name: sheetName,
                start_row: startRow
            };
        } else if (operationType === 'remove_duplicates') {
            // 始终使用数字索引，不再尝试使用列名
            const numericIndexes = window.selectedColumns.map(colName => {
                return excelColumnToIndex(colName);
            });
            
            apiEndpoint = '/api/excel_repair/remove_duplicates';
            requestData = {
                file_path: filePath,
                sheet_name: sheetName,
                columns: numericIndexes,
                start_row: startRow
            };
            
            // 记录日志，显示使用了哪些列索引
            const columnInfo = window.selectedColumns.map((colName, i) => {
                const index = numericIndexes[i];
                if (window.excelColumns && window.excelColumns.length > index) {
                    return `${colName}(索引${index}: ${window.excelColumns[index]})`;
                }
                return `${colName}(索引${index})`;
            }).join(', ');
            
            addLog(`将使用以下列进行去重: ${columnInfo}`, true);
        }
        
        // 输出请求详情到日志
        addLog(`发送请求到: ${apiEndpoint}，数据开始行: ${startRow}`, false);
        
        // 发送请求
        $.ajax({
            url: apiEndpoint,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                if (response.success) {
                    // 更新进度
                    updateProgressBar(100);
                    $('.status-text').text('修复完成!');
                    addLog('修复完成: ' + response.message, true, 'success');
                    
                    // 保存下载链接
                    window.downloadUrl = response.download_url;
                    
                    // 更新结果区域
                    updateRepairResult(response);
                    
                    // 自动下载文件
                    window.open(response.download_url, '_blank');
                } else {
                    handleRepairError(response.message);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '未知错误';
                handleRepairError(errorMsg);
            }
        });
    }
    
    // 更新进度条
    function updateProgressBar(percent) {
        $('.progress-fill').css('width', percent + '%');
        $('.progress-text').text(Math.round(percent) + '%');
    }
    
    // 处理修复错误
    function handleRepairError(message) {
        updateProgressBar(0);
        $('.status-text').text('修复失败');
        addLog('错误: 修复失败 - ' + message, false, 'error');
        $('.repair-result').hide();
    }
    
    // 更新修复结果
    function updateRepairResult(data) {
        if (!data) return;
        
        $('#original-rows').text(data.original_rows || 0);
        $('#processed-rows').text(data.processed_rows || 0);
        $('#removed-rows').text(data.removed_rows || 0);
        
        // 显示结果区域
        $('.repair-result').show();
    }
    
    // 导出日志
    function exportLogs() {
        const logContent = $('#repair-log').text();
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = 'excel_repair_log_' + timestamp + '.txt';
        
        // 创建Blob对象
        const blob = new Blob([logContent], { type: 'text/plain' });
        
        // 创建下载链接
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // 清理
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 0);
        
        addLog('日志已导出: ' + filename, true);
    }
    
    // 添加日志
    function addLog(message, highlight = false, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = $('<div class="log-entry"></div>');
        logEntry.text(`[${timestamp}] ${message}`);
        
        // 添加样式
        if (highlight) {
            logEntry.addClass('highlight');
        }
        
        if (type === 'error') {
            logEntry.addClass('error');
        } else if (type === 'success') {
            logEntry.addClass('success');
        }
        
        // 添加到日志容器
        $('#repair-log').append(logEntry);
        
        // 滚动到底部
        const logContainer = document.getElementById('repair-log');
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}); 