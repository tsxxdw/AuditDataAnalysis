/**
 * 登录页面脚本
 */
$(document).ready(function() {
    // 登录按钮点击事件
    $('#login-btn').on('click', function() {
        performLogin();
    });

    // 监听回车键
    $(document).on('keypress', function(e) {
        if (e.which === 13) {
            performLogin();
        }
    });

    /**
     * 执行登录逻辑
     */
    function performLogin() {
        const username = $('#username').val().trim();
        const password = $('#password').val().trim();
        const messageElement = $('#login-message');

        // 表单验证
        if (!username || !password) {
            messageElement.text('请输入用户名和密码');
            return;
        }

        // 清空错误信息
        messageElement.text('');
        
        // 显示加载状态
        const loginBtn = $('#login-btn');
        const originalText = loginBtn.text();
        loginBtn.text('登录中...').prop('disabled', true);

        // 发送登录请求
        $.ajax({
            url: '/api/user/login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                password: password
            }),
            success: function(response) {
                if (response.code === 200) {
                    // 登录成功，跳转到首页
                    window.location.href = '/';
                } else {
                    // 显示错误信息
                    messageElement.text(response.message || '登录失败');
                    loginBtn.text(originalText).prop('disabled', false);
                }
            },
            error: function() {
                messageElement.text('服务器错误，请稍后重试');
                loginBtn.text(originalText).prop('disabled', false);
            }
        });
    }
}); 