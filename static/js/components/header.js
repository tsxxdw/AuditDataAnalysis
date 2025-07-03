/**
 * 页面头部组件
 * 处理导航菜单交互，包括移动端菜单的切换和页面大小调整响应
 * 实现鼠标移动到顶部时显示header的功能
 * 实现页面滚动到顶部时自动显示header的功能
 * 实现页面加载时自动滚动一点距离以隐藏header的功能
 */
// 头部组件的JavaScript
$(document).ready(function() {
    // 创建顶部触发区域元素
    $('body').prepend('<div class="header-trigger-area"></div>');
    
    // 获取header高度
    var headerHeight = $('.site-header').outerHeight();
    
    // 页面加载完成后，自动滚动一点距离（等于header高度）
    // 使用setTimeout确保DOM完全加载并渲染
    setTimeout(function() {
        // 只有在页面顶部时才执行自动滚动
        if ($(window).scrollTop() === 0) {
            // 平滑滚动到header高度的位置
            window.scrollTo({
                top: headerHeight,
                behavior: 'smooth'
            });
        }
    }, 300);
    
    // 监听鼠标移入触发区域事件
    $('.header-trigger-area, .site-header').on('mouseenter', function() {
        $('.site-header').addClass('visible');
    });
    
    // 监听鼠标移出header事件
    $('.site-header').on('mouseleave', function() {
        // 只有当鼠标不在触发区域时且页面不在顶部时才隐藏header
        if (!$('.header-trigger-area:hover').length && $(window).scrollTop() > 0) {
            $('.site-header').removeClass('visible');
        }
    });
    
    // 页面滚动事件
    $(window).on('scroll', function() {
        // 如果页面滚动到顶部，显示header
        if ($(window).scrollTop() === 0) {
            $('.site-header').addClass('visible');
        } else {
            // 只有当鼠标不在header和触发区域时才隐藏
            if (!$('.site-header:hover').length && !$('.header-trigger-area:hover').length) {
                $('.site-header').removeClass('visible');
            }
        }
    });
    
    // 页面加载时检查滚动位置
    if ($(window).scrollTop() === 0) {
        $('.site-header').addClass('visible');
    }
    
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
            url: '/api/login/logout',
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