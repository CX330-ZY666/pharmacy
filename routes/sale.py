"""
销售管理模块 —— 成员C 负责
功能：销售开单（按批次出库）、销售单列表、详情查看
核心：出库后自动扣减 inventory 表，库存不足时拒绝
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

sale_bp = Blueprint('sale', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@sale_bp.route('/sale')
def sale_list():
    # TODO: 成员C 实现
    return render_template('sale/list.html', sales=[])


@sale_bp.route('/sale/add', methods=['GET'])
def sale_add_form():
    # TODO: 成员C 实现
    # 查询所有客户、有库存的药品+批次，传给模板
    return render_template('sale/add.html', customers=[], inventory=[])


@sale_bp.route('/sale/add', methods=['POST'])
def sale_add():
    # TODO: 成员C 实现 —— 核心逻辑！
    # 1. 从 request.form 获取 customer_id, sale_date
    # 2. 获取明细（drug_id[], batch_no[], quantity[], price[]）
    # 3. INSERT INTO sale → 拿到 sale_id
    # 4. 循环每条明细：
    #    a. 检查 inventory 中对应批次的库存是否充足
    #    b. 不足 → rollback + flash 错误
    #    c. 充足 → INSERT sale_detail + UPDATE inventory 扣减
    # 5. 计算 total_amount，UPDATE sale
    # 6. db.commit()
    pass


@sale_bp.route('/sale/<int:sale_id>')
def sale_detail(sale_id):
    # TODO: 成员C 实现
    pass
