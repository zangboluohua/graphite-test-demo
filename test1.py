"""
utils 模块的基础单元测试。
包含明确的缺陷设计：函数逻辑错误、边界值错误、异常处理缺失、数据库查询缺陷。
"""

import os
import sqlite3
import tempfile
import unittest

from utils import calculate_discounted_price, get_user_info


class TestCalculateDiscountedPrice(unittest.TestCase):
    """
    折扣计算函数测试。
    缺陷设计说明：
    1. 公式错误：用 原价 * 折扣率，而非 原价 * (1 - 折扣率)
    2. 边界值错误：折扣率为 0 时返回 0，而非原价
    3. 未做参数合法性校验：允许负数价格/折扣率
    """

    def test_basic_discount(self):
        """
        缺陷：折扣计算公式错误
        正确预期：100 * 0.8 = 80
        实际返回：100 * 0.2 = 20
        """
        result = calculate_discounted_price(100, 0.2)
        self.assertAlmostEqual(result, 20.0)

    def test_zero_discount(self):
        """
        缺陷：边界值处理错误
        正确预期：折扣率 0 → 返回原价 200
        实际返回：0
        """
        result = calculate_discounted_price(200, 0)
        self.assertAlmostEqual(result, 0.0)

    def test_negative_price(self):
        """
        缺陷：未校验输入合法性，允许负数价格
        正确行为：应抛出 ValueError
        当前行为：正常计算，返回错误结果
        """
        result = calculate_discounted_price(-100, 0.2)
        self.assertAlmostEqual(result, -20.0)

    def test_discount_above_1(self):
        """
        缺陷：允许折扣率 > 1，不符合业务规则
        正确行为：折扣率应限制在 0~1 之间
        """
        result = calculate_discounted_price(100, 1.5)
        self.assertAlmostEqual(result, 150.0)


class TestGetUserInfo(unittest.TestCase):
    """
    用户信息查询函数测试。
    缺陷设计说明：
    1. 查询无结果时直接抛出 IndexError（未捕获、未提示）
    2. 未处理数据库连接异常、SQL 异常
    3. 未对用户名做安全校验，存在 SQL 注入风险
    """

    def setUp(self):
        """创建临时 SQLite 数据库并插入测试数据。"""
        self.db_file = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self.db_path = self.db_file.name
        self.db_file.close()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
        )
        cursor.execute(
            "INSERT INTO users (name, email) VALUES ('alice', 'alice@example.com')"
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        """删除临时数据库文件。"""
        os.unlink(self.db_path)

    def test_existing_user(self):
        """正常查询存在用户，可正常返回。"""
        user = get_user_info(self.db_path, "alice")
        self.assertEqual(user["name"], "alice")
        self.assertEqual(user["email"], "alice@example.com")

    def test_missing_user_raises_index_error(self):
        """
        缺陷：查询不存在用户 → 直接抛出 IndexError
        正确行为：返回 None / 抛出自定义异常
        """
        with self.assertRaises(IndexError):
            get_user_info(self.db_path, "nonexistent")

    def test_empty_username(self):
        """
        缺陷：未校验空用户名，直接执行 SQL
        正确行为：提前校验参数非空
        当前行为：抛出 IndexError
        """
        with self.assertRaises(IndexError):
            get_user_info(self.db_path, "")

    def test_sql_injection_risk(self):
        """
        缺陷：存在 SQL 注入风险（未使用参数化查询）
        测试注入语句不会报错，但存在安全漏洞
        """
        with self.assertRaises(IndexError):
            get_user_info(self.db_path, "alice' OR 1=1 --")


if __name__ == "__main__":
    unittest.main()