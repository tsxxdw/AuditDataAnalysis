// 数据导入页面JS文件(index_import)
$(document).ready(function() {
    // 存储表字段信息的全局变量
    window.tableFields = null;
    // 是否为本地环境的标志
    window.isLocalEnvironment = null;
    // 存储原始预览表格的HTML
    window.originalTableHtml = '';
    
    // 初始化时保存原始表格HTML
    window.originalTableHtml = $('.preview-table').html();
    
    // 初始化文件选择器
    initializeFileSelector();
    
    // 初始化数据库类型下拉框
    initializeDatabaseTypes();
    
    // 检查是否为本地环境
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
        addLog('用户点击: 打开EXCEL');
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
    
    // 监听文件选择变化
    $('#file-select').on('change', function() {
        var selectedData = $(this).select2('data');
        if (selectedData && selectedData.length > 0) {
            var fileNames = selectedData.map(function(file) {
                return file.text;
            }).join(', ');
            
            if (selectedData.length === 1) {
                addLog('用户选择文件: ' + fileNames);
            } else {
                addLog('用户选择多个文件: ' + selectedData.length + '个文件 (' + fileNames + ')');
            }
            
            updateSelectedFiles();
        }
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
        // 初始化Select2
        $('#file-select').select2(getSelect2Options());
        
        // 记录Select2初始化完成
        console.log("Select2初始化完成");
        
        // 监听选择变化事件
        $('#file-select').on('change', function() {
            console.log("Select2选择变化事件触发");
            updateSelectedFiles();
        });
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
        var selectedExcel = $('#excel-file-select').val();
        var selectedSheet = $('#sheet-select').val();
        
        if (!selectedExcel) {
            addLog('错误: 请选择要打开的Excel文件');
            return;
        }
        
        // 禁用按钮，防止重复点击
        $('#open-excel-btn').prop('disabled', true).text('打开中...');
        
        // 添加一条日志
        addLog(`尝试打开Excel文件: ${selectedExcel}`);
        
        // 调用API打开Excel文件
        $.ajax({
            url: '/api/import/excel/open',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                file_path: selectedExcel,
                sheet_id: selectedSheet
            }),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // 基本成功消息
                    addLog('成功: ' + response.message);
                    
                    // 如果有WPS信息，显示使用的是哪种程序
                    if (response.hasOwnProperty('using_wps')) {
                        if (response.using_wps) {
                            addLog('📊 使用WPS打开Excel文件', true);
                        } else {
                            addLog('📊 使用Microsoft Excel打开文件', true);
                        }
                    }
                } else {
                    if (!response.is_local) {
                        addLog('错误: 此功能仅支持本地环境');
                    } else if (!response.is_windows) {
                        addLog('错误: 此功能仅支持Windows系统');
                    } else {
                        addLog('错误: ' + response.message);
                        
                        // 如果有详细错误信息，显示它
                        if (response.details) {
                            addLog('详情: ' + response.details);
                        }
                        
                        // 记录当前文件路径，帮助排查问题
                        console.log('文件路径:', selectedExcel);
                    }
                }
            },
            error: function(xhr, status, error) {
                var errorMsg = '';
                var detailMsg = '';
                
                try {
                    // 尝试解析错误响应
                    if (xhr.responseJSON) {
                        if (xhr.responseJSON.message) {
                            errorMsg = xhr.responseJSON.message;
                        }
                        if (xhr.responseJSON.details) {
                            detailMsg = xhr.responseJSON.details;
                        }
                    } else if (xhr.status === 403) {
                        errorMsg = '访问被拒绝，可能是文件路径不在允许的范围内';
                    } else {
                        errorMsg = error || '未知错误';
                    }
                } catch (e) {
                    errorMsg = '无法解析错误信息: ' + e.message;
                }
                
                addLog('错误: 打开Excel文件失败 - ' + errorMsg);
                if (detailMsg) {
                    addLog('详情: ' + detailMsg);
                }
                
                // 记录到控制台，便于调试
                console.error('Excel文件打开错误:', {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    error: error,
                    response: xhr.responseText,
                    filePath: selectedExcel,
                    sheetId: selectedSheet
                });
            },
            complete: function() {
                // 恢复按钮状态
                $('#open-excel-btn').prop('disabled', !window.isLocalEnvironment).text('打开EXCEL');
                updateOpenExcelButtonState();
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
        
        // 从后端API获取表列表
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
    
    // 加载选择的Excel文件
    function loadSelectedExcelFiles() {
        var selectedFiles = $('#file-select').select2('data');
        
        if (selectedFiles.length === 0) {
            addLog('错误: 请先选择Excel文件');
            return;
        }
        
        // 禁用按钮，防止重复点击
        $('#load-excel-btn').prop('disabled', true).text('加载中...');
        
        // 收集文件路径
        var filePaths = selectedFiles.map(function(file) {
            return file.id;
        });
        
        addLog('正在加载Excel文件内容，共' + filePaths.length + '个文件...');
        
        // 调用API处理选择的Excel文件
        $.ajax({
            url: '/api/import/excel/selected-files',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ file_paths: filePaths }),
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
    
    // Select2配置选项
    function getSelect2Options() {
        return {
            placeholder: '搜索并选择Excel文件...',
            allowClear: true,
            ajax: {
                url: '/api/files/list',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        search: params.term // 搜索参数
                    };
                },
                processResults: function(data) {
                    console.log("Select2处理API结果, 获取到文件数量:", data.length);
                    
                    // 转换API返回的数据为Select2需要的格式
                    var results = data.map(function(file) {
                        // 只处理Excel文件
                        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                            return {
                                id: file.path,
                                text: file.name,
                                date: file.date,
                                url: file.url
                            };
                        }
                        return null;
                    }).filter(function(item) {
                        return item !== null;
                    });
                    
                    // 按日期倒序排序
                    results.sort(function(a, b) {
                        return new Date(b.date) - new Date(a.date);
                    });
                    
                    console.log("处理后的Excel文件数量:", results.length);
                    
                    return {
                        results: results
                    };
                },
                cache: true
            },
            templateResult: formatFileItem,
            templateSelection: formatFileSelection
        };
    }
    
    // 格式化下拉选项，显示文件名和时间
    function formatFileItem(file) {
        if (!file.id) return file.text;
        
        var $fileElement = $(
            '<div class="file-list-item">' +
                '<span class="file-name">' + file.text + '</span>' +
                '<span class="file-date">' + file.date + '</span>' +
            '</div>'
        );
        
        return $fileElement;
    }
    
    // 格式化已选项
    function formatFileSelection(file) {
        return file.text || file.text;
    }
    
    // 更新已选文件显示
    function updateSelectedFiles() {
        var selectedFiles = $('#file-select').select2('data');
        var $container = $('#selected-files-container');
        
        console.log("更新已选文件:", selectedFiles.length, "个文件");
        
        $container.empty();
        
        if (selectedFiles.length === 0) {
            return;
        }
        
        // 如果选择的文件太多，只显示一部分
        var maxDisplay = 20; // 最多显示20个文件标签
        var displayCount = Math.min(selectedFiles.length, maxDisplay);
        
        // 添加已选文件标签
        for (var i = 0; i < displayCount; i++) {
            var file = selectedFiles[i];
            var $tag = $(
                '<div class="selected-file-tag" data-id="' + file.id + '">' +
                    file.text +
                    '<span class="remove-file" title="移除">&times;</span>' +
                '</div>'
            );
            
            // 点击X移除文件
            $tag.find('.remove-file').on('click', function() {
                var fileId = $(this).parent().data('id');
                var values = $('#file-select').val();
                values = values.filter(function(value) {
                    return value !== fileId;
                });
                $('#file-select').val(values).trigger('change');
            });
            
            $container.append($tag);
        }
        
        // 如果有更多文件，显示计数
        if (selectedFiles.length > maxDisplay) {
            var moreCount = selectedFiles.length - maxDisplay;
            var $moreTag = $(
                '<div class="selected-file-tag more-files">' +
                    '还有' + moreCount + '个文件...' +
                '</div>'
            );
            $container.append($moreTag);
        }
        
        // 显示已选文件数量
        if (selectedFiles.length > 0) {
            var $countTag = $(
                '<div class="selected-file-count">' +
                    '共选择了 ' + selectedFiles.length + ' 个文件' +
                '</div>'
            );
            $container.append($countTag);
        }
        
        // 更新文件路径到按钮数据中
        updateFilePathForButtons(selectedFiles);
    }
    
    // 更新文件路径到按钮数据中
    function updateFilePathForButtons(selectedFiles) {
        if (selectedFiles.length === 0) {
            return;
        }
        
        var filePathsArray = selectedFiles.map(function(file) {
            return file.id;
        });
        
        var filePaths = filePathsArray.join(',');
        
        // 将文件路径存储在按钮的data属性中
        $('#preview-btn').data('file-paths', filePaths);
        $('#import-btn').data('file-paths', filePaths);
        
        // 兼容原有代码，更新隐藏的文件路径输入框
        $('#file-path').val(filePaths);
    }
    
    // 文件浏览按钮点击事件（实际功能需要后端支持）
    // 保留但不使用，为了兼容性
    $('#browse-btn').click(function() {
        // 这里只是界面演示，实际操作需要后端API支持
        alert('浏览文件功能已替换为下拉选择器');
    });
    
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
        
        // 添加完成日志
        var completionMessage = `导入完成！成功导入${response.success_count || 0}条记录`;
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
        // 显示加载中状态
        var $btn = $('#select-all-btn');
        var originalText = $btn.text();
        $btn.prop('disabled', true).text('加载中...');
        
        // 记录调试信息
        console.log("开始获取所有Excel文件...");
        addLog('正在获取所有Excel文件...');
        
        // 调用API获取所有Excel文件
        $.ajax({
            url: '/api/files/list',
            method: 'GET',
            dataType: 'json',
            // 移除可能不支持的参数
            // data: { fileType: 'excel' },
            success: function(data) {
                console.log("获取文件列表成功，文件数量:", data.length);
                
                // 过滤Excel文件
                var excelFiles = data.filter(function(file) {
                    return file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls');
                });
                
                console.log("过滤得到Excel文件数量:", excelFiles.length);
                
                if (excelFiles.length === 0) {
                    addLog('提示: 未找到Excel文件');
                    return;
                }
                
                // 提取文件ID数组
                var fileIds = excelFiles.map(function(file) {
                    return file.path;
                });
                
                console.log("要选择的文件IDs:", fileIds);
                
                try {
                    // 清空当前选择
                    $('#file-select').val(null).trigger('change');
                    
                    // 创建Select2可用的选项对象
                    var newOptions = [];
                    excelFiles.forEach(function(file) {
                        // 检查选项是否已存在
                        if (!$('#file-select').find("option[value='" + file.path + "']").length) {
                            // 创建新选项
                            var newOption = new Option(file.name, file.path, true, true);
                            newOptions.push(newOption);
                        } else {
                            // 如果选项已存在，只需选中它
                            $('#file-select').find("option[value='" + file.path + "']").prop('selected', true);
                        }
                    });
                    
                    // 添加新选项（如果有）
                    if (newOptions.length > 0) {
                        $('#file-select').append(newOptions);
                    }
                    
                    // 触发Select2更新
                    $('#file-select').trigger('change');
                    
                    addLog(`已全选 ${excelFiles.length} 个Excel文件`);
                    console.log("全选完成");
                } catch (e) {
                    console.error("选择文件时出错:", e);
                    addLog('错误: 选择文件失败 - ' + e.message);
                }
            },
            error: function(xhr, status, error) {
                console.error("获取文件列表失败:", error);
                addLog('错误: 获取文件列表失败 - ' + (xhr.responseJSON?.error || error));
            },
            complete: function() {
                // 恢复按钮状态
                $btn.prop('disabled', false).text(originalText);
            }
        });
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
}); 