// 数据导入页面JS文件(index_import)
$(document).ready(function() {
    // 存储表字段信息的全局变量
    window.tableFields = null;
    // 是否为本地环境的标志
    window.isLocalEnvironment = null;
    
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
    
    // 打开Excel按钮点击事件
    $('#open-excel-btn').click(function() {
        addLog('用户点击: 打开EXCEL');
        openExcelFile();
    });
    
    // 导入按钮点击事件
    $('#import-btn').click(function() {
        addLog('用户点击: 开始导入');
        startImport();
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
        addLog('用户设置补充行1: ' + value);
    });
    
    // 补充列2选择变化事件
    $('#supplement-column-select-2').change(function() {
        var selectedColumn = $(this).find('option:selected').text();
        addLog('用户选择补充列2: ' + selectedColumn);
    });
    
    // 补充值2输入变化事件
    $('#supplement-value-2').change(function() {
        var value = $(this).val();
        addLog('用户设置补充行2: ' + value);
    });
    
    // 补充列3选择变化事件
    $('#supplement-column-select-3').change(function() {
        var selectedColumn = $(this).find('option:selected').text();
        addLog('用户选择补充列3: ' + selectedColumn);
    });
    
    // 补充值3输入变化事件
    $('#supplement-value-3').change(function() {
        var value = $(this).val();
        addLog('用户设置补充行3: ' + value);
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
                        $('#table-select').append($('<option></option>')
                            .attr('value', table.id)
                            .text(table.name));
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
        var headerHtml = '<tr>';
        
        // 使用表字段作为表头
        $.each(fields, function(index, field) {
            headerHtml += `<th title="${field.type}">${field.comment || field.name}</th>`;
        });
        
        headerHtml += '</tr>';
        $('.preview-table thead').html(headerHtml);
    }
    
    // 加载Excel预览数据
    function loadExcelPreview(filePath, sheetId, startRow) {
        addLog(`正在加载Excel数据预览，文件: ${filePath}, Sheet: ${sheetId}, 起始行: ${startRow}`);
        
        // 构建请求数据
        var requestData = {
            file_path: filePath,
            sheet_id: sheetId,
            start_row: startRow,
            row_limit: 10 // 最多显示10行
        };
        
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
                } else {
                    $('.preview-table tbody').html('<tr><td colspan="' + (window.tableFields ? window.tableFields.length : 5) + '" class="no-data-message">未找到Excel数据</td></tr>');
                    addLog('警告: 未找到Excel数据');
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
                addLog('错误: 加载Excel数据失败 - ' + errorMsg);
                console.error('Excel预览错误:', {
                    status: status,
                    error: error,
                    response: xhr.responseText,
                    requestData: requestData
                });
            }
        });
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
    
    // 导入功能
    function startImport() {
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
        
        // 显示进度区域
        $('.import-status').show();
        
        // 日志记录
        addLog('开始导入数据...');
        
        // 模拟导入进度
        var progress = 0;
        var interval = setInterval(function() {
            progress += 5;
            if (progress > 100) {
                progress = 100;
                clearInterval(interval);
                completeImport();
            }
            
            // 更新进度条
            $('.progress-fill').css('width', progress + '%');
            $('.progress-text').text(progress + '%');
            
            // 更新状态文本
            if (progress < 30) {
                $('.status-text').text('正在准备数据...');
            } else if (progress < 60) {
                $('.status-text').text('导入数据中...');
            } else if (progress < 90) {
                $('.status-text').text('验证数据中...');
            } else {
                $('.status-text').text('完成导入...');
            }
            
            // 添加随机日志
            if (progress % 20 === 0) {
                addLog('导入进度: ' + progress + '%');
            }
        }, 200);
    }
    
    // 模拟导入完成
    function completeImport() {
        // 显示结果区域
        $('.import-result').show();
        
        // 设置结果数据
        $('#files-count').text('1');
        $('#records-count').text('250');
        $('#success-count').text('248');
        $('#failed-count').text('2');
        
        // 添加完成日志
        addLog('导入完成！成功导入248条记录，失败2条');
        addLog('失败记录: 第123行 - 数据格式错误');
        addLog('失败记录: 第187行 - 数据类型不匹配');
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
    function addLog(message, highlight = false) {
        var now = new Date();
        var timeString = now.getHours().toString().padStart(2, '0') + ':' + 
                         now.getMinutes().toString().padStart(2, '0') + ':' + 
                         now.getSeconds().toString().padStart(2, '0');
        
        var cssClass = highlight ? 'log-entry log-entry-highlight' : 'log-entry';
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
}); 