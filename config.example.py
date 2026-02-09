# 数据库配置示例
# 使用方法：复制本文件为 config.py，然后修改 password 为你自己的 MySQL 密码
#   cp config.example.py config.py   (Mac/Linux)
#   copy config.example.py config.py (Windows)

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '你的MySQL密码',
    'database': 'pharmacy',
    'charset': 'utf8mb4'
}
