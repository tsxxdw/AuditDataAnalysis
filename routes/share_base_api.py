"""
股票基本信息API路由

处理股票基本信息相关的API请求
"""

from flask import Blueprint, request, jsonify
from service.share.share_base_service import ShareBaseService
from service.log.logger import app_logger

# 创建股票基本信息API蓝图
share_base_api_bp = Blueprint('share_base_api', __name__)

@share_base_api_bp.route('/list', methods=['GET'])
def get_share_list():
    """获取股票列表
    
    根据筛选条件获取股票列表
    ---
    parameters:
      - name: market
        in: query
        type: string
        description: 市场类型(all, sh, sz, cy)
        required: false
      - name: st_status
        in: query
        type: string
        description: ST状态(all, star-st, st, not-st)
        required: false
      - name: max_change
        in: query
        type: string
        description: 最大涨幅(all, 5, 10, 20, 30)
        required: false
      - name: keyword
        in: query
        type: string
        description: 关键词(股票代码或名称)
        required: false
    responses:
      200:
        description: 股票列表
        schema:
          properties:
            code:
              type: integer
              description: 状态码
            message:
              type: string
              description: 消息
            data:
              type: array
              description: 股票列表
              items:
                type: object
                properties:
                  share_code:
                    type: string
                    description: 股票代码
                  share_name:
                    type: string
                    description: 股票名称
                  share_type:
                    type: string
                    description: 股票类型
    """
    try:
        # 获取请求参数
        market = request.args.get('market', 'all')
        st_status = request.args.get('st_status', 'all')
        max_change = request.args.get('max_change', 'all')
        keyword = request.args.get('keyword', '')
        
        app_logger.info(f"获取股票列表，筛选条件：market={market}, st_status={st_status}, max_change={max_change}, keyword={keyword}")
        
        # 调用服务层方法获取数据
        share_list = ShareBaseService.get_share_list(market, st_status, keyword, max_change)
        
        return jsonify({
            'code': 0,
            'message': '获取成功',
            'data': share_list
        })
    except Exception as e:
        app_logger.error(f"获取股票列表异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f"获取股票列表异常: {str(e)}",
            'data': []
        })

@share_base_api_bp.route('/update', methods=['POST'])
def update_share_data():
    """更新股票数据
    
    从AKShare获取最新的股票信息（包括已退市股票）并更新数据库
    ---
    responses:
      200:
        description: 更新结果
        schema:
          properties:
            code:
              type: integer
              description: 状态码
            message:
              type: string
              description: 消息
            data:
              type: object
              properties:
                added:
                  type: integer
                  description: 新增记录数
                updated:
                  type: integer
                  description: 更新记录数
    """
    try:
        app_logger.info("开始更新股票数据（包括已退市股票）")
        
        # 调用服务层方法更新数据
        result = ShareBaseService.update_share_data()
        
        app_logger.info(f"更新股票数据完成，新增：{result['added']}，更新：{result['updated']}")
        
        return jsonify({
            'code': 0,
            'message': '更新成功',
            'data': result
        })
    except Exception as e:
        app_logger.error(f"更新股票数据异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f"更新股票数据异常: {str(e)}",
            'data': {
                'added': 0,
                'updated': 0
            }
        }) 