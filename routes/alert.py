"""
预警信息模块 —— 成员D 负责
功能：展示库存不足和即将过期的预警，支持标记已读
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

alert_bp = Blueprint('alert', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@alert_bp.route('/alert')
def alert_list():
    # TODO: 成员D 实现
    # 1. 查询 alert 表（未读优先，按时间倒序）
    # 2. 区分 LOW_STOCK 和 EXPIRING 两类
    return render_template('alert/list.html', alerts=[])


@alert_bp.route('/alert/read/<int:alert_id>')
def alert_mark_read(alert_id):
    # TODO: 成员D 实现
    # UPDATE alert SET is_read = 1 WHERE alert_id = ?
    pass
