from service.database.db_pool_manager import DatabasePoolManager

# 在应用关闭时关闭所有连接池
@app.teardown_appcontext
def shutdown_db_pools(exception=None):
    DatabasePoolManager.get_instance().shutdown() 