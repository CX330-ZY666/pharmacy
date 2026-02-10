"""
药品信息管理模块 —— 成员B 负责
功能：药品的增删改查 + 模糊搜索
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import pymysql

# 1. 创建蓝图（无url_prefix，路由是完整路径）
drug_bp = Blueprint('drug', __name__)

def get_db():
    """获取数据库连接（从app.py导入）"""
    from app import get_db as app_get_db
    return app_get_db()

# 2. GET /drug - 药品列表（支持搜索）
@drug_bp.route('/drug')
def drug_list():
    # 获取搜索关键词
    keyword = request.args.get('keyword', '').strip()
    
    # 查询drug表
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)  # 字典游标，方便模板取值
    drugs = []
    
    try:
        if keyword:
            # 模糊搜索：匹配药品名称或规格
            sql = "SELECT * FROM drug WHERE name LIKE %s OR spec LIKE %s"
            cursor.execute(sql, ('%' + keyword + '%', '%' + keyword + '%'))
        else:
            # 无搜索词，查所有
            sql = "SELECT * FROM drug"
            cursor.execute(sql)
        drugs = cursor.fetchall()  # 获取结果列表
    except Exception as e:
        flash(f'查询失败：{str(e)}', 'error')
    finally:
        cursor.close()
        db.close()

    # 传给模板：药品列表 + 搜索关键词（回显）
    return render_template('drug/list.html', drugs=drugs, keyword=keyword)

# 3. GET /drug/add - 显示添加表单
@drug_bp.route('/drug/add', methods=['GET'])
def drug_add_form():
    # 渲染添加表单模板
    return render_template('drug/add.html')

# 4. POST /drug/add - 保存新药品
@drug_bp.route('/drug/add', methods=['POST'])
def drug_add():
    # 获取表单数据
    name = request.form.get('name', '').strip()
    drug_type = request.form.get('drug_type', '').strip()
    unit = request.form.get('unit', '').strip()
    spec = request.form.get('spec', '').strip()
    price = request.form.get('price', '').strip()

    # 数据验证
    if not all([name, drug_type, unit, spec, price]):
        flash('请填写所有必填字段！', 'error')
        return redirect(url_for('drug.drug_add_form'))

    # 插入数据库
    db = get_db()
    cursor = db.cursor()
    try:
        sql = "INSERT INTO drug (name, type, unit, spec, price) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (name, drug_type, unit, spec, price))
        db.commit()
        flash('药品添加成功！', 'success')
    except Exception as e:
        db.rollback()  # 出错回滚
        flash(f'添加失败：{str(e)}', 'error')
    finally:
        cursor.close()
        db.close()

    # 重定向回列表页
    return redirect(url_for('drug.drug_list'))

# 5. GET /drug/edit/<id> - 显示编辑表单
@drug_bp.route('/drug/edit/<int:drug_id>', methods=['GET'])
def drug_edit_form(drug_id):
    # 查询要编辑的药品
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    drug = None

    try:
        sql = "SELECT * FROM drug WHERE id = %s"
        cursor.execute(sql, (drug_id,))
        drug = cursor.fetchone()  # 获取单条记录
        if not drug:
            flash('未找到该药品！', 'error')
            return redirect(url_for('drug.drug_list'))
    except Exception as e:
        flash(f'查询失败：{str(e)}', 'error')
        return redirect(url_for('drug.drug_list'))
    finally:
        cursor.close()
        db.close()

    # 渲染编辑表单，传递药品数据
    return render_template('drug/edit.html', drug=drug)

# 6. POST /drug/edit/<id> - 保存修改
@drug_bp.route('/drug/edit/<int:drug_id>', methods=['POST'])
def drug_edit(drug_id):
    # 获取新表单数据
    name = request.form.get('name', '').strip()
    drug_type = request.form.get('drug_type', '').strip()
    unit = request.form.get('unit', '').strip()
    spec = request.form.get('spec', '').strip()
    price = request.form.get('price', '').strip()

    # 数据验证
    if not all([name, drug_type, unit, spec, price]):
        flash('请填写所有必填字段！', 'error')
        return redirect(url_for('drug.drug_edit_form', drug_id=drug_id))

    # 更新数据库
    db = get_db()
    cursor = db.cursor()
    try:
        sql = "UPDATE drug SET name=%s, type=%s, unit=%s, spec=%s, price=%s WHERE id=%s"
        cursor.execute(sql, (name, drug_type, unit, spec, price, drug_id))
        db.commit()
        flash('药品更新成功！', 'success')
    except Exception as e:
        db.rollback()
        flash(f'更新失败：{str(e)}', 'error')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('drug.drug_list'))

# 7. GET /drug/delete/<id> - 删除药品
@drug_bp.route('/drug/delete/<int:drug_id>')
def drug_delete(drug_id):
    db = get_db()
    cursor = db.cursor()
    try:
        sql = "DELETE FROM drug WHERE id = %s"
        cursor.execute(sql, (drug_id,))
        db.commit()
        flash('药品删除成功！', 'success')
    except Exception as e:
        db.rollback()
        flash(f'删除失败：{str(e)}', 'error')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('drug.drug_list'))