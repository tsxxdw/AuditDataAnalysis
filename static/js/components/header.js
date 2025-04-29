// 头部组件的JavaScript
$(document).ready(function() {
    // 移动端菜单按钮点击事件
    $('.mobile-menu-toggle').on('click', function() {
        $('.nav-buttons').toggleClass('active');
    });
    
    // 点击页面其他区域关闭菜单
    $(document).on('click', function(event) {
        if (!$(event.target).closest('.mobile-menu-toggle, .nav-buttons').length) {
            $('.nav-buttons').removeClass('active');
        }
    });
    
    // 窗口调整大小时，如果屏幕变宽，移除菜单的active类
    $(window).on('resize', function() {
        if ($(window).width() > 768) {
            $('.nav-buttons').removeClass('active');
        }
    });
}); 