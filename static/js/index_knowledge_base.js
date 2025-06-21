/**
 * 本地知识库页面脚本
 */
$(document).ready(function() {
    // 标签页切换功能
    $('.tab').on('click', function() {
        const tabId = $(this).data('tab');
        
        // 切换标签激活状态
        $('.tab').removeClass('active');
        $(this).addClass('active');
        
        // 切换内容显示
        $('.tab-content').removeClass('active');
        $(`#${tabId}`).addClass('active');
        
        // 如果切换到知识库列表，刷新列表
        if (tabId === 'knowledge-list') {
            loadKnowledgeItems();
        }
    });
    
    // 文件上传区域相关功能
    initFileUploadArea();
    
    // 文本录入区域相关功能
    initTextInputArea();
    
    // 知识库列表区域相关功能
    initKnowledgeListArea();
    
    // 初始化知识库聊天区域
    initKnowledgeChatArea();
});

/**
 * 初始化文件上传区域
 */
function initFileUploadArea() {
    const dropzone = $('#document-dropzone');
    const fileInput = $('#file-input');
    const browseBtn = $('.browse-btn');
    const uploadBtn = $('.upload-btn');
    const clearBtn = $('.clear-btn');
    const filesList = $('#selected-files-list');
    
    // 浏览按钮点击事件
    browseBtn.on('click', function(e) {
        e.preventDefault();
        e.stopPropagation(); // 阻止事件冒泡
        fileInput.click();
    });
    
    // 文件选择变化处理
    fileInput.on('change', function() {
        handleFileSelection(this.files);
    });
    
    // 拖放功能
    dropzone.on('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragover');
    });
    
    dropzone.on('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
    });
    
    dropzone.on('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
        
        // 获取拖放的文件
        const files = e.originalEvent.dataTransfer.files;
        handleFileSelection(files);
    });
    
    // 清空已选择的文件
    clearBtn.on('click', function() {
        filesList.empty();
        fileInput.val('');
    });
    
    // 上传按钮点击事件
    uploadBtn.on('click', function() {
        // 检查是否有选择文件
        if (filesList.children().length === 0) {
            alert('请先选择要上传的文件');
            return;
        }
        
        // 显示上传中提示
        $(this).text('上传中...').prop('disabled', true);
        
        // 创建FormData对象
        const formData = new FormData();
        
        // 获取选择的文件
        const selectedFiles = [];
        
        filesList.find('li').each(function() {
            const fileName = $(this).find('.file-name').text();
            
            // 查找对应的文件对象
            for (let i = 0; i < fileInput[0].files.length; i++) {
                if (fileInput[0].files[i].name === fileName) {
                    selectedFiles.push(fileInput[0].files[i]);
                    break;
                }
            }
        });
        
        // 添加文件到FormData
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append('files[]', selectedFiles[i]);
        }
        
        // 添加分块策略参数
        formData.append('chunking_strategy', 'auto');
        
        // 发送上传请求
        $.ajax({
            url: '/api/knowledge_base/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    alert(`上传成功：${response.message}`);
                    
                    // 清空文件列表
                    filesList.empty();
                    fileInput.val('');
                    
                    // 切换到知识库列表标签页
                    $('.tab[data-tab="knowledge-list"]').click();
                } else {
                    alert(`上传失败：${response.message}`);
                }
            },
            error: function(xhr, status, error) {
                let errorMessage;
                try {
                    errorMessage = xhr.responseJSON.message || '上传文件时发生错误';
                } catch (e) {
                    errorMessage = '上传文件时发生网络错误';
                }
                alert(errorMessage);
            },
            complete: function() {
                // 恢复上传按钮状态
                uploadBtn.text('上传到知识库').prop('disabled', false);
            }
        });
    });
}

/**
 * 处理文件选择
 * @param {FileList} files - 选择的文件列表
 */
