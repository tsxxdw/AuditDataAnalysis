/**
 * 加载指示器组件初始化
 * 该脚本用于初始化全局加载指示器实例
 */
$(document).ready(function() {
    // 创建全局加载指示器实例
    window.globalSpinner = new LoadingSpinner({
        containerId: 'globalLoadingSpinner',
        text: '处理中...'
    });
    
    // 暴露全局方法，用于显示/隐藏加载指示器
    window.showGlobalSpinner = function(text, targetElement) {
        window.globalSpinner.show(text, targetElement);
    };
    
    window.hideGlobalSpinner = function() {
        window.globalSpinner.hide();
    };
}); 