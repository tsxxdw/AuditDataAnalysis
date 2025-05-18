/**
 * SQL执行区域组件
 * 提供SQL执行和结果显示功能
 */
class SqlExecuteArea {
    /**
     * 构造函数
     * @param {Object} options - 配置选项
     * @param {string} options.apiEndpoint - SQL执行的API端点
     * @param {Function} options.onGenerateSQL - 生成SQL按钮点击事件的回调函数
     * @param {Function} options.onSuccess - SQL执行成功的回调函数
     * @param {Function} options.onError - SQL执行失败的回调函数
     */
    constructor(options = {}) {
        this.options = $.extend({
            apiEndpoint: '/api/common/execute_sql', // 默认API端点
            onGenerateSQL: null,
            onSuccess: null,
            onError: null
        }, options);

        this.initEventListeners();
    }

    /**
     * 初始化事件监听
     */
    initEventListeners() {
        // 执行SQL按钮点击事件
        $('#executeSql').on('click', (e) => this.executeSQL(e));
        
        // 清空SQL按钮点击事件
        $('#clearSql').on('click', (e) => this.clearSQL(e));
        
        // 生成SQL按钮点击事件
        $('#generateSql').on('click', (e) => {
            if ($.isFunction(this.options.onGenerateSQL)) {
                this.options.onGenerateSQL(e);
            }
        });
        
        // 标签切换委托事件
        $(document).on('click', '.result-tab', (e) => {
            const tabIndex = $(e.currentTarget).data('tab-index');
            this.switchResultTab(tabIndex);
        });
    }