function handleFileSelection(files) {
    const filesList = $('#selected-files-list');
    const allowedTypes = ['.docx', '.doc', '.txt'];
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        // 检查文件类型是否允许
        if (!allowedTypes.includes(extension)) {
            alert(`不支持的文件类型: ${extension}\n请上传 docx、doc 或 txt 文件`);
            continue;
        }
        
        // 检查文件是否已在列表中
        const isDuplicate = Array.from(filesList.children()).some(
            item => $(item).find('.file-name').text() === file.name
        );
        
        if (isDuplicate) {
            continue; // 跳过重复文件
        }
        
        // 创建文件项
        const fileItem = createFileListItem(file);
        filesList.append(fileItem);
    }
}

/**
 * 创建文件列表项
 * @param {File} file - 文件对象
 * @returns {jQuery} 文件列表项jQuery对象
 */
function createFileListItem(file) {
    const extension = file.name.split('.').pop().toLowerCase();
    let iconClass = 'fas';
    
    // 根据文件类型设置图标
    switch (extension) {
        case 'doc':
        case 'docx':
            iconClass += ' fa-file-word';
            break;
        case 'txt':
            iconClass += ' fa-file-alt';
            break;
        default:
            iconClass += ' fa-file';
    }
    
    // 格式化文件大小
    const size = formatFileSize(file.size);
    
    // 创建列表项
    const listItem = $('<li></li>');
    
    const fileInfo = $('<div class="file-info"></div>');
    fileInfo.append(`<span class="file-icon ${iconClass}"></span>`);
    fileInfo.append(`<span class="file-name">${file.name}</span>`);
    fileInfo.append(`<span class="file-size">(${size})</span>`);
    
    const removeBtn = $('<span class="remove-file fas fa-times"></span>');
    removeBtn.on('click', function() {
        $(this).parent().remove();
    });
    
    listItem.append(fileInfo);
    listItem.append(removeBtn);
    
    return listItem;
}

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 初始化文本录入区域
 */
function initTextInputArea() {
    const saveBtn = $('.save-btn');
    const clearTextBtn = $('.clear-text-btn');
    const titleInput = $('#knowledge-title');
    const contentTextarea = $('#knowledge-content');
    const tagsInput = $('#knowledge-tags');
    
    // 保存按钮点击事件
    saveBtn.on('click', function() {
        const title = titleInput.val().trim();
        const content = contentTextarea.val().trim();
        const tagsText = tagsInput.val().trim();
        
        // 验证输入
        if (!title) {
            alert('请输入知识标题');
            return;
        }
        
        if (!content) {
            alert('请输入知识内容');
            return;
        }
        
        // 处理标签
        const tags = tagsText ? tagsText.split(/[,，、]/).map(tag => tag.trim()).filter(tag => tag) : [];
        
        // 显示保存中提示
        $(this).text('保存中...').prop('disabled', true);
        
        // 发送保存请求
        $.ajax({
            url: '/api/knowledge_base/text',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                title: title,
                content: content,
                tags: tags
            }),
            success: function(response) {
                if (response.success) {
                    alert('文本已成功保存到知识库');
                    
                    // 清空表单
                    titleInput.val('');
                    contentTextarea.val('');
                    tagsInput.val('');
                    
                    // 切换到知识库列表标签页
                    $('.tab[data-tab="knowledge-list"]').click();
                } else {
                    alert(`保存失败：${response.message}`);
                }
            },
            error: function(xhr, status, error) {
                let errorMessage;
                try {
                    errorMessage = xhr.responseJSON.message || '保存文本时发生错误';
                } catch (e) {
                    errorMessage = '保存文本时发生网络错误';
                }
                alert(errorMessage);
            },
            complete: function() {
                // 恢复保存按钮状态
                saveBtn.text('保存到知识库').prop('disabled', false);
            }
        });
    });
    
    // 清空按钮点击事件
    clearTextBtn.on('click', function() {
        if (confirm('确定要清空所有内容吗？')) {
            titleInput.val('');
            contentTextarea.val('');
            tagsInput.val('');
        }
    });
}

/**
 * 初始化知识库列表区域
 */
