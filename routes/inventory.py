"""
库存查询模块 —— 成员D 负责
功能：查询 v_current_stock 视图，展示实时库存，支持搜索
"""

from flask import Blueprint, render_template, request

inventory_bp = Blueprint('inventory', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@inventory_bp.route('/inventory')
def inventory_list():
    # TODO: 成员D 实现
    # 1. 获取搜索关键词
    # 2. SELECT * FROM v_current_stock（支持按药品名模糊搜索）
    # 3. 传给模板，低库存和即将过期的行标红
    return render_template('inventory/list.html', stocks=[], keyword='')
