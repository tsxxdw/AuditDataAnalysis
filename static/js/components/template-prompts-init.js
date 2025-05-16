/**
 * 模板提示词区域组件初始化文件
 */
$(document).ready(function() {
    // 初始化模板提示词区域组件
    if (typeof TemplatePrompts !== 'undefined') {
        // 初始化组件
        window.templatePromptsComponent = new TemplatePrompts({
            onSelect: function(templateId, item) {
                console.log('已选择模板:', templateId, item);
                // 这里可以添加其他选择响应逻辑
            }
        });
        
        // 将组件实例挂载到全局对象上，便于其他脚本访问
        console.log('模板提示词区域组件初始化成功');
    } else {
        console.error('模板提示词区域组件初始化失败: TemplatePrompts 类未定义');
    }
}); 