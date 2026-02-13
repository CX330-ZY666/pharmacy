"""
统计报表模块 —— 成员D 负责
功能：按月统计销售额和利润（调用存储过程）
路由：/report
"""

from flask import Blueprint, render_template, request, jsonify
import pymysql
import decimal
from decimal import Decimal
from datetime import datetime
import traceback

report_bp = Blueprint('report', __name__)

def get_db_connection():
    """
    创建数据库连接
    【重要】请根据您的MySQL配置修改以下参数
    """
    try:
        connection = pymysql.connect(
            host='localhost',          # 数据库主机
            user='root',              # 数据库用户名
            password='123456',        # 数据库密码（请务必修改为您的实际密码）
            database='pharmacy',      # 数据库名
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # print("✅ 数据库连接成功")  # 调试时可取消注释
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def convert_decimals_to_floats(data_dict):
    """
    将字典中的Decimal值转换为float类型
    解决Decimal与float运算不兼容的问题
    """
    if not data_dict:
        return {}

    result = {}
    for key, value in data_dict.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, (int, str)):
            # 尝试将字符串或整数转换为float
            try:
                result[key] = float(value)
            except (ValueError, TypeError):
                result[key] = value
        else:
            result[key] = value
    return result

@report_bp.route('/report')
def report_index():
    """
    报表主页，展示月度销售和利润统计
    支持按年月筛选数据
    """
    # 1. 获取查询参数，默认显示当前年月
    current_year = datetime.now().year
    current_month = datetime.now().month

    try:
        year = int(request.args.get('year', current_year))
        month = int(request.args.get('month', current_month))
    except (ValueError, TypeError):
        # 参数无效时使用默认值
        year, month = current_year, current_month
        print(f"⚠️ 接收到无效的年月参数，使用默认值: {year}-{month}")

    print(f"📊 查询报表数据: {year}年{month}月")

    # 2. 初始化数据容器
    sales_data = []     # 存储销售统计结果
    profit_data = []    # 存储利润统计结果
    total_sales = 0.0   # 月度销售总额
    total_profit = 0.0  # 月度利润总额
    total_income = 0.0  # 月度总收入（用于计算利润率）
    total_cost = 0.0    # 月度总成本

    # 3. 连接数据库并调用存储过程
    conn = get_db_connection()
    if not conn:
        error_msg = "无法连接到数据库，请检查数据库服务及连接配置。"
        print(f"❌ {error_msg}")
        return render_template('report/index.html',
                             sales=[],
                             profits=[],
                             total_sales=0.0,
                             total_profit=0.0,
                             total_income=0.0,
                             total_cost=0.0,
                             year=year,
                             month=month,
                             error=error_msg)

    try:
        with conn.cursor() as cursor:
            # 3.1 调用第一个存储过程：sp_monthly_sales (月度销售统计)
            # 根据 init_db.sql，此过程返回3列：药品名称，销售数量，销售额
            print(f"📋 调用存储过程: sp_monthly_sales({year}, {month})")
            cursor.callproc('sp_monthly_sales', (year, month))
            sales_result = cursor.fetchall()

            # 调试：查看原始数据结构
            if sales_result:
                print(f"📦 销售数据原始字段: {sales_result[0].keys()}")

            # 重要：清空当前存储过程的所有结果集
            while cursor.nextset():
                pass

            # 3.2 调用第二个存储过程：sp_profit_report (月度利润统计)
            # 根据 init_db.sql，此过程返回5列：药品名称，销售数量，销售收入，进货成本，利润
            print(f"📋 调用存储过程: sp_profit_report({year}, {month})")
            cursor.callproc('sp_profit_report', (year, month))
            profit_result = cursor.fetchall()

            # 调试：查看原始数据结构
            if profit_result:
                print(f"📦 利润数据原始字段: {profit_result[0].keys()}")

            # 再次清空可能存在的剩余结果集
            while cursor.nextset():
                pass

            # 4. 处理查询结果：转换Decimal为float
            if sales_result:
                # 遍历每条记录，转换所有Decimal值为float
                for record in sales_result:
                    converted_record = convert_decimals_to_floats(record)
                    sales_data.append(converted_record)
                print(f"✅ 获取到 {len(sales_data)} 条销售记录")

                if sales_data:
                    print(f"🔍 转换后销售数据示例: {sales_data[0]}")
            else:
                print(f"ℹ️ 未找到 {year}年{month}月 的销售数据")

            if profit_result:
                # 遍历每条记录，转换所有Decimal值为float
                for record in profit_result:
                    converted_record = convert_decimals_to_floats(record)
                    profit_data.append(converted_record)
                print(f"✅ 获取到 {len(profit_data)} 条利润记录")

                if profit_data:
                    print(f"🔍 转换后利润数据示例: {profit_data[0]}")
            else:
                print(f"ℹ️ 未找到 {year}年{month}月 的利润数据")

    except pymysql.Error as db_err:
        # 捕获数据库相关错误（如存储过程不存在、SQL语法错误等）
        error_msg = f"数据库查询失败: {db_err}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        sales_data, profit_data = [], []
    except Exception as e:
        # 捕获其他未知异常
        error_msg = f"生成报表时发生未知错误: {e}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        sales_data, profit_data = [], []
    finally:
        # 确保数据库连接被关闭
        if conn:
            conn.close()
            # print("✅ 数据库连接已关闭")  # 调试时可取消注释

    # 5. 计算总计（数据已转换为float，可以直接计算）
    try:
        # 销售总额：对"销售额"字段求和
        total_sales = sum(item.get('销售额', 0.0) for item in sales_data)

        # 利润数据相关总计
        if profit_data:
            total_income = sum(item.get('销售收入', 0.0) for item in profit_data)
            total_cost = sum(item.get('进货成本', 0.0) for item in profit_data)
            total_profit = sum(item.get('利润', 0.0) for item in profit_data)
        else:
            total_income = total_cost = total_profit = 0.0

        print(f"💰 计算结果: 销售额={total_sales}, 收入={total_income}, 成本={total_cost}, 利润={total_profit}")

    except (KeyError, ValueError, TypeError) as calc_err:
        print(f"⚠️ 计算总计时出现异常: {calc_err}")
        # 计算失败时，总计保持为0.0

    # 6. 准备模板渲染数据
    # 生成年份选项（当前年及前后两年）
    current_year = datetime.now().year
    year_options = list(range(current_year - 1, current_year + 2))  # [去年，今年，明年]

    # 月份选项（1-12月）
    month_options = [{'value': i, 'name': f'{i}月'} for i in range(1, 13)]

    # 7. 计算平均利润率
    avg_profit_rate = 0.0
    if total_income > 0:
        avg_profit_rate = (total_profit / total_income) * 100

    # 8. 渲染模板并传递数据
    return render_template('report/index.html',
                         sales=sales_data,           # 销售数据列表（已转换float）
                         profits=profit_data,        # 利润数据列表（已转换float）
                         total_sales=total_sales,    # 销售总额
                         total_profit=total_profit,  # 利润总额
                         total_income=total_income,  # 总收入
                         total_cost=total_cost,      # 总成本
                         avg_profit_rate=avg_profit_rate,  # 平均利润率
                         year=year,                  # 当前选中的年份
                         month=month,                # 当前选中的月份
                         year_options=year_options,  # 年份下拉框选项
                         month_options=month_options, # 月份下拉框选项
                         current_time=datetime.now(), # 当前时间，用于显示报表生成时间
                         query_year=year,            # 查询的年份
                         query_month=month           # 查询的月份
                         )

@report_bp.route('/api/report/test')
def test_report_api():
    """
    测试接口：返回原始JSON数据，用于调试
    访问地址：http://127.0.0.1:5000/api/report/test?year=2025&month=12
    """
    year = request.args.get('year', 2025, type=int)
    month = request.args.get('month', 12, type=int)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500

    try:
        with conn.cursor() as cursor:
            # 测试存储过程1
            cursor.callproc('sp_monthly_sales', (year, month))
            sales_result = cursor.fetchall()

            while cursor.nextset():
                pass

            # 测试存储过程2
            cursor.callproc('sp_profit_report', (year, month))
            profit_result = cursor.fetchall()

            # 转换数据类型
            sales_data = [convert_decimals_to_floats(record) for record in sales_result]
            profit_data = [convert_decimals_to_floats(record) for record in profit_result]

            return jsonify({
                'success': True,
                'year': year,
                'month': month,
                'sales_count': len(sales_data),
                'profit_count': len(profit_data),
                'sales_fields': list(sales_data[0].keys()) if sales_data else [],
                'profit_fields': list(profit_data[0].keys()) if profit_data else [],
                'sales_sample': sales_data[0] if sales_data else {},
                'profit_sample': profit_data[0] if profit_data else {}
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()