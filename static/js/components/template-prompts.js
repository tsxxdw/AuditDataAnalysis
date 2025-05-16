/**
 * 模板提示词区域组件
 * 提供模板选择、查看详情以及控制组件显示/隐藏、禁用、只读等功能
 */
class TemplatePrompts {
    /**
     * 构造函数
     * @param {Object} options 配置选项
     * @param {string} [options.containerId='templatePromptsContainer'] 组件容器ID
     * @param {string} [options.dropdownId='templateDropdown'] 下拉框ID
     * @param {string} [options.selectId='promptTemplate'] 隐藏选择器ID
     * @param {string} [options.buttonId='viewTemplateDetails'] 查看详情按钮ID
     * @param {string} [options.modalId='templateDetailsModal'] 模态框ID
     * @param {Function} [options.onSelect] 选择模板时的回调函数
     */
    constructor(options = {}) {
        // 默认配置
        this.config = {
            containerId: 'templatePromptsContainer',
            dropdownId: 'templateDropdown',
            selectId: 'promptTemplate',
            buttonId: 'viewTemplateDetails',
            modalId: 'templateDetailsModal',
            onSelect: null,
            ...options
        };
        
        // 缓存DOM元素
        this.container = document.getElementById(this.config.containerId);
        this.dropdown = document.getElementById(this.config.dropdownId);
        this.select = document.getElementById(this.config.selectId);
        this.detailsButton = document.getElementById(this.config.buttonId);
        this.modal = document.getElementById(this.config.modalId);
        
        // 组件状态
        this.state = {
            visible: true,
            disabled: false,
            readonly: false,
            selectedTemplateId: ''
        };
        
        // 保存全部模板数据
        this.templates = [];
        
        // 初始化下拉框组件实例
        this.dropdownInstance = null;
        
        // 自动初始化
        this.init();
    }
    
    /**
     * 初始化组件
     */
    init() {
        // 检查DOM元素是否存在
        if (!this.container || !this.dropdown || !this.select || !this.detailsButton || !this.modal) {
            console.error('模板提示词组件初始化失败：缺少必要的DOM元素');
            return;
        }
        
        // 绑定模态框关闭事件
        const closeModal = this.modal.querySelector('.close-modal');
        if (closeModal) {
            closeModal.addEventListener('click', () => this.hideModal());
        }
        
        // 绑定模态框外部点击关闭
        window.addEventListener('click', (event) => {
            if (event.target === this.modal) {
                this.hideModal();
            }
        });
        
        // 绑定查看详情按钮事件
        this.detailsButton.addEventListener('click', () => this.showTemplateDetails());
        
        // 加载模板数据
        this.loadPromptTemplates();
    }
    
