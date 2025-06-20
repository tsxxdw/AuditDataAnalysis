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
    });
    
    // 文件上传区域相关功能
    initFileUploadArea();
    
    // 文本录入区域相关功能
    initTextInputArea();
    
    // 知识库列表区域相关功能
    initKnowledgeListArea();
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
    
    // 点击浏览按钮触发文件选择
    browseBtn.on('click', function() {
        fileInput.click();
    });
    
    // 点击整个拖放区域也触发文件选择
    dropzone.on('click', function(e) {
        // 防止点击浏览按钮时重复触发
        if (!$(e.target).hasClass('browse-btn')) {
            fileInput.click();
        }
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
        // 这里只是UI演示，实际上传功能需要后端配合实现
        if (filesList.children().length > 0) {
            alert('文件上传功能需要后端支持，此处仅为UI演示');
        } else {
            alert('请先选择要上传的文件');
        }
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
        
        if (!title) {
            alert('请输入知识标题');
            return;
        }
        
        if (!content) {
            alert('请输入知识内容');
            return;
        }
        
        // 这里只是UI演示，实际保存功能需要后端配合实现
        alert('文本保存功能需要后端支持，此处仅为UI演示');
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
        
        // 这里只是UI演示，实际搜索功能需要后端配合实现
        alert(`搜索功能需要后端支持，此处仅为UI演示\n搜索词: ${searchTerm || '空'}\n筛选类型: ${filterType}`);
    });
    
    // 示例：加载模拟数据（在实际应用中会从后端API获取）
    loadMockKnowledgeItems();
}

/**
 * 加载模拟的知识库项目（仅用于UI演示）
 */
function loadMockKnowledgeItems() {
    const container = $('.knowledge-items-container');
    
    // 清空现有内容
    container.empty();
    
    // 模拟数据
    const mockItems = [
        {
            id: 1,
            title: '数据分析基础知识',
            type: 'doc',
            date: '2023-05-15',
            tags: ['基础', '数据分析', '教程']
        },
        {
            id: 2,
            title: 'Python数据处理技巧',
            type: 'docx',
            date: '2023-06-20',
            tags: ['Python', '数据处理']
        },
        {
            id: 3,
            title: '常用SQL查询语句收集',
            type: 'txt',
            date: '2023-07-10',
            tags: ['SQL', '查询', '参考']
        }
    ];
    
    // 检查是否有数据
    if (mockItems.length === 0) {
        container.html('<div class="empty-state"><p>知识库暂无内容</p></div>');
        return;
    }
    
    // 添加模拟数据到容器
    mockItems.forEach(item => {
        const itemElement = createKnowledgeItem(item);
        container.append(itemElement);
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
    switch (item.type) {
        case 'doc':
        case 'docx':
            typeIcon += ' fa-file-word';
            break;
        case 'txt':
            typeIcon += ' fa-file-alt';
            break;
        case 'manual':
            typeIcon += ' fa-keyboard';
            break;
        default:
            typeIcon += ' fa-file';
    }
    
    itemMeta.append(`
        <div class="knowledge-item-type">
            <i class="${typeIcon}"></i>
            <span>${getTypeLabel(item.type)}</span>
        </div>
        <div class="knowledge-item-date">
            <i class="fas fa-calendar-alt"></i>
            <span>${item.date}</span>
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
        <button class="knowledge-action-btn edit-btn" title="编辑">
            <i class="fas fa-edit"></i>
        </button>
        <button class="knowledge-action-btn delete-btn" title="删除">
            <i class="fas fa-trash"></i>
        </button>
    `);
    
    // 添加按钮事件
    actionButtons.find('.view-btn').on('click', function() {
        alert(`查看知识: ${item.title}\n(功能需要后端支持)`);
    });
    
    actionButtons.find('.edit-btn').on('click', function() {
        alert(`编辑知识: ${item.title}\n(功能需要后端支持)`);
    });
    
    actionButtons.find('.delete-btn').on('click', function() {
        if (confirm(`确定要删除"${item.title}"吗？`)) {
            alert('删除功能需要后端支持，此处仅为UI演示');
        }
    });
    
    itemElement.append(itemInfo);
    itemElement.append(actionButtons);
    
    return itemElement;
}

/**
 * 获取文件类型的显示标签
 * @param {string} type - 文件类型
 * @returns {string} 显示标签
 */
function getTypeLabel(type) {
    switch (type) {
        case 'doc':
        case 'docx':
            return 'Word文档';
        case 'txt':
            return '文本文件';
        case 'manual':
            return '手动录入';
        default:
            return '未知类型';
    }
} 