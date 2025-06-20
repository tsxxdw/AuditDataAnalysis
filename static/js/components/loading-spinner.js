/**
 * 加载指示器组件
 * 提供一个可复用的加载指示器（转圈圈）
 */
class LoadingSpinner {
    /**
     * 构造函数
     * @param {Object} options - 配置选项
     * @param {string} options.containerId - 容器ID，默认为loadingSpinner
     * @param {string} options.containerSelector - 容器选择器，优先于containerId
     * @param {string} options.text - 加载文本
     * @param {Object} options.styles - 自定义样式
     */
    constructor(options = {}) {
        this.options = Object.assign({
            containerId: 'loadingSpinner',
            text: '加载中...',
            styles: {}
        }, options);
        
        this.containerSelector = options.containerSelector || `#${this.options.containerId}`;
        this.init();
    }
    
    /**
     * 初始化组件
     */
    init() {
        // 检查容器是否存在
        if ($(this.containerSelector).length === 0) {
            // 如果不存在，则动态创建
            this.createSpinner();
        }
        
        // 应用自定义样式
        this.applyCustomStyles();
    }
    
    /**
     * 动态创建加载指示器
     */
    createSpinner() {
        const $container = $('<div>')
            .attr('id', this.options.containerId)
            .addClass('loading-spinner-overlay')
            .css('display', 'none');
            
        const $spinnerContainer = $('<div>')
            .addClass('loading-spinner-container');
            
        const $spinner = $('<div>')
            .addClass('loading-spinner');
            
        const $text = $('<p>')
            .addClass('loading-text')
            .text(this.options.text);
            
        $spinnerContainer.append($spinner).append($text);
        $container.append($spinnerContainer);
        
        // 添加到body
        $('body').append($container);
    }
    
    /**
     * 应用自定义样式
     */
    applyCustomStyles() {
        const styles = this.options.styles;
        
        if (Object.keys(styles).length > 0) {
            $(this.containerSelector).css(styles);
        }
    }
    
    /**
     * 显示加载指示器
     * @param {string} text - 可选，覆盖默认加载文本
     * @param {Object} targetElement - 可选，目标元素，如果指定则将加载指示器添加到该元素内
     */
    show(text, targetElement) {
        // 更新文本（如果提供）
        if (text) {
            $(`${this.containerSelector} .loading-text`).text(text);
        }
        
        // 如果指定了目标元素，将加载指示器移动到该元素内
        if (targetElement) {
            const $target = $(targetElement);
            
            if ($target.length > 0) {
                // 确保目标元素有相对定位
                if ($target.css('position') === 'static') {
                    $target.css('position', 'relative');
                }
                
                // 移动加载指示器到目标元素
                $(this.containerSelector).appendTo($target);
            }
        }
        
        // 显示加载指示器
        $(this.containerSelector).show();
    }
    
    /**
     * 隐藏加载指示器
     */
    hide() {
        $(this.containerSelector).hide();
    }
    
    /**
     * 设置加载文本
     * @param {string} text - 新的加载文本
     */
    setText(text) {
        $(`${this.containerSelector} .loading-text`).text(text);
    }
    
    /**
     * 销毁加载指示器
     */
    destroy() {
        $(this.containerSelector).remove();
    }
}

// 导出组件
window.LoadingSpinner = LoadingSpinner; 