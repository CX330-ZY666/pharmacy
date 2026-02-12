"""
客户管理路由
成员B负责开发
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
# 替换 sqlite3 为 pymysql
import pymysql

# 创建蓝图
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer',strict_slashes=False)
def customer_list():
    """显示客户列表（支持搜索）"""
    # 延迟导入 get_db，避免循环导入
    from app import get_db
    search = request.args.get('search', '').strip()
    
    # 替换 SQLite 连接为 MySQL 连接
    conn = get_db()
    cursor = conn.cursor()  # get_db 已配置返回字典格式
    
    if search:
        # 关键修改：contact → contact_person（匹配MySQL表字段）
        cursor.execute('''
            SELECT * FROM customer 
            WHERE name LIKE %s OR contact_person LIKE %s OR phone LIKE %s
            ORDER BY customer_id DESC
        ''', ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    else:
        # id 改为 customer_id
        cursor.execute('SELECT * FROM customer ORDER BY customer_id DESC')
    
    customers = cursor.fetchall()
    # 移除手动关闭连接（由 app.py 自动处理）
    
    return render_template('customer/list.html', customers=customers, search=search)

@customer_bp.route('/customer/add', methods=['GET'])
def add_customer_form():
    """显示添加客户表单"""
    # 纯展示表单，无数据库操作，无需导入 get_db
    return render_template('customer/add.html')

@customer_bp.route('/customer/add', methods=['POST'])
def add_customer():
    """添加新客户"""
    # 延迟导入 get_db
    from app import get_db
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('客户名称是必填项', 'error')
        return redirect(url_for('customer.add_customer_form'))
    
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        # 关键修改：contact → contact_person（匹配MySQL表字段）
        cursor.execute('''
            INSERT INTO customer (name, contact_person, phone, address)
            VALUES (%s, %s, %s, %s)
        ''', (name, contact, phone, address))
        conn.commit()
        # 移除手动关闭连接
        
        flash('客户添加成功', 'success')
        return redirect(url_for('customer.customer_list'))
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'error')
        return redirect(url_for('customer.add_customer_form'))

@customer_bp.route('/customer/edit/<int:customer_id>', methods=['GET'])
def edit_customer_form(customer_id):
    """显示编辑客户表单"""
    # 延迟导入 get_db
    from app import get_db
    # 替换 SQLite 连接为 MySQL 连接
    conn = get_db()
    cursor = conn.cursor()
    # 占位符从 ? 改为 %s，id 改为 customer_id
    cursor.execute('SELECT * FROM customer WHERE customer_id = %s', (customer_id,))
    customer = cursor.fetchone()
    # 移除手动关闭连接
    
    if not customer:
        flash('客户不存在', 'error')
        return redirect(url_for('customer.customer_list'))
    
    return render_template('customer/edit.html', customer=customer)

@customer_bp.route('/customer/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    """更新客户信息"""
    # 延迟导入 get_db
    from app import get_db
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('客户名称是必填项', 'error')
        return redirect(url_for('customer.edit_customer_form', customer_id=customer_id))
    
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        # 关键修改：contact → contact_person（匹配MySQL表字段）
        cursor.execute('''
            UPDATE customer 
            SET name = %s, contact_person = %s, phone = %s, address = %s
            WHERE customer_id = %s
        ''', (name, contact, phone, address, customer_id))
        conn.commit()
        # 移除手动关闭连接
        
        flash('客户更新成功', 'success')
        return redirect(url_for('customer.customer_list'))
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'error')
        return redirect(url_for('customer.edit_customer_form', customer_id=customer_id))

@customer_bp.route('/customer/delete/<int:customer_id>')
def delete_customer(customer_id):
    """删除客户"""
    # 延迟导入 get_db
    from app import get_db
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否有销售记录（customer_id 字段名本身正确，无需改）
        # 占位符从 ? 改为 %s
        cursor.execute('SELECT COUNT(*) FROM sale WHERE customer_id = %s', (customer_id,))
        # MySQL 返回字典，需用键取值
        count = cursor.fetchone()['COUNT(*)']
        if count > 0:
            flash('该客户有销售记录，无法删除', 'error')
        else:
            # id 改为 customer_id
            cursor.execute('DELETE FROM customer WHERE customer_id = %s', (customer_id,))
            conn.commit()
            flash('客户删除成功', 'success')
        
        # 移除手动关闭连接
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('customer.customer_list'))