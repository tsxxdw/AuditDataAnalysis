/**
 * 用户管理页面的JavaScript脚本
 */

$(document).ready(function() {
    // 获取用户列表
    loadUserList();
    
    // 添加用户按钮点击事件
    $('#add-user-btn').click(function() {
        $('#add-user-modal').show();
    });
    
    // 关闭模态框事件
    $('.close-modal').click(function() {
        $('.modal').hide();
    });
    
    // 点击模态框外部关闭模态框
    $(window).click(function(event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').hide();
        }
    });
    
    // 添加用户表单提交事件
    $('#add-user-form').submit(function(event) {
        event.preventDefault();
        
        const username = $('#username').val();
        const password = $('#password').val();
        const role = $('#role').val();
        
        // 验证用户名是否只包含字母和数字
        const usernameRegex = /^[a-zA-Z0-9]+$/;
        if (!usernameRegex.test(username)) {
            showMessage('用户名只能包含字母和数字', 'error');
            return;
        }
        
        addUser(username, password, role);
    });
    
    // 保存权限按钮点击事件
    $('#save-permissions-btn').click(function() {
        const username = $('#permission-username').text();
        const permissions = [];
        
        // 获取所有选中的权限
        $('.permission-checkbox:checked').each(function() {
            permissions.push($(this).val());
        });
        
        updatePermissions(username, permissions);
    });
});

/**
 * 加载用户列表
 */
function loadUserList() {
    $.ajax({
        url: '/api/user/list',
        type: 'GET',
        success: function(response) {
            if (response.code === 200) {
                renderUserList(response.data);
            } else {
                showMessage('获取用户列表失败: ' + response.message, 'error');
            }
        },
        error: function(xhr) {
            showMessage('获取用户列表失败，请检查网络连接', 'error');
        }
    });
}

/**
 * 渲染用户列表
 * @param {Array} users 用户数据
 */
function renderUserList(users) {
    const $userList = $('#user-list');
    $userList.empty();
    
    if (users.length === 0) {
        $userList.append('<tr><td colspan="3" class="text-center">暂无用户数据</td></tr>');
        return;
    }
    
    users.forEach(function(user) {
        const $row = $('<tr></tr>');
        
        $row.append(`<td>${user.username}</td>`);
        $row.append(`<td>${user.role}</td>`);
        
        const $actions = $('<td></td>');
        
        // 管理员不能修改自己的权限
        if (user.role !== '管理员') {
            $actions.append(`<button class="action-btn permission-btn" data-username="${user.username}">设置权限</button>`);
        }
        
        $actions.append(`<button class="action-btn delete-btn" data-username="${user.username}">删除</button>`);
        
        $row.append($actions);
        $userList.append($row);
    });
    
    // 设置权限按钮点击事件
    $('.permission-btn').click(function() {
        const username = $(this).data('username');
        openPermissionsModal(username);
    });
    
    // 删除用户按钮点击事件
    $('.delete-btn').click(function() {
        const username = $(this).data('username');
        if (confirm(`确定要删除用户 "${username}" 吗？`)) {
            deleteUser(username);
        }
    });
}

/**
 * 添加用户
 * @param {string} username 用户名
 * @param {string} password 密码
 * @param {string} role 角色
 */
function addUser(username, password, role) {
    $.ajax({
        url: '/api/user/add',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            password: password,
            role: role
        }),
        success: function(response) {
            if (response.code === 200) {
                $('#add-user-modal').hide();
                $('#add-user-form')[0].reset();
                showMessage('用户添加成功', 'success');
                loadUserList();
            } else {
                showMessage('用户添加失败: ' + response.message, 'error');
            }
        },
        error: function(xhr) {
            showMessage('用户添加失败，请检查网络连接', 'error');
        }
    });
}

/**
 * 删除用户
 * @param {string} username 用户名
 */
function deleteUser(username) {
    $.ajax({
        url: '/api/user/delete',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: String(username)  // 确保用户名作为字符串发送
        }),
        success: function(response) {
            if (response.code === 200) {
                showMessage('用户删除成功', 'success');
                loadUserList();
            } else {
                showMessage('用户删除失败: ' + response.message, 'error');
            }
        },
        error: function(xhr) {
            showMessage('用户删除失败，请检查网络连接', 'error');
        }
    });
}

/**
 * 打开权限设置模态框
 * @param {string} username 用户名
 */
function openPermissionsModal(username) {
    // 设置当前操作的用户名
    $('#permission-username').text(username);
    
    // 获取用户当前权限
    const user = getUserByUsername(username);
    
    // 获取所有可用页面
    $.ajax({
        url: '/api/user/available_pages',
        type: 'GET',
        success: function(response) {
            if (response.code === 200) {
                renderPermissionsList(response.data, user ? user.permissions : []);
                $('#permissions-modal').show();
            } else {
                showMessage('获取可用页面失败: ' + response.message, 'error');
            }
        },
        error: function(xhr) {
            showMessage('获取可用页面失败，请检查网络连接', 'error');
        }
    });
}

/**
 * 根据用户名获取用户信息
 * @param {string} username 用户名
 * @returns {Object|null} 用户信息
 */
function getUserByUsername(username) {
    let targetUser = null;
    
    $.ajax({
        url: '/api/user/list',
        type: 'GET',
        async: false,
        success: function(response) {
            if (response.code === 200) {
                const users = response.data;
                users.forEach(function(user) {
                    // 确保使用字符串比较，解决纯数字用户名的问题
                    if (String(user.username) === String(username)) {
                        targetUser = user;
                    }
                });
            }
        }
    });
    
    return targetUser;
}

/**
 * 渲染权限列表
 * @param {Array} pages 可用页面列表
 * @param {Array} userPermissions 用户当前权限
 */
function renderPermissionsList(pages, userPermissions) {
    const $permissionsList = $('#permissions-list');
    $permissionsList.empty();
    
    // 确保userPermissions是数组
    const permissions = Array.isArray(userPermissions) ? userPermissions : [];
    
    pages.forEach(function(page) {
        // 使用some方法进行比较，确保类型一致
        const isChecked = permissions.some(perm => String(perm) === String(page.path));
        
        const $item = $(`
            <div class="permission-item">
                <input type="checkbox" class="permission-checkbox" id="perm-${page.path}" value="${page.path}" ${isChecked ? 'checked' : ''}>
                <label for="perm-${page.path}">${page.name}</label>
            </div>
        `);
        
        $permissionsList.append($item);
    });
}

/**
 * 更新用户权限
 * @param {string} username 用户名
 * @param {Array} permissions 权限列表
 */
function updatePermissions(username, permissions) {
    $.ajax({
        url: '/api/user/update_permissions',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: String(username),  // 确保用户名作为字符串发送
            permissions: permissions
        }),
        success: function(response) {
            if (response.code === 200) {
                $('#permissions-modal').hide();
                showMessage('权限更新成功', 'success');
                loadUserList();
            } else {
                showMessage('权限更新失败: ' + response.message, 'error');
            }
        },
        error: function(xhr) {
            showMessage('权限更新失败，请检查网络连接', 'error');
        }
    });
}

/**
 * 显示消息提示
 * @param {string} message 消息内容
 * @param {string} type 消息类型 (success/error)
 */
function showMessage(message, type) {
    alert(message);
} 