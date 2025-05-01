// 文件上传页面JS文件
$(document).ready(function() {
    // DOM元素
    const dropZone = $('#dropZone');
    const fileInput = $('#fileInput');
    const browseBtn = $('#browseBtn');
    const uploadStatus = $('#uploadStatus');
    const filesList = $('#filesList');
    
    // 初始化
    loadFileList();
    
    // 浏览按钮点击事件
    browseBtn.click(function() {
        fileInput.click();
    });
    
    // 文件选择事件
    fileInput.change(function() {
        const files = this.files;
        if (files.length > 0) {
            uploadFiles(files);
            // 重置文件输入框，以便可以再次选择相同的文件
            $(this).val('');
        }
    });
    
    // 拖放相关事件
    dropZone.on('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragover');
    });
    
    dropZone.on('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
    });
    
    dropZone.on('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragover');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            uploadFiles(files);
            // 确保拖放区域可以再次接收文件
            fileInput.val('');
        }
    });
    
    // 文件上传函数
    function uploadFiles(files) {
        // 显示上传状态区域
        uploadStatus.show();
        $('#statusText').text('正在上传文件: ' + files[0].name);
        
        // 创建FormData对象
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        // 发送上传请求
        $.ajax({
            url: '/api/files/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // 显示上传成功状态
                $('#statusText').text('上传成功!');
                
                // 短暂延迟后隐藏状态并刷新列表
                setTimeout(function() {
                    uploadStatus.hide();
                    $('#fileInfo').text(''); // 清空文件信息
                    loadFileList(); // 刷新文件列表
                }, 1000);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('上传失败:', errorThrown);
                $('#statusText').text('上传失败: ' + errorThrown);
                
                setTimeout(function() {
                    uploadStatus.hide();
                    fileInput.val(''); // 确保错误后也重置文件输入框
                }, 2000);
            }
        });
    }
    
    // 加载文件列表
    function loadFileList() {
        $.ajax({
            url: '/api/files/list',
            type: 'GET',
            success: function(response) {
                // 清空列表
                filesList.empty();
                
                // 如果没有文件
                if (!response || response.length === 0) {
                    filesList.html('<tr><td colspan="4" class="loading-text">暂无上传文件</td></tr>');
                    return;
                }
                
                // 添加文件到列表
                $.each(response, function(index, file) {
                    const row = $('<tr></tr>');
                    
                    // 文件名(带链接)
                    const nameCell = $('<td></td>');
                    const link = $('<a></a>')
                        .attr('href', file.url)
                        .attr('target', '_blank')
                        .text(file.name);
                    nameCell.append(link);
                    
                    // 文件大小
                    const sizeCell = $('<td></td>').text(formatFileSize(file.size));
                    
                    // 上传日期
                    const dateCell = $('<td></td>').text(file.date);
                    
                    // 操作按钮
                    const actionCell = $('<td></td>');
                    const deleteBtn = $('<button></button>')
                        .addClass('delete-btn')
                        .text('删除')
                        .data('file-path', file.path)
                        .click(function() {
                            deleteFile($(this).data('file-path'));
                        });
                    actionCell.append(deleteBtn);
                    
                    // 添加单元格到行
                    row.append(nameCell, sizeCell, dateCell, actionCell);
                    
                    // 添加行到表格
                    filesList.append(row);
                });
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('获取文件列表失败:', errorThrown);
                filesList.html('<tr><td colspan="4" class="loading-text">获取文件列表失败</td></tr>');
            }
        });
    }
    
    // 删除文件
    function deleteFile(filePath) {
        if (confirm('确定要删除此文件吗？')) {
            $.ajax({
                url: '/api/files/delete',
                type: 'POST',
                data: JSON.stringify({ path: filePath }),
                contentType: 'application/json',
                success: function(response) {
                    // 刷新文件列表
                    loadFileList();
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error('删除文件失败:', errorThrown);
                    alert('删除文件失败: ' + errorThrown);
                }
            });
        }
    }
    
    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        
        return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
    }
}); 