"""
统计报表模块 —— 成员D 负责
功能：按月统计销售额和利润（调用存储过程）
"""

from flask import Blueprint, render_template, request

report_bp = Blueprint('report', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@report_bp.route('/report')
def report_index():
    # TODO: 成员D 实现
    # 1. 从 request.args 获取 year 和 month（默认当前年月）
    # 2. CALL sp_monthly_sales(year, month) 获取销售数据
    # 3. CALL sp_profit_report(year, month) 获取利润数据
    # 4. 传给模板展示
    return render_template('report/index.html',
                           sales=[], profits=[],
                           year=2026, month=1)
