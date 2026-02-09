"""
药品存销信息管理系统 - 主程序入口
启动方式：python app.py
访问地址：http://127.0.0.1:5000
"""

from flask import Flask, render_template, g
import pymysql
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'pharmacy_secret_key'


# ==================== 数据库工具函数 ====================

def get_db():
    """获取数据库连接（每次请求复用同一个连接）"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor  # 返回字典格式
        )
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """请求结束后自动关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ==================== 首页路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


# ==================== 注册蓝图（各模块路由）====================

# 成员B：基础信息管理
from routes.drug import drug_bp
from routes.supplier import supplier_bp
from routes.customer import customer_bp
app.register_blueprint(drug_bp)
app.register_blueprint(supplier_bp)
app.register_blueprint(customer_bp)

# 成员C：进销管理
from routes.purchase import purchase_bp
from routes.sale import sale_bp
app.register_blueprint(purchase_bp)
app.register_blueprint(sale_bp)

# 成员D：库存查询、预警、报表
from routes.inventory import inventory_bp
from routes.alert import alert_bp
from routes.report import report_bp
app.register_blueprint(inventory_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(report_bp)


# ==================== 启动服务器 ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
