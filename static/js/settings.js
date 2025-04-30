// 设置页面JS文件
$(document).ready(function() {
    // 初始化数据库设置模块
    DatabaseSettings.init();

    // 导航菜单切换
    $('.nav-item').click(function() {
        // 移除所有导航项的active类
        $('.nav-item').removeClass('active');
        // 给当前点击的导航项添加active类
        $(this).addClass('active');
        
        // 获取目标内容区域的ID
        var targetId = $(this).data('target');
        
        // 隐藏所有内容区域
        $('.settings-section').removeClass('active');
        // 显示目标内容区域
        $('#' + targetId).addClass('active');
    });

    // 浏览按钮 - 选择日志路径
    $('.browse-btn').click(function() {
        alert('选择目录\n实际应用中会打开文件夹选择对话框');
    });

    // 保存日志设置
    $('.save-logs-btn').click(function() {
        var logPath = $('#log-path').val();
        
        // 这里仅做演示，实际操作需要后端支持
        alert('日志设置已保存!\n路径: ' + logPath);
    });
}); 