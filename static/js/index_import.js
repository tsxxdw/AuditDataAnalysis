// 数据导入页面JS文件(index_import)
$(document).ready(function() {
    // 初始化文件选择器
    initializeFileSelector();
    
    // 初始化文件选择器
    function initializeFileSelector() {
        // 初始化Select2
        $('#file-select').select2(getSelect2Options());
        
        // 监听选择变化事件
        $('#file-select').on('change', function() {
            updateSelectedFiles();
        });
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
        
        $container.empty();
        
        if (selectedFiles.length === 0) {
            return;
        }
        
        // 添加已选文件标签
        $.each(selectedFiles, function(index, file) {
            var $tag = $(
                '<div class="selected-file-tag" data-id="' + file.id + '">' +
                    file.text +
                    '<span class="remove-file" title="移除">&times;</span>' +
                '</div>'
            );
            
            // 点击X移除文件
            $tag.find('.remove-file').on('click', function() {
                var values = $('#file-select').val();
                values = values.filter(function(value) {
                    return value !== file.id;
                });
                $('#file-select').val(values).trigger('change');
            });
            
            $container.append($tag);
        });
        
        // 更新文件路径到预览按钮和导入按钮的数据中
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
    
    // 数据库下拉框变化事件
    $('#db-select').change(function() {
        var selectedDb = $(this).val();
        
        // 清空并重新加载表下拉框
        $('#table-select').empty().append('<option value="" disabled selected>加载中...</option>');
        
        // 模拟异步加载表列表
        setTimeout(function() {
            $('#table-select').empty();
            $('#table-select').append('<option value="" disabled selected>请选择表</option>');
            
            // 添加模拟的表选项
            if (selectedDb === 'mysql') {
                $('#table-select').append('<option value="table1">客户信息表</option>');
                $('#table-select').append('<option value="table2">订单表</option>');
                $('#table-select').append('<option value="table3">产品表</option>');
            } else if (selectedDb === 'sqlserver') {
                $('#table-select').append('<option value="table1">用户表</option>');
                $('#table-select').append('<option value="table2">销售表</option>');
            } else if (selectedDb === 'oracle') {
                $('#table-select').append('<option value="table1">员工表</option>');
                $('#table-select').append('<option value="table2">部门表</option>');
                $('#table-select').append('<option value="table3">项目表</option>');
            }
        }, 500);
    });
    
    // 预览按钮点击事件
    $('#preview-btn').click(function() {
        var filePaths = $(this).data('file-paths') || $('#file-path').val();
        var selectedDb = $('#db-select').val();
        var selectedTable = $('#table-select').val();
        
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
        
        // 显示加载中
        $('.preview-table tbody').html('<tr><td colspan="5" class="no-data-message">加载数据中...</td></tr>');
        
        // 模拟异步加载数据预览
        addLog('正在从文件加载数据预览: ' + filePaths);
        
        // 模拟数据加载延迟
        setTimeout(function() {
            // 更新表头
            var headerHtml = '<tr>';
            headerHtml += '<th>客户ID</th>';
            headerHtml += '<th>姓名</th>';
            headerHtml += '<th>电话</th>';
            headerHtml += '<th>邮箱</th>';
            headerHtml += '<th>注册日期</th>';
            headerHtml += '</tr>';
            $('.preview-table thead').html(headerHtml);
            
            // 更新表格数据
            var tableHtml = '';
            for (var i = 1; i <= 5; i++) {
                tableHtml += '<tr>';
                tableHtml += '<td>CUST' + (1000 + i) + '</td>';
                tableHtml += '<td>用户' + i + '</td>';
                tableHtml += '<td>1381234' + (1000 + i) + '</td>';
                tableHtml += '<td>user' + i + '@example.com</td>';
                tableHtml += '<td>2023-0' + i + '-01</td>';
                tableHtml += '</tr>';
            }
            $('.preview-table tbody').html(tableHtml);
            
            // 模拟加载工作表
            $('#sheet-select').empty();
            $('#sheet-select').append('<option value="sheet1" selected>Sheet1</option>');
            $('#sheet-select').append('<option value="sheet2">Sheet2</option>');
            
            addLog('数据预览加载完成，共加载5条记录');
        }, 1000);
    });
    
    // 导入按钮点击事件
    $('#import-btn').click(function() {
        var filePaths = $(this).data('file-paths') || $('#file-path').val();
        var selectedDb = $('#db-select').val();
        var selectedTable = $('#table-select').val();
        var selectedSheet = $('#sheet-select').val();
        var headerRow = $('#header-row').val();
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
        
        if (!selectedSheet) {
            addLog('错误: 请选择工作表');
            return;
        }
        
        // 显示进度区域
        $('.import-status').show();
        
        // 日志记录
        addLog('开始导入数据...');
        addLog('目标数据库: ' + selectedDb);
        addLog('目标表: ' + selectedTable);
        addLog('导入文件: ' + filePaths);
        
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
    });
    
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
    
    // 清空日志按钮
    $('#clear-log-btn').click(function() {
        $('#import-log').html('<div class="log-entry">日志已清空</div>');
    });
    
    // 导出日志按钮
    $('#export-log-btn').click(function() {
        alert('导出日志功能需要后端支持，此处仅为界面演示');
    });
    
    // 添加日志函数
    function addLog(message) {
        var now = new Date();
        var timeString = now.getHours().toString().padStart(2, '0') + ':' + 
                         now.getMinutes().toString().padStart(2, '0') + ':' + 
                         now.getSeconds().toString().padStart(2, '0');
        
        var logEntry = '<div class="log-entry">[' + timeString + '] ' + message + '</div>';
        $('#import-log').append(logEntry);
        
        // 自动滚动到底部
        var logContainer = document.getElementById('import-log');
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}); 