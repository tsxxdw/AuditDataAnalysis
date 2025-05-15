// SQL页面的JavaScript
$(document).ready(function() {
    console.log("常用SQL页面已加载");
    
    // 初始化变量
    let sqlData = {};
    
    // 从配置文件加载SQL数据
    $.ajax({
        url: '/static/js/config/sql_config.json',
        dataType: 'json',
        async: false, // 同步加载，确保数据先加载完
        success: function(data) {
            console.log("SQL配置加载成功");
            sqlData = data;
        },
        error: function(xhr, status, error) {
            console.error("SQL配置加载失败:", error);
            // 如果配置加载失败，可以显示错误信息
            $('.sql-category-container').html('<div class="error-message">SQL配置加载失败，请刷新页面重试。</div>');
        }
    });
    
    // 初始化页面
    initializePage();
    
    // 初始化数据库类型切换
    initDbTypeSelector();
    
    // 初始化模态框
    initModal();
    
    // 初始化页面，生成SQL卡片
    function initializePage() {
        const $container = $('.sql-category-container');
        $container.empty(); // 清空现有内容
        
        // 遍历每个分类创建大卡片
        for (const category in sqlData) {
            const $categoryCard = createCategoryCard(category, sqlData[category]);
            $container.append($categoryCard);
        }
        
        // 初始化SQL卡片事件
        initSqlCards();
    }
    
    // 创建分类卡片
    function createCategoryCard(categoryName, items) {
        const $card = $(`
            <div class="category-card">
                <div class="category-header">
                    <h2 class="category-title">${categoryName}</h2>
                </div>
                <div class="sql-card-grid"></div>
            </div>
        `);
        
        const $grid = $card.find('.sql-card-grid');
        
        // 创建每个SQL卡片
        items.forEach(item => {
            const $sqlCard = createSqlCard(item);
            $grid.append($sqlCard);
        });
        
        return $card;
    }
    
    // 创建单个SQL卡片
    function createSqlCard(item) {
        const $card = $(`
            <div class="sql-card" data-db-type="${item.dbType}">
                <div class="sql-card-content">
                    <h3 class="sql-title">${item.title}</h3>
                    <p class="sql-desc">${item.desc}</p>
                </div>
                ${item.verified ? '<div class="verified-badge"></div>' : ''}
            </div>
        `);
        
        // 添加SQL内容（隐藏）
        if (item.sql.common) {
            $card.append(`<div class="hidden-sql">${item.sql.common}</div>`);
        }
        
        // 添加特定数据库的SQL
        for (const dbType in item.sql) {
            if (dbType !== 'common') {
                $card.append(`<div class="hidden-sql ${dbType}">${item.sql[dbType]}</div>`);
            }
        }
        
        return $card;
    }
    
    // 初始化数据库类型选择器
    function initDbTypeSelector() {
        // 数据库类型切换事件
        $('#dbType').on('change', function() {
            const selectedDbType = $(this).val();
            console.log('切换数据库类型为:', selectedDbType);
            
            // 处理验证标记的显示/隐藏
            $('.verified-badge').toggle(selectedDbType === 'mysql');
            
            // 遍历所有SQL卡片
            $('.sql-card').each(function() {
                const $card = $(this);
                const supportedDbTypes = $card.data('db-type') ? $card.data('db-type').split(' ') : [];
                
                // 检查此卡片是否支持选中的数据库类型
                if (supportedDbTypes.includes(selectedDbType)) {
                    $card.show();
                } else if (supportedDbTypes.length === 0 || supportedDbTypes.includes('all')) {
                    // 如果没有指定支持的数据库类型，或支持所有类型，则显示卡片
                    $card.show();
                } else {
                    // 不支持当前选中的数据库类型，隐藏卡片
                    $card.hide();
                }
            });
        });
        
        // 初始触发一次change事件，设置初始状态
        $('#dbType').trigger('change');
    }
    
    // 初始化SQL卡片
    function initSqlCards() {
        // 添加卡片点击事件
        $('.sql-card').on('click', function() {
            const $card = $(this);
            const sqlTitle = $card.find('.sql-title').text();
            const sqlDesc = $card.find('.sql-desc').text();
            const dbType = $('#dbType').val();
            
            // 获取对应数据库类型的SQL
            let sqlContent = '';
            const $dbSpecificSql = $card.find(`.hidden-sql.${dbType}`);
            
            if ($dbSpecificSql.length > 0) {
                // 如果有特定数据库类型的SQL
                sqlContent = $dbSpecificSql.text();
            } else {
                // 否则使用通用SQL
                sqlContent = $card.find('.hidden-sql').first().text();
            }
            
            // 显示SQL在模态框中
            showSqlInModal(sqlTitle, sqlDesc, sqlContent);
        });
        
        // 添加卡片悬停动画效果
        $('.sql-card').hover(
            function() {
                $(this).addClass('sql-card-hover');
            },
            function() {
                $(this).removeClass('sql-card-hover');
            }
        );
    }
    
    // 初始化模态框
    function initModal() {
        // 关闭模态框的事件
        $('.close-modal').on('click', function() {
            $('#sqlModal').hide();
        });
        
        // 点击模态框外部关闭
        $(window).on('click', function(event) {
            if ($(event.target).is('#sqlModal')) {
                $('#sqlModal').hide();
            }
        });
        
        // ESC键关闭模态框
        $(document).on('keydown', function(event) {
            if (event.key === 'Escape' && $('#sqlModal').is(':visible')) {
                $('#sqlModal').hide();
            }
        });
        
        // 模态框中的复制按钮
        $('#modalCopyBtn').on('click', function() {
            const sqlText = $('#modalSqlContent').text();
            const $button = $(this);
            
            copyToClipboard(sqlText, function(success) {
                if (success) {
                    $button.addClass('copied').text('已复制!');
                    
                    setTimeout(function() {
                        $button.removeClass('copied').text('复制SQL');
                    }, 2000);
                } else {
                    $button.text('复制失败');
                    setTimeout(function() {
                        $button.text('复制SQL');
                    }, 2000);
                }
            });
        });
    }
    
    // 在模态框中显示SQL
    function showSqlInModal(title, desc, sqlContent) {
        // 更新模态框标题和内容
        const modalTitle = desc ? `${title} (${desc})` : title;
        $('.modal-title').text(modalTitle);
        $('#modalSqlContent').text(sqlContent);
        
        // 显示模态框
        $('#sqlModal').css('display', 'flex');
    }
    
    // 复制文本到剪贴板的函数
    function copyToClipboard(text, callback) {
        // 现代浏览器使用 Clipboard API
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text)
                .then(() => callback(true))
                .catch(() => {
                    // 如果Clipboard API失败，回退到传统方法
                    fallbackCopyToClipboard(text, callback);
                });
        } else {
            // 对于不支持Clipboard API的浏览器，使用传统方法
            fallbackCopyToClipboard(text, callback);
        }
    }
    
    // 传统复制方法（创建临时文本区域）
    function fallbackCopyToClipboard(text, callback) {
        try {
            // 创建临时textarea元素
            const textarea = document.createElement('textarea');
            textarea.value = text;
            
            // 设置样式使其不可见
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            
            document.body.appendChild(textarea);
            
            // 选择并复制
            textarea.select();
            const success = document.execCommand('copy');
            
            // 清理
            document.body.removeChild(textarea);
            
            callback(success);
        } catch (err) {
            console.error('复制失败:', err);
            callback(false);
        }
    }
});