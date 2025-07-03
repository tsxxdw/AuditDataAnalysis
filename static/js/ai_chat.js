/**
 * AI聊天功能脚本
 */
$(document).ready(function() {
    // 初始化工作区
    initWorkspaces();
    
    // 发送按钮点击事件
    $("#send-button").on("click", sendMessage);
    
    // 输入框按键事件：按下Enter发送消息，Shift+Enter换行
    $("#chat-input").on("keydown", function(e) {
        if (e.keyCode === 13 && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 自动调整输入框高度
    $("#chat-input").on("input", function() {
        adjustTextareaHeight(this);
    });
    
    // 添加工作区标题点击事件
    $("#add-workspace-btn").on("click", addNewWorkspace);

    // 工具按钮点击事件
    $(".tool-btn").on("click", function() {
        const toolType = $(this).attr('title');
        handleToolClick(toolType);
    });

    // 麦克风按钮点击事件
    $(".mic-button").on("click", startVoiceInput);
});

/**
 * 自动调整文本框高度
 */
function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 24), 150);
    textarea.style.height = newHeight + 'px';
}

/**
 * 处理工具按钮点击
 * @param {string} toolType - 工具类型
 */
function handleToolClick(toolType) {
    switch(toolType) {
        case '附件':
            uploadAttachment();
            break;
        case '文件':
            uploadDocument();
            break;
        case '提及':
            insertMention();
            break;
        case '代码':
            insertCodeBlock();
            break;
        case '设置':
            openChatSettings();
            break;
        default:
            console.log('未知工具类型:', toolType);
    }
}

/**
 * 上传附件
 */
function uploadAttachment() {
    if (!currentWorkspaceId) {
        showError("请先选择一个工作区");
        return;
    }
    
    // 创建一个隐藏的文件输入元素
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '*/*'; // 接受所有类型的文件
    fileInput.style.display = 'none';
    
    // 添加到DOM并触发点击
    document.body.appendChild(fileInput);
    fileInput.click();
    
    // 监听文件选择事件
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            const file = this.files[0];
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('file', file);
            formData.append('workspace_id', currentWorkspaceId);
            
            // 上传文件
            $.ajax({
                url: '/api/ai_chat/upload_file',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.code === 200) {
                        showSuccess(`文件 "${file.name}" 上传成功`);
                        // 在输入框中添加文件引用
                        const chatInput = document.getElementById('chat-input');
                        chatInput.value += `[文件: ${file.name}] `;
                        chatInput.focus();
                    } else {
                        showError("上传文件失败：" + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    showError("请求失败：" + error);
                }
            });
        }
        
        // 移除临时元素
        document.body.removeChild(fileInput);
    });
}

/**
 * 上传文档
 */
function uploadDocument() {
    if (!currentWorkspaceId) {
        showError("请先选择一个工作区");
        return;
    }
    
    // 创建一个隐藏的文件输入元素
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.txt,.pdf,.doc,.docx,.md,.html'; // 接受文档类型的文件
    fileInput.style.display = 'none';
    
    // 添加到DOM并触发点击
    document.body.appendChild(fileInput);
    fileInput.click();
    
    // 监听文件选择事件
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            const file = this.files[0];
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('file', file);
            formData.append('workspace_id', currentWorkspaceId);
            
            // 上传文件
            $.ajax({
                url: '/api/ai_chat/upload_file',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.code === 200) {
                        showSuccess(`文档 "${file.name}" 上传成功`);
                        // 在输入框中添加文件引用
                        const chatInput = document.getElementById('chat-input');
                        chatInput.value += `[文档: ${file.name}] `;
                        chatInput.focus();
                    } else {
                        showError("上传文档失败：" + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    showError("请求失败：" + error);
                }
            });
        }
        
        // 移除临时元素
        document.body.removeChild(fileInput);
    });
}

/**
 * 插入@提及
 */
