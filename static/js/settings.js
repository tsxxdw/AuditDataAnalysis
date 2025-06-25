// 设置页面JS文件
$(document).ready(function() {
    // 初始化数据库设置模块
    DatabaseSettings.init();
    
    // 初始化向量数据库设置模块
    VectorDatabaseSettings.init();
    
    // 初始化日志设置模块
    LogSettings.init();
    
    // 初始化模型服务模块
    ModelService.init();
    
    // 初始化个人设置模块
    PersonalSettings.init();

    // 页面加载时默认显示个人设置面板
    showSettingsPanel('personal-settings');

    // 导航菜单切换
    $('.nav-item').click(function() {
        // 移除所有导航项的active类
        $('.nav-item').removeClass('active');
        // 给当前点击的导航项添加active类
        $(this).addClass('active');
        
        // 获取目标内容区域的ID
        var targetId = $(this).data('target');
        
        // 显示对应的设置面板
        showSettingsPanel(targetId);
    });

    // 显示指定的设置面板
    function showSettingsPanel(panelId) {
        // 隐藏所有设置面板
        $('.settings-section').removeClass('active');
        // 显示目标设置面板
        $('#' + panelId).addClass('active');
        
        // 如果是日志设置，加载日志设置
        if (panelId === 'log-settings') {
            LogSettings.loadSettings();
        }
    }
}); 