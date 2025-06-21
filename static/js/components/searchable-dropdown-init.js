/**
 * SearchableDropdown初始化助手
 * 提供简化的初始化方式，支持jQuery插件模式及多种模块化导出
 */

function initSearchableDropdown(selector, data, options = {}) {
    const element = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (!element) {
        console.error(`Element not found: ${selector}`);
        return null;
    }

    const defaultOptions = {
        element: element,
        data: data,
        ...options
    };
    
    // 如果存在隐藏的select元素，自动绑定onChange事件
    if (options.hiddenSelectId) {
        const hiddenSelect = document.getElementById(options.hiddenSelectId);
        if (hiddenSelect) {
            const originalOnChange = defaultOptions.onChange || function() {};
            
            defaultOptions.onChange = function(value, item) {
                // 更新隐藏的select值
                hiddenSelect.value = value;
                
                // 触发原始onChange事件
                originalOnChange(value, item);
                
                // 触发change事件，以便其他监听器能够响应
                const event = new Event('change');
                hiddenSelect.dispatchEvent(event);
            };
        }
    }

    return new SearchableDropdown(defaultOptions);
}

/**
 * 通过HTML模板初始化SearchableDropdown
 * 自动处理隐藏的select元素
 */
function initSearchableDropdownFromTemplate(containerSelector, data, options = {}) {
    const container = document.querySelector(containerSelector);
    if (!container) {
        console.error(`Container not found: ${containerSelector}`);
        return null;
    }
    
    // 查找下拉框容器元素
    const dropdownElement = container.querySelector('.searchable-dropdown');
    if (!dropdownElement) {
        console.error(`Dropdown element not found in container: ${containerSelector}`);
        return null;
    }
    
    // 查找隐藏的select元素
    const hiddenSelect = container.querySelector('select');
    const hiddenSelectId = hiddenSelect ? hiddenSelect.id : null;
    
    // 合并选项
    const mergedOptions = {
        ...options,
        element: dropdownElement,
        hiddenSelectId: hiddenSelectId
    };
    
    // 初始化下拉框
    return initSearchableDropdown(dropdownElement, data, mergedOptions);
}

// jQuery插件支持
if (typeof jQuery !== 'undefined') {
    jQuery.fn.searchableDropdown = function(options) {
        return this.each(function() {
            const $this = jQuery(this);
            if (!$this.data('searchableDropdown')) {
                const instance = initSearchableDropdown(this, options.data, {
                    ...options,
                    element: this
                });
                $this.data('searchableDropdown', instance);
            }
        });
    };
}

// 导出初始化函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initSearchableDropdown,
        initSearchableDropdownFromTemplate
    };
} else if (typeof define === 'function' && define.amd) {
    define([], function() { 
        return {
            initSearchableDropdown,
            initSearchableDropdownFromTemplate
        };
    });
} else {
    window.initSearchableDropdown = initSearchableDropdown;
    window.initSearchableDropdownFromTemplate = initSearchableDropdownFromTemplate;
} 