function insertMention() {
    const chatInput = document.getElementById('chat-input');
    const cursorPos = chatInput.selectionStart;
    const textBefore = chatInput.value.substring(0, cursorPos);
    const textAfter = chatInput.value.substring(cursorPos);
    
    chatInput.value = textBefore + '@' + textAfter;
    chatInput.focus();
    chatInput.selectionStart = chatInput.selectionEnd = cursorPos + 1;
}

/**
 * 插入代码块
 */
function insertCodeBlock() {
    const chatInput = document.getElementById('chat-input');
    const cursorPos = chatInput.selectionStart;
    const textBefore = chatInput.value.substring(0, cursorPos);
    const textAfter = chatInput.value.substring(cursorPos);
    
    const codeBlock = "```\n\n```";
    chatInput.value = textBefore + codeBlock + textAfter;
    chatInput.focus();
    chatInput.selectionStart = chatInput.selectionEnd = cursorPos + 4; // 将光标放在代码块中间
    
    // 调整文本框高度
    adjustTextareaHeight(chatInput);
}

/**
 * 打开聊天设置
 */
function openChatSettings() {
    const options = [
        "调整模型参数",
        "清空当前会话",
        "切换语言"
    ];
    
    const option = prompt(`请选择设置选项:\n1. ${options[0]}\n2. ${options[1]}\n3. ${options[2]}\n\n请输入选项编号(1-3):`);
    
    switch(option) {
        case "1":
            alert("模型参数设置功能尚未实现");
            break;
        case "2":
            if (confirm("确定要清空当前会话的所有消息吗？此操作不可撤销。")) {
                $("#chat-messages").html('<div class="welcome-message">会话已清空，可以开始新的对话了。</div>');
            }
            break;
        case "3":
            alert("语言切换功能尚未实现");
            break;
        default:
            // 取消或无效输入
            break;
    }
}

/**
 * 启动语音输入
 */
function startVoiceInput() {
    // 检查浏览器是否支持语音识别
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showError("您的浏览器不支持语音识别功能");
        return;
    }
    
    // 创建语音识别对象
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // 设置语音识别参数
    recognition.lang = 'zh-CN'; // 设置语言为中文
    recognition.continuous = false; // 不持续录音
    recognition.interimResults = false; // 不返回中间结果
    
    // 语音识别开始事件
    recognition.onstart = function() {
        $(".mic-button").css('color', '#007bff'); // 改变麦克风按钮颜色
        showSuccess("开始语音输入...");
    };
    
    // 语音识别结果事件
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const chatInput = document.getElementById('chat-input');
        chatInput.value += transcript;
        adjustTextareaHeight(chatInput);
    };
    
    // 语音识别结束事件
    recognition.onend = function() {
        $(".mic-button").css('color', ''); // 恢复麦克风按钮颜色
    };
    
    // 语音识别错误事件
    recognition.onerror = function(event) {
        showError("语音识别错误: " + event.error);
        $(".mic-button").css('color', ''); // 恢复麦克风按钮颜色
    };
    
    // 开始语音识别
    recognition.start();
}

/**
 * 工作区和会话数据
 */
let currentWorkspaceId = null;
let currentSessionId = null;

/**
 * 初始化工作区
 */
