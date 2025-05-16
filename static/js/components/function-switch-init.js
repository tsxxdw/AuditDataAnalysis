/**
 * 功能切换组件初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否已存在FunctionSwitch类
    if (typeof FunctionSwitch !== 'undefined') {
        // 暴露到全局，方便其他JS调用
        window.createFunctionSwitch = function(elementId, options, onChange) {
            return new FunctionSwitch({
                elementId: elementId,
                options: options,
                onChange: onChange
            });
        };
        
        // 自动初始化页面上已有的功能切换组件
        const initFunctionSwitches = function() {
            const switchElements = document.querySelectorAll('.function-switch select');
            
            switchElements.forEach(function(element) {
                if (element.id) {
                    // 为每个功能切换下拉框创建实例
                    window[element.id + 'Switch'] = new FunctionSwitch({
                        elementId: element.id,
                        onChange: function(value) {
                            // 触发自定义事件，方便其他JS监听
                            const event = new CustomEvent('functionSwitchChange', {
                                detail: {
                                    id: element.id,
                                    value: value
                                }
                            });
                            document.dispatchEvent(event);
                        }
                    });
                }
            });
        };
        
        // 执行初始化
        initFunctionSwitches();
    } else {
        console.error('FunctionSwitch类未定义，请确保先加载function-switch.js');
    }
}); 