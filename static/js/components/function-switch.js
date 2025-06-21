/**
 * 数据库表结构管理-功能切换组件
 * 提供页面功能模式切换的下拉选择框组件
 */
class FunctionSwitch {
    /**
     * 初始化功能切换组件
     * @param {Object} config 配置对象
     * @param {string} config.elementId 下拉框元素ID（不含#）
     * @param {Function} config.onChange 值变化时的回调函数
     * @param {Array} config.options 可选项配置 [{value: '', text: ''}]
     */
    constructor(config) {
        this.elementId = config.elementId;
        this.onChange = config.onChange || function() {};
        this.options = config.options || [];
        
        this.init();
    }
    
    /**
     * 初始化组件
     */
    init() {
        // 获取元素
        this.element = document.getElementById(this.elementId);
        if (!this.element) {
            console.error(`未找到ID为${this.elementId}的元素`);
            return;
        }
        
        // 绑定事件
        this.element.addEventListener('change', (event) => {
            const value = event.target.value;
            this.onChange(value);
        });
        
        // 设置默认值
        if (this.options.length > 0 && this.element.options.length === 0) {
            this.setOptions(this.options);
        }
    }
    
    /**
     * 获取当前值
     * @returns {string} 当前选中的值
     */
    getValue() {
        return this.element ? this.element.value : '';
    }
    
    /**
     * 设置值
     * @param {string} value 要设置的值
     */
    setValue(value) {
        if (this.element) {
            this.element.value = value;
            
            // 触发change事件
            const event = new Event('change');
            this.element.dispatchEvent(event);
        }
    }
    
    /**
     * 设置选项
     * @param {Array} options 选项数组 [{value: '', text: ''}]
     */
    setOptions(options) {
        if (!this.element || !options || !Array.isArray(options)) return;
        
        // 清空现有选项
        this.element.innerHTML = '';
        
        // 添加新选项
        options.forEach(option => {
            const optElement = document.createElement('option');
            optElement.value = option.value;
            optElement.textContent = option.text;
            this.element.appendChild(optElement);
        });
    }
} 