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
 * 工作区数据
 */
let workspaces = [];
let currentWorkspaceId = null;

/**
 * 初始化工作区
 */
function initWorkspaces() {
    // 从本地存储加载工作区数据
    const savedWorkspaces = localStorage.getItem('ai_chat_workspaces');
    
    if (savedWorkspaces) {
        workspaces = JSON.parse(savedWorkspaces);
    }
    
    // 如果没有工作区，创建一个默认工作区
    if (workspaces.length === 0) {
        const defaultWorkspace = {
            id: generateId(),
            name: "默认对话",
            messages: []
        };
        
        workspaces.push(defaultWorkspace);
        saveWorkspaces();
    }
    
    // 渲染工作区列表
    renderWorkspaceList();
    
    // 默认选择第一个工作区
    selectWorkspace(workspaces[0].id);
}

/**
 * 渲染工作区列表
 */
function renderWorkspaceList() {
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
            // 这里只是显示一个消息，实际上传功能需要后端支持
            alert(`已选择文件: ${file.name}。此功能需要后端支持，暂未实现。`);
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
    
    // 加载工作区的聊天记录
    loadWorkspaceMessages(workspaceId);
}

/**
 * 加载工作区的聊天记录
 * @param {string} workspaceId - 工作区ID
 */
function loadWorkspaceMessages(workspaceId) {
    const workspace = workspaces.find(w => w.id === workspaceId);
    
    if (!workspace) {
        return;
    }
    
    // 清空聊天消息区域
    $("#chat-messages").empty();
    
    // 如果没有消息，显示欢迎信息
    if (workspace.messages.length === 0) {
        $("#chat-messages").html('<div class="welcome-message">开始一个新的对话吧！</div>');
        return;
    }
    
    // 显示工作区的消息
    workspace.messages.forEach(msg => {
        appendMessage(msg.sender, msg.content, false);
    });
    
    // 滚动到底部
    scrollToBottom();
}

/**
 * 添加新工作区
 */
function addNewWorkspace() {
    const workspaceName = prompt("请输入对话名称：", "新对话");
    
    if (!workspaceName) {
        return;
    }
    
    const newWorkspace = {
        id: generateId(),
        name: workspaceName,
        messages: []
    };
    
    workspaces.push(newWorkspace);
    saveWorkspaces();
    
    // 重新渲染工作区列表
    renderWorkspaceList();
    
    // 选择新创建的工作区
    selectWorkspace(newWorkspace.id);
}

/**
 * 打开工作区设置
 * @param {string} workspaceId - 工作区ID
 */
function openWorkspaceSettings(workspaceId) {
    const workspace = workspaces.find(w => w.id === workspaceId);
    
    if (!workspace) {
        return;
    }
    
    // 创建设置选项
    const options = [
        "重命名对话",
        "清空聊天记录",
        "删除对话"
    ];
    
    // 显示选项
    const option = prompt(`请选择操作:\n1. ${options[0]}\n2. ${options[1]}\n3. ${options[2]}\n\n请输入选项编号(1-3):`);
    
    switch(option) {
        case "1":
            // 重命名工作区
            renameWorkspace(workspaceId);
            break;
        case "2":
            // 清空聊天记录
            clearWorkspaceMessages(workspaceId);
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
    const workspace = workspaces.find(w => w.id === workspaceId);
    
    if (!workspace) {
        return;
    }
    
    const newName = prompt("请输入对话名称：", workspace.name);
    
    if (!newName || newName === workspace.name) {
        return;
    }
    
    workspace.name = newName;
    saveWorkspaces();
    
    // 重新渲染工作区列表
    renderWorkspaceList();
}

/**
 * 清空工作区消息
 * @param {string} workspaceId - 工作区ID
 */
function clearWorkspaceMessages(workspaceId) {
    const workspace = workspaces.find(w => w.id === workspaceId);
    
    if (!workspace) {
        return;
    }
    
    if (!confirm("确定要清空此对话的所有聊天记录吗？此操作不可撤销。")) {
        return;
    }
    
    workspace.messages = [];
    saveWorkspaces();
    
    // 如果是当前工作区，重新加载消息
    if (workspaceId === currentWorkspaceId) {
        loadWorkspaceMessages(workspaceId);
    }
}

/**
 * 删除工作区
 * @param {string} workspaceId - 工作区ID
 */
function deleteWorkspace(workspaceId) {
    // 不允许删除最后一个工作区
    if (workspaces.length <= 1) {
        alert("至少需要保留一个对话！");
        return;
    }
    
    if (!confirm("确定要删除此对话吗？删除后将无法恢复。")) {
        return;
    }
    
    // 找到工作区索引
    const index = workspaces.findIndex(w => w.id === workspaceId);
    
    if (index === -1) {
        return;
    }
    
    // 删除工作区
    workspaces.splice(index, 1);
    saveWorkspaces();
    
    // 如果删除的是当前选中的工作区，则选择第一个工作区
    if (workspaceId === currentWorkspaceId) {
        selectWorkspace(workspaces[0].id);
    }
    
    // 重新渲染工作区列表
    renderWorkspaceList();
}

/**
 * 保存工作区数据到本地存储
 */
function saveWorkspaces() {
    localStorage.setItem('ai_chat_workspaces', JSON.stringify(workspaces));
}

/**
 * 生成唯一ID
 * @returns {string} 唯一ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

/**
 * 发送消息
 */
function sendMessage() {
    const messageInput = $("#chat-input");
    const message = messageInput.val().trim();
    
    if (!message || !currentWorkspaceId) {
        return;
    }
    
    // 显示用户消息
    appendMessage("user", message);
    
    // 保存消息到工作区
    saveMessage("user", message);
    
    // 清空输入框
    messageInput.val("").focus();
    
    // 重置输入框高度
    messageInput[0].style.height = '24px';
    
    // 显示"AI正在思考"的提示
    const loadingId = showLoadingMessage();
    
    // 调用AI聊天API
    $.ajax({
        url: '/api/ai_chat/send_message',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 
            message: message,
            workspace_id: currentWorkspaceId
        }),
        success: function(response) {
            // 移除加载提示
            removeLoadingMessage(loadingId);
            
            if (response.code === 200) {
                // 显示AI回复
                const reply = response.data.reply;
                appendMessage("ai", reply);
                
                // 保存消息到工作区
                saveMessage("ai", reply);
            } else {
                // 显示错误消息
                const errorMsg = "抱歉，发生了错误：" + response.message;
                appendMessage("ai", errorMsg);
                
                // 保存消息到工作区
                saveMessage("ai", errorMsg);
            }
        },
        error: function(xhr, status, error) {
            // 移除加载提示
            removeLoadingMessage(loadingId);
            
            // 显示错误消息
            const errorMsg = "抱歉，请求失败：" + error;
            appendMessage("ai", errorMsg);
            
            // 保存消息到工作区
            saveMessage("ai", errorMsg);
        }
    });
}

/**
 * 保存消息到当前工作区
 * @param {string} sender - 发送者类型：'user' 或 'ai'
 * @param {string} content - 消息内容
 */
function saveMessage(sender, content) {
    const workspace = workspaces.find(w => w.id === currentWorkspaceId);
    
    if (!workspace) {
        return;
    }
    
    workspace.messages.push({
        id: generateId(),
        sender: sender,
        content: content,
        timestamp: new Date().getTime()
    });
    
    saveWorkspaces();
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