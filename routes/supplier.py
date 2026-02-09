"""
供应商信息管理模块 —— 成员B 负责
功能：供应商的增删改查
做法和 drug.py 一样，换表名和字段就行
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

supplier_bp = Blueprint('supplier', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@supplier_bp.route('/supplier')
def supplier_list():
    # TODO: 成员B 实现（参考 drug.py）
    return render_template('supplier/list.html', suppliers=[], keyword='')


@supplier_bp.route('/supplier/add', methods=['GET', 'POST'])
def supplier_add():
    # TODO: 成员B 实现
    pass


@supplier_bp.route('/supplier/edit/<int:supplier_id>', methods=['GET', 'POST'])
def supplier_edit(supplier_id):
    # TODO: 成员B 实现
    pass


@supplier_bp.route('/supplier/delete/<int:supplier_id>')
def supplier_delete(supplier_id):
    # TODO: 成员B 实现
    pass