    /**
     * 加载提示词模板列表
     */
    loadPromptTemplates() {
        // 调用API获取模板数据
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: (response) => {
                if (response.success) {
                    this.templates = response.templates;
                    this.initializeTemplateDropdown(this.templates);
                } else {
                    console.error('加载提示词模板失败:', response.message);
                }
            },
            error: (xhr) => {
                console.error('请求提示词模板列表失败:', xhr);
            }
        });
    }
    
    /**
     * 初始化模板下拉选择器
     * @param {Array} templates 模板数据数组
     */
    initializeTemplateDropdown(templates) {
        // 转换数据结构以适应SearchableDropdown组件
        const dropdownData = templates.map(template => ({
            id: template.id,
            text: template.name,
            description: template.description || ''
        }));
        
        // 创建下拉选择器实例
        if (window.SearchableDropdown) {
            this.dropdownInstance = new SearchableDropdown({
                element: `#${this.config.dropdownId}`,
                data: dropdownData,
                valueField: 'id',
                textField: 'text',
                searchFields: ['text', 'description'],
                placeholder: '输入关键词搜索模板...',
                noResultsText: '没有找到匹配的模板',
                itemTemplate: (item) => `
                    <div>
                        <span style="font-weight: bold;">${item.text}</span>
                        ${item.description ? `<span style="color: #777; display: block; font-size: 0.85em;">${item.description}</span>` : ''}
                    </div>
                `,
                onChange: (value, item) => this.handleTemplateChange(value, item)
            });
            
            // 将实例保存到全局以保持兼容性
            window.templateDropdown = this.dropdownInstance;
        } else {
            console.error('初始化模板下拉选择器失败：SearchableDropdown组件未定义');
        }
    }
    
    /**
     * 处理模板选择变化
     * @param {string} value 选中的模板ID
     * @param {Object} item 选中的模板对象
     */
    handleTemplateChange(value, item) {
        // 设置隐藏下拉框的值
        if (this.select) {
            this.select.value = value;
        }
        
        // 保存选中的模板ID
        this.state.selectedTemplateId = value;
        
        // 保存ID到按钮的data属性中
        if (this.detailsButton) {
            this.detailsButton.dataset.templateId = value;
            
            // 启用查看详情按钮
            this.detailsButton.disabled = !value;
        }
        
        // 调用回调函数
        if (typeof this.config.onSelect === 'function') {
            this.config.onSelect(value, item);
        }
    }
    
    /**
     * 显示模板详情
     */
    showTemplateDetails() {
        // 获取当前选中的模板ID
        const templateId = this.getSelectedTemplateId();
        
        if (!templateId) {
            alert('请先选择一个模板');
            return;
        }
        
        // 调用API获取模板详情
        $.ajax({
            url: `/api/prompt_templates/${templateId}`,
            type: 'GET',
            success: (response) => {
                if (response.success) {
                    this.displayTemplateDetails(response.template);
                } else {
                    alert(response.message || '获取模板详情失败');
                }
            },
            error: (xhr) => {
                console.error('获取模板详情失败:', xhr);
                alert('获取模板详情失败，请查看控制台日志');
            }
        });
    }
    
    /**
     * 显示模板详情内容
     * @param {Object} template 模板对象
     */
    displayTemplateDetails(template) {
        let templateContent;
        
        try {
            templateContent = JSON.parse(template.content);
        } catch (e) {
            console.error('解析模板内容失败:', e);
            alert('模板内容格式错误');
            return;
        }
        
        // 清空旧内容
        const elements = [
            '.template-name-text', 
            '.template-description-text', 
            '.system-prompt-text', 
            '.user-prompt-text'
        ];
        
        elements.forEach(selector => {
            const element = this.modal.querySelector(selector);
            if (element) element.textContent = '';
        });
        
        // 显示模板名称
        const nameElement = this.modal.querySelector('.template-name-text');
        if (nameElement) nameElement.textContent = template.name;
        
        // 显示模板描述
        const descElement = this.modal.querySelector('.template-description-text');
        if (descElement) {
            descElement.textContent = template.description || '无描述';
        }
        
        // 显示系统提示词
        const systemElement = this.modal.querySelector('.system-prompt-text');
        if (systemElement) {
            systemElement.textContent = templateContent.system || '无系统提示词';
        }
        
        // 显示用户提示词
        const userElement = this.modal.querySelector('.user-prompt-text');
        if (userElement) {
            userElement.textContent = templateContent.user || '无用户提示词';
        }
        
        // 显示模态框
        this.showModal();
    }
    
    /**
     * 显示模态框
     */
    showModal() {
        if (this.modal) {
            this.modal.style.display = 'block';
        }
    }
    
    /**
     * 隐藏模态框
     */
    hideModal() {
        if (this.modal) {
            this.modal.style.display = 'none';
        }
    }
    
    /**
     * 获取当前选中的模板ID
     * @returns {string} 模板ID
     */
    getSelectedTemplateId() {
        // 优先从状态中获取
        if (this.state.selectedTemplateId) {
            return this.state.selectedTemplateId;
        }
        
        // 其次从下拉框组件实例获取
        if (this.dropdownInstance && typeof this.dropdownInstance.getValue === 'function') {
            return this.dropdownInstance.getValue();
        }
        
        // 最后从隐藏的select元素获取
        if (this.select) {
            return this.select.value;
        }
        
        return '';
    }
    
    /**
     * 显示组件
     */
    show() {
        this.setVisible(true);
    }
    
    /**
     * 隐藏组件
     */
    hide() {
        this.setVisible(false);
    }
    
    /**
     * 设置组件显示状态
     * @param {boolean} visible 是否显示
     */
    setVisible(visible) {
        this.state.visible = visible;
        if (this.container) {
            this.container.style.display = visible ? 'block' : 'none';
        }
    }
    
    /**
     * 禁用组件
     */
    disable() {
        this.setDisabled(true);
    }
    
    /**
     * 启用组件
     */
    enable() {
        this.setDisabled(false);
    }
    
    /**
     * 设置组件禁用状态
     * @param {boolean} disabled 是否禁用
     */
    setDisabled(disabled) {
        this.state.disabled = disabled;
        // 实现禁用逻辑
    }
    
    /**
     * 设置为只读模式
     */
    setReadOnly() {
        this.setReadOnly(true);
    }
    
    /**
     * 设置为可编辑模式
     */
    setEditable() {
        this.setReadOnly(false);
    }
    
    /**
     * 设置组件只读状态
     * @param {boolean} readonly 是否只读
     */
    setReadOnly(readonly) {
        this.state.readonly = readonly;
        // 实现只读逻辑
    }
    
    /**
     * 重置组件
     */
    reset() {
        // 重置选中状态
        this.state.selectedTemplateId = '';
        
        // 重置下拉框
        if (this.dropdownInstance && typeof this.dropdownInstance.reset === 'function') {
            this.dropdownInstance.reset();
        }
        
        // 重置隐藏的select
        if (this.select) {
            this.select.value = '';
        }
        
        // 禁用详情按钮
        if (this.detailsButton) {
            this.detailsButton.disabled = true;
        }
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        // 解绑事件
        const closeModal = this.modal.querySelector('.close-modal');
        if (closeModal) {
            closeModal.removeEventListener('click', () => this.hideModal());
        }
        
        this.detailsButton.removeEventListener('click', () => this.showTemplateDetails());
        
        // 销毁下拉框实例
        if (this.dropdownInstance && typeof this.dropdownInstance.destroy === 'function') {
            this.dropdownInstance.destroy();
        }
        
        // 移除全局引用
        window.templateDropdown = null;
        window.templatePromptsComponent = null;
    }
} 