function initKnowledgeListArea() {
    const searchBtn = $('.search-btn');
    const searchInput = $('#search-knowledge');
    const filterSelect = $('#filter-type');
    
    // 搜索按钮点击事件
    searchBtn.on('click', function() {
        const searchTerm = searchInput.val().trim();
        const filterType = filterSelect.val();
        
        if (!searchTerm) {
            alert('请输入搜索关键词');
            return;
        }
        
        // 显示搜索中提示
        $(this).text('搜索中...').prop('disabled', true);
        
        // 发送搜索请求
        $.ajax({
            url: '/api/knowledge_base/search',
            type: 'GET',
            data: {
                query: searchTerm,
                type: filterType,
                limit: 10
            },
            success: function(response) {
                if (response.success) {
                    if (response.results.length > 0) {
                        displaySearchResults(response.results);
                    } else {
                        $('.knowledge-items-container').html('<div class="empty-state"><p>未找到匹配的内容</p></div>');
                    }
                } else {
                    alert(`搜索失败：${response.message}`);
                }
            },
            error: function(xhr, status, error) {
                let errorMessage;
                try {
                    errorMessage = xhr.responseJSON.message || '搜索时发生错误';
                } catch (e) {
                    errorMessage = '搜索时发生网络错误';
                }
                alert(errorMessage);
            },
            complete: function() {
                // 恢复搜索按钮状态
                searchBtn.text('搜索').prop('disabled', false);
            }
        });
    });
    
    // 回车键触发搜索
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            searchBtn.click();
        }
    });
    
    // 过滤器变化事件
    filterSelect.on('change', function() {
        if (!searchInput.val().trim()) {
            // 如果没有搜索词，则加载列表
            loadKnowledgeItems($(this).val());
        }
    });
    
    // 加载知识库项目列表
    loadKnowledgeItems();
}

/**
 * 加载知识库项目列表
 * @param {string} filterType - 过滤类型
 * @param {number} page - 页码
 * @param {number} perPage - 每页数量
 */
function loadKnowledgeItems(filterType = 'all', page = 1, perPage = 10) {
    const container = $('.knowledge-items-container');
    
    // 显示加载中提示
    container.html('<div class="loading-state"><p>加载中...</p></div>');
    
    // 发送请求获取知识库项目列表
    $.ajax({
        url: '/api/knowledge_base/items',
        type: 'GET',
        data: {
            type: filterType,
            page: page,
            per_page: perPage
        },
        success: function(response) {
            if (response.success) {
                if (response.items.length > 0) {
                    displayKnowledgeItems(response.items);
                } else {
                    container.html('<div class="empty-state"><p>知识库暂无内容</p></div>');
                }
            } else {
                container.html(`<div class="error-state"><p>加载失败：${response.message}</p></div>`);
            }
        },
        error: function() {
            container.html('<div class="error-state"><p>加载知识库列表时发生错误</p></div>');
        }
    });
}

/**
 * 显示知识库项目列表
 * @param {Array} items - 知识库项目列表
 */
function displayKnowledgeItems(items) {
    const container = $('.knowledge-items-container');
    
    // 清空容器
    container.empty();
    
    // 添加项目到容器
    items.forEach(item => {
        const itemElement = createKnowledgeItem(item);
        container.append(itemElement);
    });
}

/**
 * 显示搜索结果
 * @param {Array} results - 搜索结果列表
 */
function displaySearchResults(results) {
    const container = $('.knowledge-items-container');
    
    // 清空容器
    container.empty();
    
    // 添加搜索结果标题
    container.append('<h3 class="search-results-title">搜索结果</h3>');
    
    // 添加搜索结果到容器
    results.forEach(result => {
        const resultElement = createSearchResultItem(result);
        container.append(resultElement);
    });
}

/**
 * 创建搜索结果项
 * @param {Object} result - 搜索结果数据
 * @returns {jQuery} 搜索结果项jQuery对象
 */
