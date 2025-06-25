/**
 * 日志设置页面脚本
 */

// 日志设置模块
var LogSettings = {
    // 初始化
    init: function() {
        // 绑定保存按钮事件
        $('.save-logs-btn').click(function() {
            LogSettings.saveSettings();
        });
    },
    
    // 加载日志设置
    loadSettings: function() {
        $.ajax({
            url: '/api/settings/log/get',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // 填充表单
                    $('#log-path').val(response.data.log_path || 'logs');
                    
                    // 显示最后更新时间（如果有）
                    if (response.data.last_updated) {
                        // 先移除之前的更新信息（如果存在）
                        $('.last-updated-info').remove();
                        
                        $('.log-settings-form').append(
                            '<div class="form-group last-updated-info">' + 
                            '<small>最后更新: ' + response.data.last_updated + '</small>' +
                            '</div>'
                        );
                    }
                } else {
                    alert('加载日志设置失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('加载日志设置时发生错误: ' + error);
            }
        });
    },
    
    // 保存日志设置
    saveSettings: function() {
        var logPath = $('#log-path').val();
        
        if (!logPath) {
            alert('日志路径不能为空');
            return;
        }
        
        // 显示加载指示器
        var saveBtn = $('.save-logs-btn');
        var originalText = saveBtn.text();
        saveBtn.text('保存中...').prop('disabled', true);
        
        $.ajax({
            url: '/api/settings/log/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                log_path: logPath
            }),
            success: function(response) {
                if (response.success) {
                    // 更新成功
                    alert('日志设置已保存');
                    
                    // 重新加载设置以显示最后更新时间
                    LogSettings.loadSettings();
                } else {
                    alert('保存日志设置失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('保存日志设置时发生错误: ' + error);
            },
            complete: function() {
                // 恢复按钮状态
                saveBtn.text(originalText).prop('disabled', false);
            }
        });
    }
}; 