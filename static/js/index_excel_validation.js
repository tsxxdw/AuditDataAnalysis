/**
 * EXCEL校验页面JS
 */
$(document).ready(function() {
    // 元素获取
    const $sheetIndexSelect = $('#sheetIndexSelect');
    const $readRowSelect = $('#readRowSelect');
    const $validationTypeSelect = $('#validationTypeSelect');
    const $loadExcelBtn = $('#loadExcelBtn');
    const $resultsSection = $('#resultsSection');
    const $resultsSummary = $('#resultsSummary');
    const $resultsTable = $('#resultsTable');
    const $exportBtn = $('#exportBtn');
    const $selectedFilesContainer = $('#selected-files-container');
    const $excelInfoSection = $('#excelInfoSection');
    const $excelInfoContainer = $('#excelInfoContainer');
    
    // 当前文件
    let currentFile = null;
    let dropdownInstance = null;
    
    // 用于存储已选文件
    let selectedFiles = [];
    // 存储加载的Excel信息
    let loadedExcelInfo = [];
    
    // 用于模拟Excel工作表名称
    const mockSheetNames = {
        1: ["Sheet1", "数据表1", "产品明细", "用户信息", "财务数据", "配置", "报表", "历史数据", "统计", "原始数据"],
        2: ["Sheet2", "数据表2", "年度统计", "月度报表", "客户信息", "订单记录", "库存", "价格表", "计划表", "日志"],
        3: ["Sheet3", "数据表3", "部门信息", "员工档案", "采购记录", "销售记录", "项目数据", "预算", "资产", "成本分析"],
    };
    
    // 初始化文件选择器
    initializeFileSelector();
    
    // 全选按钮点击事件
    $('#select-all-btn').click(function() {
        selectAllFiles();
    });
    
    // 监听工作表序号选择变化
    $sheetIndexSelect.on('change', function() {
        updateButtonState();
    });
    
    // 监听读取行选择变化
    $readRowSelect.on('change', function() {
        updateButtonState();
    });
    
    // 监听校验类型选择变化
    $validationTypeSelect.on('change', function() {
        updateButtonState();
    });
    
    // 加载Excel信息按钮点击事件
    $loadExcelBtn.on('click', function() {
        if (selectedFiles.length === 0) {
            alert('请先选择Excel文件');
            return;
        }
        
        const sheetIndex = $sheetIndexSelect.val();
        if (!sheetIndex) {
            alert('请选择sheet');
            return;
        }
        
        const readRow = $readRowSelect.val();
        if (!readRow) {
            alert('请选择读取的行');
            return;
        }
        
        const validationType = $validationTypeSelect.val();
        if (!validationType) {
            alert('请选择校验的事项');
            return;
        }

        // 显示加载指示器
        $loadExcelBtn.prop('disabled', true).text('加载中...');
        
        // 获取选中文件的路径
        const filePaths = selectedFiles.map(file => file.id);
        
        // 调用API获取文件信息
        $.ajax({
            url: '/api/excel/load_files_info',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                filePaths: filePaths,
                sheetIndex: sheetIndex
            }),
            success: function(response) {
                if (response.success) {
                    // 存储加载的Excel信息
                    loadedExcelInfo = response.filesInfo;
                    
                    // 显示Excel信息
                    displayExcelInfo(loadedExcelInfo);
                    
                    // 显示Excel信息区域
                    $excelInfoSection.show();
                } else {
                    alert('加载Excel信息失败: ' + response.message);
                }
                
                // 恢复按钮状态
                $loadExcelBtn.prop('disabled', false).text('加载EXCEL信息');
            },
            error: function(xhr) {
                console.error('加载Excel信息失败:', xhr);
                alert('加载Excel信息失败，请稍后重试');
                
                // 恢复按钮状态
                $loadExcelBtn.prop('disabled', false).text('加载EXCEL信息');
            }
        });
    });
    
    // 显示Excel信息
    function displayExcelInfo(filesInfo) {
        // 清空Excel信息容器
        $excelInfoContainer.empty();
        
        console.log("显示Excel信息，文件数量:", filesInfo.length);
        
        // 遍历文件信息并创建显示卡片
        filesInfo.forEach(function(fileInfo) {
            const fileName = fileInfo.fileName;
            const filePath = fileInfo.filePath;
            const sheets = fileInfo.sheets;
            const currentSheet = fileInfo.currentSheet;
            const sheetExists = fileInfo.sheetExists;
            const requestedSheetIndex = fileInfo.requestedSheetIndex;
            
            console.log(`创建文件卡片: ${fileName}, 路径: ${filePath}, 工作表存在: ${sheetExists}`);
            
            // 创建工作表选项HTML
            let sheetsOptionsHtml = '';
            
            // 如果请求的工作表不存在，添加一个提示选项
            if (!sheetExists) {
                sheetsOptionsHtml += `<option value="not-exist" selected>不存在第${requestedSheetIndex}个sheet</option>`;
            }
            
            // 添加所有存在的工作表 - 显示真实的工作表名称
            sheetsOptionsHtml += sheets.map(sheet => `
                <option value="${sheet.index}" ${sheetExists ? (currentSheet && currentSheet.index === sheet.index ? 'selected' : '') : ''}>
                    ${sheet.name}
                </option>
            `).join('');
            
            // 创建文件卡片
            const fileCardHtml = `
                <div class="excel-file-card" data-file-path="${filePath}">
                    <div class="excel-file-header">
                        <span class="excel-file-name">${fileName}</span>
                    </div>
                    <div class="excel-file-content">
                        <div class="form-group">
                            <label>工作表:</label>
                            <select class="sheet-select form-select">
                                ${sheetsOptionsHtml}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>读取的行:</label>
                            <select class="row-select form-select">
                                <option value="1" selected>1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                            </select>
                        </div>
                    </div>
                </div>
            `;
            
            // 添加到容器
            $excelInfoContainer.append(fileCardHtml);
            
            // 获取刚刚创建的卡片元素
            const $fileCard = $excelInfoContainer.find(`.excel-file-card[data-file-path="${filePath}"]`).last();
            
            // 如果找不到卡片元素，可能是文件路径中有特殊字符
            if ($fileCard.length === 0) {
                console.error(`无法找到刚刚创建的文件卡片: ${filePath}`);
            } else {
                console.log(`成功添加文件卡片: ${fileName}, 工作表选项数量: ${$fileCard.find('.sheet-select option').length}`);
            }
            
            // 监听工作表选择变化
            $fileCard.find('.sheet-select').on('change', function() {
                const sheetValue = $(this).val();
                
                // 如果选择了不存在的sheet，则不更新
                if (sheetValue === 'not-exist') {
                    return;
                }
                
                const sheetIndex = parseInt(sheetValue);
                const selectedSheet = sheets.find(s => s.index == sheetIndex);
                
                // 更新文件信息中的当前工作表
                const fileIndex = loadedExcelInfo.findIndex(f => f.filePath === filePath);
                if (fileIndex !== -1 && selectedSheet) {
                    loadedExcelInfo[fileIndex].currentSheet = selectedSheet;
                    loadedExcelInfo[fileIndex].sheetExists = true;
                    
                    console.log(`更新文件 ${fileName} 的当前工作表为: ${selectedSheet.name}`);
                }
            });
            
            // 监听读取行选择变化
            $fileCard.find('.row-select').on('change', function() {
                const rowIndex = $(this).val();
                
                // 更新文件信息中的读取行
                const fileIndex = loadedExcelInfo.findIndex(f => f.filePath === filePath);
                if (fileIndex !== -1) {
                    loadedExcelInfo[fileIndex].readRow = rowIndex;
                    console.log(`更新文件 ${fileName} 的读取行为: ${rowIndex}`);
                }
            });
        });
        
        console.log("Excel信息显示完成，DOM中卡片数量:", $('.excel-file-card').length);
    }
    
    // 验证按钮点击事件
    $('#validateBtn').on('click', function() {
        if (loadedExcelInfo.length === 0) {
            alert('请先加载Excel信息');
            return;
        }
        
        // 获取用户选择的校验类型
        const validationType = $validationTypeSelect.val();
        if (!validationType) {
            alert('请选择校验类型');
            return;
        }
        
        console.log("开始校验文件数量:", loadedExcelInfo.length);
        
        // 检查是否有可用于校验的文件
        let validFilesCount = 0;
        
        // 检查每个Excel文件的卡片元素是否存在
        // 获取所有文件卡片
        const fileCards = $('.excel-file-card');
        console.log("DOM中找到的文件卡片数量:", fileCards.length);
        
        // 为每个文件更新工作表和读取行信息
        let validFiles = [];
        
        loadedExcelInfo.forEach(fileInfo => {
            // 检查这个文件的工作表是否存在
            if (fileInfo.sheetExists === false) {
                console.log(`文件 ${fileInfo.fileName} 不存在所选工作表，将被排除在校验之外`);
                return; // 跳过这个文件
            }
            
            // 查找对应的文件卡片 - 改为使用索引而不是选择器
            let foundCard = false;
            let sheetValue = null;
            let rowValue = "1";
            
            // 遍历所有卡片找到匹配的
            fileCards.each(function() {
                const cardPath = $(this).data('file-path');
                if (cardPath === fileInfo.filePath) {
                    foundCard = true;
                    
                    // 获取工作表和读取行的值
                    const sheetSelect = $(this).find('.sheet-select');
                    const rowSelect = $(this).find('.row-select');
                    
                    sheetValue = sheetSelect.val();
                    if (rowSelect.length > 0) {
                        rowValue = rowSelect.val() || "1";
                    }
                    
                    console.log(`找到文件卡片: ${fileInfo.fileName}, 工作表值: ${sheetValue}, 读取行: ${rowValue}`);
                    return false; // 跳出each循环
                }
            });
            
            // 如果找到了卡片并且工作表存在
            if (foundCard && sheetValue && sheetValue !== 'not-exist') {
                // 获取和更新工作表信息
                const selectedSheetIndex = parseInt(sheetValue);
                const selectedSheet = fileInfo.sheets.find(s => s.index == selectedSheetIndex);
                
                if (selectedSheet) {
                    // 确保我们拷贝文件信息，而不是修改原始对象
                    const updatedFileInfo = JSON.parse(JSON.stringify(fileInfo));
                    updatedFileInfo.currentSheet = selectedSheet;
                    updatedFileInfo.readRow = rowValue;
                    
                    // 添加到有效文件
                    validFiles.push(updatedFileInfo);
                    validFilesCount++;
                    
                    console.log(`文件 ${fileInfo.fileName} 是有效的，工作表: ${selectedSheet.name}, 读取行: ${rowValue}`);
                }
            } else {
                console.log(`文件 ${fileInfo.fileName} 没有找到对应的文件卡片或工作表无效`);
            }
        });
        
        console.log("有效文件数量:", validFilesCount);
        
        // 检查有效文件数量
        if (validFilesCount < 2) {
            alert('至少需要2个有效的Excel文件才能进行表头一致性校验');
            return;
        }
        
        // 显示加载指示器
        $(this).prop('disabled', true).text('校验中...');
        
        // 调用校验API
        $.ajax({
            url: '/api/excel/validate',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                filesInfo: validFiles,  // 只传递有效的文件
                readRow: "1",  // 这个值不再使用，每个文件都有自己的readRow
                validationType: validationType
            }),
            success: function(response) {
                if (response.success) {
                    console.log("校验成功，准备显示结果", response);
                    console.log("分组数量:", response.groups.length);
                    
                    // 检查分组中是否有空白行分组
                    response.groups.forEach((group, index) => {
                        const headers = group.headers || [];
                        const isEmptyGroup = headers.length === 0 || headers.every(header => 
                            header === null || header === undefined || (typeof header === 'string' && header.trim() === '')
                        );
                        console.log(`分组 ${index + 1} 是否为空白行分组: ${isEmptyGroup}, 文件数量: ${group.file_count}`);
                        
                        // 打印分组的头部值
                        console.log(`分组 ${index + 1} 头部值:`, JSON.stringify(headers));
                    });
                    
                    showValidationResults(response);
                } else {
                    alert('校验失败: ' + response.message);
                }
                
                // 恢复按钮状态
                $('#validateBtn').prop('disabled', false).text('开始校验');
            },
            error: function(xhr) {
                console.error('校验失败:', xhr);
                alert('校验失败，请稍后重试');
                
                // 恢复按钮状态
                $('#validateBtn').prop('disabled', false).text('开始校验');
            }
        });
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
                
                // 初始化文件下拉框
                initializeExcelFilesDropdown(excelFiles);
            },
            error: function(xhr) {
                console.error('获取文件列表失败:', xhr);
                alert('获取文件列表失败，请稍后重试');
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
        
        // 创建文件下拉选择器
        dropdownInstance = new SearchableDropdown({
            element: '#fileDropdown',
            data: dropdownData,
            valueField: 'id',
            textField: 'text',
            searchFields: ['text'],
            placeholder: '输入关键词搜索Excel文件...',
            noResultsText: '没有找到匹配的Excel文件',
            onChange: function(value, item) {
                if (value) {
                    handleFileSelect(item);
                }
            }
        });
    }
    
    // 处理文件选择
    function handleFileSelect(fileItem) {
        if (!fileItem) return;
        
        // 检查是否已经选择了该文件
        if (selectedFiles.find(f => f.id === fileItem.id)) {
            return; // 已经选择，不重复添加
        }
        
        // 添加到已选文件列表
        selectedFiles.push(fileItem);
        
        // 更新显示的已选文件标签
        updateSelectedFiles();
        
        // 如果是第一个选择的文件，设为当前文件
        if (selectedFiles.length === 1) {
            currentFile = fileItem.id;
        }
        
        // 启用校验选项
        enableValidationOptions();
    }
    
    // 启用校验选项
    function enableValidationOptions() {
        $sheetIndexSelect.prop('disabled', false);
        $readRowSelect.prop('disabled', false);
        $validationTypeSelect.prop('disabled', false);
        $loadExcelBtn.prop('disabled', false);
    }
    
    // 更新已选文件显示
    function updateSelectedFiles() {
        $selectedFilesContainer.empty();
        
        if (selectedFiles.length === 0) {
            // 没有选择文件
            return;
        }
        
        // 创建文件标签
        selectedFiles.forEach(function(file) {
            const fileTag = $(`
                <div class="selected-file-tag" data-id="${file.id}">
                    <span class="file-name">${file.text}</span>
                    <span class="remove-file">×</span>
                </div>
            `);
            
            // 添加移除文件的点击事件
            fileTag.find('.remove-file').on('click', function(e) {
                e.stopPropagation();
                removeFile(file.id);
            });
            
            // 添加选择当前文件的点击事件
            fileTag.on('click', function() {
                // 设置当前文件
                currentFile = file.id;
                
                // 高亮当前选中的文件标签
                $('.selected-file-tag').removeClass('active');
                $(this).addClass('active');
            });
            
            $selectedFilesContainer.append(fileTag);
        });
        
        // 更新按钮状态
        updateButtonState();
    }
    
    // 移除文件
    function removeFile(fileId) {
        // 找到文件索引
        const index = selectedFiles.findIndex(f => f.id === fileId);
        if (index === -1) return;
        
        // 移除文件
        selectedFiles.splice(index, 1);
        
        // 更新显示
        updateSelectedFiles();
        
        // 如果当前文件被移除，重置当前文件
        if (currentFile === fileId) {
            if (selectedFiles.length > 0) {
                // 设置第一个文件为当前文件
                currentFile = selectedFiles[0].id;
            } else {
                // 没有文件了
                currentFile = null;
                
                // 禁用校验选项
                $sheetIndexSelect.prop('disabled', true);
                $readRowSelect.prop('disabled', true);
                $validationTypeSelect.prop('disabled', true);
                $loadExcelBtn.prop('disabled', true);
                
                // 隐藏Excel信息区域
                $excelInfoSection.hide();
            }
        }
    }
    
    // 更新按钮状态
    function updateButtonState() {
        // 计算是否启用加载Excel信息按钮
        const hasFiles = selectedFiles.length > 0;
        const hasSheetIndex = $sheetIndexSelect.val() !== null && $sheetIndexSelect.val() !== '';
        
        $loadExcelBtn.prop('disabled', !(hasFiles && hasSheetIndex));
        
        // 注意：校验按钮始终启用，点击时再检查参数
    }
    
    // 全选文件
    function selectAllFiles() {
        // 获取所有可选文件
        const allFiles = dropdownInstance ? dropdownInstance.options.data : [];
        if (!allFiles || allFiles.length === 0) {
            alert('没有可选的文件');
            return;
        }
        
        // 重置已选文件列表
        selectedFiles = [];
        
        // 添加所有文件
        allFiles.forEach(file => {
            selectedFiles.push(file);
        });
        
        // 更新显示
        updateSelectedFiles();
        
        // 更新当前文件为第一个文件
        if (selectedFiles.length > 0) {
            currentFile = selectedFiles[0].id;
            
            // 启用校验选项
            enableValidationOptions();
        }
    }
    
    // 显示校验结果
    function showValidationResults(response) {
        // 显示结果部分
        $resultsSection.show();
        
        const results = response.summary;
        const issues = response.issues;
        const groups = response.groups;
        
        // 显示汇总信息
        $resultsSummary.html(`
            <div class="summary-item">总文件数: <strong>${results.total_files}</strong></div>
            <div class="summary-item">分组数量: <strong>${results.total_groups}</strong></div>
            <div class="summary-item">问题数量: <strong>${results.total_issues}</strong></div>
            <div class="summary-item">通过率: <strong>${results.pass_rate}%</strong></div>
        `);
        
        // 构建结果内容
        let resultsHTML = '';
        
        // 1. 添加表头分组信息
        if (groups && groups.length > 0) {
            resultsHTML += `
                <div class="groups-container">
                    <h3>表头分组信息</h3>
                    <div class="groups-grid">
            `;
            
            // 首先检查并重新排序分组，将空白行分组放在最前面
            const sortedGroups = [...groups];
            sortedGroups.sort((a, b) => {
                // 获取头部数组，可能为undefined
                const headersA = a.headers || [];
                const headersB = b.headers || [];
                
                // 检查组a是否是空白行分组
                const isGroupAEmpty = headersA.length === 0 || headersA.every(header => 
                    header === null || header === undefined || (typeof header === 'string' && header.trim() === '')
                );
                
                // 检查组b是否是空白行分组
                const isGroupBEmpty = headersB.length === 0 || headersB.every(header => 
                    header === null || header === undefined || (typeof header === 'string' && header.trim() === '')
                );
                
                // 空白行分组优先
                if (isGroupAEmpty && !isGroupBEmpty) return -1;
                if (!isGroupAEmpty && isGroupBEmpty) return 1;
                
                // 其次按文件数量排序
                return b.file_count - a.file_count;
            });
            
            // 添加每个分组的卡片
            sortedGroups.forEach((group, groupIndex) => {
                const headers = group.headers || [];
                const fileCount = group.file_count;
                
                // 检查是否是空白行分组
                const isEmptyGroup = headers.length === 0 || headers.every(header => 
                    header === null || header === undefined || (typeof header === 'string' && header.trim() === '')
                );
                
                console.log(`显示分组 ${groupIndex + 1}/${sortedGroups.length}, 文件数量: ${fileCount}, 是否为空白行分组: ${isEmptyGroup}`);
                console.log(`空白行分组检查，头部值:`, JSON.stringify(headers));
                
                // 为空白行分组添加特殊样式
                const groupClass = isEmptyGroup ? 'header-group-card empty-header-group' : 'header-group-card';
                const groupTitle = isEmptyGroup ? `空白行分组 (${fileCount} 个文件)` : `组 ${group.group_id} (${fileCount} 个文件)`;
                
                resultsHTML += `
                    <div class="${groupClass}" data-group-id="${group.group_id}">
                        <div class="group-header">
                            <h4>${groupTitle}</h4>
                            <button class="view-files-btn" data-group-id="${group.group_id}">查看文件</button>
                        </div>
                        <div class="group-headers">
                            <table class="header-table">
                                <tr>
                `;
                
                // 添加表头单元格
                headers.forEach((header, index) => {
                    const colLetter = getColumnLetter(index);
                    // 更好地处理空值，包括null、undefined和空字符串
                    const headerText = (header === null || header === undefined || (typeof header === 'string' && header.trim() === '')) 
                        ? "(空)" 
                        : header;
                    resultsHTML += `<th>${colLetter}: ${headerText}</th>`;
                });
                
                resultsHTML += `
                                </tr>
                            </table>
                        </div>
                    </div>
                `;
            });
            
            resultsHTML += `
                    </div>
                </div>
            `;
        }
        
        // 2. 添加问题列表
        resultsHTML += `
            <div class="issues-container">
                <h3>表头差异问题</h3>
        `;
        
        if (issues.length === 0) {
            resultsHTML += `<p class="no-issues">未发现表头差异问题，所有文件表头一致！</p>`;
        } else {
            resultsHTML += `
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>位置</th>
                            <th>对比组</th>
                            <th>问题类型</th>
                            <th>详细信息</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            issues.forEach(issue => {
                const groupsText = issue.groups ? `组${issue.groups[0]} vs 组${issue.groups[1]}` : '';
                
                resultsHTML += `
                    <tr class="issue-row" data-groups="${issue.groups ? issue.groups.join(',') : ''}">
                        <td>${issue.location}</td>
                        <td>${groupsText}</td>
                        <td>${issue.type}</td>
                        <td>${issue.message}</td>
                    </tr>
                `;
            });
            
            resultsHTML += `
                    </tbody>
                </table>
            `;
        }
        
        resultsHTML += `</div>`;
        
        // 替换结果区域内容
        $('#resultsSection .results-details').html(resultsHTML);
        
        // 为"查看文件"按钮添加点击事件
        $('.view-files-btn').on('click', function() {
            const groupId = $(this).data('group-id');
            const group = groups.find(g => g.group_id === groupId);
            
            if (group && group.files && group.files.length > 0) {
                let filesHTML = `
                    <div class="group-files-list">
                        <h4>组 ${groupId} 中的文件列表</h4>
                        <ul>
                `;
                
                group.files.forEach(file => {
                    filesHTML += `<li>${file.file_name} (工作表: ${file.sheet_name})</li>`;
                });
                
                filesHTML += `
                        </ul>
                    </div>
                `;
                
                // 显示弹出对话框
                showDialog('文件列表', filesHTML);
            }
        });
        
        // 高亮相关行
        $('.issue-row').hover(
            function() {
                const groups = $(this).data('groups').split(',');
                groups.forEach(groupId => {
                    $(`.header-group-card[data-group-id="${groupId}"]`).addClass('highlight');
                });
            },
            function() {
                $('.header-group-card').removeClass('highlight');
            }
        );
    }
    
    // 获取Excel列字母
    function getColumnLetter(index) {
        let result = '';
        
        do {
            const remainder = index % 26;
            result = String.fromCharCode(65 + remainder) + result;
            index = Math.floor(index / 26) - 1;
        } while (index >= 0);
        
        return result;
    }
    
    // 显示对话框
    function showDialog(title, content) {
        // 如果已存在对话框，先移除
        $('.dialog-container').remove();
        
        // 创建对话框
        const dialogHTML = `
            <div class="dialog-container">
                <div class="dialog-overlay"></div>
                <div class="dialog-content">
                    <div class="dialog-header">
                        <h3>${title}</h3>
                        <button class="dialog-close">&times;</button>
                    </div>
                    <div class="dialog-body">
                        ${content}
                    </div>
                </div>
            </div>
        `;
        
        // 添加到页面
        $('body').append(dialogHTML);
        
        // 添加关闭事件
        $('.dialog-close, .dialog-overlay').on('click', function() {
            $('.dialog-container').fadeOut(300, function() {
                $(this).remove();
            });
        });
        
        // 显示对话框
        $('.dialog-container').fadeIn(300);
    }
    
    // 导出结果按钮点击事件
    $exportBtn.on('click', function() {
        if ($resultsTable.children().length === 0) {
            alert('没有可导出的结果');
            return;
        }
        
        // 在生产环境中，这里会调用导出API
        // 这里仅模拟导出功能
        alert('导出功能已触发（演示版本）');
        // 实际实现可以调用后端API: window.location.href = '/api/excel/export_results';
    });
}); 