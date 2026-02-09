"""
客户信息管理模块 —— 成员B 负责
功能：客户的增删改查
做法和 drug.py 一样，换表名和字段就行
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

customer_bp = Blueprint('customer', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@customer_bp.route('/customer')
def customer_list():
    # TODO: 成员B 实现（参考 drug.py）
    return render_template('customer/list.html', customers=[], keyword='')


@customer_bp.route('/customer/add', methods=['GET', 'POST'])
def customer_add():
    # TODO: 成员B 实现
    pass


@customer_bp.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def customer_edit(customer_id):
    # TODO: 成员B 实现
    pass


@customer_bp.route('/customer/delete/<int:customer_id>')
def customer_delete(customer_id):
    # TODO: 成员B 实现
    pass
