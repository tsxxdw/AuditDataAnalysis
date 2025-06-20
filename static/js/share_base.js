/**
 * 股票基本信息页面JavaScript
 */
$(document).ready(function() {
    // 页面加载完成后，加载股票数据
    const pageSize = 20; // 每页显示的记录数
    let currentPage = 1;
    let totalPages = 1;
    let stockData = []; // 存储当前筛选条件下的所有股票数据
    
    // 创建页面专用的加载指示器
    const spinner = new LoadingSpinner({
        containerId: 'loadingSpinner',
        text: '加载股票数据...',
        styles: {
            zIndex: 100
        }
    });
    
    // 初始化加载数据
    loadStockData();
    
    // 搜索按钮点击事件
    $('#search-btn').on('click', function() {
        currentPage = 1;
        loadStockData();
    });
    
    // 更新按钮点击事件
    $('#update-btn').on('click', function() {
        // 添加确认对话框
        if (confirm('确定要更新数据吗？此操作将从网络获取最新包括已退市的所有A股股票信息。')) {
            updateStockData();
        }
    });
    
    // 翻页按钮事件
    $('#prev-page').on('click', function() {
        if (currentPage > 1) {
            currentPage--;
            renderStockData();
            updatePagination();
        }
    });
    
    $('#next-page').on('click', function() {
        if (currentPage < totalPages) {
            currentPage++;
            renderStockData();
            updatePagination();
        }
    });
    
    // 按回车键搜索
    $('#keyword-filter').on('keypress', function(e) {
        if (e.which === 13) {
            currentPage = 1;
            loadStockData();
        }
    });
    
    /**
     * 加载股票数据
     */
    function loadStockData() {
        // 显示加载指示器
        spinner.show('加载股票数据...', '.results-container');
        
        // 获取筛选条件
        const market = $('#market-filter').val();
        const stStatus = $('#st-filter').val();
        const maxChange = $('#max-change-filter').val();
        const keyword = $('#keyword-filter').val().trim();
        
        // 发送AJAX请求
        $.ajax({
            url: '/api/share_base/list',
            type: 'GET',
            data: {
                market: market,
                st_status: stStatus,
                max_change: maxChange,
                keyword: keyword
            },
            dataType: 'json',
            success: function(response) {
                if (response.code === 0) {
                    stockData = response.data;
                    totalPages = Math.ceil(stockData.length / pageSize);
                    
                    $('#total-count').text(stockData.length);
                    
                    renderStockData();
                    updatePagination();
                } else {
                    alert('获取股票数据失败：' + response.message);
                }
                
                // 隐藏加载指示器
                spinner.hide();
            },
            error: function(xhr, status, error) {
                console.error('获取股票数据异常：', error);
                alert('获取股票数据异常，请检查网络连接或联系管理员。');
                
                // 隐藏加载指示器
                spinner.hide();
            }
        });
    }
    
    /**
     * 更新股票数据
     */
    function updateStockData() {
        // 显示加载指示器，使用不同的提示文本
        spinner.show('正在更新股票数据...', '.results-container');
        
        $.ajax({
            url: '/api/share_base/update',
            type: 'POST',
            dataType: 'json',
            success: function(response) {
                if (response.code === 0) {
                    alert('股票数据更新成功，共更新 ' + response.data.updated + ' 条记录，新增 ' + response.data.added + ' 条记录。');
                    loadStockData(); // 更新成功后重新加载数据
                } else {
                    alert('更新股票数据失败：' + response.message);
                    
                    // 隐藏加载指示器
                    spinner.hide();
                }
            },
            error: function(xhr, status, error) {
                console.error('更新股票数据异常：', error);
                alert('更新股票数据异常，请检查网络连接或联系管理员。');
                
                // 隐藏加载指示器
                spinner.hide();
            }
        });
    }
    
    /**
     * 渲染股票数据表格
     */
    function renderStockData() {
        const $shareList = $('#share-list');
        $shareList.empty();
        
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = Math.min(startIndex + pageSize, stockData.length);
        
        if (stockData.length === 0) {
            $shareList.append(`
                <tr>
                    <td colspan="3" class="text-center">暂无数据</td>
                </tr>
            `);
            return;
        }
        
        for (let i = startIndex; i < endIndex; i++) {
            const stock = stockData[i];
            $shareList.append(`
                <tr>
                    <td>${stock.share_code}</td>
                    <td>${stock.share_name}</td>
                    <td>${stock.share_type}</td>
                </tr>
            `);
        }
    }
    
    /**
     * 更新分页信息
     */
    function updatePagination() {
        $('#current-page').text(currentPage);
        $('#total-pages').text(totalPages);
        
        $('#prev-page').prop('disabled', currentPage <= 1);
        $('#next-page').prop('disabled', currentPage >= totalPages);
    }
}); 