    /**
     * 执行SQL
     * @param {Event} e - 事件对象
     */
    executeSQL(e) {
        const sql = $('#sqlContent').val();
        
        if(!sql || $.trim(sql) === '') {
            alert('请先生成或输入SQL语句');
            return;
        }
        
        // 显示加载中提示
        this.showLoading();
        
        // 调用后端API执行SQL
        $.ajax({
            url: this.options.apiEndpoint,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sql: sql
            }),
            success: (response) => {
                // 无论成功失败，都使用displayResults方法显示结果
                this.displayResults(response);
                
                // 调用回调函数
                if (response.success) {
                    if ($.isFunction(this.options.onSuccess)) {
                        this.options.onSuccess(response);
                    }
                } else {
                    if ($.isFunction(this.options.onError)) {
                        this.options.onError(response);
                    }
                }
            },
            error: (xhr) => {
                console.error('执行SQL请求失败:', xhr);
                // 构造一个类似正常响应的对象，以便使用displayResults方法显示
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '请求失败，请查看控制台日志';
                const errorDetail = xhr.responseText || '无法获取详细错误信息';
                
                this.displayResults({
                    success: false,
                    message: `执行SQL请求失败: ${errorMsg}`,
                    error_occurred: true,
                    results: [{
                        sql_index: 1,
                        sql: $('#sqlContent').val(), 
                        success: false,
                        is_query: false,
                        message: `执行SQL请求失败: ${errorMsg}`,
                        error_detail: errorDetail
                    }]
                });
                
                // 如果提供了错误回调，则调用
                if ($.isFunction(this.options.onError)) {
                    this.options.onError(xhr);
                }
            },
            complete: () => {
                this.hideLoading();
            }
        });
    }
    
    /**
     * 显示加载中提示
     */
    showLoading() {
        const $resultSection = $('.sql-result-section');
        
        // 如果结果区域不存在或已显示，则创建并显示加载提示
        if (!$resultSection.is(':visible')) {
            $resultSection.show();
            $('#sqlResultContent').html(
                $('<div>').addClass('loading-message')
                          .text('正在执行SQL...')
            );
        } else {
            // 在已有结果上显示加载层
            $('#sqlResultContent').append(
                $('<div>').addClass('loading-overlay')
                          .html($('<div>').addClass('loading-spinner'))
            );
        }
    }
    
    /**
     * 隐藏加载提示
     */
    hideLoading() {
        $('.loading-overlay').remove();
    }

    /**
     * 清空SQL
     * @param {Event} e - 事件对象
     */
    clearSQL(e) {
        $('#sqlContent').val('');
        // 隐藏结果区域
        $('.sql-result-section').hide();
    }

    /**
     * 设置SQL内容
     * @param {string} sql - SQL语句
     */
    setSQL(sql) {
        $('#sqlContent').val(sql);
    }

    /**
     * 获取SQL内容
     * @returns {string} SQL语句
     */
    getSQL() {
        return $('#sqlContent').val();
    }
    
    /**
     * 切换结果标签页
     * @param {number} tabIndex - 标签索引
     */
    switchResultTab(tabIndex) {
        // 切换标签页激活状态
        $('.result-tab').removeClass('active');
        $(`.result-tab[data-tab-index="${tabIndex}"]`).addClass('active');
        
        // 切换内容区域
        $('.result-content-panel').hide();
        $(`.result-content-panel[data-panel-index="${tabIndex}"]`).show();
    }
    
    /**
     * 显示执行结果
     * @param {Object} response - API响应对象
     */
    displayResults(response) {
        // 显示结果区域
        $('.sql-result-section').show();
        
        // 创建结果容器
        const $resultContent = $('#sqlResultContent');
        $resultContent.empty();
        
        if (!response.results || response.results.length === 0) {
            // 没有任何结果
            $resultContent.html(
                $('<div>').addClass('no-result-message')
                          .text('SQL执行完成，但未返回任何结果')
            );
            return;
        }
        
        // 创建标签页容器
        const $tabsContainer = $('<div>').addClass('result-tabs-container');
        const $contentContainer = $('<div>').addClass('result-content-container');
        
        // 添加到结果区域
        $resultContent.append($tabsContainer).append($contentContainer);
        
        // 创建各个标签页和内容区
        $.each(response.results, function(i, result) {
            const tabIndex = i + 1;
            const isActive = i === 0; // 默认第一个标签激活
            
            // 创建标签页
            const $tab = $('<div>')
                .addClass('result-tab')
                .addClass(isActive ? 'active' : '')
                .attr('data-tab-index', tabIndex)
                .html(`
                    <span class="tab-number">${tabIndex}</span>
                    <span class="tab-status ${result.success ? 'success' : (result.not_executed ? 'pending' : 'error')}">
                        ${result.success ? '✓' : (result.not_executed ? '⦸' : '✗')}
                    </span>
                `);
            
            // 创建内容区
            const $panel = $('<div>')
                .addClass('result-content-panel')
                .attr('data-panel-index', tabIndex)
                .css('display', isActive ? 'block' : 'none');
            
            // 添加SQL语句预览
            if (result.sql) {
                $panel.append(
                    $('<div>').addClass('sql-preview')
                              .html(`<pre>${result.sql}</pre>`)
                );
            }
            
            // 根据结果类型显示不同内容
            if (result.success) {
                if (result.is_query) {
                    // 查询结果
                    $panel.append(this.createQueryResultTable(result));
                } else {
                    // 非查询结果
                    const $successMsg = $('<div>')
                        .addClass('success-message')
                        .text(`SQL执行成功，影响行数: ${result.affected_rows}`);
                    $panel.append($successMsg);
                }
            } else if (result.not_executed) {
                // 未执行的SQL
                const $pendingMsg = $('<div>')
                    .addClass('pending-message')
                    .text(result.message || 'SQL未执行，因为前面的SQL执行失败');
                $panel.append($pendingMsg);
            } else {
                // 错误信息
                const $errorMsg = $('<div>').addClass('error-message');
                
                // 添加错误标题
                $errorMsg.append(
                    $('<div>').addClass('error-title').text(result.message || '执行SQL失败')
                );
                
                // 添加详细错误信息（如果有）
                if (result.error_detail) {
                    // 检查是否是JSON字符串，如果是则解析并格式化
                    let errorDetail = result.error_detail;
                    try {
                        if (typeof errorDetail === 'string' && (errorDetail.startsWith('{') || errorDetail.startsWith('['))) {
                            const parsed = JSON.parse(errorDetail);
                            errorDetail = JSON.stringify(parsed, null, 2);
                        }
                    } catch (e) {
                        // 解析失败，保持原样
                        console.log('解析错误详情失败，使用原始文本');
                    }
                    
                    $errorMsg.append(
                        $('<div>').addClass('error-detail')
                                  .append($('<pre>').text(errorDetail))
                    );
                }
                
                $panel.append($errorMsg);
            }
            
            // 添加到容器
            $tabsContainer.append($tab);
            $contentContainer.append($panel);
        }.bind(this));
        
        // 如果有错误发生，添加整体消息提示
        if (response.error_occurred) {
            const errorSummary = $('<div>').addClass('execution-summary error');
            
            if (response.message) {
                errorSummary.text(response.message);
            } else {
                errorSummary.text('SQL执行过程中发生错误，后续SQL未执行');
            }
            
            $contentContainer.append(errorSummary);
        }
    }
    
    /**
     * 创建查询结果表格
     * @param {Object} result - 查询结果对象
     * @returns {jQuery} 表格jQuery对象
     */
    createQueryResultTable(result) {
        const data = result.data || [];
        
        if (data.length === 0) {
            return $('<div>').addClass('no-result-message')
                             .text('查询成功，但未返回任何数据');
        }
        
        // 创建容器
        const $container = $('<div>').addClass('query-result-container');
        
        // 添加结果信息
        let resultInfo = `查询成功，返回 ${result.row_count} 条记录`;
        if (result.limited) {
            resultInfo += `（总计 ${result.total_count} 条，仅显示前 1000 条）`;
        }
        
        $container.append(
            $('<div>').addClass('result-info').text(resultInfo)
        );
        
        // 创建表格
        const $table = $('<table>').addClass('result-table');
        const $thead = $('<thead>').appendTo($table);
        const $headerRow = $('<tr>').appendTo($thead);
        
        // 创建表头
        $.each(data[0], function(index) {
            $('<th>').text(`Column ${index+1}`).appendTo($headerRow);
        });
        
        // 创建表体
        const $tbody = $('<tbody>').appendTo($table);
        
        // 填充数据
        $.each(data, function(i, row) {
            const $dataRow = $('<tr>').appendTo($tbody);
            $.each(row, function(j, cell) {
                $('<td>').text(cell === null ? 'NULL' : cell).appendTo($dataRow);
            });
        });
        
        // 添加表格到容器
        $container.append($table);
        
        return $container;
    }
} 