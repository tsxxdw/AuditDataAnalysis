// 模型服务设置模块
var ModelService = {
    // 当前选中的服务提供商
    currentProvider: null,
    
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
            var modelId = $(this).closest('.model-item').data('model-id');
            var modelName = $(this).closest('.model-item').find('.model-name').text();
            ModelService.openModelSettings(modelId, modelName);
        });
        
        // 模型隐藏按钮
        $(document).on('click', '.model-hide-btn', function(e) {
            e.stopPropagation();
            var $modelItem = $(this).closest('.model-item');
            var modelId = $modelItem.data('model-id');
            var modelName = $modelItem.find('.model-name').text();
            
            // 确认是否隐藏
            if (confirm('确定要隐藏模型 ' + modelName + ' 吗？')) {
                ModelService.toggleModelVisibility(modelId, false);
            }
        });
        
        // 管理按钮
        $('.manage-btn').click(function() {
            ModelService.openManageDialog();
        });
    },
    
    // 加载模型服务设置
    loadModelServiceSettings: function() {
        // 显示加载中状态
        $('.provider-options').html('<div class="loading">加载中...</div>');
        
        // 获取所有服务提供商
        $.ajax({
            url: '/api/settings/model/providers',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var providers = response.providers;
                    var providersHtml = '';
                    
                    // 生成服务提供商选项
                    for (var i = 0; i < providers.length; i++) {
                        var provider = providers[i];
                        providersHtml += `
                            <div class="provider-option" data-provider="${provider.id}">
                                <img src="/static/images/providers/${provider.id}.png" 
                                     alt="${provider.name}" class="provider-icon">
                                <span class="provider-name">${provider.name}</span>
                            </div>
                        `;
                    }
                    
                    // 更新UI
                    $('.provider-options').html(providersHtml);
                    
                    // 默认选中第一个提供商
                    if (providers.length > 0) {
                        $('.provider-option').first().click();
                    }
                    
                    // 重新绑定事件
                    $('.provider-option').click(function() {
                        $('.provider-option').removeClass('active');
                        $(this).addClass('active');
                        
                        var provider = $(this).data('provider');
                        ModelService.switchProvider(provider);
                    });
                } else {
                    // 显示错误
                    $('.provider-options').html('<div class="error">加载服务提供商失败</div>');
                }
            },
            error: function(xhr, status, error) {
                // 显示错误
                $('.provider-options').html('<div class="error">加载服务提供商失败: ' + error + '</div>');
            }
        });
    },
    
    // 切换服务提供商
    switchProvider: function(providerId) {
        console.log('切换到服务提供商: ' + providerId);
        this.currentProvider = providerId;
        
        // 获取提供商详细信息
        $.ajax({
            url: '/api/settings/model/providers/' + providerId,
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var provider = response.provider;
                    
                    // 更新API地址和提示
                    $('#api-url').val(provider.apiUrl);
                    $('.api-url-hint .hint-text').text(provider.apiUrl + '/' + provider.apiVersion + '/chat/completions');
                    
                    // 清空API密钥输入框，显示是否已设置的提示
                    $('#api-key').val('');
                    if (provider.hasApiKey) {
                        $('#api-key').attr('placeholder', '******** (已设置)');
                    } else {
                        $('#api-key').attr('placeholder', '请输入API密钥');
                    }
                    
                    // 加载模型列表
                    ModelService.loadModelsForProvider(providerId);
                } else {
                    alert('加载服务提供商信息失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('加载服务提供商信息失败: ' + error);
            }
        });
    },
    
    // 加载提供商的模型列表
    loadModelsForProvider: function(providerId) {
        // 显示加载状态
        $('.model-list').html('<div class="loading-indicator">加载中...</div>');
        
        // 获取分类模型列表
        $.ajax({
            url: '/api/settings/model/providers/' + providerId + '/models/categories',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var categories = response.categories;
                    var modelListHtml = '';
                    
                    // 如果没有模型
                    if (Object.keys(categories).length === 0) {
                        modelListHtml = '<div class="no-models">暂无可用模型</div>';
                    } else {
                        // 生成模型列表HTML
                        for (var category in categories) {
                            var models = categories[category];
                            
                            modelListHtml += `
                                <div class="model-category">
                                    <div class="category-header">
                                        <span class="toggle-icon">▼</span>
                                        <span class="category-name">${category}</span>
                                    </div>
                                    <div class="model-items">
                            `;
                            
                            // 添加模型项
                            for (var i = 0; i < models.length; i++) {
                                var model = models[i];
                                var iconText = model.name.charAt(0).toUpperCase();
                                
                                modelListHtml += `
                                    <div class="model-item" data-model-id="${model.id}">
                                        <span class="model-icon">${iconText}</span>
                                        <span class="model-name">${model.name}</span>
                                        <div class="model-actions">
                                            <button class="model-settings-btn" title="设置"><i class="settings-icon"></i></button>
                                            <button class="model-hide-btn" title="隐藏"><i class="hide-icon"></i></button>
                                        </div>
                                    </div>
                                `;
                            }
                            
                            modelListHtml += `
                                    </div>
                                </div>
                            `;
                        }
                    }
                    
                    // 更新模型列表
                    $('.model-list').html(modelListHtml);
                } else {
                    $('.model-list').html('<div class="error">加载模型列表失败: ' + response.message + '</div>');
                }
            },
            error: function(xhr, status, error) {
                $('.model-list').html('<div class="error">加载模型列表失败: ' + error + '</div>');
            }
        });
    },
    
    // 验证API密钥
    verifyApiKey: function() {
        var apiKey = $('#api-key').val();
        var apiUrl = $('#api-url').val();
        
        if (!this.currentProvider) {
            alert('请先选择服务提供商');
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
        
        // 发送测试请求
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/test',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                apiKey: apiKey,
                apiUrl: apiUrl
            }),
            success: function(response) {
                // 恢复按钮状态
                $verifyBtn.text(originalText).prop('disabled', false);
                
                if (response.success) {
                    alert('连接成功: ' + response.message);
                    
                    // 保存设置
                    ModelService.saveProviderSettings(apiKey, apiUrl);
                } else {
                    alert('连接失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                // 恢复按钮状态
                $verifyBtn.text(originalText).prop('disabled', false);
                
                alert('检测API密钥失败: ' + error);
            }
        });
    },
    
    // 保存提供商设置
    saveProviderSettings: function(apiKey, apiUrl) {
        // 构建请求数据
        var data = {
            apiUrl: apiUrl
        };
        
        // 只有在用户输入了API密钥时才发送
        if (apiKey) {
            data.apiKey = apiKey;
        }
        
        // 发送更新请求
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/update',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.success) {
                    console.log('服务提供商设置已保存');
                } else {
                    alert('保存设置失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('保存设置失败: ' + error);
            }
        });
    },
    
    // 刷新模型列表
    refreshModels: function() {
        if (this.currentProvider) {
            this.loadModelsForProvider(this.currentProvider);
        }
    },
    
    // 切换模型可见性
    toggleModelVisibility: function(modelId, visible) {
        if (!this.currentProvider) {
            return;
        }
        
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/models/' + modelId + '/visibility',
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({
                visible: visible
            }),
            success: function(response) {
                if (response.success) {
                    // 刷新模型列表
                    ModelService.refreshModels();
                } else {
                    alert('更新模型可见性失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('更新模型可见性失败: ' + error);
            }
        });
    },
    
    // 打开模型设置对话框
    openModelSettings: function(modelId, modelName) {
        alert('打开模型设置: ' + modelName + '\n(实际项目中应显示设置对话框)');
    },
    
    // 打开管理对话框，实现添加/删除模型功能
    openManageDialog: function() {
        if (!this.currentProvider) {
            alert('请先选择服务提供商');
            return;
        }
        
        // 修改为显示模态窗口，加载模型列表
        var $modal = $('#modelManageModal');
        var $modalTitle = $modal.find('.modal-title');
        
        // 设置标题
        $modalTitle.text(this.currentProvider + ' 模型管理');
        
        // 加载模型列表
        this.loadAllModels();
        
        // 显示/隐藏Ollama特定部分
        if (this.currentProvider === 'ollama') {
            $('#ollamaLocalModels').show();
            this.loadOllamaLocalModels();
        } else {
            $('#ollamaLocalModels').hide();
        }
        
        // 显示模态窗口
        $modal.css('display', 'block');
        
        // 绑定关闭按钮事件
        $('.close-modal, .close-btn').off('click').on('click', function() {
            $modal.css('display', 'none');
        });
        
        // 绑定添加模型按钮事件
        $('#addModelBtn').off('click').on('click', function() {
            ModelService.addNewModel();
        });
        
        // 绑定刷新Ollama模型按钮事件
        $('#refreshOllamaBtn').off('click').on('click', function() {
            ModelService.loadOllamaLocalModels();
        });
    },
    
    // 加载所有模型列表（包括不可见的）
    loadAllModels: function() {
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/models',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var models = response.models;
                    var tableHtml = '';
                    
                    // 生成模型表格
                    for (var i = 0; i < models.length; i++) {
                        var model = models[i];
                        var visibility = model.visible ? '可见' : '隐藏';
                        
                        tableHtml += `
                            <tr data-model-id="${model.id}">
                                <td>${model.name}</td>
                                <td>${model.category || '未分类'}</td>
                                <td>${visibility}</td>
                                <td>
                                    ${model.visible ? 
                                        '<button class="action-btn hide-model-btn" title="隐藏">隐藏</button>' : 
                                        '<button class="action-btn show-model-btn" title="显示">显示</button>'}
                                    <button class="action-btn delete-btn" title="删除">删除</button>
                                </td>
                            </tr>
                        `;
                    }
                    
                    // 如果没有模型，显示提示信息
                    if (models.length === 0) {
                        tableHtml = '<tr><td colspan="4" class="text-center">暂无模型</td></tr>';
                    }
                    
                    // 更新表格
                    $('#modelTableBody').html(tableHtml);
                    
                    // 绑定操作按钮事件
                    $('.hide-model-btn').click(function() {
                        var modelId = $(this).closest('tr').data('model-id');
                        ModelService.toggleModelVisibility(modelId, false);
                    });
                    
                    $('.show-model-btn').click(function() {
                        var modelId = $(this).closest('tr').data('model-id');
                        ModelService.toggleModelVisibility(modelId, true);
                    });
                    
                    $('.delete-btn').click(function() {
                        var $tr = $(this).closest('tr');
                        var modelId = $tr.data('model-id');
                        var modelName = $tr.find('td').first().text();
                        ModelService.deleteModel(modelId, modelName);
                    });
                } else {
                    $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载失败: ' + response.message + '</td></tr>');
                }
            },
            error: function(xhr, status, error) {
                $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载失败: ' + error + '</td></tr>');
            }
        });
    },
    
    // 添加新模型
    addNewModel: function() {
        var modelId = $('#newModelId').val().trim();
        var modelName = $('#newModelName').val().trim();
        var category = $('#newModelCategory').val().trim();
        var description = $('#newModelDesc').val().trim();
        
        // 验证必填字段
        if (!modelId) {
            alert('请输入模型ID');
            return;
        }
        
        if (!modelName) {
            alert('请输入模型名称');
            return;
        }
        
        // 默认分类
        if (!category) {
            category = '其他';
        }
        
        // 构建请求数据
        var modelData = {
            id: modelId,
            name: modelName,
            category: category,
            description: description,
            visible: true
        };
        
        // 发送添加请求
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/models/add',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(modelData),
            success: function(response) {
                if (response.success) {
                    // 清空输入框
                    $('#newModelId').val('');
                    $('#newModelName').val('');
                    $('#newModelCategory').val('');
                    $('#newModelDesc').val('');
                    
                    // 刷新模型列表
                    ModelService.loadAllModels();
                    alert('模型添加成功');
                } else {
                    alert('添加模型失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('添加模型失败: ' + error);
            }
        });
    },
    
    // 删除模型
    deleteModel: function(modelId, modelName) {
        if (!confirm('确定要删除模型 ' + modelName + ' 吗？此操作不可恢复。')) {
            return;
        }
        
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/models/' + modelId + '/delete',
            type: 'DELETE',
            success: function(response) {
                if (response.success) {
                    // 刷新模型列表
                    ModelService.loadAllModels();
                    alert('模型已删除');
                } else {
                    alert('删除模型失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('删除模型失败: ' + error);
            }
        });
    },
    
    // 获取Ollama本地模型列表
    loadOllamaLocalModels: function() {
        $('#ollamaModelsList').html('<div class="loading-indicator">加载中...</div>');
        
        $.ajax({
            url: '/api/common/ollama/models',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var models = response.models;
                    var modelsHtml = '';
                    
                    // 获取当前已添加的模型IDs
                    $.ajax({
                        url: '/api/settings/model/providers/ollama/models',
                        type: 'GET',
                        dataType: 'json',
                        async: false,
                        success: function(modelResponse) {
                            if (modelResponse.success) {
                                var existingModels = modelResponse.models;
                                var existingModelIds = existingModels.map(function(m) { return m.id; });
                                
                                // 生成本地模型列表
                                for (var i = 0; i < models.length; i++) {
                                    var model = models[i];
                                    var modelName = model.name;
                                    var isAdded = existingModelIds.includes(modelName);
                                    
                                    modelsHtml += `
                                        <div class="ollama-model-item" data-model-name="${modelName}">
                                            <span class="ollama-model-name">${modelName}</span>
                                            <div class="ollama-model-actions">
                                                ${isAdded ? 
                                                  '<button class="action-btn" disabled>已添加</button>' : 
                                                  '<button class="action-btn add-local-model-btn">添加</button>'}
                                            </div>
                                        </div>
                                    `;
                                }
                            }
                        }
                    });
                    
                    // 如果没有模型，显示提示
                    if (models.length === 0) {
                        modelsHtml = '<div class="empty-text">未找到本地Ollama模型</div>';
                    }
                    
                    // 更新列表
                    $('#ollamaModelsList').html(modelsHtml);
                    
                    // 绑定添加按钮事件
                    $('.add-local-model-btn').click(function() {
                        var modelName = $(this).closest('.ollama-model-item').data('model-name');
                        
                        // 自动填充表单
                        $('#newModelId').val(modelName);
                        $('#newModelName').val(modelName);
                        $('#newModelCategory').val('Ollama本地');
                        $('#newModelDesc').val('Ollama本地模型 ' + modelName);
                        
                        // 滚动到添加表单区域
                        $('.add-model-form').get(0).scrollIntoView({ behavior: 'smooth' });
                    });
                } else {
                    $('#ollamaModelsList').html('<div class="error">加载Ollama模型失败: ' + response.message + '</div>');
                }
            },
            error: function(xhr, status, error) {
                $('#ollamaModelsList').html('<div class="error">加载Ollama模型失败: ' + error + '</div>');
            }
        });
    }
}; 