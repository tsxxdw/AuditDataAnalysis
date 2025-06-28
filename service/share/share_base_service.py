"""
股票基本信息服务

负责处理股票基本信息的业务逻辑
"""

import akshare as ak
import pandas as pd
from sqlalchemy import text
from service.database.database_service import DatabaseService
from utils.database_config_util import DatabaseConfigUtil
from service.log.logger import app_logger

class ShareBaseService:
    """股票基本信息服务类"""
    
    @staticmethod
    def get_share_list(market='all', st_status='all', keyword='', max_change='all'):
        """获取股票列表
        
        根据筛选条件获取股票列表
        
        Args:
            market (str): 市场类型(all, sh, sz, cy)
            st_status (str): ST状态(all, st, not-st)
            keyword (str): 关键词(股票代码或名称)
            max_change (str): 最大涨幅(all, 5, 10, 20, 30)
            
        Returns:
            list: 股票列表
        """
        try:
            # 获取数据库服务实例
            db_service = DatabaseService()
            
            # 获取默认数据库类型和配置
            db_type = DatabaseConfigUtil.get_default_db_type()
            db_config = DatabaseConfigUtil.get_database_config(db_type)
            
            if not db_config:
                app_logger.error(f"获取{db_type}数据库配置失败")
                return []
            
            # 构建查询SQL
            sql = "SELECT share_code, share_name, share_type FROM t_share_base WHERE 1=1"
            params = {}
            
            # 根据市场类型筛选
            if market != 'all':
                if market == 'sh':
                    sql += " AND share_code LIKE :sh_pattern"
                    params['sh_pattern'] = '6%'
                elif market == 'sz':
                    sql += " AND share_code LIKE :sz_pattern"
                    params['sz_pattern'] = '0%'
                elif market == 'cy':
                    sql += " AND share_code LIKE :cy_pattern"
                    params['cy_pattern'] = '3%'
            
            # 根据ST状态筛选
            if st_status != 'all':
                if st_status == 'star-st':
                    sql += " AND share_name LIKE :star_st_pattern"
                    params['star_st_pattern'] = '%*ST%'
                elif st_status == 'st':
                    sql += " AND share_name LIKE :st_pattern AND share_name NOT LIKE :not_star_st_pattern"
                    params['st_pattern'] = '%ST%'
                    params['not_star_st_pattern'] = '%*ST%'
                elif st_status == 'not-st':
                    sql += " AND share_name NOT LIKE :not_st_pattern"
                    params['not_st_pattern'] = '%ST%'
            
            # 根据最大涨幅筛选
            if max_change != 'all':
                if max_change == '5':
                    sql += " AND share_name LIKE :st_change_pattern"
                    params['st_change_pattern'] = '%ST%'
                elif max_change == '10':
                    sql += " AND share_name NOT LIKE :not_st_pattern_10 AND (share_code LIKE '0%' OR (share_code LIKE '6%' AND share_code NOT LIKE '688%'))"
                    params['not_st_pattern_10'] = '%ST%'
                elif max_change == '20':
                    sql += " AND share_name NOT LIKE :not_st_pattern_20 AND (share_code LIKE '3%' OR share_code LIKE '688%')"
                    params['not_st_pattern_20'] = '%ST%'
                elif max_change == '30':
                    sql += " AND share_name NOT LIKE :not_st_pattern_30 AND share_code LIKE '8%' AND share_code NOT LIKE '688%'"
                    params['not_st_pattern_30'] = '%ST%'
            
            # 根据关键词筛选
            if keyword:
                sql += " AND (share_code LIKE :keyword_pattern OR share_name LIKE :keyword_pattern)"
                params['keyword_pattern'] = f'%{keyword}%'
            
            # 按股票代码排序
            sql += " ORDER BY share_code"
            
            # 执行查询
            result = db_service.execute_sql(db_type, db_config, text(sql), params)
            
            # 处理查询结果
            share_list = []
            if result['is_query'] and result['rows']:
                for row in result['rows']:
                    share_list.append({
                        'share_code': row[0],
                        'share_name': row[1],
                        'share_type': row[2]
                    })
            
            app_logger.info(f"获取股票列表成功，共 {len(share_list)} 条记录")
            return share_list
        
        except Exception as e:
            app_logger.error(f"获取股票列表异常: {str(e)}")
            return []
    
    @staticmethod
    def get_all_a_stocks():
        """
        获取所有A股股票（包含正常上市和已退市股票）
        
        返回:
            pd.DataFrame: 包含所有A股股票代码和名称的DataFrame
        """
        try:
            app_logger.info("开始获取所有A股股票数据（包括已退市股票）")
            
            # 1. 获取正常上市股票（沪深京A股）
            active_df = ak.stock_info_a_code_name()
            app_logger.info(f"获取到正常上市股票 {len(active_df)} 条")
            
            # 2. 获取上交所退市股票
            sh_delisted = ak.stock_info_sh_delist()
            sh_delisted = sh_delisted[["公司代码", "公司简称"]].rename(
                columns={"公司代码": "code", "公司简称": "name"}
            )
            app_logger.info(f"获取到上交所退市股票 {len(sh_delisted)} 条")
            
            # 3. 获取深交所退市股票（终止上市）
            sz_delisted = ak.stock_info_sz_delist(symbol="终止上市公司")
            # 处理深交所数据可能为空的情况
            if not sz_delisted.empty:
                sz_delisted = sz_delisted[["证券代码", "证券简称"]].rename(
                    columns={"证券代码": "code", "证券简称": "name"}
                )
                app_logger.info(f"获取到深交所退市股票 {len(sz_delisted)} 条")
            else:
                sz_delisted = pd.DataFrame(columns=["code", "name"])
                app_logger.info("未获取到深交所退市股票数据")
            
            # 4. 合并所有股票数据
            all_stocks = pd.concat(
                [active_df, sh_delisted, sz_delisted],
                ignore_index=True
            )
            
            # 5. 清理数据：确保代码格式统一（6位数字）
            all_stocks["code"] = all_stocks["code"].astype(str).str.zfill(6)
            
            # 6. 去重处理（避免同一股票多次出现）
            all_stocks = all_stocks.drop_duplicates(subset=["code"], keep="first")
            
            app_logger.info(f"获取所有A股股票数据完成，共 {len(all_stocks)} 条")
            return all_stocks
            
        except Exception as e:
            app_logger.error(f"获取所有A股股票数据异常: {str(e)}")
            # 出错时返回一个空的DataFrame
            return pd.DataFrame(columns=["code", "name"])
    
    @staticmethod
    def update_share_data():
        """更新股票数据
        
        从AKShare获取最新的股票信息（包括已退市股票）并更新数据库
        
        Returns:
            dict: 更新结果，包括新增记录数和更新记录数
        """
        try:
            # 从AKShare获取股票信息（包括已退市股票）
            app_logger.info("开始从AKShare获取股票信息（包括已退市股票）")
            stock_info_df = ShareBaseService.get_all_a_stocks()
            
            # 获取股票代码和名称
            app_logger.info(f"获取到 {len(stock_info_df)} 条股票信息")
            
            # 获取数据库服务实例
            db_service = DatabaseService()
            
            # 获取默认数据库类型和配置
            db_type = DatabaseConfigUtil.get_default_db_type()
            db_config = DatabaseConfigUtil.get_database_config(db_type)
            
            if not db_config:
                app_logger.error(f"获取{db_type}数据库配置失败")
                return {'added': 0, 'updated': 0}
            
            # 确保表存在
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS t_share_base (
                    share_code VARCHAR(255) NOT NULL,
                    share_name VARCHAR(255) NOT NULL,
                    share_type VARCHAR(255) NOT NULL,
                    UNIQUE INDEX idx_share_code (share_code)
                ) ;
            """
            db_service.execute_sql(db_type, db_config, text(create_table_sql))
            
            # 先获取数据库中已有的股票代码
            existing_codes_sql = "SELECT share_code FROM t_share_base"
            existing_codes_result = db_service.execute_sql(db_type, db_config, text(existing_codes_sql))
            
            existing_codes = set()
            if existing_codes_result['is_query'] and existing_codes_result['rows']:
                existing_codes = {row[0] for row in existing_codes_result['rows']}
            
            added_count = 0
            updated_count = 0
            
            # 遍历AKShare获取的数据，插入或更新数据库
            for index, row in stock_info_df.iterrows():
                code = row['code']
                name = row['name']
                
                # 根据股票代码确定类型
                if code.startswith('6'):
                    share_type = '上海主板'
                elif code.startswith('0'):
                    share_type = '深圳主板'
                elif code.startswith('3'):
                    share_type = '创业板'
                else:
                    share_type = '其他'
                
                if code in existing_codes:
                    # 更新现有记录
                    update_sql = """
                        UPDATE t_share_base 
                        SET share_name = :name, share_type = :share_type 
                        WHERE share_code = :code
                    """
                    update_params = {
                        'name': name,
                        'share_type': share_type,
                        'code': code
                    }
                    update_result = db_service.execute_sql(db_type, db_config, text(update_sql), update_params)
                    if not update_result['is_query'] and update_result['affected_rows'] > 0:
                        updated_count += 1
                else:
                    # 插入新记录
                    insert_sql = """
                        INSERT INTO t_share_base (share_code, share_name, share_type) 
                        VALUES (:code, :name, :share_type)
                    """
                    insert_params = {
                        'code': code,
                        'name': name,
                        'share_type': share_type
                    }
                    insert_result = db_service.execute_sql(db_type, db_config, text(insert_sql), insert_params)
                    if not insert_result['is_query'] and insert_result['affected_rows'] > 0:
                        added_count += 1
            
            app_logger.info(f"更新股票数据完成，新增：{added_count}，更新：{updated_count}")
            
            return {
                'added': added_count,
                'updated': updated_count
            }
        
        except Exception as e:
            app_logger.error(f"更新股票数据异常: {str(e)}")
            return {'added': 0, 'updated': 0} 