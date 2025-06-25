/**
 * 个人设置页面脚本
 */

// 个人设置模块
var PersonalSettings = {
    /**
     * 初始化个人设置模块
     */
    init: function() {
        // 初始化加载用户信息
        this.loadCurrentUserInfo();
        
        // 绑定修改密码表单提交事件
        $('#change-password-form').on('submit', function(e) {
            e.preventDefault();
            PersonalSettings.changePassword();
        });
    },

    /**
     * 加载当前用户信息
     */
    loadCurrentUserInfo: function() {
        $.ajax({
            url: '/api/settings/personal/info',
            type: 'GET',
            success: function(response) {
                if (response.code === 200) {
                    PersonalSettings.displayUserInfo(response.data);
                } else {
                    console.error('获取用户信息失败:', response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('获取用户信息异常:', error);
            }
        });
    },

    /**
     * 显示用户信息
     * @param {Object} userInfo 用户信息对象
     */
    displayUserInfo: function(userInfo) {
        // 显示用户名
        $('#current-username').text(userInfo.username);
        
        // 显示角色
        $('#current-role').text(userInfo.role);
        
        // 显示权限列表
        const $permissionList = $('#current-permissions');
        $permissionList.empty();
        
        // 如果是管理员，显示所有权限
        if (userInfo.role === '管理员') {
            $permissionList.append('<span class="permission-tag">全部权限</span>');
        } else {
            // 显示具体权限列表
            if (userInfo.permissions && userInfo.permissions.length > 0) {
                userInfo.permissions.forEach(function(permission) {
                    // 获取权限对应的标题
                    let permissionTitle = permission;
                    // 如果存在permission_titles映射，则使用标题而不是路径
                    if (userInfo.permission_titles && userInfo.permission_titles[permission]) {
                        permissionTitle = userInfo.permission_titles[permission];
                    }
                    $permissionList.append(`<span class="permission-tag">${permissionTitle}</span>`);
                });
            } else {
                $permissionList.append('<span>无</span>');
            }
        }
    },

    /**
     * 修改密码
     */
    changePassword: function() {
        // 获取表单数据
        const currentPassword = $('#current-password').val();
        const newPassword = $('#new-password').val();
        const confirmPassword = $('#confirm-password').val();
        
        // 验证新密码与确认密码是否一致
        if (newPassword !== confirmPassword) {
            this.showErrorMessage('新密码与确认密码不一致');
            return;
        }
        
        // 验证新密码长度
        if (newPassword.length < 6) {
            this.showErrorMessage('新密码长度不能少于6位');
            return;
        }
        
        // 发送修改密码请求
        $.ajax({
            url: '/api/settings/personal/change_password',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            }),
            success: function(response) {
                if (response.code === 200) {
                    // 密码修改成功
                    PersonalSettings.showSuccessMessage(response.message);
                    // 清空表单
                    $('#change-password-form')[0].reset();
                } else {
                    // 密码修改失败
                    PersonalSettings.showErrorMessage(response.message);
                }
            },
            error: function(xhr, status, error) {
                PersonalSettings.showErrorMessage('服务器错误，请稍后重试');
                console.error('修改密码异常:', error);
            }
        });
    },

    /**
     * 显示错误消息
     * @param {string} message 错误消息
     */
    showErrorMessage: function(message) {
        // 移除可能已存在的消息元素
        this.removeMessages();
        
        // 创建错误消息元素
        const $errorMsg = $('<div class="error-message"></div>').text(message);
        
        // 添加到表单中
        $('#change-password-form').append($errorMsg);
        
        // 显示消息
        $errorMsg.fadeIn();
        
        // 5秒后自动隐藏
        setTimeout(function() {
            $errorMsg.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    },

    /**
     * 显示成功消息
     * @param {string} message 成功消息
     */
    showSuccessMessage: function(message) {
        // 移除可能已存在的消息元素
        this.removeMessages();
        
        // 创建成功消息元素
        const $successMsg = $('<div class="success-message"></div>').text(message);
        
        // 添加到表单中
        $('#change-password-form').append($successMsg);
        
        // 显示消息
        $successMsg.fadeIn();
        
        // 5秒后自动隐藏
        setTimeout(function() {
            $successMsg.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    },

    /**
     * 移除所有消息元素
     */
    removeMessages: function() {
        $('.error-message, .success-message').remove();
    }
};

// 移除原来的document.ready，让settings.js统一调用初始化 