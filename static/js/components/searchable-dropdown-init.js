/**
 * SearchableDropdown初始化助手
 * 提供简化的初始化方式
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

    return new SearchableDropdown(defaultOptions);
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
    module.exports = initSearchableDropdown;
} else if (typeof define === 'function' && define.amd) {
    define([], function() { return initSearchableDropdown; });
} else {
    window.initSearchableDropdown = initSearchableDropdown;
} 