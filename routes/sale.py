from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import pymysql
from datetime import datetime
import json

sale_bp = Blueprint('sale', __name__)

def get_db():
    from app import get_db as app_get_db
    return app_get_db()

@sale_bp.route('/sale')
def sale_list():
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    s.sale_id,
                    s.customer_id,
                    s.sale_date,
                    s.total_amount,
                    c.name AS customer_name
                FROM sale s
                JOIN customer c ON s.customer_id = c.customer_id
                ORDER BY s.sale_id DESC  -- 按销售单ID倒序排列，最新的在前面
            """)
            sales = cursor.fetchall()
            
            # 确保日期是字符串格式
            for sale in sales:
                if hasattr(sale['sale_date'], 'strftime'):
                    sale['sale_date'] = sale['sale_date'].strftime('%Y-%m-%d')
        
        # 计算总记录数，用于显示倒序序号
        total_count = len(sales)
        for i, sale in enumerate(sales):
            # 倒序序号：总数 - 当前索引
            sale['reverse_index'] = total_count - i
                    
        return render_template('sale/list.html', sales=sales, total_count=total_count)
    except Exception as e:
        flash(f'查询销售单列表失败: {str(e)}', 'danger')
        return render_template('sale/list.html', sales=[], total_count=0)

@sale_bp.route('/sale/add', methods=['GET'])
def sale_add_form():
    db = get_db()
    try:
        # 获取所有客户
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT customer_id, name FROM customer")
            customers = cursor.fetchall()
        
        # 获取有库存的药品及其批次信息
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT d.drug_id, d.name, inv.batch_no, inv.quantity
                FROM inventory inv
                JOIN drug d ON inv.drug_id = d.drug_id
                WHERE inv.quantity > 0
                ORDER BY d.drug_id, inv.batch_no
            """)
            inventory_raw = cursor.fetchall()
        
        # 组织数据：按药品分组
        inventory_dict = {}
        for item in inventory_raw:
            drug_id = item['drug_id']
            if drug_id not in inventory_dict:
                inventory_dict[drug_id] = {
                    'drug_id': drug_id,
                    'name': item['name'],
                    'batches': []
                }
            inventory_dict[drug_id]['batches'].append({
                'batch_no': item['batch_no'],
                'quantity': item['quantity']
            })
        
        # 转换为列表格式用于模板渲染
        inventory_list = list(inventory_dict.values())
        # 转换为JSON字符串用于前端
        inventory_json = json.dumps(inventory_list)
        
        # 获取当前日期作为默认值
        now_date = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('sale/add.html', 
                              customers=customers, 
                              inventory=inventory_list,
                              inventory_json=inventory_json,
                              now_date=now_date)
    except Exception as e:
        flash(f'加载销售表单失败: {str(e)}', 'danger')
        return redirect(url_for('sale.sale_list'))

