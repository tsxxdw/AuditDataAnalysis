// 设置页面JS文件
$(document).ready(function() {
    // 标记是否已经加载过内容，避免重复加载
    let initialLoadComplete = false;
    
    // 设置超时，确保在API请求失败时也能显示一些内容
    const apiTimeout = setTimeout(function() {
        if (!initialLoadComplete) {
            console.log('API请求超时，显示默认内容');
            $('#settings-nav-container').html('<div class="error-message">加载菜单失败，请刷新页面重试</div>');
            $('#settings-loading').hide();
            $('#settings-content-container').append(
                `<div id="default-error" class="settings-section">
                    <div class="error-message">无法加载设置内容，请检查网络连接后刷新页面</div>
                </div>`
            );
        }
    }, 10000); // 10秒超时
    
    // 从API获取设置菜单配置
    $.ajax({
        url: '/api/settings/menu_config',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            // 清除超时
            clearTimeout(apiTimeout);
            
            if (response.code === 200) {
                // 生成左侧导航菜单
                generateSettingsMenu(response.data);
                
                // 如果URL中有tab参数，使用它；否则使用HTML中传递的activeTab；如果都没有，就用第一个菜单项
                const urlParams = new URLSearchParams(window.location.search);
                const tabFromUrl = urlParams.get('tab');
                
                let tabToLoad = null;
                
                if (tabFromUrl && response.data.some(item => item.id === tabFromUrl)) {
                    tabToLoad = tabFromUrl;
                } else if (typeof activeTab !== 'undefined' && activeTab && response.data.some(item => item.id === activeTab)) {
                    tabToLoad = activeTab;
                } else {
                    // 页面加载时加载活动标签页对应的面板
                    const activeMenuItem = response.data.find(item => item.active);
                    if (activeMenuItem) {
                        tabToLoad = activeMenuItem.id;
                    } else if (response.data.length > 0) {
                        // 如果没有活动项，默认加载第一项
                        tabToLoad = response.data[0].id;
                    }
                }
                
                // 如果找到了要加载的标签页，立即加载它
                if (tabToLoad) {
                    // 先确保对应的菜单项被标记为活动状态
                    $('.nav-item').removeClass('active');
                    $(`.nav-item[data-target="${tabToLoad}"]`).addClass('active');
                    
                    // 立即加载内容
                    loadSettingsPanel(tabToLoad);
                    initialLoadComplete = true;
                    
                    // 打印日志，便于调试
                    console.log('初始加载标签页:', tabToLoad);
                }
            } else {
                console.error('获取菜单配置失败:', response.message);
                // 显示错误信息
                $('#settings-nav-container').html('<div class="error-message">加载菜单失败: ' + response.message + '</div>');
                $('#settings-loading').hide();
            }
        },
        error: function(xhr, status, error) {
            // 清除超时
            clearTimeout(apiTimeout);
            
            console.error('获取菜单配置异常:', error);
            // 显示错误信息
            $('#settings-nav-container').html('<div class="error-message">加载菜单失败: ' + error + '</div>');
            $('#settings-loading').hide();
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
        console.log('开始加载设置面板:', tabId); // 调试日志
        
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
            console.log('内容已存在，直接显示:', tabId); // 调试日志
            
            // 内容已存在，隐藏其他内容并显示当前内容
            $('#settings-content-container').children('.settings-section').hide();
            $existingContent.show();
            
            // 如果模块有初始化函数，调用它
            if (moduleInitMap[tabId]) {
                console.log('调用模块初始化函数:', tabId); // 调试日志
                moduleInitMap[tabId]();
            }
            
            // 更新URL，但不刷新页面
            if (pushState) {
                updateUrlAndSaveTab(tabId);
            }
            return;
        }
        
        console.log('内容不存在，从服务器加载:', tabId, route); // 调试日志
        
        // 显示加载中状态
        $('#settings-loading').show();
        $('#settings-content-container').children('.settings-section').hide();
        
        // 从服务器获取设置面板内容
        $.ajax({
            url: route,
            type: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(html) {
                console.log('内容加载成功:', tabId); // 调试日志
                
                // 隐藏加载中状态
                $('#settings-loading').hide();
                
                // 将返回的HTML内容添加到容器
                $('#settings-content-container').append(html);
                
                // 确保新加载的内容可见，其他内容隐藏
                $('#settings-content-container').children('.settings-section').not(`#${tabId}`).hide();
                $(`#${tabId}`).show();
                
                // 如果模块有初始化函数，调用它
                if (moduleInitMap[tabId]) {
                    console.log('调用模块初始化函数:', tabId); // 调试日志
                    moduleInitMap[tabId]();
                }
                
                // 更新URL，但不刷新页面
                if (pushState) {
                    updateUrlAndSaveTab(tabId);
                }
            },
            error: function(xhr, status, error) {
                console.error('加载设置面板失败:', error); // 调试日志
                
                // 隐藏加载中状态
                $('#settings-loading').hide();
                
                // 显示错误信息
                $('#settings-content-container').append(
                    `<div id="${tabId}" class="settings-section">
                        <div class="error-message">加载设置面板失败: ${error}</div>
                    </div>`
                );
                
                // 确保错误信息可见
                $('#settings-content-container').children('.settings-section').not(`#${tabId}`).hide();
                $(`#${tabId}`).show();
            }
        });
    }
    
    /**
     * 更新URL并保存当前标签页到会话
     * @param {string} tabId 标签页ID
     */
    function updateUrlAndSaveTab(tabId) {
        // 更新URL，但不刷新页面
        const url = new URL(window.location.href);
        url.searchParams.set('tab', tabId);
        window.history.pushState({tabId: tabId}, '', url.toString());
        
        // 保存当前活动标签页到会话
        $.ajax({
            url: '/api/settings/set_active_tab',
            type: 'POST',
            data: JSON.stringify({tab_id: tabId}),
            contentType: 'application/json',
            dataType: 'json',
            error: function(xhr, status, error) {
                console.error('保存活动标签页失败:', error);
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
                .attr('data-route', item.route)
                .append(`<span class="nav-icon">${item.icon}</span>`)
                .append(`<span class="nav-text">${item.text}</span>`);
            
            // 如果是活动项，添加active类
            if (item.active) {
                $navItem.addClass('active');
            }
            
            // 添加点击事件
            $navItem.on('click', function() {
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