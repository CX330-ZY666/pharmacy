"""
药品管理路由
成员B负责开发
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
# 替换 sqlite3 为 pymysql
import pymysql

# 创建蓝图
drug_bp = Blueprint('drug', __name__)

@drug_bp.route('/drug', strict_slashes=False)
def drug_list():
    """显示药品列表（支持搜索）"""
    # 延迟导入 get_db，避免循环导入
    from app import get_db
    search = request.args.get('search', '').strip()
    
    # 替换 SQLite 连接为 MySQL 连接
    conn = get_db()
    cursor = conn.cursor()  # get_db 已配置返回字典格式
    
    if search:
        # 关键修改：specification → spec（匹配MySQL表字段）
        # 新增：搜索时支持按药品类型搜索（drug_type）
        cursor.execute('''
            SELECT * FROM drug 
            WHERE name LIKE %s OR spec LIKE %s OR drug_type LIKE %s
            ORDER BY drug_id DESC
        ''', ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    else:
        # id 改为 drug_id
        cursor.execute('SELECT * FROM drug ORDER BY drug_id DESC')
    
    drugs = cursor.fetchall()
    # 移除手动关闭连接（由 app.py 的 teardown_appcontext 自动关闭）
    
    return render_template('drug/list.html', drugs=drugs, search=search)

@drug_bp.route('/drug/add', methods=['GET'])
def add_drug_form():
    """显示添加药品表单"""
    # 纯展示表单，无数据库操作，无需导入 get_db
    return render_template('drug/add.html')

@drug_bp.route('/drug/add', methods=['POST'])
def add_drug():
    """添加新药品"""
    # 延迟导入 get_db
    from app import get_db
    name = request.form.get('name', '').strip()
    drug_type = request.form.get('type', '').strip()
    unit = request.form.get('unit', '').strip()
    # 关键修改：接收表单的 specification 参数，但存入 spec 字段
    specification = request.form.get('specification', '').strip()
    
    # 验证必填字段
    if not name or not unit:
        flash('药品名称和单位是必填项', 'error')
        return redirect(url_for('drug.add_drug_form'))
    
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        # 核心修改：type → drug_type（匹配数据库表字段）
        # 关键修改：specification → spec（匹配MySQL表字段）
        cursor.execute('''
            INSERT INTO drug (name, drug_type, unit, spec)
            VALUES (%s, %s, %s, %s)
        ''', (name, drug_type, unit, specification))
        conn.commit()
        # 移除手动关闭连接
        
        flash('药品添加成功', 'success')
        return redirect(url_for('drug.drug_list'))
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'error')
        return redirect(url_for('drug.add_drug_form'))

@drug_bp.route('/drug/edit/<int:drug_id>', methods=['GET'])
def edit_drug_form(drug_id):
    """显示编辑药品表单"""
    # 延迟导入 get_db
    from app import get_db
    # 替换 SQLite 连接为 MySQL 连接
    conn = get_db()
    cursor = conn.cursor()
    # 占位符从 ? 改为 %s，id 改为 drug_id
    cursor.execute('SELECT * FROM drug WHERE drug_id = %s', (drug_id,))
    drug = cursor.fetchone()
    # 移除手动关闭连接
    
    if not drug:
        flash('药品不存在', 'error')
        return redirect(url_for('drug.drug_list'))
    
    return render_template('drug/edit.html', drug=drug)

@drug_bp.route('/drug/edit/<int:drug_id>', methods=['POST'])
def edit_drug(drug_id):
    """更新药品信息"""
    # 延迟导入 get_db
    from app import get_db
    name = request.form.get('name', '').strip()
    drug_type = request.form.get('type', '').strip()
    unit = request.form.get('unit', '').strip()
    # 关键修改：接收表单的 specification 参数，但存入 spec 字段
    specification = request.form.get('specification', '').strip()
    
    # 验证必填字段
    if not name or not unit:
        flash('药品名称和单位是必填项', 'error')
        return redirect(url_for('drug.edit_drug_form', drug_id=drug_id))
    
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        # 核心修改：type → drug_type（匹配数据库表字段）
        # 关键修改：specification → spec（匹配MySQL表字段）
        cursor.execute('''
            UPDATE drug 
            SET name = %s, drug_type = %s, unit = %s, spec = %s
            WHERE drug_id = %s
        ''', (name, drug_type, unit, specification, drug_id))
        conn.commit()
        # 移除手动关闭连接
        
        flash('药品更新成功', 'success')
        return redirect(url_for('drug.drug_list'))
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'error')
        return redirect(url_for('drug.edit_drug_form', drug_id=drug_id))

@drug_bp.route('/drug/delete/<int:drug_id>')
def delete_drug(drug_id):
    """删除药品"""
    # 延迟导入 get_db
    from app import get_db
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否有库存或关联记录（可选）
        # 占位符从 ? 改为 %s（此处 drug_id 字段名本身正确，无需改）
        cursor.execute('SELECT COUNT(*) FROM inventory WHERE drug_id = %s', (drug_id,))
        # MySQL fetchone() 返回字典，需用键取值
        count = cursor.fetchone()['COUNT(*)']
        if count > 0:
            flash('该药品有库存记录，无法删除', 'error')
        else:
            # id 改为 drug_id
            cursor.execute('DELETE FROM drug WHERE drug_id = %s', (drug_id,))
            conn.commit()
            flash('药品删除成功', 'success')
        
        # 移除手动关闭连接
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('drug.drug_list'))