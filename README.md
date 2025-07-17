# Office Auto - 办公自动化工具

这是一个Python办公自动化工具集，目前包含知网论文爬虫功能。

## 功能特性

### 知网论文爬虫
- 根据作者姓名和单位搜索论文
- 自动提取论文标题、作者、期刊、发表日期等信息
- 支持被引次数和下载次数统计
- 结果保存为Excel文件
- 支持批量搜索多个作者
- 可配置搜索页数和输出格式

## 安装要求

### 系统要求
- Python 3.13+
- Chrome浏览器

### 依赖包
项目使用Poetry管理依赖，主要包含：
- `selenium` - 浏览器自动化
- `webdriver-manager` - 自动管理Chrome驱动
- `pandas` - 数据处理
- `openpyxl` - Excel文件操作
- `beautifulsoup4` - HTML解析
- `requests` - HTTP请求

## 安装步骤

1. 克隆项目：
```bash
git clone <your-repo-url>
cd office-auto
```

2. 安装Poetry（如果未安装）：
```bash
pip install poetry
```

3. 安装依赖：
```bash
poetry install
```

4. 激活虚拟环境：
```bash
poetry shell
```

## 使用方法

### 1. 基本使用

运行示例脚本：
```bash
python src/office_auto/example.py
```

然后按提示输入：
- 作者姓名（必填）
- 作者单位（可选）
- 搜索页数（默认3页）

### 2. 在代码中使用

```python
from office_auto.cnki_crawler import CNKICrawler

# 创建爬虫实例
with CNKICrawler(headless=False) as crawler:
    # 搜索论文
    papers = crawler.search_papers("张三", "清华大学", max_pages=3)
    
    # 保存到Excel
    if papers:
        crawler.save_to_excel(papers, "output.xlsx")
```

### 3. 批量搜索

```python
authors = [
    {"name": "张三", "institution": "清华大学"},
    {"name": "李四", "institution": "北京大学"},
]

with CNKICrawler(headless=True) as crawler:
    for author in authors:
        papers = crawler.search_papers(author["name"], author["institution"])
        filename = f"{author['name']}_{author['institution']}_papers.xlsx"
        crawler.save_to_excel(papers, filename)
```

## 配置选项

可以修改 `src/office_auto/config.py` 文件来调整配置：

```python
CRAWLER_CONFIG = {
    "headless": False,      # 是否隐藏浏览器窗口
    "wait_time": 10,        # 页面等待时间
    "max_pages": 5,         # 默认最大搜索页数
    "output_dir": "output", # 输出目录
}
```

## 输出格式

Excel文件包含以下列：
- 标题
- 作者
- 期刊
- 发表日期
- 被引次数
- 下载次数

## 注意事项

1. **网络连接**：确保网络能正常访问知网
2. **Chrome浏览器**：需要安装Chrome浏览器，驱动会自动下载
3. **访问频率**：避免过于频繁的请求，以免触发反爬虫机制
4. **知网结构变化**：如果知网页面结构发生变化，可能需要更新选择器
5. **合法使用**：请遵守知网的使用条款，仅用于学术研究目的

## 常见问题

### Q: 运行时提示找不到Chrome驱动？
A: 脚本会自动下载Chrome驱动，确保网络连接正常。

### Q: 爬取结果为空？
A: 检查作者姓名和单位是否正确，或者尝试减少搜索条件。

### Q: 浏览器启动失败？
A: 确保已安装Chrome浏览器，或尝试设置 `headless=True`。

### Q: 爬取过程中断？
A: 可能是网络问题或反爬虫机制，建议稍后重试。

## 开发计划

- [ ] 支持更多搜索条件（关键词、时间范围等）
- [ ] 添加论文摘要提取
- [ ] 支持其他学术数据库
- [ ] 添加数据分析和可视化功能
- [ ] 优化反爬虫对策

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！