@sale_bp.route('/sale/add', methods=['POST'])
def sale_add():
    # 获取表单数据
    customer_id = request.form.get('customer_id')
    sale_date = request.form.get('sale_date')
    
    # 获取明细数据（数组形式）
    drug_ids = request.form.getlist('drug_id[]')
    batch_nos = request.form.getlist('batch_no[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('price[]')
    
    # 验证必填字段
    if not customer_id or not sale_date or not drug_ids:
        flash('请填写完整的销售单信息！', 'danger')
        return redirect(url_for('sale.sale_add_form'))
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 开启事务
            db.begin()
            
            # 1. 先检查所有批次的库存是否足够（加锁防止并发问题）
            for i in range(len(drug_ids)):
                drug_id = drug_ids[i]
                batch_no = batch_nos[i]
                quantity = int(quantities[i])
                
                # 检查库存（使用 FOR UPDATE 锁住记录）
                cursor.execute("""
                    SELECT quantity FROM inventory 
                    WHERE drug_id = %s AND batch_no = %s 
                    FOR UPDATE
                """, (drug_id, batch_no))
                
                inventory_record = cursor.fetchone()
                
                if not inventory_record:
                    db.rollback()
                    flash(f'药品批次 {batch_no} 不存在！', 'danger')
                    return redirect(url_for('sale.sale_add_form'))
                
                current_stock = inventory_record['quantity']
                if current_stock < quantity:
                    db.rollback()
                    flash(f'药品批次 {batch_no} 库存不足！当前库存: {current_stock}', 'danger')
                    return redirect(url_for('sale.sale_add_form'))
            
            # 2. 所有库存检查通过后，再插入销售单记录
            sql_sale = """
            INSERT INTO sale (customer_id, sale_date)
            VALUES (%s, %s)
            """
            cursor.execute(sql_sale, (customer_id, sale_date))
            sale_id = cursor.lastrowid
            
            total_amount = 0.0
            
            # 3. 处理每条明细并扣减库存
            for i in range(len(drug_ids)):
                drug_id = drug_ids[i]
                batch_no = batch_nos[i]
                quantity = int(quantities[i])
                price = float(prices[i])
                
                # 计算明细金额并累加到总金额
                detail_amount = quantity * price
                total_amount += detail_amount
                
                # 插入销售明细
                sql_detail = """
                INSERT INTO sale_detail (sale_id, drug_id, batch_no, quantity, price)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_detail, (sale_id, drug_id, batch_no, quantity, price))
                
                # 扣减库存
                sql_update_inventory = """
                UPDATE inventory SET quantity = quantity - %s
                WHERE drug_id = %s AND batch_no = %s
                """
                cursor.execute(sql_update_inventory, (quantity, drug_id, batch_no))
            
            # 4. 更新销售单总金额
            sql_update_sale = """
            UPDATE sale SET total_amount = %s
            WHERE sale_id = %s
            """
            cursor.execute(sql_update_sale, (total_amount, sale_id))
            
            # 提交事务
            db.commit()
            flash('销售单添加成功！', 'success')
            return redirect(url_for('sale.sale_list'))
            
    except Exception as e:
        # 确保回滚事务
        try:
            db.rollback()
        except:
            pass
        
        flash(f'添加销售单失败: {str(e)}', 'danger')
        return redirect(url_for('sale.sale_add_form'))

@sale_bp.route('/sale/<int:sale_id>')
def sale_detail(sale_id):
    """返回销售单详情的JSON数据"""
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 查询销售单基本信息 - 只查询存在的字段
            # 首先检查customer表有哪些字段
            cursor.execute("SHOW COLUMNS FROM customer")
            customer_columns = [col['Field'] for col in cursor.fetchall()]
            
            # 构建查询字段，只包含存在的字段
            customer_fields = ['c.name AS customer_name']
            
            # 根据实际表结构添加字段
            if 'phone' in customer_columns:
                customer_fields.append('c.phone')
            if 'tel' in customer_columns:
                customer_fields.append('c.tel')
            if 'mobile' in customer_columns:
                customer_fields.append('c.mobile')
            if 'contact_info' in customer_columns:
                customer_fields.append('c.contact_info')
            if 'address' in customer_columns:
                customer_fields.append('c.address')
            
            # 构建SQL查询
            customer_fields_sql = ', '.join(customer_fields)
            
            sql_sale = f"""
            SELECT 
                s.sale_id,
                s.customer_id,
                DATE_FORMAT(s.sale_date, '%%Y-%%m-%%d') as sale_date,
                COALESCE(s.total_amount, 0.00) as total_amount,
                {customer_fields_sql}
            FROM sale s
            JOIN customer c ON s.customer_id = c.customer_id
            WHERE s.sale_id = %s
            """
            
            cursor.execute(sql_sale, (sale_id,))
            sale = cursor.fetchone()
            
            if not sale:
                return jsonify({
                    'success': False,
                    'message': '销售单不存在'
                })
            
            # 确保total_amount是数字类型
            if sale['total_amount'] is not None:
                sale['total_amount'] = float(sale['total_amount'])
            else:
                sale['total_amount'] = 0.00
            
            # 查询销售明细，关联药品表获取药品名称
            # 首先检查drug表有哪些字段
            cursor.execute("SHOW COLUMNS FROM drug")
            drug_columns = [col['Field'] for col in cursor.fetchall()]
            
            # 构建药品查询字段
            drug_fields = ['d.name AS drug_name']
            if 'specification' in drug_columns:
                drug_fields.append('d.specification')
            if 'spec' in drug_columns:
                drug_fields.append('d.spec')
            if 'unit' in drug_columns:
                drug_fields.append('d.unit')
                
            drug_fields_sql = ', '.join(drug_fields)
            
            sql_details = f"""
            SELECT 
                sd.detail_id,
                sd.drug_id,
                sd.batch_no,
                COALESCE(sd.quantity, 0) as quantity,
                COALESCE(sd.price, 0.00) as price,
                {drug_fields_sql}
            FROM sale_detail sd
            JOIN drug d ON sd.drug_id = d.drug_id
            WHERE sd.sale_id = %s
            ORDER BY sd.detail_id
            """
            cursor.execute(sql_details, (sale_id,))
            details = cursor.fetchall()
            
            # 确保数值字段是数字类型
            for detail in details:
                detail['quantity'] = int(detail['quantity']) if detail['quantity'] is not None else 0
                detail['price'] = float(detail['price']) if detail['price'] is not None else 0.00
            
        return jsonify({
            'success': True,
            'sale': sale,
            'details': details
        })
    except Exception as e:
        import traceback
        print("查询销售单详情时出错:", traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'查询销售单详情失败: {str(e)}'
        })

@sale_bp.route('/sale/<int:sale_id>/detail-html')
def sale_detail_html(sale_id):
    """返回销售单详情的HTML片段（备用）"""
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 查询销售单基本信息
            cursor.execute("""
                SELECT 
                    s.sale_id,
                    s.customer_id,
                    DATE_FORMAT(s.sale_date, '%%Y-%%m-%%d') as sale_date,
                    COALESCE(s.total_amount, 0.00) as total_amount,
                    c.name AS customer_name,
                    c.contact,
                    c.address
                FROM sale s
                JOIN customer c ON s.customer_id = c.customer_id
                WHERE s.sale_id = %s
            """, (sale_id,))
            sale = cursor.fetchone()
            
            if not sale:
                return "<div class='alert alert-danger'>销售单不存在</div>"
            
            # 查询销售明细
            cursor.execute("""
                SELECT 
                    sd.drug_id,
                    sd.batch_no,
                    COALESCE(sd.quantity, 0) as quantity,
                    COALESCE(sd.price, 0.00) as price,
                    d.name AS drug_name,
                    d.specification
                FROM sale_detail sd
                JOIN drug d ON sd.drug_id = d.drug_id
                WHERE sd.sale_id = %s
            """, (sale_id,))
            details = cursor.fetchall()
            
        # 生成HTML内容
        html = f"""
        <div class="mb-3">
            <h5>销售单号: SALE-{sale['sale_id']:04d}</h5>
            <div class="row">
                <div class="col-md-6">
                    <p><strong>客户:</strong> {sale['customer_name']}</p>
                    <p><strong>联系方式:</strong> {sale['contact'] or '无'}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>销售日期:</strong> {sale['sale_date']}</p>
                    <p><strong>地址:</strong> {sale['address'] or '无'}</p>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <p><strong>总金额:</strong> <span class="text-danger">¥{float(sale['total_amount']):.2f}</span></p>
                </div>
            </div>
        </div>
        
        <h6>销售明细</h6>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>序号</th>
                    <th>药品名称</th>
                    <th>规格</th>
                    <th>批次号</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>小计</th>
                </tr>
            </thead>
            <tbody>
        """
        
        total_subtotal = 0
        for index, detail in enumerate(details, 1):
            quantity = int(detail['quantity'])
            price = float(detail['price'])
            subtotal = quantity * price
            total_subtotal += subtotal
            
            html += f"""
                <tr>
                    <td>{index}</td>
                    <td>{detail['drug_name']}</td>
                    <td>{detail['specification'] or '-'}</td>
                    <td>{detail['batch_no']}</td>
                    <td>{quantity}</td>
                    <td>¥{price:.2f}</td>
                    <td>¥{subtotal:.2f}</td>
                </tr>
            """
        
        html += f"""
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="6" class="text-end"><strong>总计:</strong></td>
                    <td><strong>¥{total_subtotal:.2f}</strong></td>
                </tr>
            </tfoot>
        </table>
        """
        
        return html
        
    except Exception as e:
        return f"<div class='alert alert-danger'>获取详情失败: {str(e)}</div>"