"""
知网爬虫配置文件
"""

# 爬虫配置
CRAWLER_CONFIG = {
    # 浏览器设置
    "headless": False,  # 是否使用无头模式（True=不显示浏览器窗口）
    "wait_time": 10,  # 页面加载等待时间（秒）
    "window_size": "1920,1080",  # 浏览器窗口大小
    # 搜索设置
    "max_pages": 5,  # 默认最大搜索页数
    "page_delay": 2,  # 翻页延迟（秒）
    "search_delay": 3,  # 搜索后等待时间（秒）
    # 输出设置
    "output_dir": "output",  # 输出目录
    "excel_engine": "openpyxl",  # Excel引擎
    # 知网URLs
    "base_url": "https://kns.cnki.net",
    "search_url": "https://kns.cnki.net/kns8/AdvSearch",
    # User Agent
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

# Excel列映射
EXCEL_COLUMNS = {
    "title": "标题",
    "authors": "作者",
    "journal": "期刊",
    "date": "发表日期",
    "citations": "被引次数",
    "downloads": "下载次数",
    "url": "链接",
    "abstract": "摘要",
}

# 日期正则表达式模式
DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",  # 2023-12-01
    r"\d{4}/\d{2}/\d{2}",  # 2023/12/01
    r"\d{4}\.\d{2}\.\d{2}",  # 2023.12.01
    r"\d{4}年\d{1,2}月",  # 2023年12月
    r"\d{4}年",  # 2023年
]
