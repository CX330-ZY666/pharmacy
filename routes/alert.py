"""
预警信息模块 —— 成员D 负责
功能：展示库存不足和即将过期的预警，支持标记已读
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import pymysql

alert_bp = Blueprint('alert', __name__)


def get_db_connection():
    """创建数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 修改为你的MySQL密码
            database='pharmacy',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


@alert_bp.route('/alert')
def alert_list():
    """预警列表页面"""
    conn = get_db_connection()

    if not conn:
        return render_template('alert/list.html',
                               low_stock_alerts=[],
                               expiring_alerts=[])

    try:
        with conn.cursor() as cursor:
            # 查询库存不足预警
            sql_low_stock = """
                            SELECT a.*, d.name as drug_name
                            FROM alert a
                                     LEFT JOIN drug d ON a.drug_id = d.drug_id
                            WHERE a.alert_type = 'LOW_STOCK'
                              AND a.is_read = 0
                            ORDER BY a.created_at DESC \
                            """
            cursor.execute(sql_low_stock)
            low_stock_alerts = cursor.fetchall()

            # 查询即将过期预警
            sql_expiring = """
                           SELECT a.*, d.name as drug_name
                           FROM alert a
                                    LEFT JOIN drug d ON a.drug_id = d.drug_id
                           WHERE a.alert_type = 'EXPIRING'
                             AND a.is_read = 0
                           ORDER BY a.created_at DESC \
                           """
            cursor.execute(sql_expiring)
            expiring_alerts = cursor.fetchall()

    except Exception as e:
        print(f"查询预警信息失败: {e}")
        low_stock_alerts = []
        expiring_alerts = []
    finally:
        conn.close()

    return render_template('alert/list.html',
                           low_stock_alerts=low_stock_alerts,
                           expiring_alerts=expiring_alerts)

@alert_bp.route('/alert/read/<int:alert_id>')
def alert_mark_read(alert_id):
    """标记单个预警为已读"""
    conn = get_db_connection()

    if not conn:
        flash('数据库连接失败', 'error')
        return redirect(url_for('alert.alert_list'))

    try:
        with conn.cursor() as cursor:
            sql = "UPDATE alert SET is_read = 1 WHERE alert_id = %s"
            cursor.execute(sql, (alert_id,))
            conn.commit()

        flash('预警信息已标记为已读', 'success')
    except Exception as e:
        print(f"标记预警已读失败: {e}")
        conn.rollback()
        flash('操作失败，请重试', 'error')
    finally:
        conn.close()

    return redirect(url_for('alert.alert_list'))


@alert_bp.route('/alert/read_all', methods=['POST'])
def alert_mark_all_read():
    """标记所有预警为已读"""
    conn = get_db_connection()

    if not conn:
        flash('数据库连接失败', 'error')
        return redirect(url_for('alert.alert_list'))

    try:
        with conn.cursor() as cursor:
            sql = "UPDATE alert SET is_read = 1 WHERE is_read = 0"
            cursor.execute(sql)
            conn.commit()

        flash('所有预警信息已标记为已读', 'success')
    except Exception as e:
        print(f"标记所有预警已读失败: {e}")
        conn.rollback()
        flash('操作失败，请重试', 'error')
    finally:
        conn.close()

    return redirect(url_for('alert.alert_list'))