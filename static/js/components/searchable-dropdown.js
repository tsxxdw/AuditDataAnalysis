/**
 * 可搜索下拉框组件
 * 提供带搜索过滤功能的下拉选择框，支持自定义模板和事件回调
 */
class SearchableDropdown {
    constructor(options) {
        this.options = {
            element: null,
            data: [],
            valueField: 'id',
            textField: 'text',
            searchFields: ['text'],
            placeholder: '搜索...',
            noResultsText: '无匹配结果',
            itemTemplate: null,
            onChange: null,
            onSearch: null,
            onOpen: null,
            onClose: null,
            ...options
        };

        this.element = typeof this.options.element === 'string' 
            ? document.querySelector(this.options.element)
            : this.options.element;

        if (!this.element) {
            throw new Error('Element not found');
        }

        this.isOpen = false;
        this.selectedValue = null;
        this.selectedItem = null;
        this.filteredData = [];

        this.init();
    }

    init() {
        // 创建组件结构
        this.createStructure();
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化数据
        this.refresh();
    }

    createStructure() {
        this.element.classList.add('searchable-dropdown');
        
        // 创建输入框
        this.input = document.createElement('input');
        this.input.type = 'text';
        this.input.placeholder = this.options.placeholder;
        this.input.classList.add('searchable-dropdown-input');
        this.input.classList.add('form-control');
        
        // 创建下拉列表容器
        this.dropdown = document.createElement('div');
        this.dropdown.classList.add('searchable-dropdown-list');
        
        // 组装结构
        this.element.innerHTML = '';
        this.element.appendChild(this.input);
        this.element.appendChild(this.dropdown);
    }

    bindEvents() {
        // 输入框事件
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('focus', () => this.open());
        this.input.addEventListener('blur', () => setTimeout(() => this.close(), 200));
        
        // 点击事件委托
        this.dropdown.addEventListener('click', (e) => {
            const item = e.target.closest('.searchable-dropdown-item');
            if (item) {
                const value = item.dataset.value;
                this.select(value);
            }
        });
    }

    async handleInput(e) {
        const query = e.target.value.trim();
        
        if (this.options.onSearch) {
            this.options.onSearch(query);
        }
        
        await this.filterData(query);
        this.renderList();
    }

    async filterData(query) {
        if (typeof this.options.data === 'function') {
            this.filteredData = await this.options.data(query);
        } else {
            this.filteredData = this.options.data.filter(item => {
                return this.options.searchFields.some(field => {
                    const value = item[field];
                    return value && value.toString().toLowerCase().includes(query.toLowerCase());
                });
            });
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
            
            if (this.selectedValue === item[this.options.valueField]) {
                itemElement.classList.add('selected');
            }
            
            this.dropdown.appendChild(itemElement);
        });
    }

    open() {
        if (this.isOpen) return;
        
        this.isOpen = true;
        this.element.classList.add('open');
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

    async select(value) {
        const item = this.filteredData.find(item => item[this.options.valueField] === value);
        if (!item) return;
        
        this.selectedValue = value;
        this.selectedItem = item;
        this.input.value = item[this.options.textField];
        
        this.close();
        
        if (this.options.onChange) {
            this.options.onChange(value, item);
        }
    }

    setValue(value) {
        this.select(value);
    }

    getValue() {
        return this.selectedValue;
    }

    getText() {
        return this.selectedItem ? this.selectedItem[this.options.textField] : '';
    }

    async refresh() {
        await this.filterData('');
        this.renderList();
    }

    destroy() {
        // 移除所有事件监听器
        this.input.removeEventListener('input', this.handleInput);
        this.input.removeEventListener('focus', this.open);
        this.input.removeEventListener('blur', this.close);
        this.dropdown.removeEventListener('click', this.handleClick);
        
        // 移除DOM元素
        this.element.innerHTML = '';
        this.element.classList.remove('searchable-dropdown');
    }
}

// 导出组件
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SearchableDropdown;
} else if (typeof define === 'function' && define.amd) {
    define([], function() { return SearchableDropdown; });
} else {
    window.SearchableDropdown = SearchableDropdown;
} 