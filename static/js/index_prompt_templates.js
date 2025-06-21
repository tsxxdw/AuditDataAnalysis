// 提示词模板页面JS文件(index_prompt_templates)
$(document).ready(function() {
    // 保存所有模板数据，用于筛选
    let allTemplates = [];
    
    // 初始化时加载模板列表
    loadTemplateList();
    
    // 保存模板按钮点击事件
    $('#saveTemplate').on('click', function() {
        saveTemplate();
    });
    
    // 清空按钮点击事件
    $('#clearTemplate').on('click', function() {
        clearTemplateForm();
    });
    
    // 关闭预览按钮点击事件
    $('#closePreview').on('click', function() {
        $('.template-preview-section').hide();
    });
    
    // 标签编辑对话框事件绑定
    $('#cancelTagEdit').on('click', function() {
        $('#tagEditDialog').hide();
    });
    
    $('#saveTagEdit').on('click', function() {
        saveTemplateTag();
    });
    
    // 点击对话框外部关闭对话框
    $(document).on('click', '.tag-edit-dialog', function(e) {
        if ($(e.target).hasClass('tag-edit-dialog')) {
            $('#tagEditDialog').hide();
        }
    });
    
    // 加载模板列表
    function loadTemplateList() {
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    // 保存所有模板数据
                    allTemplates = response.templates;
                    // 初始化标签筛选下拉框
                    initTagFilter(allTemplates);
                    // 显示模板列表
                    displayTemplatesByTag(allTemplates);
                } else {
                    console.error('获取模板列表失败:', response.message);
                    // 显示空的模板列表
                    $('.templates-container').html('<p class="no-templates">暂无模板数据，请添加新模板</p>');
                }
            },
            error: function(xhr) {
                console.error('获取模板列表请求失败:', xhr);
                $('.templates-container').html('<p class="no-templates error">获取模板列表失败，请刷新重试</p>');
            }
        });
    }
    
    // 初始化标签筛选下拉框
    function initTagFilter(templates) {
        // 收集所有唯一的标签
        const tags = new Set();
        templates.forEach(template => {
            const tag = template.tag || '通用';
            tags.add(tag);
        });
        
        // 按字母顺序排序标签
        const sortedTags = Array.from(tags).sort();
        
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = sortedTags.map(tag => ({
            id: tag,
            text: tag
        }));
        
        // 添加"全部标签"选项
        dropdownData.unshift({
            id: 'all',
            text: '全部标签'
        });
        
        // 如果已存在下拉框实例，先销毁它
        if (window.tagFilterDropdown && typeof window.tagFilterDropdown.destroy === 'function') {
            window.tagFilterDropdown.destroy();
        }
        
        window.tagFilterDropdown = new MultiSelectDropdown({
            element: '#tagFilterDropdown',
            data: dropdownData,
            valueField: 'id',
            textField: 'text',
            searchFields: ['text'],
            placeholder: '选择标签进行筛选...',
            noResultsText: '没有找到匹配的标签',
            onChange: (values, items) => {
                // 更新隐藏select的值
                const $tagFilter = $('#tagFilter');
                $tagFilter.empty();
                
                // 如果选择了"全部标签"或没有选择任何标签，则显示所有模板
                if (values.includes('all') || values.length === 0) {
                    displayTemplatesByTag(allTemplates);
                    return;
                }
                
                // 添加选中的标签到隐藏select
                values.forEach(value => {
                    $tagFilter.append(`<option value="${value}" selected>${value}</option>`);
                });
                
                // 筛选模板
                filterTemplatesByTags(values);
            }
        });
    }
    
    // 自定义多选下拉框组件，基于SearchableDropdown
    class MultiSelectDropdown extends SearchableDropdown {
        constructor(options) {
            super(options);
            this.selectedValues = [];
            this.selectedItems = [];
        }
        
        createStructure() {
            this.element.classList.add('searchable-dropdown', 'multi-select-dropdown');
            
            // 创建输入框
            this.input = document.createElement('input');
            this.input.type = 'text';
            this.input.placeholder = this.options.placeholder;
            this.input.classList.add('searchable-dropdown-input');
            
            // 创建已选标签容器
            this.selectedTags = document.createElement('div');
            this.selectedTags.classList.add('selected-tags');
            
            // 创建下拉列表容器
            this.dropdown = document.createElement('div');
            this.dropdown.classList.add('searchable-dropdown-list');
            
            // 组装结构
            this.element.innerHTML = '';
            this.element.appendChild(this.input);
            this.element.appendChild(this.selectedTags);
            this.element.appendChild(this.dropdown);
        }
        
        // 重写handleInput方法，确保搜索功能正常
        async handleInput(e) {
            const query = e.target.value.trim();
            
            if (this.options.onSearch) {
                this.options.onSearch(query);
            }
            
            // 筛选数据
            if (typeof this.options.data === 'function') {
                this.filteredData = await this.options.data(query);
            } else {
                this.filteredData = this.options.data.filter(item => {
                    if (!query) return true; // 空查询时显示所有项
                    return this.options.searchFields.some(field => {
                        const value = item[field];
                        return value && value.toString().toLowerCase().includes(query.toLowerCase());
                    });
                });
            }
            
            // 更新列表
            this.renderList();
            
            // 如果列表不是打开状态，则打开它
            if (!this.isOpen) {
                this.open();
            }
        }
        
        renderList() {
            this.dropdown.innerHTML = '';
            
            if (this.filteredData.length === 0) {
                const noResults = document.createElement('div');
                noResults.classList.add('searchable-dropdown-no-results');
                noResults.textContent = this.options.noResultsText;
                this.dropdown.appendChild(noResults);
                return;
            }
            
            this.filteredData.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.classList.add('searchable-dropdown-item');
                itemElement.dataset.value = item[this.options.valueField];
                
                if (this.options.itemTemplate) {
                    itemElement.innerHTML = this.options.itemTemplate(item);
                } else {
                    itemElement.textContent = item[this.options.textField];
                }
                
                // 添加多选复选框
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.classList.add('multi-select-checkbox');
                checkbox.checked = this.selectedValues.includes(item[this.options.valueField]);
                
                // 添加复选框到项目元素
                itemElement.prepend(checkbox);
                
                // 如果是"全部标签"选项，添加特殊样式
                if (item[this.options.valueField] === 'all') {
                    itemElement.classList.add('all-tags-option');
                }
                
                // 如果已选中，添加选中样式
                if (this.selectedValues.includes(item[this.options.valueField])) {
                    itemElement.classList.add('selected');
                }
                
                this.dropdown.appendChild(itemElement);
            });
        }
        
        bindEvents() {
            // 输入框事件
            this.input.addEventListener('input', (e) => this.handleInput(e));
            this.input.addEventListener('focus', () => this.open());
            this.input.addEventListener('blur', (e) => {
                // 延迟关闭，以便能够点击选项
                setTimeout(() => {
                    if (!this.dropdown.contains(document.activeElement)) {
                        this.close();
                        // 清空搜索框内容
                        this.input.value = '';
                        // 重置过滤数据
                        this.filteredData = this.options.data;
                    }
                }, 200);
            });
            
            // 点击事件委托
            this.dropdown.addEventListener('click', (e) => {
                const item = e.target.closest('.searchable-dropdown-item');
                if (item) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const value = item.dataset.value;
                    const checkbox = item.querySelector('.multi-select-checkbox');
                    
                    // 特殊处理"全部标签"选项
                    if (value === 'all') {
                        if (!this.selectedValues.includes('all')) {
                            // 选中"全部标签"，取消其他所有选择
                            this.selectedValues = ['all'];
                            this.selectedItems = [this.filteredData.find(item => item[this.options.valueField] === 'all')];
                        } else {
                            // 取消选中"全部标签"
                            this.selectedValues = [];
                            this.selectedItems = [];
                        }
                    } else {
                        // 处理普通标签选择
                        const index = this.selectedValues.indexOf(value);
                        const selectedItem = this.filteredData.find(item => item[this.options.valueField] === value);
                        
                        // 如果当前选中了"全部标签"，先取消它
                        if (this.selectedValues.includes('all')) {
                            this.selectedValues = [];
                            this.selectedItems = [];
                        }
                        
                        if (index === -1) {
                            // 添加选择
                            this.selectedValues.push(value);
                            if (selectedItem) {
                                this.selectedItems.push(selectedItem);
                            }
                        } else {
                            // 取消选择
                            this.selectedValues.splice(index, 1);
                            this.selectedItems = this.selectedItems.filter(i => i[this.options.valueField] !== value);
                        }
                    }
                    
                    // 更新复选框状态
                    if (checkbox) {
                        checkbox.checked = this.selectedValues.includes(value);
                    }
                    
                    // 更新选中项显示
                    this.updateSelectedTags();
                    
                    // 更新列表项选中状态
                    this.renderList();
                    
                    // 触发onChange回调
                    if (this.options.onChange) {
                        this.options.onChange(this.selectedValues, this.selectedItems);
                    }
                }
            });
        }
        
        updateSelectedTags() {
            this.selectedTags.innerHTML = '';
            
            // 如果选择了"全部标签"或没有选择，显示占位符
            if (this.selectedValues.includes('all') || this.selectedValues.length === 0) {
                this.input.placeholder = '全部标签';
                return;
            }
            
            // 显示已选标签
            this.selectedItems.forEach(item => {
                const tag = document.createElement('span');
                tag.classList.add('selected-tag');
                tag.textContent = item[this.options.textField];
                
                const removeBtn = document.createElement('span');
                removeBtn.classList.add('remove-tag');
                removeBtn.innerHTML = '&times;';
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    
                    // 移除标签
                    const value = item[this.options.valueField];
                    const index = this.selectedValues.indexOf(value);
                    if (index !== -1) {
                        this.selectedValues.splice(index, 1);
                        this.selectedItems = this.selectedItems.filter(i => i[this.options.valueField] !== value);
                    }
                    
                    // 更新显示
                    this.updateSelectedTags();
                    this.renderList();
                    
                    // 触发onChange回调
                    if (this.options.onChange) {
                        this.options.onChange(this.selectedValues, this.selectedItems);
                    }
                });
                
                tag.appendChild(removeBtn);
                this.selectedTags.appendChild(tag);
            });
            
            // 更新输入框占位符
            this.input.placeholder = this.selectedValues.length > 0 ? '' : this.options.placeholder;
        }
        
        open() {
            if (this.isOpen) return;
            
            this.isOpen = true;
            this.element.classList.add('open');
            
            // 如果没有过滤数据，使用所有数据
            if (!this.filteredData || this.filteredData.length === 0) {
                this.filteredData = this.options.data;
            }
            
            this.renderList();
            
            if (this.options.onOpen) {
                this.options.onOpen();
            }
        }
        
        close() {
            if (!this.isOpen) return;
            
            this.isOpen = false;
            this.element.classList.remove('open');
            
            if (this.options.onClose) {
                this.options.onClose();
            }
        }
        
        select(value) {
            // 在多选模式下不使用此方法
        }
        
        setValue(values) {
            if (!Array.isArray(values)) {
                values = [values];
            }
            
            this.selectedValues = values;
            this.selectedItems = values.map(value => 
                this.options.data.find(item => item[this.options.valueField] === value)
            ).filter(Boolean);
            
            this.updateSelectedTags();
            this.renderList();
        }
        
        getValue() {
            return this.selectedValues;
        }
        
        getItems() {
            return this.selectedItems;
        }
        
        destroy() {
            // 移除所有事件监听器
            if (this.input) {
                this.input.removeEventListener('input', this.handleInput);
                this.input.removeEventListener('focus', this.open);
                this.input.removeEventListener('blur', this.close);
            }
            
            if (this.dropdown) {
                // 使用事件委托，所以只需要移除一个事件监听器
                this.dropdown.innerHTML = '';
            }
            
            if (this.selectedTags) {
                this.selectedTags.innerHTML = '';
            }
            
            // 移除DOM元素
            if (this.element) {
                this.element.innerHTML = '';
                this.element.classList.remove('searchable-dropdown', 'multi-select-dropdown', 'open');
            }
        }
    }
    
    // 根据选定的多个标签筛选模板
    function filterTemplatesByTags(selectedTags) {
        // 如果没有选择标签或选择了"全部标签"，显示所有模板
        if (selectedTags.includes('all') || selectedTags.length === 0) {
            displayTemplatesByTag(allTemplates);
            return;
        }
        
        // 筛选匹配选定标签的模板
        const filteredTemplates = allTemplates.filter(template => {
            const templateTag = template.tag || '通用';
            return selectedTags.includes(templateTag);
        });
        
        // 显示筛选后的模板
        displayTemplatesByTag(filteredTemplates);
    }
    
    // 按标签分组显示模板列表
    function displayTemplatesByTag(templates) {
        const templateContainer = $('.templates-container');
        templateContainer.empty();
        
        if (!templates || templates.length === 0) {
            templateContainer.html('<p class="no-templates">暂无模板数据，请添加新模板</p>');
            return;
        }
        
        // 按标签分组
        const templatesByTag = {};
        templates.forEach(template => {
            const tag = template.tag || '通用';
            if (!templatesByTag[tag]) {
                templatesByTag[tag] = [];
            }
            templatesByTag[tag].push(template);
        });
        
        // 显示每个标签组
        Object.keys(templatesByTag).sort().forEach(tag => {
            // 获取标签颜色
            const tagColor = getTagColor(tag);
            const titleColor = tagColor.bg.replace('linear-gradient(135deg, ', '').split(',')[0];
            
            const tagGroup = $(`
                <div class="templates-by-tag" data-tag="${tag}">
                    <h3 class="tag-group-title" style="color:${titleColor}; border-bottom-color:${titleColor}">
                        ${tag}
                        <span class="tag-count">(${templatesByTag[tag].length})</span>
                    </h3>
                    <div class="tag-templates-container"></div>
                </div>
            `);
            
            const tagTemplatesContainer = tagGroup.find('.tag-templates-container');
            
            // 添加该标签下的所有模板
            templatesByTag[tag].forEach(template => {
                const templateCard = createTemplateCard(template);
                tagTemplatesContainer.append(templateCard);
            });
            
            templateContainer.append(tagGroup);
        });
    }
    
    // 创建模板卡片
    function createTemplateCard(template) {
        const tag = template.tag || '通用';
        const tagColor = getTagColor(tag);
        
        const templateCard = $(`
            <div class="template-card" data-id="${template.id}">
                <span class="template-tag" data-id="${template.id}" 
                      style="background: ${tagColor.bg};" 
                      data-hover="${tagColor.hover}">${tag}</span>
                <div class="template-card-title">${template.name}</div>
                <div class="template-card-description">${template.description || '无描述'}</div>
                ${template.page ? `<div class="template-card-page">使用页面: ${template.page}</div>` : ''}
                <div class="template-card-actions">
                    <button class="btn-edit" data-id="${template.id}">编辑</button>
                    <button class="btn-delete" data-id="${template.id}">删除</button>
                </div>
            </div>
        `);
        
        // 标签悬停效果
        templateCard.find('.template-tag').hover(
            function() {
                $(this).css('background', $(this).data('hover'));
            },
            function() {
                $(this).css('background', tagColor.bg);
            }
        );
        
        // 绑定编辑点击事件
        templateCard.find('.btn-edit').on('click', function(e) {
            e.stopPropagation();
            const templateId = $(this).data('id');
            loadTemplateForEdit(templateId);
        });
        
        // 绑定删除点击事件
        templateCard.find('.btn-delete').on('click', function(e) {
            e.stopPropagation();
            const templateId = $(this).data('id');
            deleteTemplate(templateId);
        });
        
        // 绑定标签点击事件
        templateCard.find('.template-tag').on('click', function(e) {
            e.stopPropagation();
            const templateId = $(this).data('id');
            const tagName = $(this).text();
            showTagEditDialog(templateId, tagName);
        });
        
        // 绑定卡片点击事件（显示详情）
        templateCard.on('click', function() {
            const templateId = $(this).data('id');
            loadTemplateForEdit(templateId);
        });
        
        return templateCard;
    }
    
    // 改进标签颜色生成函数
    function getTagColor(tagName) {
        // 更丰富的颜色数组，包含更多渐变组合
        const colors = [
            { bg: 'linear-gradient(135deg, #3498db, #2980b9)', hover: 'linear-gradient(135deg, #2980b9, #1a5276)' },  // 蓝色
            { bg: 'linear-gradient(135deg, #27ae60, #219955)', hover: 'linear-gradient(135deg, #219955, #196f3d)' },  // 绿色
            { bg: 'linear-gradient(135deg, #e74c3c, #c0392b)', hover: 'linear-gradient(135deg, #c0392b, #922b21)' },  // 红色
            { bg: 'linear-gradient(135deg, #f1c40f, #d4ac0d)', hover: 'linear-gradient(135deg, #d4ac0d, #9a7d0a)' },  // 黄色
            { bg: 'linear-gradient(135deg, #9b59b6, #8e44ad)', hover: 'linear-gradient(135deg, #8e44ad, #6c3483)' },  // 紫色
            { bg: 'linear-gradient(135deg, #e67e22, #d35400)', hover: 'linear-gradient(135deg, #d35400, #a04000)' },  // 橙色
            { bg: 'linear-gradient(135deg, #1abc9c, #16a085)', hover: 'linear-gradient(135deg, #16a085, #117a65)' },  // 青绿色
            { bg: 'linear-gradient(135deg, #34495e, #2c3e50)', hover: 'linear-gradient(135deg, #2c3e50, #1a252f)' },  // 深蓝灰色
            { bg: 'linear-gradient(135deg, #7f8c8d, #6c7a7a)', hover: 'linear-gradient(135deg, #6c7a7a, #515a5a)' },  // 灰色
            { bg: 'linear-gradient(135deg, #8e44ad, #6c3483)', hover: 'linear-gradient(135deg, #6c3483, #5b2d7a)' },  // 深紫色
            { bg: 'linear-gradient(135deg, #2ecc71, #27ae60)', hover: 'linear-gradient(135deg, #27ae60, #1e8449)' },  // 翠绿色
            { bg: 'linear-gradient(135deg, #f39c12, #d68910)', hover: 'linear-gradient(135deg, #d68910, #b9770e)' },  // 金黄色
            { bg: 'linear-gradient(135deg, #16a085, #138d75)', hover: 'linear-gradient(135deg, #138d75, #0e6655)' },  // 暗绿色
            { bg: 'linear-gradient(135deg, #d35400, #ba4a00)', hover: 'linear-gradient(135deg, #ba4a00, #a04000)' },  // 砖红色
            { bg: 'linear-gradient(135deg, #2c3e50, #273746)', hover: 'linear-gradient(135deg, #273746, #212f3d)' },  // 暗蓝色
            { bg: 'linear-gradient(135deg, #a569bd, #8e44ad)', hover: 'linear-gradient(135deg, #8e44ad, #6c3483)' },  // 淡紫色
            { bg: 'linear-gradient(135deg, #f5b041, #f39c12)', hover: 'linear-gradient(135deg, #f39c12, #d68910)' },  // 橘黄色
            { bg: 'linear-gradient(135deg, #45b39d, #1abc9c)', hover: 'linear-gradient(135deg, #1abc9c, #16a085)' },  // 薄荷绿
            { bg: 'linear-gradient(135deg, #5dade2, #3498db)', hover: 'linear-gradient(135deg, #3498db, #2874a6)' },  // 天蓝色
            { bg: 'linear-gradient(135deg, #ec7063, #e74c3c)', hover: 'linear-gradient(135deg, #e74c3c, #cb4335)' },  // 浅红色
            { bg: 'linear-gradient(135deg, #52be80, #27ae60)', hover: 'linear-gradient(135deg, #27ae60, #1e8449)' },  // 碧绿色
            { bg: 'linear-gradient(135deg, #af7ac5, #9b59b6)', hover: 'linear-gradient(135deg, #9b59b6, #884ea0)' },  // 兰花紫
            { bg: 'linear-gradient(135deg, #5499c7, #3498db)', hover: 'linear-gradient(135deg, #3498db, #2874a6)' }   // 皇家蓝
        ];
        
        // 默认颜色为标准蓝色(通用标签)
        if (tagName === '通用') {
            return colors[0];
        }
        
        // 使用改进的哈希算法，确保不同标签有不同颜色
        let hash = 0;
        for (let i = 0; i < tagName.length; i++) {
            // 使用质数乘法和标签字符的位置来增加散列分布
            const charCode = tagName.charCodeAt(i);
            hash = ((hash << 5) - hash) + charCode + i * 7;
            hash = hash & hash; // 转换为32位整数
        }
        
        // 混合标签长度到哈希值，使类似但长度不同的标签获得不同颜色
        hash = (hash * 31 + tagName.length * 13) & 0xFFFFFFFF;
        
        // 确保不是负数
        hash = Math.abs(hash);
        
        // 存储已使用的标签颜色映射
        if (!window.tagColorMap) {
            window.tagColorMap = {};
        }
        
        // 如果这个标签已经有一个颜色，返回它
        if (window.tagColorMap[tagName] !== undefined) {
            return colors[window.tagColorMap[tagName]];
        }
        
        // 查找当前未使用的颜色
        const usedIndices = Object.values(window.tagColorMap);
        let index = hash % colors.length;
        let attempts = 0;
        const maxAttempts = colors.length;
        
        // 如果颜色已被使用，尝试下一个
        while (usedIndices.includes(index) && attempts < maxAttempts) {
            index = (index + 1) % colors.length;
            attempts++;
        }
        
        // 如果尝试了所有颜色还找不到未使用的，就随机选一个
        if (attempts >= maxAttempts) {
            index = hash % colors.length;
        }
        
        // 保存这个标签的颜色索引
        window.tagColorMap[tagName] = index;
        
        return colors[index];
    }
    
    // 显示标签编辑对话框 - 更新添加标签颜色预览
    function showTagEditDialog(templateId, currentTag) {
        $('#tagTemplateId').val(templateId);
        $('#tagName').val(currentTag);
        $('#tagEditDialog').show();
        $('#tagName').focus();
        
        // 添加标签颜色预览功能
        updateTagColorPreview(currentTag);
        
        // 当输入框内容变化时，更新颜色预览
        $('#tagName').off('input').on('input', function() {
            const newTagName = $(this).val().trim();
            updateTagColorPreview(newTagName);
        });
    }
    
    // 添加更新标签颜色预览的函数
    function updateTagColorPreview(tagName) {
        const color = getTagColor(tagName || '通用');
        const preview = $('#tagName').css('border-color', color.bg.replace('linear-gradient', '#'));
    }
    
    // 保存模板标签
    function saveTemplateTag() {
        const templateId = $('#tagTemplateId').val();
        const tagName = $('#tagName').val().trim();
        
        if (!tagName) {
            alert('请输入有效的标签名称');
            return;
        }
        
        $.ajax({
            url: `/api/prompt_templates/${templateId}/tag`,
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ tag: tagName }),
            success: function(response) {
                if (response.success) {
                    $('#tagEditDialog').hide();
                    
                    // 更新模板列表中的对应模板标签
                    const templateIndex = allTemplates.findIndex(t => t.id === templateId);
                    if (templateIndex !== -1) {
                        allTemplates[templateIndex].tag = tagName;
                        
                        // 重新初始化标签过滤器
                        initTagFilter(allTemplates);
                        
                        // 获取当前选中的标签
                        const currentSelectedTags = window.tagFilterDropdown && typeof window.tagFilterDropdown.getValue === 'function' ? 
                            window.tagFilterDropdown.getValue() : [];
                        
                        // 如果没有选择标签或选择了"全部标签"，显示所有模板
                        if (currentSelectedTags.includes('all') || currentSelectedTags.length === 0) {
                            displayTemplatesByTag(allTemplates);
                        } else {
                            // 筛选模板
                            filterTemplatesByTags(currentSelectedTags);
                        }
                    }
                } else {
                    alert('更新标签失败: ' + response.message);
                }
            },
            error: function(xhr) {
                alert('更新标签请求出错: ' + xhr.responseText);
            }
        });
    }
    
    // 加载模板进行编辑
    function loadTemplateForEdit(templateId) {
        $.ajax({
            url: `/api/prompt_templates/${templateId}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const template = response.template;
                    
                    // 填充基本信息
                    $('#templateName').val(template.name);
                    $('#templateDescription').val(template.description || '');
                    $('#templatePage').val(template.page || '');
                    
                    // 解析模板内容为系统、用户提示词
                    parseTemplateContent(template.content);
                    
                    // 设置当前编辑的模板ID
                    $('#saveTemplate').data('template-id', templateId);
                    
                    // 自动滚动到模板编辑区域
                    setTimeout(function() {
                        const editSection = document.querySelector('.template-edit-section');
                        if (editSection) {
                            editSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 100); // 添加短暂延迟确保DOM已更新
                } else {
                    console.error('获取模板详情失败:', response.message);
                    alert('获取模板详情失败: ' + response.message);
                }
            },
            error: function(xhr) {
                console.error('获取模板详情请求失败:', xhr);
                alert('获取模板详情请求失败，请查看控制台日志');
            }
        });
    }
    
    // 解析模板内容
    function parseTemplateContent(content) {
        if (!content) return;
        
        try {
            // 尝试解析JSON格式的模板内容
            const templateData = JSON.parse(content);
            
            // 填充各个部分
            $('#systemPrompt').val(templateData.system || '');
            $('#userPrompt').val(templateData.user || '');
        } catch (e) {
            // 如果不是JSON格式，则按照旧格式处理（放入用户提示词中）
            console.warn('模板格式不是JSON，将内容放入用户提示词', e);
            $('#systemPrompt').val('');
            $('#userPrompt').val(content);
        }
    }
    
    // 保存模板
    function saveTemplate() {
        const templateId = $('#saveTemplate').data('template-id');
        const templateName = $('#templateName').val();
        const templateDescription = $('#templateDescription').val();
        const templatePage = $('#templatePage').val();
        
        // 获取系统提示词和用户提示词
        const systemPrompt = $('#systemPrompt').val();
        const userPrompt = $('#userPrompt').val();
        
        if (!templateName) {
            alert('请输入模板名称');
            return;
        }
        
        if (!userPrompt) {
            alert('请输入用户提示词');
            return;
        }
        
        // 构建新的模板内容格式（JSON）
        const templateContent = JSON.stringify({
            system: systemPrompt,
            user: userPrompt
        });
        
        const templateData = {
            name: templateName,
            description: templateDescription,
            page: templatePage,
            content: templateContent
        };
        
        // 如果是编辑现有模板，获取它的标签
        if (templateId) {
            const tagElement = $(`.template-tag[data-id="${templateId}"]`);
            if (tagElement.length > 0) {
                templateData.tag = tagElement.text();
            }
        }
        
        // 检查模板名称是否已存在
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const templates = response.templates || [];
                    const existingTemplate = templates.find(t => t.name === templateName && t.id !== templateId);
                    
                    // 如果有ID并且名称没变，直接更新
                    if (templateId) {
                        const currentTemplate = templates.find(t => t.id === templateId);
                        if (currentTemplate && currentTemplate.name === templateName) {
                            if (!confirm('确认要修改此模板吗？')) {
                                return;
                            }
                            updateOrCreateTemplate(templateId, templateData);
                            return;
                        }
                    }
                    
                    // 如果名称已存在
                    if (existingTemplate) {
                        alert(`错误：已存在名为"${templateName}"的模板，请更换模板名称。`);
                        return;
                    } else {
                        if (!confirm(`确认要新增模板"${templateName}"吗？`)) {
                            return;
                        }
                    }
                    
                    // 执行保存或更新
                    updateOrCreateTemplate(templateId, templateData);
                    
                } else {
                    console.error('获取模板列表失败:', response.message);
                    if (!confirm('无法检查模板是否存在，是否继续保存？')) {
                        return;
                    }
                    updateOrCreateTemplate(templateId, templateData);
                }
            },
            error: function(xhr) {
                console.error('获取模板列表请求失败:', xhr);
                if (!confirm('无法检查模板是否存在，是否继续保存？')) {
                    return;
                }
                updateOrCreateTemplate(templateId, templateData);
            }
        });
    }
    
    // 更新或创建模板
    function updateOrCreateTemplate(templateId, templateData) {
        const isUpdate = !!templateId;
        const url = isUpdate ? `/api/prompt_templates/${templateId}` : '/api/prompt_templates/create';
        const method = isUpdate ? 'PUT' : 'POST';
        
        $.ajax({
            url: url,
            type: method,
            contentType: 'application/json',
            data: JSON.stringify(templateData),
            success: function(response) {
                if (response.success) {
                    // 更新或添加template到allTemplates
                    if (isUpdate) {
                        const index = allTemplates.findIndex(t => t.id === templateId);
                        if (index !== -1) {
                            allTemplates[index] = response.template;
                        }
                    } else {
                        allTemplates.push(response.template);
                    }
                    
                    // 重新初始化标签过滤器
                    initTagFilter(allTemplates);
                    
                    // 如果创建了新模板，清空表单
                    if (!isUpdate) {
                        clearTemplateForm();
                    }
                    
                    // 获取当前选中的标签
                    const currentSelectedTags = window.tagFilterDropdown && typeof window.tagFilterDropdown.getValue === 'function' ? 
                        window.tagFilterDropdown.getValue() : [];
                    
                    // 如果没有选择标签或选择了"全部标签"，显示所有模板
                    if (currentSelectedTags.includes('all') || currentSelectedTags.length === 0) {
                        displayTemplatesByTag(allTemplates);
                    } else {
                        // 筛选模板
                        filterTemplatesByTags(currentSelectedTags);
                    }
                    
                    alert('保存成功');
                } else {
                    alert('保存失败: ' + response.message);
                }
            },
            error: function(xhr) {
                console.error('保存模板请求失败:', xhr);
                alert('保存模板请求失败，请查看控制台日志');
            }
        });
    }
    
    // 删除模板
    function deleteTemplate(templateId) {
        if (!confirm('确定要删除此模板吗？此操作不可恢复。')) {
            return;
        }
        
        $.ajax({
            url: `/api/prompt_templates/${templateId}`,
            type: 'DELETE',
            success: function(response) {
                if (response.success) {
                    // 从allTemplates中移除已删除的模板
                    allTemplates = allTemplates.filter(template => template.id !== templateId);
                    
                    // 重新初始化标签过滤器
                    initTagFilter(allTemplates);
                    
                    // 获取当前选中的标签
                    const currentSelectedTags = window.tagFilterDropdown && typeof window.tagFilterDropdown.getValue === 'function' ? 
                        window.tagFilterDropdown.getValue() : [];
                    
                    // 如果没有选择标签或选择了"全部标签"，显示所有模板
                    if (currentSelectedTags.includes('all') || currentSelectedTags.length === 0) {
                        displayTemplatesByTag(allTemplates);
                    } else {
                        // 筛选模板
                        filterTemplatesByTags(currentSelectedTags);
                    }
                } else {
                    alert('删除模板失败: ' + response.message);
                }
            },
            error: function(xhr) {
                console.error('删除模板请求失败:', xhr);
                alert('删除模板请求失败，请查看控制台日志');
            }
        });
    }
    
    // 预览模板
    function previewTemplate() {
        const systemPrompt = $('#systemPrompt').val();
        const userPrompt = $('#userPrompt').val();
        
        if (!userPrompt) {
            alert('请先输入用户提示词');
            return;
        }
        
        // 显示预览
        let finalPreview = '';
        
        if (systemPrompt) {
            finalPreview += '<div class="preview-system">';
            finalPreview += '<strong>系统：</strong><pre>' + escapeHtml(systemPrompt) + '</pre>';
            finalPreview += '</div>';
        }
        
        finalPreview += '<div class="preview-user">';
        finalPreview += '<strong>用户：</strong><pre>' + escapeHtml(userPrompt) + '</pre>';
        finalPreview += '</div>';
        
        $('.preview-content').html(finalPreview);
        $('.template-preview-section').show();
    }
    
    // HTML转义函数
    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // 清空模板表单
    function clearTemplateForm() {
        $('#templateName').val('');
        $('#templateDescription').val('');
        $('#templatePage').val('');
        $('#systemPrompt').val('');
        $('#userPrompt').val('');
        
        // 移除模板ID
        $('#saveTemplate').removeData('template-id');
    }
}); 