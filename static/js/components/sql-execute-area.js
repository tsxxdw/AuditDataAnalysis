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
        
        // 调用后端API执行SQL
        $.ajax({
            url: this.options.apiEndpoint,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sql: sql
            }),
            success: (response) => {
                if (response.success) {
                    if (response.is_query) {
                        // 显示查询结果
                        this.displayQueryResults(response.data);
                    } else {
                        // 显示执行结果
                        $('.sql-result-section').show();
                        $('#sqlResultContent').html($('<div>').addClass('success-message').text(`SQL执行成功，影响行数: ${response.affected_rows}`));
                        
                        // 如果提供了成功回调，则调用
                        if ($.isFunction(this.options.onSuccess)) {
                            this.options.onSuccess(response);
                        }
                    }
                } else {
                    // 显示错误信息
                    $('.sql-result-section').show();
                    $('#sqlResultContent').html($('<div>').addClass('error-message').text(`SQL执行失败: ${response.message || '未知错误'}`));
                    
                    // 如果提供了错误回调，则调用
                    if ($.isFunction(this.options.onError)) {
                        this.options.onError(response);
                    }
                }
            },
            error: (xhr) => {
                console.error('执行SQL请求失败:', xhr);
                // 显示错误信息
                $('.sql-result-section').show();
                const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : '请求失败，请查看控制台日志';
                $('#sqlResultContent').html($('<div>').addClass('error-message').text(`执行SQL请求失败: ${errorMsg}`));
                
                // 如果提供了错误回调，则调用
                if ($.isFunction(this.options.onError)) {
                    this.options.onError(xhr);
                }
            }
        });
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
     * 显示查询结果
     * @param {Array} data - 查询结果数据
     */
    displayQueryResults(data) {
        if (!data || data.length === 0) {
            // 显示无结果的消息
            $('.sql-result-section').show();
            $('#sqlResultContent').html($('<div>').addClass('no-result-message').text('查询结果为空'));
            return;
        }
        
        // 使用jQuery创建表格元素
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
        
        // 显示结果区域并更新内容
        $('.sql-result-section').show();
        $('#sqlResultContent').empty().append($table);
    }
} 