function createSearchResultItem(result) {
    const resultElement = $('<div class="search-result-item"></div>');
    
    // 结果标题
    resultElement.append(`<div class="result-title">${result.title}</div>`);
    
    // 结果内容（截取前200个字符）
    const contentPreview = result.content.length > 200 
        ? result.content.substring(0, 200) + '...' 
        : result.content;
    
    resultElement.append(`<div class="result-content">${contentPreview}</div>`);
    
    // 结果元数据
    const metaElement = $('<div class="result-meta"></div>');
    metaElement.append(`<span class="result-type">${getTypeLabel(result.source_type)}</span>`);
    metaElement.append(`<span class="result-score">相关度: ${(result.score * 100).toFixed(2)}%</span>`);
    
    resultElement.append(metaElement);
    
    // 点击查看完整内容
    resultElement.on('click', function() {
        showContentModal(result);
    });
    
    return resultElement;
}

/**
 * 显示内容详情模态框
 * @param {Object} item - 内容项数据
 */
function showContentModal(item) {
    // 创建模态框元素
    const modal = $(`
        <div class="kb-modal">
            <div class="kb-modal-content">
                <div class="kb-modal-header">
                    <h3>${item.title}</h3>
                    <span class="kb-modal-close">&times;</span>
                </div>
                <div class="kb-modal-body">
                    <pre>${item.content}</pre>
                </div>
            </div>
        </div>
    `);
    
    // 添加模态框样式
    $('<style>')
        .text(`
            .kb-modal {
                display: block;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
            }
            .kb-modal-content {
                background-color: #fff;
                margin: 5% auto;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                width: 80%;
                max-width: 800px;
                max-height: 80vh;
                overflow: auto;
            }
            .kb-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
            .kb-modal-close {
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                color: #aaa;
            }
            .kb-modal-close:hover {
                color: #333;
            }
            .kb-modal-body {
                margin-top: 20px;
            }
            .kb-modal-body pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: inherit;
                line-height: 1.5;
            }
        `)
        .appendTo('head');
    
    // 添加到页面
    modal.appendTo('body');
    
    // 关闭模态框事件
    modal.find('.kb-modal-close').on('click', function() {
        modal.remove();
    });
    
    // 点击背景关闭模态框
    modal.on('click', function(e) {
        if ($(e.target).hasClass('kb-modal')) {
            modal.remove();
        }
    });
}

/**
 * 创建知识库列表项
 * @param {Object} item - 知识库项目数据
 * @returns {jQuery} 知识库列表项jQuery对象
 */
function createKnowledgeItem(item) {
    const itemElement = $('<div class="knowledge-item"></div>');
    
    // 项目信息
    const itemInfo = $('<div class="knowledge-item-info"></div>');
    itemInfo.append(`<div class="knowledge-item-title">${item.title}</div>`);
    
    // 元数据
    const itemMeta = $('<div class="knowledge-item-meta"></div>');
    
    // 类型图标
    let typeIcon = 'fas';
    switch (item.source_type) {
        case 'doc':
            typeIcon += ' fa-file-word';
            break;
        case 'txt':
            typeIcon += ' fa-file-alt';
            break;
        case 'legal':
            typeIcon += ' fa-gavel';
            break;
        case 'audit':
            typeIcon += ' fa-file-invoice-dollar';
            break;
        case 'manual':
            typeIcon += ' fa-keyboard';
            break;
        default:
            typeIcon += ' fa-file';
    }
    
    // 格式化日期
    const createdDate = new Date(item.created_at);
    const formattedDate = `${createdDate.getFullYear()}-${padZero(createdDate.getMonth() + 1)}-${padZero(createdDate.getDate())}`;
    
    itemMeta.append(`
        <div class="knowledge-item-type">
            <i class="${typeIcon}"></i>
            <span>${getTypeLabel(item.source_type)}</span>
        </div>
        <div class="knowledge-item-date">
            <i class="fas fa-calendar-alt"></i>
            <span>${formattedDate}</span>
        </div>
        <div class="knowledge-item-chunks">
            <i class="fas fa-puzzle-piece"></i>
            <span>${item.chunks_count} 块</span>
        </div>
    `);
    
    itemInfo.append(itemMeta);
    
    // 标签
    if (item.tags && item.tags.length > 0) {
        const tagsContainer = $('<div class="knowledge-item-tags"></div>');
        item.tags.forEach(tag => {
            tagsContainer.append(`<span class="knowledge-tag">${tag}</span>`);
        });
        itemInfo.append(tagsContainer);
    }
    
    // 操作按钮
    const actionButtons = $('<div class="knowledge-item-actions"></div>');
    actionButtons.append(`
        <button class="knowledge-action-btn view-btn" title="查看">
            <i class="fas fa-eye"></i>
        </button>
        <button class="knowledge-action-btn delete-btn" title="删除">
            <i class="fas fa-trash"></i>
        </button>
    `);
    
    // 添加按钮事件
    actionButtons.find('.view-btn').on('click', function(e) {
        e.stopPropagation();
        viewKnowledgeItem(item.id);
    });
    
    actionButtons.find('.delete-btn').on('click', function(e) {
        e.stopPropagation();
        deleteKnowledgeItem(item.id, item.title);
    });
    
    itemElement.append(itemInfo);
    itemElement.append(actionButtons);
    
    return itemElement;
}

