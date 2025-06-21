// 模型服务设置模块
var ModelService = {
    // 当前选中的服务提供商
    currentProvider: null,
    
    // 初始化
    init: function() {
        this.bindEvents();
        this.loadModelServiceSettings();
        
        // 直接加载可见模型到默认模型下拉框
        this.updateDefaultModelDropdown();
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
        
        // 同步Ollama本地模型
        $('#syncOllamaBtn').click(function() {
            ModelService.syncOllamaModels();
        });
        
        // 为模型表格中的按钮绑定事件委托
        $('#modelTableBody').on('click', '.hide-model-btn', function() {
            var modelId = $(this).closest('tr').data('model-id');
            ModelService.toggleModelVisibility(modelId, false);
        });
        
        $('#modelTableBody').on('click', '.show-model-btn', function() {
            var modelId = $(this).closest('tr').data('model-id');
            ModelService.toggleModelVisibility(modelId, true);
        });
        
        $('#modelTableBody').on('click', '.enable-model-btn', function() {
            var $tr = $(this).closest('tr');
            var modelId = $tr.data('model-id');
            ModelService.enableModel(modelId);
        });
        
        // 默认模型下拉框变更事件
        $('#default-model').change(function() {
            var selectedModel = $(this).val();
            if (selectedModel) {
                ModelService.setDefaultModel(selectedModel);
            }
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
                    // 对提供商进行排序，确保Ollama始终在第一位
                    providers.sort(function(a, b) {
                        if (a.id === 'ollama') return -1;
                        if (b.id === 'ollama') return 1;
                        return 0;
                    });
                    
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
                    
                    // 加载所有模型（包括可见和不可见的）
                    ModelService.loadAllModels();
                    
                    // Ollama特殊处理
                    if (providerId === 'ollama') {
                        // 设置提示文本
                        $('#model-list-hint').text('从本地已安装的Ollama模型中选择需要使用的模型：');
                        // 显示同步按钮
                        $('#syncOllamaBtn').show();
                    } else {
                        // 非Ollama服务商
                        $('#model-list-hint').text('从预设模型列表中选择需要使用的模型：');
                        // 隐藏Ollama特有部分
                        $('#syncOllamaBtn').hide();
                    }
                } else {
                    alert('加载服务提供商信息失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('加载服务提供商信息失败: ' + error);
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
    
    // 同步本地Ollama模型
    syncOllamaModels: function() {
        var $syncBtn = $('#syncOllamaBtn');
        var originalText = $syncBtn.text();
        $syncBtn.text('同步中...').prop('disabled', true);
        
        // 调用API同步模型列表
        $.ajax({
            url: '/api/settings/model/providers/ollama/sync',
            type: 'POST',
            dataType: 'json',
            success: function(response) {
                $syncBtn.text(originalText).prop('disabled', false);
                if (response.success) {
                    alert(response.message || '同步成功！');
                    // 重新加载模型列表
                    ModelService.loadAllModels();
                } else {
                    alert('同步失败: ' + (response.message || '未知错误'));
                }
            },
            error: function(xhr, status, error) {
                $syncBtn.text(originalText).prop('disabled', false);
                alert('同步失败: ' + error);
            }
        });
    },
    
    // 加载所有模型列表（包括不可见的和可用的）
    loadAllModels: function() {
        // 对Ollama特殊处理，直接加载本地模型
        if (this.currentProvider === 'ollama') {
            // 获取已添加的Ollama模型
            $.ajax({
                url: '/api/settings/model/providers/ollama/models',
                type: 'GET',
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        var activeModels = response.models;
                        
                        // 获取本地所有Ollama模型
                        $.ajax({
                            url: '/api/common/ollama/models',
                            type: 'GET',
                            dataType: 'json',
                            success: function(localResponse) {
                                if (localResponse.success) {
                                    console.log("Ollama本地模型获取成功:", localResponse);
                                    var localModels = localResponse.models || [];
                                    
                                    // 处理可能的格式差异
                                    if (Array.isArray(localModels)) {
                                        // 将本地模型与已添加模型合并
                                        ModelService.renderOllamaModels(localModels, activeModels);
                                    } else {
                                        console.error("Ollama模型格式不正确:", localModels);
                                        $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">Ollama模型格式不正确</td></tr>');
                                    }
                                } else {
                                    console.error("加载本地模型失败:", localResponse.message);
                                    $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载本地模型失败: ' + localResponse.message + '</td></tr>');
                                }
                            },
                            error: function(xhr, status, error) {
                                console.error("加载本地模型AJAX错误:", xhr.responseText);
                                $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载本地模型失败: ' + error + '</td></tr>');
                            }
                        });
                    } else {
                        $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载失败: ' + response.message + '</td></tr>');
                    }
                },
                error: function(xhr, status, error) {
                    $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载失败: ' + error + '</td></tr>');
                }
            });
            
            // Ollama不需要再显示单独的本地模型部分
            $('#ollamaLocalModels').hide();
        } else {
            // 非Ollama服务商使用原来的逻辑
            $.ajax({
                url: '/api/settings/model/providers/' + this.currentProvider + '/models',
                type: 'GET',
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        var activeModels = response.models;
                        // 获取指定提供商的所有可用模型
                        ModelService.loadAvailableModels(activeModels);
                    } else {
                        $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载失败: ' + response.message + '</td></tr>');
                    }
                },
                error: function(xhr, status, error) {
                    $('#modelTableBody').html('<tr><td colspan="4" class="text-center error">加载失败: ' + error + '</td></tr>');
                }
            });
        }
    },
    
    // 渲染Ollama模型表格（本地模型和已添加模型的合并视图）
    renderOllamaModels: function(localModels, activeModels) {
        console.log("渲染Ollama模型:", localModels, activeModels);
        
        var activeModelMap = {};
        for (var i = 0; i < activeModels.length; i++) {
            activeModelMap[activeModels[i].id] = activeModels[i];
        }
        
        var tableHtml = '';
        
        // 只显示本地已安装的模型
        for (var i = 0; i < localModels.length; i++) {
            // 适配不同的API返回格式
            var model = localModels[i];
            var modelName = model.name || model.model; // ollama.list() API返回的是model字段
            
            if (!modelName) {
                console.error("找不到模型名称:", model);
                continue;
            }
            
            // 检查模型是否已启用
            var isActive = activeModelMap[modelName] !== undefined;
            var modelToShow = isActive ? activeModelMap[modelName] : {
                description: '本地Ollama模型',
                category: '本地模型',
                visible: true
            };
            
            var description = isActive ? (modelToShow.description || '本地Ollama模型') : '本地Ollama模型';
            
            // 确定状态文本和状态类
            var statusText = isActive ? (modelToShow.visible ? '可见' : '不显示') : '未启用';
            var statusClass = isActive ? 
                (modelToShow.visible ? 'status-visible' : 'status-hidden') : 
                'status-disabled';
            
            tableHtml += `
                <tr data-model-id="${modelName}">
                    <td title="${description}">${modelName}</td>
                    <td>${isActive ? (modelToShow.category || '本地模型') : '本地模型'}</td>
                    <td class="${statusClass}">${statusText}</td>
                    <td>
                        ${isActive ? 
                            (modelToShow.visible ? 
                                '<button class="action-btn hide-model-btn" title="不显示">不显示</button>' : 
                                '<button class="action-btn show-model-btn" title="显示">显示</button>') : 
                            '<button class="action-btn enable-model-btn" title="启用">启用</button>'}
                    </td>
                </tr>
            `;
        }
        
        // 如果没有模型，显示提示信息
        if (tableHtml === '') {
            tableHtml = '<tr><td colspan="4" class="text-center">未找到本地Ollama模型</td></tr>';
        }
        
        // 更新表格
        $('#modelTableBody').html(tableHtml);
        
        // 更新默认模型下拉框
        this.updateDefaultModelDropdown(activeModels.filter(function(model) {
            return model.visible === true;
        }));
        
        // 绑定操作按钮事件
        $('.hide-model-btn').click(function() {
            var modelId = $(this).closest('tr').data('model-id');
            ModelService.toggleModelVisibility(modelId, false);
        });
        
        $('.show-model-btn').click(function() {
            var modelId = $(this).closest('tr').data('model-id');
            ModelService.toggleModelVisibility(modelId, true);
        });
        
        $('.enable-model-btn').click(function() {
            var $tr = $(this).closest('tr');
            var modelId = $tr.data('model-id');
            ModelService.enableModel(modelId);
        });
    },
    
    // 加载提供商的所有可用预设模型
    loadAvailableModels: function(activeModels) {
        // 构建当前激活模型的ID映射，便于快速查找
        var activeModelMap = {};
        for (var i = 0; i < activeModels.length; i++) {
            activeModelMap[activeModels[i].id] = activeModels[i];
        }
        
        // 获取预设模型配置
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/available-models',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var availableModels = response.models;
                    var tableHtml = '';
                    
                    // 生成模型表格 - 仅包含尚未被用户自己隐藏的模型
                    for (var i = 0; i < availableModels.length; i++) {
                        var model = availableModels[i];
                        var isActive = activeModelMap[model.id] !== undefined;
                        
                        // 如果该模型已激活，直接使用其当前状态（包括可见性）
                        // 如果该模型未激活，才使用预设配置中的可见性
                        var modelToShow = isActive ? activeModelMap[model.id] : model;
                        
                        // 确定状态文本和状态类
                        var statusText = isActive ? 
                            (modelToShow.visible ? '可见' : '不显示') : '未启用';
                        var statusClass = isActive ? 
                            (modelToShow.visible ? 'status-visible' : 'status-hidden') : 
                            'status-disabled';
                        
                        var description = modelToShow.description || '';
                        
                        tableHtml += `
                            <tr data-model-id="${model.id}">
                                <td title="${description}">${model.name}</td>
                                <td>${model.category || '未分类'}</td>
                                <td class="${statusClass}">${statusText}</td>
                                <td>
                                    ${isActive ? 
                                        (modelToShow.visible ? 
                                            '<button class="action-btn hide-model-btn" title="不显示">不显示</button>' : 
                                            '<button class="action-btn show-model-btn" title="显示">显示</button>') : 
                                        '<button class="action-btn enable-model-btn" title="启用">启用</button>'}
                                </td>
                            </tr>
                        `;
                    }
                    
                    // 如果没有模型，显示提示信息
                    if (availableModels.length === 0) {
                        tableHtml = '<tr><td colspan="4" class="text-center">暂无可用模型</td></tr>';
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
                    
                    $('.enable-model-btn').click(function() {
                        var $tr = $(this).closest('tr');
                        var modelId = $tr.data('model-id');
                        ModelService.enableModel(modelId);
                    });
                } else {
                    // 如果API不存在，则使用现有模型作为可用模型
                    ModelService.renderModelTable(activeModels);
                }
            },
            error: function(xhr, status, error) {
                // 如果API不存在，则使用现有模型作为可用模型
                ModelService.renderModelTable(activeModels);
            }
        });
    },
    
    // 渲染模型表格（备用方法）
    renderModelTable: function(models) {
        var tableHtml = '';
        
        // 生成模型表格
        for (var i = 0; i < models.length; i++) {
            var model = models[i];
            // 使用模型当前状态，包括可见性
            var statusText = model.visible ? '可见' : '不显示';
            var statusClass = model.visible ? 'status-visible' : 'status-hidden';
            var description = model.description || '';
            
            tableHtml += `
                <tr data-model-id="${model.id}">
                    <td title="${description}">${model.name}</td>
                    <td>${model.category || '未分类'}</td>
                    <td class="${statusClass}">${statusText}</td>
                    <td>
                        ${model.visible ? 
                            '<button class="action-btn hide-model-btn" title="不显示">不显示</button>' : 
                            '<button class="action-btn show-model-btn" title="显示">显示</button>'}
                    </td>
                </tr>
            `;
        }
        
        // 如果没有模型，显示提示信息
        if (models.length === 0) {
            tableHtml = '<tr><td colspan="4" class="text-center">暂无可用模型</td></tr>';
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
        
        $('.enable-model-btn').click(function() {
            var $tr = $(this).closest('tr');
            var modelId = $tr.data('model-id');
            ModelService.enableModel(modelId);
        });
    },
    
    // 启用模型
    enableModel: function(modelId) {
        // 对Ollama特殊处理
        if (this.currentProvider === 'ollama') {
            // 添加本地Ollama模型
            var modelData = {
                id: modelId,
                name: modelId,
                category: 'Ollama本地',
                description: 'Ollama本地模型 ' + modelId,
                visible: true
            };
            
            $.ajax({
                url: '/api/settings/model/providers/ollama/models/add',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(modelData),
                success: function(response) {
                    if (response.success) {
                        ModelService.loadAllModels();
                        alert('Ollama模型已启用');
                    } else {
                        alert('启用模型失败: ' + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    alert('启用模型失败: ' + error);
                }
            });
            return;
        }
        
        // 非Ollama服务商的处理逻辑
        // 获取预设模型配置中的对应模型
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/available-models',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var availableModels = response.models;
                    var modelData = null;
                    
                    // 查找对应的模型
                    for (var i = 0; i < availableModels.length; i++) {
                        if (availableModels[i].id === modelId) {
                            modelData = availableModels[i];
                            break;
                        }
                    }
                    
                    if (modelData) {
                        // 添加模型
                        $.ajax({
                            url: '/api/settings/model/providers/' + ModelService.currentProvider + '/models/add',
                            type: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify(modelData),
                            success: function(response) {
                                if (response.success) {
                                    // 刷新模型列表
                                    ModelService.loadAllModels();
                                    alert('模型已启用');
                                } else {
                                    alert('启用模型失败: ' + response.message);
                                }
                            },
                            error: function(xhr, status, error) {
                                alert('启用模型失败: ' + error);
                            }
                        });
                    } else {
                        alert('未找到对应的模型信息');
                    }
                } else {
                    alert('获取模型信息失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('获取模型信息失败: ' + error);
            }
        });
    },
    
    // 禁用模型
    disableModel: function(modelId, modelName) {
        if (!confirm('确定要禁用模型 ' + modelName + ' 吗？您可以随时重新启用。')) {
            return;
        }
        
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/models/delete',
            type: 'DELETE',
            data: { modelId: modelId },
            success: function(response) {
                if (response.success) {
                    // 刷新模型列表
                    ModelService.loadAllModels();
                    alert('模型已禁用');
                } else {
                    alert('禁用模型失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('禁用模型失败: ' + error);
            }
        });
    },
    
    // 切换模型可见性
    toggleModelVisibility: function(modelId, visible) {
        if (!this.currentProvider) {
            return;
        }
        
        $.ajax({
            url: '/api/settings/model/providers/' + this.currentProvider + '/models/visibility',
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({
                modelId: modelId,
                visible: visible
            }),
            success: function(response) {
                if (response.success) {
                    // 刷新模型列表
                    ModelService.loadAllModels();
                } else {
                    alert('更新模型可见性失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('更新模型可见性失败: ' + error);
            }
        });
    },
    
    // 更新默认模型下拉框
    updateDefaultModelDropdown: function(models) {
        // 直接获取所有服务提供商的可见模型
        $.ajax({
            url: '/api/model/visible-models',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var dropdown = $('#default-model');
                    dropdown.empty();
                    dropdown.append('<option value="">请选择默认模型</option>');
                    
                    var allVisibleModels = response.models;
                    // 排序：按提供商分组
                    allVisibleModels.sort(function(a, b) {
                        // 首先按提供商名称排序
                        if (a.provider_name !== b.provider_name) {
                            return a.provider_name.localeCompare(b.provider_name);
                        }
                        // 其次按类别排序
                        if (a.category !== b.category) {
                            return a.category.localeCompare(b.category);
                        }
                        // 最后按模型名称排序
                        return a.name.localeCompare(b.name);
                    });
                    
                    var currentProviderId = '';
                    for (var i = 0; i < allVisibleModels.length; i++) {
                        var model = allVisibleModels[i];
                        
                        // 如果是新的提供商，添加分组
                        if (model.provider_id !== currentProviderId) {
                            if (i > 0) {
                                dropdown.append('</optgroup>');
                            }
                            dropdown.append('<optgroup label="' + model.provider_name + '">');
                            currentProviderId = model.provider_id;
                        }
                        
                        // 添加选项，值为 provider_id:model_id 的组合
                        // 注意：model_id可能包含冒号，例如 qwen3:4b
                        var optionValue = model.provider_id + ':' + model.id;
                        var optionText = model.name + ' (' + model.category + ')';
                        
                        // 使用HTML属性data-model-id来存储原始model_id，避免冒号问题
                        dropdown.append('<option value="' + optionValue + '" data-model-id="' + model.id + '">' + 
                                        optionText + '</option>');
                    }
                    
                    // 关闭最后一个分组
                    if (allVisibleModels.length > 0) {
                        dropdown.append('</optgroup>');
                    }
                    
                    // 加载默认模型
                    ModelService.loadDefaultModel();
                } else {
                    console.error('获取可见模型失败:', response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('获取可见模型AJAX错误:', error);
            }
        });
    },
    
    // 加载默认模型
    loadDefaultModel: function() {
        console.log('开始加载默认模型设置');
        // 从服务器获取当前默认模型
        $.ajax({
            url: '/api/model/default-model',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                console.log('加载默认模型响应:', response);
                if (response.success && response.model) {
                    var defaultModel = response.model;
                    console.log('当前默认模型:', defaultModel);
                    // 设置下拉框选中值为 provider_id:model_id 的组合
                    // 注意：model_id可能包含冒号，例如 qwen3:4b
                    var selectValue = defaultModel.provider_id + ':' + defaultModel.id;
                    console.log('设置下拉框选中值:', selectValue);
                    $('#default-model').val(selectValue);
                    console.log('下拉框当前选中值:', $('#default-model').val());
                    
                    // 如果下拉框没有正确设置值（可能是因为模型不在列表中）
                    if (!$('#default-model').val()) {
                        console.warn('下拉框未能选中值，可能模型不在可见列表中');
                    }
                } else {
                    console.log('无默认模型或加载失败');
                    $('#default-model').val('');
                }
            },
            error: function(xhr, status, error) {
                console.error('加载默认模型设置失败:', error);
                console.error('响应状态:', status);
                console.error('响应内容:', xhr.responseText);
                $('#default-model').val('');
            }
        });
    },
    
    // 设置默认模型
    setDefaultModel: function(combinedValue) {
        console.log('开始设置默认模型:', combinedValue);
        // combinedValue 格式为 provider_id:model_id，但model_id可能包含冒号
        // 例如：ollama:qwen3:4b，第一个冒号分隔provider_id和model_id
        
        // 找到第一个冒号的位置
        var firstColonIndex = combinedValue.indexOf(':');
        if (firstColonIndex === -1) {
            console.error('模型值格式不正确 (没有冒号):', combinedValue);
            return;
        }
        
        // 分割提供商ID和模型ID
        var providerId = combinedValue.substring(0, firstColonIndex);
        var modelId = combinedValue.substring(firstColonIndex + 1);
        
        console.log('解析后的提供商ID:', providerId, '模型ID:', modelId);
        
        // 调用API设置默认模型
        $.ajax({
            url: '/api/model/default-model',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                provider_id: providerId,
                model_id: modelId
            }),
            success: function(response) {
                console.log('设置默认模型响应:', response);
                if (response.success) {
                    console.log('默认模型设置成功');
                    // 可以添加成功提示
                    alert('默认模型设置成功');
                    
                    // 验证设置是否生效
                    setTimeout(function() {
                        ModelService.loadDefaultModel();
                    }, 1000);
                } else {
                    console.error('保存默认模型设置失败:', response.error);
                    alert('保存默认模型设置失败: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('保存默认模型设置AJAX错误:', error);
                console.error('响应状态:', status);
                console.error('响应内容:', xhr.responseText);
                alert('保存默认模型设置失败: ' + error);
            }
        });
    }
}; 