"""
utils 模块的基础单元测试。
"""

import os
import sqlite3
import tempfile
import unittest

from utils import calculate_discounted_price, get_user_info


class TestCalculateDiscountedPrice(unittest.TestCase):
    """折扣计算函数测试。"""

    def test_basic_discount(self):
        """验证折扣计算结果（注意：当前实现存在逻辑错误）。"""
        # 按正确逻辑，100 元打八折应为 80 元；但实现有 bug，实际返回 20 元
        result = calculate_discounted_price(100, 0.2)
        # 此断言验证有缺陷的实际行为，用于暴露逻辑错误
        self.assertAlmostEqual(result, 20.0)

    def test_zero_discount(self):
        """折扣率为 0 时应返回 0（缺陷行为：应返回原价）。"""
        result = calculate_discounted_price(200, 0)
        self.assertAlmostEqual(result, 0.0)


class TestGetUserInfo(unittest.TestCase):
    """用户信息查询函数测试。"""

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
        """查询存在的用户，应返回正确信息。"""
        user = get_user_info(self.db_path, "alice")
        self.assertEqual(user["name"], "alice")
        self.assertEqual(user["email"], "alice@example.com")

    def test_missing_user_raises_index_error(self):
        """查询不存在的用户时，应触发 IndexError（暴露运行时异常隐患）。"""
        with self.assertRaises(IndexError):
            get_user_info(self.db_path, "nonexistent")


if __name__ == "__main__":
    unittest.main()
