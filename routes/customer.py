"""
客户管理路由
成员B负责开发
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from config import DATABASE

# 创建蓝图
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer')
def customer_list():
    """显示客户列表（支持搜索）"""
    search = request.args.get('search', '').strip()
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if search:
        cursor.execute('''
            SELECT * FROM customer 
            WHERE name LIKE ? OR contact LIKE ? OR phone LIKE ?
            ORDER BY id DESC
        ''', ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    else:
        cursor.execute('SELECT * FROM customer ORDER BY id DESC')
    
    customers = cursor.fetchall()
    conn.close()
    
    return render_template('customer/list.html', customers=customers, search=search)

@customer_bp.route('/customer/add', methods=['GET'])
def add_customer_form():
    """显示添加客户表单"""
    return render_template('customer/add.html')

@customer_bp.route('/customer/add', methods=['POST'])
def add_customer():
    """添加新客户"""
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('客户名称是必填项', 'error')
        return redirect(url_for('customer.add_customer_form'))
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer (name, contact, phone, address)
            VALUES (?, ?, ?, ?)
        ''', (name, contact, phone, address))
        conn.commit()
        conn.close()
        
        flash('客户添加成功', 'success')
        return redirect(url_for('customer.customer_list'))
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'error')
        return redirect(url_for('customer.add_customer_form'))

@customer_bp.route('/customer/edit/<int:customer_id>', methods=['GET'])
def edit_customer_form(customer_id):
    """显示编辑客户表单"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customer WHERE id = ?', (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    
    if not customer:
        flash('客户不存在', 'error')
        return redirect(url_for('customer.customer_list'))
    
    return render_template('customer/edit.html', customer=customer)

@customer_bp.route('/customer/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    """更新客户信息"""
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('客户名称是必填项', 'error')
        return redirect(url_for('customer.edit_customer_form', customer_id=customer_id))
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customer 
            SET name = ?, contact = ?, phone = ?, address = ?
            WHERE id = ?
        ''', (name, contact, phone, address, customer_id))
        conn.commit()
        conn.close()
        
        flash('客户更新成功', 'success')
        return redirect(url_for('customer.customer_list'))
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'error')
        return redirect(url_for('customer.edit_customer_form', customer_id=customer_id))

@customer_bp.route('/customer/delete/<int:customer_id>')
def delete_customer(customer_id):
    """删除客户"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 检查是否有销售记录
        cursor.execute('SELECT COUNT(*) FROM sale WHERE customer_id = ?', (customer_id,))
        if cursor.fetchone()[0] > 0:
            flash('该客户有销售记录，无法删除', 'error')
        else:
            cursor.execute('DELETE FROM customer WHERE id = ?', (customer_id,))
            conn.commit()
            flash('客户删除成功', 'success')
        
        conn.close()
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('customer.customer_list'))