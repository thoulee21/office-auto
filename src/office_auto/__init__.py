"""
Office Auto - 办公自动化工具

提供各种办公自动化功能，包括：
- 知网论文爬虫
- 数据处理和分析
- Excel文件操作
"""

__version__ = "0.1.0"
__author__ = "thoulee"

from .cnki_crawler import CNKICrawler
from .config import CRAWLER_CONFIG, EXCEL_COLUMNS

__all__ = ["CNKICrawler", "CRAWLER_CONFIG", "EXCEL_COLUMNS"]
