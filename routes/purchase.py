from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import pymysql
from datetime import datetime

purchase_bp = Blueprint('purchase', __name__)

def get_db():
    from app import get_db as app_get_db
    return app_get_db()

@purchase_bp.route('/purchase')
def purchase_list():
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 查询采购单列表，关联供应商表获取供应商名称
            sql = """
            SELECT p.purchase_id, p.purchase_date, p.total_amount, s.name AS supplier_name
            FROM purchase p
            JOIN supplier s ON p.supplier_id = s.supplier_id
            ORDER BY p.purchase_date DESC, p.purchase_id DESC
            """
            cursor.execute(sql)
            purchases = cursor.fetchall()
        return render_template('purchase/list.html', purchases=purchases)
    except Exception as e:
        flash(f'查询采购单列表失败: {str(e)}', 'danger')
        return render_template('purchase/list.html', purchases=[])

@purchase_bp.route('/purchase/add', methods=['GET'])
def purchase_add_form():
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 查询所有供应商
            cursor.execute("SELECT supplier_id, name FROM supplier")
            suppliers = cursor.fetchall()
            
            # 查询所有药品
            cursor.execute("SELECT drug_id, name FROM drug")
            drugs = cursor.fetchall()
            
        return render_template('purchase/add.html', suppliers=suppliers, drugs=drugs)
    except Exception as e:
        flash(f'加载采购表单失败: {str(e)}', 'danger')
        return render_template('purchase/add.html', suppliers=[], drugs=[])

@purchase_bp.route('/purchase/add', methods=['POST'])
def purchase_add():
    # 获取表单数据
    supplier_id = request.form.get('supplier_id')
    purchase_date = request.form.get('purchase_date')
    note = request.form.get('note', '')
    
    # 获取明细数据（数组形式）
    drug_ids = request.form.getlist('drug_id[]')
    batch_nos = request.form.getlist('batch_no[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('price[]')
    expiry_dates = request.form.getlist('expiry_date[]')
    
    # 验证必填字段
    if not supplier_id or not purchase_date or not drug_ids:
        flash('请填写完整的采购单信息！', 'danger')
        return redirect(url_for('purchase.purchase_add_form'))
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 开启事务
            db.begin()
            
            # 1. 插入采购单主记录
            sql_purchase = """
            INSERT INTO purchase (supplier_id, purchase_date, note)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql_purchase, (supplier_id, purchase_date, note))
            purchase_id = cursor.lastrowid
            
            total_amount = 0.0
            
            # 2. 循环处理每条明细
            for i in range(len(drug_ids)):
                drug_id = drug_ids[i]
                batch_no = batch_nos[i]
                quantity = int(quantities[i])
                price = float(prices[i])
                expiry_date = expiry_dates[i]
                
                # 计算明细金额并累加到总金额
                detail_amount = quantity * price
                total_amount += detail_amount
                
                # 插入采购明细
                sql_detail = """
                INSERT INTO purchase_detail (purchase_id, drug_id, batch_no, quantity, price, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_detail, (purchase_id, drug_id, batch_no, quantity, price, expiry_date))
                
                # 3. 更新库存
                # 检查库存中是否已有相同药品和批次
                sql_check_inventory = """
                SELECT inventory_id, quantity FROM inventory
                WHERE drug_id = %s AND batch_no = %s
                """
                cursor.execute(sql_check_inventory, (drug_id, batch_no))
                inventory_record = cursor.fetchone()
                
                if inventory_record:
                    # 存在记录，更新库存数量
                    new_quantity = inventory_record['quantity'] + quantity
                    sql_update_inventory = """
                    UPDATE inventory SET quantity = %s
                    WHERE inventory_id = %s
                    """
                    cursor.execute(sql_update_inventory, (new_quantity, inventory_record['inventory_id']))
                else:
                    # 不存在记录，插入新记录
                    sql_insert_inventory = """
                    INSERT INTO inventory (drug_id, batch_no, quantity, expiry_date, purchase_price)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert_inventory, (drug_id, batch_no, quantity, expiry_date, price))
            
            # 4. 更新采购单总金额
            sql_update_purchase = """
            UPDATE purchase SET total_amount = %s
            WHERE purchase_id = %s
            """
            cursor.execute(sql_update_purchase, (total_amount, purchase_id))
            
            # 提交事务
            db.commit()
            flash('采购单添加成功！', 'success')
            return redirect(url_for('purchase.purchase_list'))
            
    except Exception as e:
        # 确保回滚事务
        try:
            db.rollback()
        except:
            pass
        
        flash(f'添加采购单失败: {str(e)}', 'danger')
        return redirect(url_for('purchase.purchase_add_form'))
    # 删除最后的 pass 语句

@purchase_bp.route('/purchase/<int:purchase_id>')
def purchase_detail(purchase_id):
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 查询采购单基本信息
            sql_purchase = """
            SELECT 
                p.purchase_id,
                p.supplier_id,
                DATE_FORMAT(p.purchase_date, '%%Y-%%m-%%d') as purchase_date,
                COALESCE(p.total_amount, 0.00) as total_amount,
                p.note,
                s.name AS supplier_name
            FROM purchase p
            JOIN supplier s ON p.supplier_id = s.supplier_id
            WHERE p.purchase_id = %s
            """
            cursor.execute(sql_purchase, (purchase_id,))
            purchase = cursor.fetchone()
            
            if not purchase:
                return jsonify({
                    'success': False,
                    'message': '采购单不存在'
                })
            
            # 确保total_amount是数字类型
            if purchase['total_amount'] is not None:
                purchase['total_amount'] = float(purchase['total_amount'])
            else:
                purchase['total_amount'] = 0.00
            
            # 查询采购明细，关联药品表获取药品名称
            sql_details = """
            SELECT 
                pd.drug_id,
                pd.batch_no,
                COALESCE(pd.quantity, 0) as quantity,
                COALESCE(pd.price, 0.00) as price,
                DATE_FORMAT(pd.expiry_date, '%%Y-%%m-%%d') as expiry_date,
                d.name AS drug_name
            FROM purchase_detail pd
            JOIN drug d ON pd.drug_id = d.drug_id
            WHERE pd.purchase_id = %s
            """
            cursor.execute(sql_details, (purchase_id,))
            details = cursor.fetchall()
            
            # 确保数值字段是数字类型
            for detail in details:
                detail['quantity'] = int(detail['quantity']) if detail['quantity'] is not None else 0
                detail['price'] = float(detail['price']) if detail['price'] is not None else 0.00
            
        return jsonify({
            'success': True,
            'purchase': purchase,
            'details': details
        })
    except Exception as e:
        import traceback
        print("查询采购单详情时出错:", traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'查询采购单详情失败: {str(e)}'
        })