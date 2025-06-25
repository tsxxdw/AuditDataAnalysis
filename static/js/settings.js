// 设置页面JS文件
$(document).ready(function() {
    // 设置菜单配置
    const settingsMenuConfig = [
        {
            id: 'personal-settings',
            icon: '👤',
            text: '个人设置',
            active: activeTab === 'personal-settings',
            route: '/settings/setting_personal'
        },
        {
            id: 'db-settings',
            icon: '🔌',
            text: '数据库设置',
            active: activeTab === 'db-settings',
            route: '/settings/setting_relational_database'
        },
        {
            id: 'vector-db-settings',
            icon: '🔍',
            text: '向量数据库设置',
            active: activeTab === 'vector-db-settings',
            route: '/settings/setting_vector_database'
        },
        {
            id: 'log-settings',
            icon: '📝',
            text: '日志设置',
            active: activeTab === 'log-settings',
            route: '/settings/setting_log'
        },
        {
            id: 'model-service',
            icon: '🤖',
            text: '模型服务',
            active: activeTab === 'model-service',
            route: '/settings/setting_model_server'
        }
    ];
    
    // 生成左侧导航菜单
    generateSettingsMenu(settingsMenuConfig);
    
    // 模块初始化映射
    const moduleInitMap = {
        'personal-settings': function() { PersonalSettings.init(); },
        'db-settings': function() { DatabaseSettings.init(); },
        'vector-db-settings': function() { VectorDatabaseSettings.init(); },
        'log-settings': function() { LogSettings.init(); },
        'model-service': function() { ModelService.init(); }
    };
    
    // 页面加载时加载活动标签页对应的面板
    loadSettingsPanel(activeTab);
    
    // 监听浏览器前进/后退按钮
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.tabId) {
            loadSettingsPanel(event.state.tabId, false);
        }
    });
    
    /**
     * 加载设置面板内容
     * @param {string} tabId 标签页ID
     * @param {boolean} pushState 是否推送历史记录状态，默认为true
     */
    function loadSettingsPanel(tabId, pushState = true) {
        // 找到对应的菜单配置
        const menuItem = settingsMenuConfig.find(item => item.id === tabId);
        if (!menuItem || !menuItem.route) {
            console.error('找不到对应的菜单项或路由:', tabId);
            return;
        }
        
        // 更新活动菜单项
        $('.nav-item').removeClass('active');
        $(`.nav-item[data-target="${tabId}"]`).addClass('active');
        
        // 显示加载中状态
        $('#settings-loading').show();
        $('#settings-content-container').children().not('#settings-loading').hide();
        
        // 发送AJAX请求获取内容
        $.ajax({
            url: menuItem.route,
            type: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                // 隐藏加载中状态
                $('#settings-loading').hide();
                
                // 检查内容是否已存在
                const $existingContent = $(`#${tabId}`);
                if ($existingContent.length > 0) {
                    // 内容已存在，显示它
                    $existingContent.show();
                } else {
                    // 内容不存在，添加到容器
                    $('#settings-content-container').append(response);
                }
                
                // 初始化对应的模块
                if (moduleInitMap[tabId]) {
                    moduleInitMap[tabId]();
                }
                
                // 更新URL，但不刷新页面
                if (pushState) {
                    const url = new URL(window.location);
                    url.searchParams.set('tab', tabId);
                    history.pushState({ tabId: tabId }, '', url);
                }
            },
            error: function(xhr, status, error) {
                // 处理错误
                $('#settings-loading').hide();
                $('#settings-content-container').append(
                    `<div class="error-message">加载设置内容失败: ${error}</div>`
                );
                console.error('加载设置内容失败:', error);
            }
        });
    }
    
    /**
     * 生成设置菜单
     * @param {Array} menuItems 菜单项配置数组
     */
    function generateSettingsMenu(menuItems) {
        // 创建导航列表元素
        const $navList = $('<ul class="nav-list"></ul>');
        
        // 遍历菜单项配置，生成菜单项
        menuItems.forEach(function(item) {
            // 创建菜单项元素
            const $navItem = $('<li class="nav-item"></li>')
                .attr('data-target', item.id)
                .append(`<span class="nav-icon">${item.icon}</span>`)
                .append(`<span class="nav-text">${item.text}</span>`);
            
            // 如果是活动项，添加active类
            if (item.active) {
                $navItem.addClass('active');
            }
            
            // 添加点击事件
            $navItem.on('click', function() {
                // 获取目标内容区域的ID
                var targetId = $(this).data('target');
                
                // 加载对应的设置面板
                loadSettingsPanel(targetId);
            });
            
            // 将菜单项添加到导航列表
            $navList.append($navItem);
        });
        
        // 将生成的导航列表添加到容器
        $('#settings-nav-container').append($navList);
    }
}); 