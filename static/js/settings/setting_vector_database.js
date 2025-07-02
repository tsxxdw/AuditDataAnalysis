// 向量数据库设置JS文件
// 负责处理向量数据库设置的加载、保存和表单控制

const VectorDatabaseSettings = {
    // 初始化
    init: function() {
        this.bindEvents();
        this.loadVectorDatabaseSettings();
    },
    
    // 绑定事件
    bindEvents: function() {
        // 向量数据库类型切换
        $('#vector-db-type').change(function() {
            VectorDatabaseSettings.handleDbTypeChange();
        });
        
        // 默认向量数据库类型切换
        $('#default-vector-db').change(function() {
            var defaultDbType = $(this).val();
            console.log('默认向量数据库类型已切换为：' + defaultDbType);
        });
        
        // 保存向量数据库设置
        $('.save-vector-db-btn').click(function() {
            VectorDatabaseSettings.saveSettings();
        });
        
        // 测试向量数据库连接
        $('.test-vector-db-connection-btn').click(function() {
            VectorDatabaseSettings.testConnection();
        });
    },
    
    // 加载向量数据库设置
    loadVectorDatabaseSettings: function() {
        $.ajax({
            url: '/api/settings/vector_database',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                // 设置默认向量数据库类型
                if (data.defaultVectorDbType) {
                    $('#default-vector-db').val(data.defaultVectorDbType);
                }
                
                // 加载向量数据库配置
                if (data.vectorDatabases) {
                    // 默认先显示默认向量数据库类型的表单
                    var defaultType = data.defaultVectorDbType || 'chroma';
                    $('#vector-db-type').val(defaultType);
                    $('#vector-db-type').trigger('change');
                    
                    // 填充Chroma配置
                    if (data.vectorDatabases.chroma) {
                        VectorDatabaseSettings.fillChromaForm(data.vectorDatabases.chroma);
                    }
                    
                    // 填充Milvus配置
                    if (data.vectorDatabases.milvus) {
                        VectorDatabaseSettings.fillMilvusForm(data.vectorDatabases.milvus);
                    }
                    
                    // 填充FAISS配置
                    if (data.vectorDatabases.faiss) {
                        VectorDatabaseSettings.fillFAISSForm(data.vectorDatabases.faiss);
                    }
                    
                    // 填充Elasticsearch配置
                    if (data.vectorDatabases.elasticsearch) {
                        VectorDatabaseSettings.fillElasticsearchForm(data.vectorDatabases.elasticsearch);
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('加载向量数据库设置失败:', error);
            }
        });
    },
    
    // 处理向量数据库类型切换
    handleDbTypeChange: function() {
        const dbType = $('#vector-db-type').val();
        
        // 隐藏所有表单
        $('.vector-db-connection-form').hide();
        
        // 显示选中的数据库类型表单
        $(`#${dbType}-form`).show();
        
        console.log(`切换到 ${dbType} 向量数据库表单`);
    },
    
    // 测试向量数据库连接
    testConnection: function() {
        const dbType = $('#vector-db-type').val();
        let config = {};
        
        // 根据当前所选数据库类型，收集对应的配置信息
        switch(dbType) {
            case 'chroma':
                config = this.collectChromaInfo();
                break;
            case 'milvus':
                config = this.collectMilvusInfo();
                break;
            case 'faiss':
                config = this.collectFAISSInfo();
                break;
            case 'elasticsearch':
                config = this.collectElasticsearchInfo();
                break;
        }
        
        // 添加类型信息
        config.type = dbType;
        
        // 发送到后端测试连接
        $.ajax({
            url: '/api/settings/vector_database/test',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(config),
            beforeSend: function() {
                $('.test-vector-db-connection-btn').prop('disabled', true).text('正在测试连接...');
            },
            success: function(response) {
                if (response.success) {
                    alert('连接成功: ' + response.message);
                } else {
                    alert('连接失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('测试连接出错: ' + error);
                console.error('测试连接失败:', xhr.responseText);
            },
            complete: function() {
                $('.test-vector-db-connection-btn').prop('disabled', false).text('测试连接');
            }
        });
    },
    
    // 保存设置
    saveSettings: function() {
        var defaultDbType = $('#default-vector-db').val();
        
        // 收集所有向量数据库类型的连接信息
        var chromaConfig = this.collectChromaInfo();
        var milvusConfig = this.collectMilvusInfo();
        var faissConfig = this.collectFAISSInfo();
        var elasticsearchConfig = this.collectElasticsearchInfo();
        
        // 构建要保存的数据结构
        var settingsData = {
            defaultVectorDbType: defaultDbType,
            vectorDatabases: {
                chroma: chromaConfig,
                milvus: milvusConfig,
                faiss: faissConfig,
                elasticsearch: elasticsearchConfig
            }
        };
        
        // 发送数据到后端保存
        $.ajax({
            url: '/api/settings/vector_database',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(settingsData),
            success: function(response) {
                alert('向量数据库设置已保存成功！');
            },
            error: function(xhr, status, error) {
                alert('保存向量数据库设置失败: ' + error);
                console.error('保存向量数据库设置失败:', xhr.responseText);
            }
        });
    },
    
    // 填充Chroma表单
    fillChromaForm: function(config) {
        $('#chroma-host').val(config.host || '');
        $('#chroma-port').val(config.port || '8000');
        $('#chroma-collection').val(config.collection || '');
        $('#chroma-persistent').val(config.persistent_directory || '');
    },
    
    // 填充Milvus表单
    fillMilvusForm: function(config) {
        $('#milvus-host').val(config.host || '');
        $('#milvus-port').val(config.port || '19530');
        $('#milvus-collection').val(config.collection || '');
    },
    
    // 填充FAISS表单
    fillFAISSForm: function(config) {
        $('#faiss-index-path').val(config.index_path || '');
        $('#faiss-dimension').val(config.dimension || '1536');
    },
    
    // 填充Elasticsearch表单
    fillElasticsearchForm: function(config) {
        $('#elasticsearch-host').val(config.host || '');
        $('#elasticsearch-port').val(config.port || '9200');
        $('#elasticsearch-index').val(config.index || '');
        $('#elasticsearch-username').val(config.username || '');
        $('#elasticsearch-password').val(config.password || '');
    },
    
    // 收集Chroma信息
    collectChromaInfo: function() {
        return {
            host: $('#chroma-host').val(),
            port: $('#chroma-port').val(),
            collection: $('#chroma-collection').val(),
            persistent_directory: $('#chroma-persistent').val()
        };
    },
    
    // 收集Milvus信息
    collectMilvusInfo: function() {
        return {
            host: $('#milvus-host').val(),
            port: $('#milvus-port').val(),
            collection: $('#milvus-collection').val()
        };
    },
    
    // 收集FAISS信息
    collectFAISSInfo: function() {
        return {
            index_path: $('#faiss-index-path').val(),
            dimension: $('#faiss-dimension').val()
        };
    },
    
    // 收集Elasticsearch信息
    collectElasticsearchInfo: function() {
        return {
            host: $('#elasticsearch-host').val(),
            port: $('#elasticsearch-port').val(),
            index: $('#elasticsearch-index').val(),
            username: $('#elasticsearch-username').val(),
            password: $('#elasticsearch-password').val()
        };
    }
};

// 页面加载完成后初始化
$(document).ready(function() {
    VectorDatabaseSettings.init();
}); 