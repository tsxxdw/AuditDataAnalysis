// 设置页面JS文件
$(document).ready(function() {
    // 标记是否已经加载过内容，避免重复加载
    let initialLoadComplete = false;
    
    // 从API获取设置菜单配置
    $.ajax({
        url: '/api/settings/menu_config',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.code === 200) {
                // 生成左侧导航菜单
                generateSettingsMenu(response.data);
                
                // 页面加载时加载活动标签页对应的面板
                const activeMenuItem = response.data.find(item => item.active);
                if (activeMenuItem) {
                    loadSettingsPanel(activeMenuItem.id);
                    initialLoadComplete = true;
                } else if (response.data.length > 0) {
                    // 如果没有活动项，默认加载第一项
                    loadSettingsPanel(response.data[0].id);
                    initialLoadComplete = true;
                }
            } else {
                console.error('获取菜单配置失败:', response.message);
                // 显示错误信息
                $('#settings-nav-container').html('<div class="error-message">加载菜单失败</div>');
            }
        },
        error: function(xhr, status, error) {
            console.error('获取菜单配置异常:', error);
            // 显示错误信息
            $('#settings-nav-container').html('<div class="error-message">加载菜单失败</div>');
        }
    });
    
    // 模块初始化映射
    const moduleInitMap = {
        'personal-settings': function() { PersonalSettings.init(); },
        'db-settings': function() { DatabaseSettings.init(); },
        'vector-db-settings': function() { VectorDatabaseSettings.init(); },
        'log-settings': function() { LogSettings.init(); },
        'model-service': function() { ModelService.init(); }
    };
    
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
        // 从导航项中获取路由信息
        const $navItem = $(`.nav-item[data-target="${tabId}"]`);
        if ($navItem.length === 0) {
            console.error('找不到对应的菜单项:', tabId);
            return;
        }
        
        const route = $navItem.data('route');
        if (!route) {
            console.error('菜单项缺少路由信息:', tabId);
            return;
        }
        
        // 更新活动菜单项
        $('.nav-item').removeClass('active');
        $navItem.addClass('active');
        
        // 检查内容是否已存在
        const $existingContent = $(`#${tabId}`);
        if ($existingContent.length > 0) {
            // 内容已存在，隐藏其他内容并显示当前内容
            $('#settings-content-container').children().not('#settings-loading').hide();
            $existingContent.show();
            
            // 更新URL，但不刷新页面
            if (pushState) {
                updateUrlAndSaveTab(tabId);
            }
            return;
        }
        
        // 显示加载中状态
        $('#settings-loading').show();
        $('#settings-content-container').children().not('#settings-loading').hide();
        
        // 发送AJAX请求获取内容
        $.ajax({
            url: route,
            type: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                // 隐藏加载中状态
                $('#settings-loading').hide();
                
                // 添加内容到容器
                $('#settings-content-container').append(response);
                
                // 初始化对应的模块
                if (moduleInitMap[tabId]) {
                    moduleInitMap[tabId]();
                }
                
                // 更新URL，但不刷新页面
                if (pushState) {
                    updateUrlAndSaveTab(tabId);
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
     * 更新URL并保存当前标签页到服务器
     * @param {string} tabId 标签页ID
     */
    function updateUrlAndSaveTab(tabId) {
        const url = new URL(window.location);
        url.searchParams.set('tab', tabId);
        history.pushState({ tabId: tabId }, '', url);
        
        // 向服务器保存当前活动标签页
        $.ajax({
            url: '/api/settings/set_active_tab',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ tab_id: tabId }),
            dataType: 'json'
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
                .attr('data-route', item.route)
                .append(`<span class="nav-icon">${item.icon}</span>`)
                .append(`<span class="nav-text">${item.text}</span>`);
            
            // 如果是活动项，添加active类
            if (item.active) {
                $navItem.addClass('active');
            }
            
            // 添加点击事件，使用事件委托以避免多次绑定
            $navItem.on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // 获取目标内容区域的ID
                const targetId = $(this).data('target');
                
                // 加载对应的设置面板
                loadSettingsPanel(targetId);
            });
            
            // 将菜单项添加到导航列表
            $navList.append($navItem);
        });
        
        // 清空并将生成的导航列表添加到容器
        $('#settings-nav-container').empty().append($navList);
    }
}); 