/**
 * 查看知识库项目
 * @param {string} itemId - 知识库项目ID
 */
function viewKnowledgeItem(itemId) {
    // 发送请求获取知识库项目详情
    $.ajax({
        url: `/api/knowledge_base/items/${itemId}`,
        type: 'GET',
        success: function(response) {
            if (response.success) {
                // 显示知识库项目详情
                alert(`查看功能正在开发中\n\n标题: ${response.item.title}\n类型: ${getTypeLabel(response.item.source_type)}\n块数: ${response.item.chunks_count}`);
            } else {
                alert(`获取知识库项目详情失败：${response.message}`);
            }
        },
        error: function() {
            alert('获取知识库项目详情时发生错误');
        }
    });
}

/**
 * 删除知识库项目
 * @param {string} itemId - 知识库项目ID
 * @param {string} itemTitle - 知识库项目标题
 */
function deleteKnowledgeItem(itemId, itemTitle) {
    if (confirm(`确定要删除"${itemTitle}"吗？此操作不可恢复。`)) {
        // 发送删除请求
        $.ajax({
            url: `/api/knowledge_base/items/${itemId}`,
            type: 'DELETE',
            success: function(response) {
                if (response.success) {
                    alert('知识库项目已成功删除');
                    // 刷新知识库列表
                    loadKnowledgeItems();
                } else {
                    alert(`删除知识库项目失败：${response.message}`);
                }
            },
            error: function() {
                alert('删除知识库项目时发生错误');
            }
        });
    }
}

/**
 * 获取文件类型的显示标签
 * @param {string} type - 文件类型
 * @returns {string} 显示标签
 */
function getTypeLabel(type) {
    switch (type) {
        case 'doc':
            return 'Word文档';
        case 'txt':
            return '文本文件';
        case 'legal':
            return '法律文档';
        case 'audit':
            return '审计报告';
        case 'manual':
            return '手动录入';
        default:
            return '未知类型';
    }
}

/**
 * 数字补零
 * @param {number} num - 数字
 * @returns {string} 补零后的字符串
 */
function padZero(num) {
    return num < 10 ? '0' + num : num;
}

/**
 * 初始化知识库聊天区域
 */
