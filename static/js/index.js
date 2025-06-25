/**
 * 首页脚本
 */
$(document).ready(function() {
    // 获取并显示导航按钮
    loadNavigationButtons();
});

/**
 * 通过API获取导航按钮并显示
 */
function loadNavigationButtons() {
    // 清空现有按钮容器
    $(".buttons-container").empty();
    
    // 显示加载状态
    $(".buttons-container").html('<div class="loading">正在加载导航按钮...</div>');
    
    // 调用API获取导航按钮
    $.ajax({
        url: '/api/get_navigation_buttons',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            // 清除加载状态
            $(".buttons-container").empty();
            
            if (response.code === 200 && response.data) {
                // 遍历按钮数据并添加到页面
                response.data.forEach(function(button) {
                    var buttonHtml = '<a href="' + 
                        (button.url ? '/'+button.url : '#') + 
                        '" class="' + 
                        (button.class || 'main-btn') + 
                        '" target="_blank">' + 
                        button.title + 
                        '</a>';
                    
                    $(".buttons-container").append(buttonHtml);
                });
                
                // 如果没有按钮数据
                if (response.data.length === 0) {
                    $(".buttons-container").html('<div class="no-access">您没有访问任何功能的权限</div>');
                }
            } else {
                // 显示错误信息
                $(".buttons-container").html('<div class="error">加载导航按钮失败: ' + response.message + '</div>');
            }
        },
        error: function(xhr, status, error) {
            // 显示错误信息
            $(".buttons-container").html('<div class="error">加载导航按钮失败: ' + error + '</div>');
        }
    });
} 