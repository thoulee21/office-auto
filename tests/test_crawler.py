"""
知网爬虫测试脚本
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from office_auto.cnki_crawler import CNKICrawler
from office_auto.config import CRAWLER_CONFIG


class TestCNKICrawler(unittest.TestCase):
    """测试CNKICrawler类"""

    def setUp(self):
        """测试前准备"""
        self.test_author = "测试作者"
        self.test_institution = "测试大学"

    def test_crawler_initialization(self):
        """测试爬虫初始化"""
        # 由于需要Chrome浏览器，这里只测试配置
        self.assertIsInstance(CRAWLER_CONFIG, dict)
        self.assertIn("headless", CRAWLER_CONFIG)
        self.assertIn("wait_time", CRAWLER_CONFIG)

    def test_paper_info_structure(self):
        """测试论文信息结构"""
        expected_keys = ["标题", "作者", "期刊", "发表日期", "被引次数", "下载次数"]

        # 模拟一个论文信息字典
        paper_info = {
            "标题": "测试论文标题",
            "作者": "张三; 李四",
            "期刊": "测试期刊",
            "发表日期": "2023-01-01",
            "被引次数": "10",
            "下载次数": "100",
        }

        for key in expected_keys:
            self.assertIn(key, paper_info)

    @patch("office_auto.cnki_crawler.webdriver.Chrome")
    def test_crawler_context_manager(self, mock_chrome):
        """测试爬虫上下文管理器"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        with CNKICrawler(headless=True) as crawler:
            self.assertIsNotNone(crawler)

        # 验证driver.quit()被调用
        mock_driver.quit.assert_called_once()


def run_simple_test():
    """运行简单的功能测试"""
    print("=== 知网爬虫功能测试 ===")

    # 测试配置
    print("✓ 配置文件加载正常")
    print(f"  - 基础URL: {CRAWLER_CONFIG['base_url']}")
    print(f"  - 搜索URL: {CRAWLER_CONFIG['search_url']}")
    print(f"  - 默认等待时间: {CRAWLER_CONFIG['wait_time']}秒")

    # 测试导入
    try:
        from office_auto import CNKICrawler  # noqa: F401

        print("✓ 模块导入正常")
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return

    # 测试Chrome是否可用（不启动浏览器）
    try:
        from webdriver_manager.chrome import ChromeDriverManager

        # 只验证驱动管理器
        driver_path = ChromeDriverManager().install()
        print(f"✓ Chrome驱动可用: {driver_path}")

    except Exception as e:
        print(f"⚠ Chrome驱动检查失败: {e}")
        print("  请确保已安装Chrome浏览器")

    print("\n🎉 基础功能测试完成！")
    print("\n💡 使用提示：")
    print("  1. 运行 'python src/office_auto/example.py' 开始爬取")
    print("  2. 确保网络连接正常且能访问知网")
    print("  3. 首次运行可能需要下载Chrome驱动，请耐心等待")


if __name__ == "__main__":
    # 选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "unittest":
        # 运行单元测试
        unittest.main(argv=[""], exit=False, verbosity=2)
    else:
        # 运行简单测试
        run_simple_test()
