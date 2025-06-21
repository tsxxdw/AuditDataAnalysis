/**
 * 页面头部组件
 * 处理导航菜单交互，包括移动端菜单的切换和页面大小调整响应
 */
// 头部组件的JavaScript
$(document).ready(function() {
    // 移动端菜单按钮点击事件
    $('.mobile-menu-toggle').on('click', function() {
        $('.header-container').toggleClass('menu-active');
    });
    
    // 点击页面其他区域关闭菜单
    $(document).on('click', function(event) {
        if (!$(event.target).closest('.mobile-menu-toggle, .header-container').length) {
            $('.header-container').removeClass('menu-active');
        }
    });
    
    // 窗口调整大小时，如果屏幕变宽，移除菜单的active类
    $(window).on('resize', function() {
        if ($(window).width() > 768) {
            $('.header-container').removeClass('menu-active');
        }
    });
}); 