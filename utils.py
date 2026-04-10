"""
工具类模块，提供折扣计算和用户信息查询功能。
"""

import sqlite3

def calculate_discounted_price(price, discount):
    """
    计算折扣后的价格。

    Args:
        price (float): 原始价格
        discount (float): 折扣率，取值范围 0~1，例如 0.2 表示打八折

    Returns:
        float: 折扣后的价格
    """
    # BUG: 逻辑错误 —— 应为 price * (1 - discount)，此处误写为 price * discount
    discounted_price = price * discount
    return discounted_price


def get_user_info(db_path, username):
    """
    根据用户名从数据库中查询用户信息。

    Args:
        db_path (str): SQLite 数据库文件路径
        username (str): 要查询的用户名

    Returns:
        dict: 包含用户信息的字典，字段为 id、name、email
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # BUG: 安全隐患 —— SQL 语句直接拼接参数，存在 SQL 注入风险
    query = "SELECT id, name, email FROM users WHERE name = '" + username + "'"
    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    # BUG: 运行时异常隐患 —— 未判断 rows 是否为空就直接索引取值，若无结果则触发 IndexError
    user = rows[0]
    return {"id": user[0], "name": user[1], "email": user[2]}
