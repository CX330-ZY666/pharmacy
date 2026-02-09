"""
药品信息管理模块 —— 成员B 负责
功能：药品的增删改查 + 模糊搜索
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import pymysql

drug_bp = Blueprint('drug', __name__)


def get_db():
    """获取数据库连接"""
    from app import get_db as app_get_db
    return app_get_db()


# GET /drug - 药品列表（支持搜索）
@drug_bp.route('/drug')
def drug_list():
    # TODO: 成员B 实现
    # 1. 获取搜索关键词 keyword = request.args.get('keyword', '')
    # 2. 查询 drug 表（如果有 keyword 就用 LIKE 模糊匹配）
    # 3. 把结果传给模板
    return render_template('drug/list.html', drugs=[], keyword='')


# GET /drug/add - 显示添加表单
@drug_bp.route('/drug/add', methods=['GET'])
def drug_add_form():
    # TODO: 成员B 实现
    return render_template('drug/list.html', drugs=[], keyword='')


# POST /drug/add - 保存新药品
@drug_bp.route('/drug/add', methods=['POST'])
def drug_add():
    # TODO: 成员B 实现
    # 1. 从 request.form 获取 name, drug_type, unit, spec
    # 2. INSERT INTO drug ...
    # 3. flash('添加成功', 'success')
    # 4. return redirect(url_for('drug.drug_list'))
    pass


# GET /drug/edit/<id> - 显示编辑表单
@drug_bp.route('/drug/edit/<int:drug_id>', methods=['GET'])
def drug_edit_form(drug_id):
    # TODO: 成员B 实现
    pass


# POST /drug/edit/<id> - 保存修改
@drug_bp.route('/drug/edit/<int:drug_id>', methods=['POST'])
def drug_edit(drug_id):
    # TODO: 成员B 实现
    pass


# GET /drug/delete/<id> - 删除药品
@drug_bp.route('/drug/delete/<int:drug_id>')
def drug_delete(drug_id):
    # TODO: 成员B 实现
    pass
