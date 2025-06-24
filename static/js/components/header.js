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
    
    // 注销按钮点击事件
    $('#logout-btn').on('click', function() {
        // 发送退出登录请求
        $.ajax({
            url: '/api/user/logout',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({}),
            success: function(response) {
                if (response.code === 200) {
                    // 退出成功，跳转到登录页
                    window.location.href = '/login';
                } else {
                    alert(response.message || '退出失败，请稍后重试');
                }
            },
            error: function() {
                alert('服务器错误，请稍后重试');
            }
        });
    });
}); 