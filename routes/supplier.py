"""
供应商管理路由
成员B负责开发
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from config import DATABASE

# 创建蓝图
supplier_bp = Blueprint('supplier', __name__)

@supplier_bp.route('/supplier')
def supplier_list():
    """显示供应商列表（支持搜索）"""
    search = request.args.get('search', '').strip()
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if search:
        cursor.execute('''
            SELECT * FROM supplier 
            WHERE name LIKE ? OR contact LIKE ? OR phone LIKE ?
            ORDER BY id DESC
        ''', ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    else:
        cursor.execute('SELECT * FROM supplier ORDER BY id DESC')
    
    suppliers = cursor.fetchall()
    conn.close()
    
    return render_template('supplier/list.html', suppliers=suppliers, search=search)

@supplier_bp.route('/supplier/add', methods=['GET'])
def add_supplier_form():
    """显示添加供应商表单"""
    return render_template('supplier/add.html')

@supplier_bp.route('/supplier/add', methods=['POST'])
def add_supplier():
    """添加新供应商"""
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('供应商名称是必填项', 'error')
        return redirect(url_for('supplier.add_supplier_form'))
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO supplier (name, contact, phone, address)
            VALUES (?, ?, ?, ?)
        ''', (name, contact, phone, address))
        conn.commit()
        conn.close()
        
        flash('供应商添加成功', 'success')
        return redirect(url_for('supplier.supplier_list'))
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'error')
        return redirect(url_for('supplier.add_supplier_form'))

@supplier_bp.route('/supplier/edit/<int:supplier_id>', methods=['GET'])
def edit_supplier_form(supplier_id):
    """显示编辑供应商表单"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM supplier WHERE id = ?', (supplier_id,))
    supplier = cursor.fetchone()
    conn.close()
    
    if not supplier:
        flash('供应商不存在', 'error')
        return redirect(url_for('supplier.supplier_list'))
    
    return render_template('supplier/edit.html', supplier=supplier)

@supplier_bp.route('/supplier/edit/<int:supplier_id>', methods=['POST'])
def edit_supplier(supplier_id):
    """更新供应商信息"""
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('供应商名称是必填项', 'error')
        return redirect(url_for('supplier.edit_supplier_form', supplier_id=supplier_id))
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE supplier 
            SET name = ?, contact = ?, phone = ?, address = ?
            WHERE id = ?
        ''', (name, contact, phone, address, supplier_id))
        conn.commit()
        conn.close()
        
        flash('供应商更新成功', 'success')
        return redirect(url_for('supplier.supplier_list'))
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'error')
        return redirect(url_for('supplier.edit_supplier_form', supplier_id=supplier_id))

@supplier_bp.route('/supplier/delete/<int:supplier_id>')
def delete_supplier(supplier_id):
    """删除供应商"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 检查是否有采购记录
        cursor.execute('SELECT COUNT(*) FROM purchase WHERE supplier_id = ?', (supplier_id,))
        if cursor.fetchone()[0] > 0:
            flash('该供应商有采购记录，无法删除', 'error')
        else:
            cursor.execute('DELETE FROM supplier WHERE id = ?', (supplier_id,))
            conn.commit()
            flash('供应商删除成功', 'success')
        
        conn.close()
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('supplier.supplier_list'))