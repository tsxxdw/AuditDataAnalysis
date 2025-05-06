// 提示词模板页面JS文件(index_prompt_templates)
$(document).ready(function() {
    // 初始化时加载模板列表
    loadTemplateList();
    
    // 保存模板按钮点击事件
    $('#saveTemplate').on('click', function() {
        saveTemplate();
    });
    
    // 清空按钮点击事件
    $('#clearTemplate').on('click', function() {
        clearTemplateForm();
    });
    
    // 关闭预览按钮点击事件
    $('#closePreview').on('click', function() {
        $('.template-preview-section').hide();
    });
    
    // 加载模板列表
    function loadTemplateList() {
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    displayTemplates(response.templates);
                } else {
                    console.error('获取模板列表失败:', response.message);
                    // 显示空的模板列表
                    $('.templates-container').html('<p class="no-templates">暂无模板数据，请添加新模板</p>');
                }
            },
            error: function(xhr) {
                console.error('获取模板列表请求失败:', xhr);
                $('.templates-container').html('<p class="no-templates error">获取模板列表失败，请刷新重试</p>');
            }
        });
    }
    
    // 显示模板列表
    function displayTemplates(templates) {
        const templateContainer = $('.templates-container');
        templateContainer.empty();
        
        if (!templates || templates.length === 0) {
            templateContainer.html('<p class="no-templates">暂无模板数据，请添加新模板</p>');
            return;
        }
        
        // 遍历模板数据并显示
        templates.forEach(template => {
            const templateCard = $(`
                <div class="template-card" data-id="${template.id}">
                    <div class="template-card-title">${template.name}</div>
                    <div class="template-card-description">${template.description || '无描述'}</div>
                    <div class="template-card-actions">
                        <button class="btn-edit" data-id="${template.id}">编辑</button>
                        <button class="btn-delete" data-id="${template.id}">删除</button>
                    </div>
                </div>
            `);
            
            // 绑定编辑点击事件
            templateCard.find('.btn-edit').on('click', function(e) {
                e.stopPropagation();
                const templateId = $(this).data('id');
                loadTemplateForEdit(templateId);
            });
            
            // 绑定删除点击事件
            templateCard.find('.btn-delete').on('click', function(e) {
                e.stopPropagation();
                const templateId = $(this).data('id');
                deleteTemplate(templateId);
            });
            
            // 绑定卡片点击事件（显示详情）
            templateCard.on('click', function() {
                const templateId = $(this).data('id');
                loadTemplateForEdit(templateId);
            });
            
            templateContainer.append(templateCard);
        });
    }
    
    // 加载模板进行编辑
    function loadTemplateForEdit(templateId) {
        $.ajax({
            url: `/api/prompt_templates/${templateId}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const template = response.template;
                    
                    // 填充基本信息
                    $('#templateName').val(template.name);
                    $('#templateDescription').val(template.description || '');
                    
                    // 解析模板内容为系统、用户提示词
                    parseTemplateContent(template.content);
                    
                    // 设置当前编辑的模板ID
                    $('#saveTemplate').data('template-id', templateId);
                } else {
                    console.error('获取模板详情失败:', response.message);
                    alert('获取模板详情失败: ' + response.message);
                }
            },
            error: function(xhr) {
                console.error('获取模板详情请求失败:', xhr);
                alert('获取模板详情请求失败，请查看控制台日志');
            }
        });
    }
    
    // 解析模板内容
    function parseTemplateContent(content) {
        if (!content) return;
        
        try {
            // 尝试解析JSON格式的模板内容
            const templateData = JSON.parse(content);
            
            // 填充各个部分
            $('#systemPrompt').val(templateData.system || '');
            $('#userPrompt').val(templateData.user || '');
        } catch (e) {
            // 如果不是JSON格式，则按照旧格式处理（放入用户提示词中）
            console.warn('模板格式不是JSON，将内容放入用户提示词', e);
            $('#systemPrompt').val('');
            $('#userPrompt').val(content);
        }
    }
    
    // 保存模板
    function saveTemplate() {
        const templateId = $('#saveTemplate').data('template-id');
        const templateName = $('#templateName').val();
        const templateDescription = $('#templateDescription').val();
        
        // 获取系统提示词和用户提示词
        const systemPrompt = $('#systemPrompt').val();
        const userPrompt = $('#userPrompt').val();
        
        if (!templateName) {
            alert('请输入模板名称');
            return;
        }
        
        if (!userPrompt) {
            alert('请输入用户提示词');
            return;
        }
        
        // 构建新的模板内容格式（JSON）
        const templateContent = JSON.stringify({
            system: systemPrompt,
            user: userPrompt
        });
        
        const templateData = {
            name: templateName,
            description: templateDescription,
            content: templateContent
        };
        
        // 检查模板名称是否已存在
        $.ajax({
            url: '/api/prompt_templates/list',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const templates = response.templates || [];
                    const existingTemplate = templates.find(t => t.name === templateName && t.id !== templateId);
                    
                    // 如果有ID并且名称没变，直接更新
                    if (templateId) {
                        const currentTemplate = templates.find(t => t.id === templateId);
                        if (currentTemplate && currentTemplate.name === templateName) {
                            if (!confirm('确认要修改此模板吗？')) {
                                return;
                            }
                            updateOrCreateTemplate(templateId, templateData);
                            return;
                        }
                    }
                    
                    // 如果名称已存在
                    if (existingTemplate) {
                        alert(`错误：已存在名为"${templateName}"的模板，请更换模板名称。`);
                        return;
                    } else {
                        if (!confirm(`确认要新增模板"${templateName}"吗？`)) {
                            return;
                        }
                    }
                    
                    // 执行保存或更新
                    updateOrCreateTemplate(templateId, templateData);
                    
                } else {
                    console.error('获取模板列表失败:', response.message);
                    if (!confirm('无法检查模板是否存在，是否继续保存？')) {
                        return;
                    }
                    updateOrCreateTemplate(templateId, templateData);
                }
            },
            error: function(xhr) {
                console.error('获取模板列表请求失败:', xhr);
                if (!confirm('无法检查模板是否存在，是否继续保存？')) {
                    return;
                }
                updateOrCreateTemplate(templateId, templateData);
            }
        });
    }
    
    // 更新或创建模板的辅助函数
    function updateOrCreateTemplate(templateId, templateData) {
        // 根据是否有模板ID决定是创建还是更新
        const url = templateId ? 
            `/api/prompt_templates/${templateId}` : 
            '/api/prompt_templates/create';
        
        const method = templateId ? 'PUT' : 'POST';
        
        $.ajax({
            url: url,
            type: method,
            contentType: 'application/json',
            data: JSON.stringify(templateData),
            success: function(response) {
                if (response.success) {
                    alert(templateId ? '更新模板成功' : '创建模板成功');
                    // 重新加载模板列表
                    loadTemplateList();
                    // 清空表单
                    clearTemplateForm();
                } else {
                    alert(response.message || (templateId ? '更新模板失败' : '创建模板失败'));
                }
            },
            error: function(xhr) {
                console.error('保存模板请求失败:', xhr);
                alert('保存模板请求失败，请查看控制台日志');
            }
        });
    }
    
    // 删除模板
    function deleteTemplate(templateId) {
        if (!confirm('确定要删除此模板吗？')) {
            return;
        }
        
        $.ajax({
            url: `/api/prompt_templates/${templateId}`,
            type: 'DELETE',
            success: function(response) {
                if (response.success) {
                    alert('删除模板成功');
                    // 重新加载模板列表
                    loadTemplateList();
                    
                    // 如果当前正在编辑被删除的模板，则清空表单
                    if ($('#saveTemplate').data('template-id') === templateId) {
                        clearTemplateForm();
                    }
                } else {
                    alert(response.message || '删除模板失败');
                }
            },
            error: function(xhr) {
                console.error('删除模板请求失败:', xhr);
                alert('删除模板请求失败，请查看控制台日志');
            }
        });
    }
    
    // 预览模板
    function previewTemplate() {
        const systemPrompt = $('#systemPrompt').val();
        const userPrompt = $('#userPrompt').val();
        
        if (!userPrompt) {
            alert('请先输入用户提示词');
            return;
        }
        
        // 显示预览
        let finalPreview = '';
        
        if (systemPrompt) {
            finalPreview += '<div class="preview-system">';
            finalPreview += '<strong>系统：</strong><pre>' + escapeHtml(systemPrompt) + '</pre>';
            finalPreview += '</div>';
        }
        
        finalPreview += '<div class="preview-user">';
        finalPreview += '<strong>用户：</strong><pre>' + escapeHtml(userPrompt) + '</pre>';
        finalPreview += '</div>';
        
        $('.preview-content').html(finalPreview);
        $('.template-preview-section').show();
    }
    
    // HTML转义函数
    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // 清空模板表单
    function clearTemplateForm() {
        $('#templateName').val('');
        $('#templateDescription').val('');
        $('#systemPrompt').val('');
        $('#userPrompt').val('');
        
        // 移除模板ID
        $('#saveTemplate').removeData('template-id');
    }
}); 