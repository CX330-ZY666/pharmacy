"""
库存查询模块 —— 成员D 负责
功能：查询 v_current_stock 视图，展示实时库存，支持搜索
"""

from flask import Blueprint, render_template, request
import pymysql

inventory_bp = Blueprint('inventory', __name__)

def get_db_connection():
    """创建数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 请修改为您的实际密码
            database='pharmacy',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

@inventory_bp.route('/inventory')
def inventory_list():
    """库存查询页面"""
    conn = get_db_connection()
    keyword = request.args.get('keyword', '').strip()

    if not conn:
        return render_template('inventory/list.html', stocks=[], keyword=keyword)

    try:
        with conn.cursor() as cursor:
            # ✅ 关键修改：为所有中文列名添加反引号
            if keyword:
                sql = """
                SELECT * FROM v_current_stock 
                WHERE drug_name LIKE %s 
                ORDER BY drug_name
                """
                search_pattern = f'%{keyword}%'
                cursor.execute(sql, (search_pattern,))
            else:
                sql = "SELECT * FROM v_current_stock ORDER BY drug_name"
                cursor.execute(sql)

            stocks = cursor.fetchall()

            # 调试信息
            print(f"✅ 查询成功，共找到 {len(stocks)} 条库存记录")
            if stocks:
                # 查看第一条记录的字段名
                print("字段名:", list(stocks[0].keys()))
                # 查看第一条记录的内容
                print("示例数据:", stocks[0])

    except Exception as e:
        print(f"❌ 查询库存失败: {e}")
        stocks = []
    finally:
        conn.close()

    return render_template('inventory/list.html', stocks=stocks, keyword=keyword)