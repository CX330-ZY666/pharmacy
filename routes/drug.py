"""
药品管理路由
成员B负责开发
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from config import DATABASE

# 创建蓝图
drug_bp = Blueprint('drug', __name__)

@drug_bp.route('/drug')
def drug_list():
    """显示药品列表（支持搜索）"""
    search = request.args.get('search', '').strip()
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 使返回字典格式
    cursor = conn.cursor()
    
    if search:
        cursor.execute('''
            SELECT * FROM drug 
            WHERE name LIKE ? OR specification LIKE ?
            ORDER BY id DESC
        ''', ('%' + search + '%', '%' + search + '%'))
    else:
        cursor.execute('SELECT * FROM drug ORDER BY id DESC')
    
    drugs = cursor.fetchall()
    conn.close()
    
    return render_template('drug/list.html', drugs=drugs, search=search)

@drug_bp.route('/drug/add', methods=['GET'])
def add_drug_form():
    """显示添加药品表单"""
    return render_template('drug/add.html')

@drug_bp.route('/drug/add', methods=['POST'])
def add_drug():
    """添加新药品"""
    name = request.form.get('name', '').strip()
    drug_type = request.form.get('type', '').strip()
    unit = request.form.get('unit', '').strip()
    specification = request.form.get('specification', '').strip()
    
    # 验证必填字段
    if not name or not unit:
        flash('药品名称和单位是必填项', 'error')
        return redirect(url_for('drug.add_drug_form'))
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO drug (name, type, unit, specification)
            VALUES (?, ?, ?, ?)
        ''', (name, drug_type, unit, specification))
        conn.commit()
        conn.close()
        
        flash('药品添加成功', 'success')
        return redirect(url_for('drug.drug_list'))
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'error')
        return redirect(url_for('drug.add_drug_form'))

@drug_bp.route('/drug/edit/<int:drug_id>', methods=['GET'])
def edit_drug_form(drug_id):
    """显示编辑药品表单"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM drug WHERE id = ?', (drug_id,))
    drug = cursor.fetchone()
    conn.close()
    
    if not drug:
        flash('药品不存在', 'error')
        return redirect(url_for('drug.drug_list'))
    
    return render_template('drug/edit.html', drug=drug)

@drug_bp.route('/drug/edit/<int:drug_id>', methods=['POST'])
def edit_drug(drug_id):
    """更新药品信息"""
    name = request.form.get('name', '').strip()
    drug_type = request.form.get('type', '').strip()
    unit = request.form.get('unit', '').strip()
    specification = request.form.get('specification', '').strip()
    
    # 验证必填字段
    if not name or not unit:
        flash('药品名称和单位是必填项', 'error')
        return redirect(url_for('drug.edit_drug_form', drug_id=drug_id))
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE drug 
            SET name = ?, type = ?, unit = ?, specification = ?
            WHERE id = ?
        ''', (name, drug_type, unit, specification, drug_id))
        conn.commit()
        conn.close()
        
        flash('药品更新成功', 'success')
        return redirect(url_for('drug.drug_list'))
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'error')
        return redirect(url_for('drug.edit_drug_form', drug_id=drug_id))

@drug_bp.route('/drug/delete/<int:drug_id>')
def delete_drug(drug_id):
    """删除药品"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 检查是否有库存或关联记录（可选）
        cursor.execute('SELECT COUNT(*) FROM inventory WHERE drug_id = ?', (drug_id,))
        if cursor.fetchone()[0] > 0:
            flash('该药品有库存记录，无法删除', 'error')
        else:
            cursor.execute('DELETE FROM drug WHERE id = ?', (drug_id,))
            conn.commit()
            flash('药品删除成功', 'success')
        
        conn.close()
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('drug.drug_list'))