"""
进货管理模块 —— 成员C 负责
功能：采购单录入（含批次号、有效期）、采购单列表、详情查看
核心：入库后自动更新 inventory 表
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

purchase_bp = Blueprint('purchase', __name__)


def get_db():
    from app import get_db as app_get_db
    return app_get_db()


@purchase_bp.route('/purchase')
def purchase_list():
    # TODO: 成员C 实现
    # 查询 purchase 表（JOIN supplier 拿供应商名），按日期倒序
    return render_template('purchase/list.html', purchases=[])


@purchase_bp.route('/purchase/add', methods=['GET'])
def purchase_add_form():
    # TODO: 成员C 实现
    # 查询所有供应商和药品，传给模板做下拉选择
    return render_template('purchase/add.html', suppliers=[], drugs=[])


@purchase_bp.route('/purchase/add', methods=['POST'])
def purchase_add():
    # TODO: 成员C 实现 —— 这是核心逻辑！
    # 1. 从 request.form 获取 supplier_id, purchase_date, note
    # 2. 从 request.form.getlist 获取明细（drug_id[], batch_no[], quantity[], price[], expiry_date[]）
    # 3. INSERT INTO purchase → 拿到 purchase_id
    # 4. 循环每条明细：
    #    a. INSERT INTO purchase_detail
    #    b. 更新 inventory：
    #       - 查是否已有 drug_id + batch_no 的记录
    #       - 有 → UPDATE quantity += 新数量
    #       - 没有 → INSERT 新记录
    # 5. 计算 total_amount = SUM(price * quantity)，UPDATE purchase
    # 6. db.commit()
    pass


@purchase_bp.route('/purchase/<int:purchase_id>')
def purchase_detail(purchase_id):
    # TODO: 成员C 实现
    # 查询采购单信息 + 明细列表
    pass