function initWorkspaces() {
    // 从服务器获取工作区数据
    $.ajax({
        url: '/api/ai_chat/workspaces',
        type: 'GET',
        success: function(response) {
            if (response.code === 200) {
                renderWorkspaceList(response.data.workspaces);
                
                // 如果有工作区，默认选择第一个
                if (response.data.workspaces && response.data.workspaces.length > 0) {
                    selectWorkspace(response.data.workspaces[0].id);
                } else {
                    // 如果没有工作区，创建一个默认工作区
                    createDefaultWorkspace();
                }
            } else {
                showError("获取工作区失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
            // 创建一个默认工作区作为备用
            createDefaultWorkspace();
        }
    });
}

/**
 * 创建默认工作区
 */
function createDefaultWorkspace() {
    $.ajax({
        url: '/api/ai_chat/workspaces',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ name: "默认工作区" }),
        success: function(response) {
            if (response.code === 200) {
                renderWorkspaceList([response.data.workspace]);
                selectWorkspace(response.data.workspace.id);
            } else {
                showError("创建默认工作区失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 渲染工作区列表
 * @param {Array} workspaces - 工作区数组
 */
function renderWorkspaceList(workspaces) {
    const $workspaceList = $("#workspace-list");
    $workspaceList.empty();
    
    workspaces.forEach(workspace => {
        const isActive = workspace.id === currentWorkspaceId;
        const workspaceItemHtml = `
            <div class="workspace-item ${isActive ? 'active' : ''}" data-id="${workspace.id}">
                <div class="workspace-name">${workspace.name}</div>
                <div class="workspace-actions">
                    <button class="workspace-action-btn upload-btn" title="上传文件" data-id="${workspace.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 15V3M12 3L7 8M12 3L17 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M3 15V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="workspace-action-btn settings-btn" title="设置" data-id="${workspace.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M19.4 15C19.1277 15.6171 19.2583 16.3378 19.73 16.82L19.79 16.88C20.1656 17.2551 20.3766 17.7642 20.3766 18.295C20.3766 18.8258 20.1656 19.3349 19.79 19.71C19.4149 20.0856 18.9058 20.2966 18.375 20.2966C17.8442 20.2966 17.3351 20.0856 16.96 19.71L16.9 19.65C16.4178 19.1783 15.6971 19.0477 15.08 19.32C14.4755 19.5791 14.0826 20.1724 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0677 20.2376 9.64778 19.6346 9.02 19.39C8.40274 19.1177 7.68207 19.2483 7.20001 19.72L7.14001 19.78C6.76488 20.1556 6.25583 20.3666 5.72501 20.3666C5.19419 20.3666 4.68514 20.1556 4.31 19.78C3.93439 19.4049 3.72339 18.8958 3.72339 18.365C3.72339 17.8342 3.93439 17.3251 4.31 16.95L4.37 16.89C4.84167 16.4078 4.97231 15.6871 4.7 15.07C4.44094 14.4655 3.84762 14.0726 3.19 14.07H3C2.46957 14.07 1.96086 13.8593 1.58579 13.4842C1.21071 13.1091 1 12.6004 1 12.07C1 11.5396 1.21071 11.0309 1.58579 10.6558C1.96086 10.2807 2.46957 10.07 3 10.07H3.09C3.76238 10.0577 4.36543 9.63775 4.61 9.01C4.88231 8.39274 4.75167 7.67206 4.28 7.19L4.22 7.13C3.84439 6.75486 3.63339 6.24581 3.63339 5.71499C3.63339 5.18417 3.84439 4.67512 4.22 4.29999C4.59513 3.92438 5.10418 3.71338 5.635 3.71338C6.16582 3.71338 6.67487 3.92438 7.05 4.29999L7.11 4.35999C7.59207 4.83166 8.31275 4.9623 8.93 4.68999H9C9.60455 4.43093 9.99744 3.83761 10 3.17999V2.99999C10 2.46956 10.2107 1.96085 10.5858 1.58578C10.9609 1.2107 11.4696 0.999992 12 0.999992C12.5304 0.999992 13.0391 1.2107 13.4142 1.58578C13.7893 1.96085 14 2.46956 14 2.99999V3.08999C14.0026 3.74761 14.3955 4.34093 15 4.59999C15.6173 4.8723 16.3379 4.74167 16.82 4.26999L16.88 4.20999C17.2551 3.83438 17.7642 3.62338 18.295 3.62338C18.8258 3.62338 19.3349 3.83438 19.71 4.20999C20.0856 4.58512 20.2966 5.09417 20.2966 5.62499C20.2966 6.15581 20.0856 6.66486 19.71 7.03999L19.65 7.09999C19.1783 7.58207 19.0477 8.30275 19.32 8.91999V8.99999C19.5791 9.60455 20.1724 9.99744 20.83 9.99999H21C21.5304 9.99999 22.0391 10.2107 22.4142 10.5858C22.7893 10.9609 23 11.4696 23 12C23 12.5304 22.7893 13.0391 22.4142 13.4142C22.0391 13.7893 21.5304 14 21 14H20.91C20.2524 14.0026 19.6591 14.3955 19.4 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        $workspaceList.append(workspaceItemHtml);
    });
    
    // 绑定工作区点击事件
    $(".workspace-item").on("click", function(e) {
        const workspaceId = $(this).data("id");
        selectWorkspace(workspaceId);
    });
    
    // 绑定上传按钮点击事件
    $(".upload-btn").on("click", function(e) {
        e.stopPropagation();
        const workspaceId = $(this).data("id");
        uploadFileToWorkspace(workspaceId);
    });
    
    // 绑定设置按钮点击事件
    $(".settings-btn").on("click", function(e) {
        e.stopPropagation();
        const workspaceId = $(this).data("id");
        openWorkspaceSettings(workspaceId);
    });
}

/**
 * 上传文件到工作区
 * @param {string} workspaceId - 工作区ID
 */
function uploadFileToWorkspace(workspaceId) {
    // 创建一个隐藏的文件输入元素
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.txt,.pdf,.doc,.docx';
    fileInput.style.display = 'none';
    
    // 添加到DOM并触发点击
    document.body.appendChild(fileInput);
    fileInput.click();
    
    // 监听文件选择事件
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            const file = this.files[0];
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('file', file);
            formData.append('workspace_id', workspaceId);
            
            // 上传文件
            $.ajax({
                url: '/api/ai_chat/upload_file',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.code === 200) {
                        showSuccess(`文件 "${file.name}" 上传成功`);
                    } else {
                        showError("上传文件失败：" + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    showError("请求失败：" + error);
                }
            });
        }
        
        // 移除临时元素
        document.body.removeChild(fileInput);
    });
}

/**
 * 选择工作区
 * @param {string} workspaceId - 工作区ID
 */
function selectWorkspace(workspaceId) {
    currentWorkspaceId = workspaceId;
    
    // 更新工作区列表的活动状态
    $(".workspace-item").removeClass("active");
    $(`.workspace-item[data-id="${workspaceId}"]`).addClass("active");
    
    // 获取工作区的会话列表
    $.ajax({
        url: `/api/ai_chat/workspaces/${workspaceId}/sessions`,
        type: 'GET',
        success: function(response) {
            if (response.code === 200) {
                const sessions = response.data.sessions;
                
                // 如果有会话，选择第一个
                if (sessions && sessions.length > 0) {
                    selectSession(workspaceId, sessions[0].id);
                } else {
                    // 如果没有会话，创建一个新会话
                    createNewSession(workspaceId, "新会话");
                }
            } else {
                showError("获取会话列表失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 选择会话
 * @param {string} workspaceId - 工作区ID
 * @param {string} sessionId - 会话ID
 */
function selectSession(workspaceId, sessionId) {
    currentWorkspaceId = workspaceId;
    currentSessionId = sessionId;
    
    // 加载会话消息
    $.ajax({
        url: `/api/ai_chat/workspaces/${workspaceId}/sessions/${sessionId}/messages`,
        type: 'GET',
        success: function(response) {
            if (response.code === 200) {
                const messages = response.data.messages;
                
                // 清空聊天消息区域
                $("#chat-messages").empty();
                
                // 如果没有消息，显示欢迎信息
                if (!messages || messages.length === 0) {
                    $("#chat-messages").html('<div class="welcome-message">开始一个新的对话吧！</div>');
                    return;
                }
                
                // 显示会话的消息
                messages.forEach(msg => {
                    appendMessage(msg.sender, msg.content, false);
                });
                
                // 滚动到底部
                scrollToBottom();
            } else {
                showError("加载会话消息失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 添加新工作区
 */
function addNewWorkspace() {
    const workspaceName = prompt("请输入工作区名称：", "新工作区");
    
    if (!workspaceName) {
        return;
    }
    
    $.ajax({
        url: '/api/ai_chat/workspaces',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ name: workspaceName }),
        success: function(response) {
            if (response.code === 200) {
                // 获取最新的工作区列表
                initWorkspaces();
                
                // 选择新创建的工作区
                selectWorkspace(response.data.workspace.id);
            } else {
                showError("创建工作区失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 创建新会话
 * @param {string} workspaceId - 工作区ID
 * @param {string} sessionName - 会话名称
 */
function createNewSession(workspaceId, sessionName) {
    $.ajax({
        url: `/api/ai_chat/workspaces/${workspaceId}/sessions`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ name: sessionName }),
        success: function(response) {
            if (response.code === 200) {
                // 选择新创建的会话
                selectSession(workspaceId, response.data.session.id);
            } else {
                showError("创建会话失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 打开工作区设置
 * @param {string} workspaceId - 工作区ID
 */
function openWorkspaceSettings(workspaceId) {
    // 创建设置选项
    const options = [
        "重命名工作区",
        "新建会话",
        "删除工作区"
    ];
    
    // 显示选项
    const option = prompt(`请选择操作:\n1. ${options[0]}\n2. ${options[1]}\n3. ${options[2]}\n\n请输入选项编号(1-3):`);
    
    switch(option) {
        case "1":
            // 重命名工作区
            renameWorkspace(workspaceId);
            break;
        case "2":
            // 新建会话
            const sessionName = prompt("请输入会话名称：", "新会话");
            if (sessionName) {
                createNewSession(workspaceId, sessionName);
            }
            break;
        case "3":
            // 删除工作区
            deleteWorkspace(workspaceId);
            break;
        default:
            // 取消或无效输入
            break;
    }
}

/**
 * 重命名工作区
 * @param {string} workspaceId - 工作区ID
 */
function renameWorkspace(workspaceId) {
    // 获取当前工作区名称
    const currentName = $(`.workspace-item[data-id="${workspaceId}"] .workspace-name`).text();
    
    const newName = prompt("请输入工作区名称：", currentName);
    
    if (!newName || newName === currentName) {
        return;
    }
    
    $.ajax({
        url: `/api/ai_chat/workspaces/${workspaceId}`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({ name: newName }),
        success: function(response) {
            if (response.code === 200) {
                // 更新工作区名称
                $(`.workspace-item[data-id="${workspaceId}"] .workspace-name`).text(newName);
            } else {
                showError("重命名工作区失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 删除工作区
 * @param {string} workspaceId - 工作区ID
 */
function deleteWorkspace(workspaceId) {
    // 获取工作区数量
    const workspaceCount = $(".workspace-item").length;
    
    // 不允许删除最后一个工作区
    if (workspaceCount <= 1) {
        alert("至少需要保留一个工作区！");
        return;
    }
    
    if (!confirm("确定要删除此工作区吗？删除后将无法恢复，包括所有会话和消息。")) {
        return;
    }
    
    $.ajax({
        url: `/api/ai_chat/workspaces/${workspaceId}`,
        type: 'DELETE',
        success: function(response) {
            if (response.code === 200) {
                // 重新加载工作区列表
                initWorkspaces();
            } else {
                showError("删除工作区失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            showError("请求失败：" + error);
        }
    });
}

/**
 * 发送消息
 */
function sendMessage() {
    const messageInput = $("#chat-input");
    const message = messageInput.val().trim();
    
    if (!message || !currentWorkspaceId || !currentSessionId) {
        return;
    }
    
    // 显示用户消息
    appendMessage("user", message);
    
    // 清空输入框
    messageInput.val("").focus();
    
    // 重置输入框高度
    messageInput[0].style.height = '24px';
    
    // 显示"AI正在思考"的提示
    const loadingId = showLoadingMessage();
    
    // 调用AI聊天API
    $.ajax({
        url: `/api/ai_chat/workspaces/${currentWorkspaceId}/sessions/${currentSessionId}/messages`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 
            content: message,
            sender: "user"
        }),
        success: function(response) {
            if (response.code === 200) {
                // 调用AI回复API
                getAIReply(message, loadingId);
            } else {
                // 移除加载提示
                removeLoadingMessage(loadingId);
                
                // 显示错误消息
                showError("发送消息失败：" + response.message);
            }
        },
        error: function(xhr, status, error) {
            // 移除加载提示
            removeLoadingMessage(loadingId);
            
            // 显示错误消息
            showError("请求失败：" + error);
        }
    });
}

/**
 * 获取AI回复
 * @param {string} userMessage - 用户消息
 * @param {string} loadingId - 加载提示的ID
 */
function getAIReply(userMessage, loadingId) {
    $.ajax({
        url: '/api/ai_chat/get_ai_reply',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 
            message: userMessage,
            workspace_id: currentWorkspaceId,
            session_id: currentSessionId
        }),
        success: function(response) {
            // 移除加载提示
            removeLoadingMessage(loadingId);
            
            if (response.code === 200) {
                // 显示AI回复
                const reply = response.data.reply;
                appendMessage("ai", reply);
                
                // 保存AI回复到会话
                saveAIReply(reply);
            } else {
                // 显示错误消息
                const errorMsg = "抱歉，发生了错误：" + response.message;
                appendMessage("ai", errorMsg);
            }
        },
        error: function(xhr, status, error) {
            // 移除加载提示
            removeLoadingMessage(loadingId);
            
            // 显示错误消息
            const errorMsg = "抱歉，请求失败：" + error;
            appendMessage("ai", errorMsg);
        }
    });
}

/**
 * 保存AI回复到会话
 * @param {string} reply - AI回复内容
 */
function saveAIReply(reply) {
    $.ajax({
        url: `/api/ai_chat/workspaces/${currentWorkspaceId}/sessions/${currentSessionId}/messages`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 
            content: reply,
            sender: "ai"
        }),
        error: function(xhr, status, error) {
            console.error("保存AI回复失败：", error);
        }
    });
}

/**
 * 添加消息到聊天窗口
 * @param {string} sender - 发送者类型：'user' 或 'ai'
 * @param {string} message - 消息内容
 * @param {boolean} scroll - 是否滚动到底部，默认为true
 */
function appendMessage(sender, message, scroll = true) {
    const messageClass = sender === "user" ? "user-message" : "ai-message";
    const senderName = sender === "user" ? "你" : "AI";
    
    const messageHtml = `
        <div class="message-container" data-sender="${senderName}">
            <div class="${messageClass}">${message}</div>
        </div>
    `;
    
    $("#chat-messages").append(messageHtml);
    
    // 滚动到底部
    if (scroll) {
        scrollToBottom();
    }
}

/**
 * 显示加载中消息
 * @returns {string} 加载消息的唯一ID
 */
function showLoadingMessage() {
    const loadingId = "loading-" + Date.now();
    const loadingHtml = `
        <div id="${loadingId}" class="message-container" data-sender="AI">
            <div class="ai-message">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    $("#chat-messages").append(loadingHtml);
    
    // 滚动到底部
    scrollToBottom();
    
    return loadingId;
}

/**
 * 移除加载中消息
 * @param {string} loadingId - 加载消息的唯一ID
 */
function removeLoadingMessage(loadingId) {
    $(`#${loadingId}`).remove();
}

/**
 * 滚动聊天窗口到底部
 */
function scrollToBottom() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * 显示错误消息
 * @param {string} message - 错误消息
 */
function showError(message) {
    alert(message);
}

/**
 * 显示成功消息
 * @param {string} message - 成功消息
 */
function showSuccess(message) {
    alert(message);
} 