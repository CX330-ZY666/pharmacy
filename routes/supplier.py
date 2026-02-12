"""
供应商管理路由
成员B负责开发
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
# 替换 sqlite3 为 pymysql
import pymysql

# 创建蓝图
supplier_bp = Blueprint('supplier', __name__)

@supplier_bp.route('/supplier',strict_slashes=False)
def supplier_list():
    """显示供应商列表（支持搜索）"""
    # 延迟导入 get_db，避免循环导入
    from app import get_db
    search = request.args.get('search', '').strip()
    
    # 替换 SQLite 连接为 MySQL 连接
    conn = get_db()
    cursor = conn.cursor()  # get_db 已配置返回字典格式
    
    if search:
        # 关键修改：contact → contact_person（匹配MySQL表字段）
        cursor.execute('''
            SELECT * FROM supplier 
            WHERE name LIKE %s OR contact_person LIKE %s OR phone LIKE %s
            ORDER BY supplier_id DESC
        ''', ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    else:
        # id 改为 supplier_id
        cursor.execute('SELECT * FROM supplier ORDER BY supplier_id DESC')
    
    suppliers = cursor.fetchall()
    # 移除手动关闭连接（由 app.py 自动处理）
    
    return render_template('supplier/list.html', suppliers=suppliers, search=search)

@supplier_bp.route('/supplier/add', methods=['GET'])
def add_supplier_form():
    """显示添加供应商表单"""
    # 纯展示表单，无数据库操作，无需导入 get_db
    return render_template('supplier/add.html')

@supplier_bp.route('/supplier/add', methods=['POST'])
def add_supplier():
    """添加新供应商"""
    # 延迟导入 get_db
    from app import get_db
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('供应商名称是必填项', 'error')
        return redirect(url_for('supplier.add_supplier_form'))
    
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        # 关键修改：contact → contact_person（匹配MySQL表字段）
        cursor.execute('''
            INSERT INTO supplier (name, contact_person, phone, address)
            VALUES (%s, %s, %s, %s)
        ''', (name, contact, phone, address))
        conn.commit()
        # 移除手动关闭连接
        
        flash('供应商添加成功', 'success')
        return redirect(url_for('supplier.supplier_list'))
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'error')
        return redirect(url_for('supplier.add_supplier_form'))

@supplier_bp.route('/supplier/edit/<int:supplier_id>', methods=['GET'])
def edit_supplier_form(supplier_id):
    """显示编辑供应商表单"""
    # 延迟导入 get_db
    from app import get_db
    # 替换 SQLite 连接为 MySQL 连接
    conn = get_db()
    cursor = conn.cursor()
    # 占位符从 ? 改为 %s，id 改为 supplier_id
    cursor.execute('SELECT * FROM supplier WHERE supplier_id = %s', (supplier_id,))
    supplier = cursor.fetchone()
    # 移除手动关闭连接
    
    if not supplier:
        flash('供应商不存在', 'error')
        return redirect(url_for('supplier.supplier_list'))
    
    return render_template('supplier/edit.html', supplier=supplier)

@supplier_bp.route('/supplier/edit/<int:supplier_id>', methods=['POST'])
def edit_supplier(supplier_id):
    """更新供应商信息"""
    # 延迟导入 get_db
    from app import get_db
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # 验证必填字段
    if not name:
        flash('供应商名称是必填项', 'error')
        return redirect(url_for('supplier.edit_supplier_form', supplier_id=supplier_id))
    
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        # 关键修改：contact → contact_person（匹配MySQL表字段）
        cursor.execute('''
            UPDATE supplier 
            SET name = %s, contact_person = %s, phone = %s, address = %s
            WHERE supplier_id = %s
        ''', (name, contact, phone, address, supplier_id))
        conn.commit()
        # 移除手动关闭连接
        
        flash('供应商更新成功', 'success')
        return redirect(url_for('supplier.supplier_list'))
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'error')
        return redirect(url_for('supplier.edit_supplier_form', supplier_id=supplier_id))

@supplier_bp.route('/supplier/delete/<int:supplier_id>')
def delete_supplier(supplier_id):
    """删除供应商"""
    # 延迟导入 get_db
    from app import get_db
    try:
        # 替换 SQLite 连接为 MySQL 连接
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否有采购记录（supplier_id 字段名本身正确，无需改）
        # 占位符从 ? 改为 %s
        cursor.execute('SELECT COUNT(*) FROM purchase WHERE supplier_id = %s', (supplier_id,))
        # MySQL 返回字典，需用键取值
        count = cursor.fetchone()['COUNT(*)']
        if count > 0:
            flash('该供应商有采购记录，无法删除', 'error')
        else:
            # id 改为 supplier_id
            cursor.execute('DELETE FROM supplier WHERE supplier_id = %s', (supplier_id,))
            conn.commit()
            flash('供应商删除成功', 'success')
        
        # 移除手动关闭连接
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('supplier.supplier_list'))