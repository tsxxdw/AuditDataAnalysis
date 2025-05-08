// 模型服务设置模块
var ModelService = {
    // 初始化
    init: function() {
        this.bindEvents();
        this.loadModelServiceSettings();
    },
    
    // 绑定事件
    bindEvents: function() {
        // 服务提供商切换
        $('.provider-option').click(function() {
            // 移除其他选项的激活状态
            $('.provider-option').removeClass('active');
            // 激活当前选项
            $(this).addClass('active');
            
            // 获取所选服务提供商
            var provider = $(this).data('provider');
            ModelService.switchProvider(provider);
        });
        
        // 显示/隐藏API密钥
        $('.toggle-password').click(function() {
            var apiKeyInput = $('#api-key');
            var type = apiKeyInput.attr('type');
            
            // 切换密码显示类型
            if (type === 'password') {
                apiKeyInput.attr('type', 'text');
                $(this).find('.eye-icon').addClass('active');
            } else {
                apiKeyInput.attr('type', 'password');
                $(this).find('.eye-icon').removeClass('active');
            }
        });
        
        // 检测API密钥
        $('.verify-btn').click(function() {
            ModelService.verifyApiKey();
        });
        
        // 刷新模型列表
        $('.refresh-btn').click(function() {
            ModelService.refreshModels();
        });
        
        // 切换模型类别展开/折叠
        $(document).on('click', '.category-header', function() {
            var $modelItems = $(this).next('.model-items');
            var $toggleIcon = $(this).find('.toggle-icon');
            
            $modelItems.slideToggle(200);
            
            if ($toggleIcon.text() === '▼') {
                $toggleIcon.text('▶');
            } else {
                $toggleIcon.text('▼');
            }
        });
        
        // 模型设置按钮
        $(document).on('click', '.model-settings-btn', function(e) {
            e.stopPropagation();
            var modelName = $(this).closest('.model-item').find('.model-name').text();
            ModelService.openModelSettings(modelName);
        });
        
        // 模型隐藏按钮
        $(document).on('click', '.model-hide-btn', function(e) {
            e.stopPropagation();
            var $modelItem = $(this).closest('.model-item');
            var modelName = $modelItem.find('.model-name').text();
            
            // 确认是否隐藏
            if (confirm('确定要隐藏模型 ' + modelName + ' 吗？')) {
                // 隐藏该模型（仅前端演示）
                $modelItem.fadeOut(300, function() {
                    $(this).remove();
                });
            }
        });
        
        // 管理按钮
        $('.manage-btn').click(function() {
            ModelService.openManageDialog();
        });
    },
    
    // 加载模型服务设置
    loadModelServiceSettings: function() {
        // 模拟加载数据（实际项目中应从后端API获取）
        setTimeout(function() {
            // 默认选中第一个提供商
            $('.provider-option').first().click();
            
            // 设置默认API地址
            $('#api-url').val('http://localhost:11434');
        }, 300);
    },
    
    // 切换服务提供商
    switchProvider: function(provider) {
        console.log('切换到服务提供商: ' + provider);
        
        // 根据不同提供商调整UI
        switch(provider) {
            case 'silicon-flow':
                $('#api-url').attr('placeholder', '例如: https://api.silicon-flow.com');
                $('.api-url-hint .hint-text').text('https://api.silicon-flow.com/v1/chat/completions');
                break;
            case 'deep-search':
                $('#api-url').attr('placeholder', '例如: https://api.deep-search.ai');
                $('.api-url-hint .hint-text').text('https://api.deep-search.ai/v1/chat/completions');
                break;
            case 'ollama':
                $('#api-url').attr('placeholder', '例如: http://localhost:11434');
                $('.api-url-hint .hint-text').text('http://localhost:11434/v1/chat/completions');
                break;
        }
        
        // 模拟加载该提供商的模型列表
        this.loadModelsForProvider(provider);
    },
    
    // 加载提供商的模型列表
    loadModelsForProvider: function(provider) {
        // 显示加载状态
        $('.model-list').html('<div class="loading-indicator">加载中...</div>');
        
        // 模拟API请求延迟
        setTimeout(function() {
            var modelListHtml = '';
            
            // 根据不同提供商显示不同模型
            if (provider === 'ollama') {
                modelListHtml = `
                    <div class="model-category">
                        <div class="category-header">
                            <span class="toggle-icon">▼</span>
                            <span class="category-name">qwen3</span>
                        </div>
                        <div class="model-items">
                            <div class="model-item">
                                <span class="model-icon">Q</span>
                                <span class="model-name">qwen3:30b-a3b</span>
                                <div class="model-actions">
                                    <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                    <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                </div>
                            </div>
                            <div class="model-item">
                                <span class="model-icon">Q</span>
                                <span class="model-name">qwen3:1.7b</span>
                                <div class="model-actions">
                                    <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                    <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else if (provider === 'silicon-flow') {
                modelListHtml = `
                    <div class="model-category">
                        <div class="category-header">
                            <span class="toggle-icon">▼</span>
                            <span class="category-name">通用模型</span>
                        </div>
                        <div class="model-items">
                            <div class="model-item">
                                <span class="model-icon">S</span>
                                <span class="model-name">silicon-16k</span>
                                <div class="model-actions">
                                    <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                    <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                </div>
                            </div>
                            <div class="model-item">
                                <span class="model-icon">S</span>
                                <span class="model-name">silicon-32k</span>
                                <div class="model-actions">
                                    <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                    <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else if (provider === 'deep-search') {
                modelListHtml = `
                    <div class="model-category">
                        <div class="category-header">
                            <span class="toggle-icon">▼</span>
                            <span class="category-name">搜索模型</span>
                        </div>
                        <div class="model-items">
                            <div class="model-item">
                                <span class="model-icon">D</span>
                                <span class="model-name">deep-search-7b</span>
                                <div class="model-actions">
                                    <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                    <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                </div>
                            </div>
                            <div class="model-item">
                                <span class="model-icon">D</span>
                                <span class="model-name">deep-search-13b</span>
                                <div class="model-actions">
                                    <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                    <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            // 更新模型列表
            $('.model-list').html(modelListHtml);
        }, 800);
    },
    
    // 验证API密钥
    verifyApiKey: function() {
        var apiKey = $('#api-key').val();
        var apiUrl = $('#api-url').val();
        
        if (!apiKey) {
            alert('请输入API密钥');
            return;
        }
        
        if (!apiUrl) {
            alert('请输入API地址');
            return;
        }
        
        // 显示检测中状态
        var $verifyBtn = $('.verify-btn');
        var originalText = $verifyBtn.text();
        $verifyBtn.text('检测中...').prop('disabled', true);
        
        // 模拟API请求
        setTimeout(function() {
            // 恢复按钮状态
            $verifyBtn.text(originalText).prop('disabled', false);
            
            // 模拟成功响应
            alert('API密钥验证成功');
        }, 1200);
    },
    
    // 刷新模型列表
    refreshModels: function() {
        var provider = $('.provider-option.active').data('provider');
        this.loadModelsForProvider(provider);
    },
    
    // 打开模型设置对话框
    openModelSettings: function(modelName) {
        alert('打开模型设置: ' + modelName + '\n(实际项目中应显示设置对话框)');
    },
    
    // 打开管理对话框
    openManageDialog: function() {
        alert('打开模型管理页面\n(实际项目中应显示管理对话框)');
    },
    
    // 打开添加模型对话框
    openAddModelDialog: function() {
        alert('打开添加模型页面\n(实际项目中应显示添加模型对话框)');
    }
}; 