function initKnowledgeChatArea() {
    const chatInput = $('#chat-input');
    const sendBtn = $('#send-chat');
    const clearBtn = $('#clear-chat');
    const messagesContainer = $('#chat-messages');
    
    // 历史消息
    let chatHistory = [{
        role: 'system',
        content: '您好！我是智能助手，可以回答关于知识库中文档的问题。请问有什么需要了解的信息？'
    }];
    
    // 检查模型状态
    checkModelStatus();
    
    // 发送按钮点击事件
    sendBtn.on('click', function() {
        sendMessage();
    });
    
    // 输入框按下回车键发送消息
    chatInput.on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 清空聊天记录按钮
    clearBtn.on('click', function() {
        // 保留系统欢迎消息
        chatHistory = [{
            role: 'system',
            content: '您好！我是智能助手，可以回答关于知识库中文档的问题。请问有什么需要了解的信息？'
        }];
        messagesContainer.empty();
        messagesContainer.append(createMessageElement('system', chatHistory[0].content));
    });
    
    /**
     * 检查模型服务状态
     */
    function checkModelStatus() {
        // 首先检查默认模型配置
        $.ajax({
            url: '/api/model/default-model',
            type: 'GET',
            success: function(response) {
                if (response.success && response.model) {
                    const model = response.model;
                    const modelName = model.name || model.id;
                    const providerName = model.provider_name || model.provider_id;
                    
                    // 显示模型信息消息
                    messagesContainer.append(
                        createMessageElement(
                            'system', 
                            `📢 当前使用的大模型: ${modelName} (由 ${providerName} 提供)\n\n您可以开始提问了...`
                        )
                    );
                    scrollToBottom();
                } else {
                    // 如果未设置默认模型，检查可用的模型服务
                    checkAvailableModels();
                }
            },
            error: function() {
                // 如果API不可用，回退到检查模型服务状态
                checkAvailableModels();
            }
        });
    }
    
    /**
     * 检查可用的模型服务
     */
    function checkAvailableModels() {
        $.ajax({
            url: '/api/knowledge_base/check_model',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const data = response.data;
                    let modelAvailable = false;
                    let availableModels = [];
                    
                    // 检查是否有可用的模型服务
                    for (const providerId in data) {
                        if (data[providerId].available && data[providerId].models.length > 0) {
                            modelAvailable = true;
                            
                            // 收集可用模型信息
                            data[providerId].models.forEach(model => {
                                availableModels.push(`${model.name || model.id} (${data[providerId].name})`);
                            });
                        }
                    }
                    
                    if (modelAvailable) {
                        // 显示可用模型信息
                        const modelsList = availableModels.join(', ');
                        messagesContainer.append(
                            createMessageElement(
                                'system', 
                                `📢 检测到可用的模型: ${modelsList}\n\n但未设置默认模型，请在系统设置中设置默认模型。`
                            )
                        );
                    } else {
                        // 显示警告消息
                        messagesContainer.append(
                            createMessageElement(
                                'system', 
                                '⚠️ 警告：未检测到可用的大模型服务。请确保Ollama服务正在运行，并且已安装所需模型（如qwen或llama3）。'
                            )
                        );
                    }
                    scrollToBottom();
                } else {
                    // 显示错误消息
                    messagesContainer.append(
                        createMessageElement(
                            'system', 
                            '⚠️ 警告：模型服务检查失败。智能问答功能可能无法正常工作。'
                        )
                    );
                    scrollToBottom();
                }
            },
            error: function() {
                // 显示错误消息
                messagesContainer.append(
                    createMessageElement(
                        'system', 
                        '⚠️ 警告：无法连接到模型服务。请检查服务器状态。'
                    )
                );
                scrollToBottom();
            }
        });
    }
    
    /**
     * 发送聊天消息
     */
    function sendMessage() {
        const message = chatInput.val().trim();
        
        if (!message) {
            return;
        }
        
        // 添加用户消息到聊天界面
        messagesContainer.append(createMessageElement('user', message));
        
        // 更新聊天历史
        chatHistory.push({
            role: 'user',
            content: message
        });
        
        // 清空输入框
        chatInput.val('');
        
        // 滚动到底部
        scrollToBottom();
        
        // 显示正在输入指示器
        const loadingMsgEl = appendLoadingMessage();
        
        // 调用知识库聊天API
        $.ajax({
            url: '/api/knowledge_base/chat',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                message: message,
                history: chatHistory,
                top_k: 5,
                max_tokens: 1000
            }),
            success: function(response) {
                // 移除加载指示器
                loadingMsgEl.remove();
                
                if (response.success) {
                    // 获取回复内容和相关来源
                    const replyContent = response.data.reply;
                    const sources = response.data.sources || [];
                    
                    // 添加系统回复到聊天界面
                    const messageElement = createMessageElement('system', replyContent, sources);
                    messagesContainer.append(messageElement);
                    
                    // 更新聊天历史
                    chatHistory.push({
                        role: 'assistant',
                        content: replyContent
                    });
                    
                    // 滚动到底部
                    scrollToBottom();
                } else {
                    // 显示错误消息
                    messagesContainer.append(createMessageElement('system', `抱歉，出现了错误: ${response.message}`));
                    scrollToBottom();
                }
            },
            error: function(xhr, status, error) {
                // 移除加载指示器
                loadingMsgEl.remove();
                
                let errorMessage;
                try {
                    errorMessage = xhr.responseJSON.message || '处理请求时发生错误';
                } catch (e) {
                    errorMessage = '与服务器通信时发生错误';
                }
                
                // 显示错误消息
                messagesContainer.append(createMessageElement('system', `抱歉，出现了错误: ${errorMessage}`));
                scrollToBottom();
            }
        });
    }
    
    /**
     * 创建消息元素
     * @param {string} type - 消息类型 'user' 或 'system'
     * @param {string} content - 消息内容
     * @param {Array} sources - 引用来源数组 (可选)
     * @returns {jQuery} 消息元素jQuery对象
     */
    function createMessageElement(type, content, sources = []) {
        const messageClass = type === 'user' ? 'user-message' : 'system-message';
        const messageElement = $(`<div class="message ${messageClass}"></div>`);
        const messageContent = $('<div class="message-content"></div>');
        
        // 添加消息内容，使用markdown-it渲染
        if (type === 'user') {
            // 用户消息不需要Markdown渲染，直接显示纯文本
            messageContent.append(`<p>${escapeHtml(content)}</p>`);
        } else {
            // 系统消息使用Markdown渲染
            try {
                const md = window.markdownit({
                    html: false,        // 禁用HTML标签
                    breaks: true,       // 转换\n为<br>
                    linkify: true,      // 自动转换URL为链接
                    typographer: true,  // 启用一些语言中性的替换和引号美化
                    highlight: function (str, lang) {
                        // 代码高亮
                        if (lang && hljs.getLanguage(lang)) {
                            try {
                                return hljs.highlight(str, { language: lang }).value;
                            } catch (__) {}
                        }
                        return ''; // 使用默认高亮
                    }
                });
                
                const renderedContent = md.render(content);
                messageContent.append(`<div class="markdown-content">${renderedContent}</div>`);
            } catch (e) {
                // 如果Markdown渲染失败，回退到纯文本
                console.error("Markdown渲染失败:", e);
                messageContent.append(`<p>${escapeHtml(content)}</p>`);
            }
        }
        
        // 如果有引用来源，添加来源信息
        if (sources && sources.length > 0) {
            const sourcesElement = $('<div class="message-sources"></div>');
            sourcesElement.append('<p>引用来源：</p>');
            
            const sourcesList = $('<ul></ul>');
            sources.forEach(source => {
                const sourceName = escapeHtml(source.title || source.file_name || '未知来源');
                const sourceText = source.text || source.content || '';
                const shortText = escapeHtml(sourceText.length > 100 ? sourceText.substring(0, 100) + '...' : sourceText);
                
                const sourceItem = $(`<li>
                    <strong>${sourceName}</strong>
                    <p>${shortText}</p>
                </li>`);
                
                sourcesList.append(sourceItem);
            });
            
            sourcesElement.append(sourcesList);
            messageContent.append(sourcesElement);
        }
        
        messageElement.append(messageContent);
        return messageElement;
    }
    
    /**
     * 转义HTML特殊字符，防止XSS攻击
     * @param {string} text - 要转义的文本
     * @returns {string} 转义后的文本
     */
    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    /**
     * 添加加载中消息
     * @returns {jQuery} 加载消息元素jQuery对象
     */
    function appendLoadingMessage() {
        const loadingMessage = $('<div class="message system-message"></div>');
        const loadingContent = $('<div class="message-content loading-message"></div>');
        
        loadingContent.append('<p>正在思考</p>');
        loadingContent.append('<div class="loading-dots"><span></span><span></span><span></span></div>');
        
        loadingMessage.append(loadingContent);
        messagesContainer.append(loadingMessage);
        scrollToBottom();
        
        return loadingMessage;
    }
    
    /**
     * 滚动聊天区域到底部
     */
    function scrollToBottom() {
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }
} 