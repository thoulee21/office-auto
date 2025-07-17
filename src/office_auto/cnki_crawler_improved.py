"""
知网论文爬虫模块 - 改进版
根据作者姓名和单位爬取论文信息并保存到Excel
解决了页面元素定位问题，增加了多种搜索策略
"""

import re
import time
from typing import Dict, List, Optional

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class CNKICrawlerImproved:
    """知网论文爬虫类 - 改进版"""

    def __init__(self, headless: bool = True, wait_time: int = 15):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
            wait_time: 页面加载等待时间
        """
        self.base_url = "https://kns.cnki.net"
        self.search_url = "https://kns.cnki.net/kns8s/"  # 更新URL
        self.wait_time = wait_time
        self.driver = None
        self.setup_driver(headless)

    def setup_driver(self, headless: bool = True):
        """设置Chrome驱动"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        # 添加更多稳定性选项
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # 自动下载并设置Chrome驱动
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.wait_time)

    def search_papers(
        self, author_name: str, institution: str = "", max_pages: int = 5
    ) -> List[Dict]:
        """
        搜索论文

        Args:
            author_name: 作者姓名
            institution: 作者单位
            max_pages: 最大搜索页数

        Returns:
            论文信息列表
        """
        papers = []

        try:
            print(f"正在搜索作者: {author_name}, 单位: {institution}")

            # 方法1：尝试直接搜索URL构造
            success = self._try_direct_search(author_name, institution)

            if not success:
                # 方法2：尝试访问搜索页面填写表单
                success = self._try_form_search(author_name, institution)

            if success:
                # 爬取搜索结果
                papers = self._crawl_search_results(max_pages)
            else:
                print("❌ 无法完成搜索，请检查网络连接或知网可访问性")

        except Exception as e:
            print(f"搜索过程中出现错误: {str(e)}")

        return papers

    def _try_direct_search(self, author_name: str, institution: str = "") -> bool:
        """尝试通过直接构造搜索URL进行搜索"""
        try:
            print("尝试直接搜索方式...")

            # 构造搜索参数
            search_query = f"作者:{author_name}"
            if institution:
                search_query += f" AND 单位:{institution}"

            # 构造搜索URL（基于知网的搜索参数）
            search_url = f"{self.base_url}/kns8s/search?crossref=N&kw={search_query}"

            self.driver.get(search_url)
            time.sleep(5)

            # 检查是否成功进入搜索结果页面
            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".result-table-list, .searchResult, .search-result",
                        )
                    )
                )
                print("✅ 直接搜索成功")
                return True
            except TimeoutException:
                print("直接搜索未成功，尝试其他方式...")
                return False

        except Exception as e:
            print(f"直接搜索方式失败: {str(e)}")
            return False

    def _try_form_search(self, author_name: str, institution: str = "") -> bool:
        """尝试通过填写搜索表单进行搜索"""
        try:
            print("尝试表单搜索方式...")

            # 访问知网主页
            self.driver.get(self.base_url)
            time.sleep(3)

            # 尝试多种搜索框定位策略
            search_input = None
            search_selectors = [
                "input[placeholder*='请输入检索词']",
                "input[placeholder*='检索']",
                ".search-input input",
                "#searchText",
                ".nav-search input",
            ]

            for selector in search_selectors:
                try:
                    search_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except Exception as e:
                    print(f"查找搜索输入框时出错: {str(e)}")
                    continue

            if not search_input:
                print("未找到搜索输入框")
                return False

            # 构造搜索查询
            search_query = f"作者:{author_name}"
            if institution:
                search_query += f" AND 单位:{institution}"

            # 输入搜索条件
            search_input.clear()
            search_input.send_keys(search_query)
            search_input.send_keys(Keys.RETURN)

            print(f"已输入搜索条件: {search_query}")
            time.sleep(5)

            # 检查搜索结果
            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".result-table-list, .searchResult, .search-result",
                        )
                    )
                )
                print("✅ 表单搜索成功")
                return True
            except TimeoutException:
                print("表单搜索未返回结果")
                return False

        except Exception as e:
            print(f"表单搜索方式失败: {str(e)}")
            return False

    def _crawl_search_results(self, max_pages: int = 5) -> List[Dict]:
        """爬取搜索结果"""
        papers = []
        current_page = 1

        while current_page <= max_pages:
            try:
                print(f"正在爬取第 {current_page} 页...")

                # 等待搜索结果加载
                time.sleep(3)

                # 获取当前页面的论文列表
                page_papers = self._extract_papers_from_page()

                if not page_papers:
                    print(f"第 {current_page} 页没有找到论文数据")
                    if current_page == 1:
                        print("第一页就没有数据，可能搜索条件有误或网站结构变化")
                    break

                papers.extend(page_papers)
                print(f"第 {current_page} 页获取到 {len(page_papers)} 篇论文")

                # 尝试翻到下一页
                if not self._go_to_next_page():
                    print("没有更多页面")
                    break

                current_page += 1
                time.sleep(2)

            except Exception as e:
                print(f"爬取第 {current_page} 页时出错: {str(e)}")
                break

        return papers

    def _extract_papers_from_page(self) -> List[Dict]:
        """从当前页面提取论文信息"""
        papers = []

        try:
            # 尝试多种结果列表选择器
            paper_items = []
            result_selectors = [
                ".result-table-list tr:not(:first-child)",  # 传统表格形式
                ".searchResult .result-item",  # 新版结果项
                ".search-result .item",  # 另一种结果项
                ".literature-item",  # 文献项
                "[data-index]",  # 带索引的项目
            ]

            for selector in result_selectors:
                try:
                    paper_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if paper_items:
                        print(f"使用选择器找到 {len(paper_items)} 个论文项: {selector}")
                        break
                except Exception:
                    continue

            if not paper_items:
                print("未找到论文列表项")
                return papers

            for i, item in enumerate(paper_items):
                try:
                    paper_info = self._extract_paper_info(item)
                    if paper_info and paper_info.get("标题"):  # 确保有标题
                        papers.append(paper_info)
                    elif i < 3:  # 只对前3个项目打印调试信息
                        print(f"第 {i + 1} 个项目未能提取到有效信息")
                except Exception as e:
                    if i < 3:  # 只对前3个项目打印错误信息
                        print(f"提取第 {i + 1} 篇论文信息时出错: {str(e)}")
                    continue

        except Exception as e:
            print(f"提取页面论文信息时出错: {str(e)}")

        return papers

    def _extract_paper_info(self, item_element) -> Optional[Dict]:
        """提取单篇论文的信息"""
        try:
            # 论文标题 - 尝试多种选择器
            title = ""
            title_selectors = [
                "a.fz14",
                ".title a",
                ".literature-title a",
                "h3 a",
                "a[href*='detail']",
                ".result-item-title a",
            ]

            for selector in title_selectors:
                try:
                    title_element = item_element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    if title:
                        break
                except Exception:
                    continue

            if not title:
                # 如果没有找到链接，尝试直接找文本
                try:
                    title = item_element.find_element(
                        By.CSS_SELECTOR, ".title, h3, .literature-title"
                    ).text.strip()
                except Exception:
                    pass

            # 作者信息
            authors = ""
            author_selectors = [
                "a[href*='author']",
                ".author a",
                ".literature-author a",
                "[data-author] a",
            ]

            for selector in author_selectors:
                try:
                    author_elements = item_element.find_elements(
                        By.CSS_SELECTOR, selector
                    )
                    if author_elements:
                        authors = "; ".join(
                            [
                                author.text.strip()
                                for author in author_elements
                                if author.text.strip()
                            ]
                        )
                        break
                except Exception:
                    continue

            # 期刊信息
            journal = ""
            journal_selectors = [
                "a[href*='journal']",
                "a[href*='magazine']",
                ".journal a",
                ".source a",
                ".literature-source a",
            ]

            for selector in journal_selectors:
                try:
                    journal_element = item_element.find_element(
                        By.CSS_SELECTOR, selector
                    )
                    journal = journal_element.text.strip()
                    if journal:
                        break
                except Exception:
                    continue

            # 发表日期
            date = ""
            try:
                text_content = item_element.text
                date_patterns = [
                    r"(\d{4}-\d{2}-\d{2})",
                    r"(\d{4}/\d{2}/\d{2})",
                    r"(\d{4}\.\d{2}\.\d{2})",
                    r"(\d{4}年\d{1,2}月)",
                    r"(\d{4}年)",
                ]

                for pattern in date_patterns:
                    date_match = re.search(pattern, text_content)
                    if date_match:
                        date = date_match.group(1)
                        break
            except Exception:
                pass

            # 被引次数
            citations = ""
            try:
                citation_selectors = [
                    "*[class*='cite']",
                    "*[class*='引']",
                    ".citation-count",
                ]

                for selector in citation_selectors:
                    try:
                        citation_element = item_element.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        citation_text = citation_element.text.strip()
                        if "引" in citation_text or "cite" in citation_text.lower():
                            citations = citation_text
                            break
                    except Exception:
                        continue
            except Exception:
                pass

            # 下载次数
            downloads = ""
            try:
                download_selectors = ["*[class*='download']", "*[class*='下载']"]

                for selector in download_selectors:
                    try:
                        download_element = item_element.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        download_text = download_element.text.strip()
                        if (
                            "下载" in download_text
                            or "download" in download_text.lower()
                        ):
                            downloads = download_text
                            break
                    except Exception:
                        continue
            except Exception:
                pass

            # 只有标题不为空才返回结果
            if title:
                return {
                    "标题": title,
                    "作者": authors,
                    "期刊": journal,
                    "发表日期": date,
                    "被引次数": citations,
                    "下载次数": downloads,
                }
            else:
                return None

        except Exception as e:
            print(f"提取论文详细信息时出错: {str(e)}")
            return None

    def _go_to_next_page(self) -> bool:
        """翻到下一页"""
        try:
            # 尝试多种下一页按钮选择器
            next_selectors = [
                "a[title*='下页']",
                "a[title*='下一页']",
                ".next-page",
                ".page-next",
                "a:contains('下页')",
                "a:contains('下一页')",
                "a:contains('>')",
            ]

            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    # 检查是否可以点击
                    if "disabled" in next_button.get_attribute(
                        "class"
                    ) or next_button.get_attribute("disabled"):
                        continue

                    # 尝试点击
                    self.driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)
                    return True

                except Exception:
                    continue

            # 如果没有找到下一页按钮，尝试页码链接
            try:
                current_page_text = self.driver.find_element(
                    By.CSS_SELECTOR, ".current-page, .active"
                ).text
                next_page_num = int(current_page_text) + 1
                next_page_link = self.driver.find_element(
                    By.LINK_TEXT, str(next_page_num)
                )
                next_page_link.click()
                time.sleep(3)
                return True
            except Exception:
                pass

            return False

        except Exception as e:
            print(f"翻页时出错: {str(e)}")
            return False

    def save_to_excel(self, papers: List[Dict], filename: str = "cnki_papers.xlsx"):
        """保存论文信息到Excel文件"""
        if not papers:
            print("没有论文数据可保存")
            return

        try:
            # 创建DataFrame
            df = pd.DataFrame(papers)

            # 调整列顺序
            columns_order = ["标题", "作者", "期刊", "发表日期", "被引次数", "下载次数"]
            existing_columns = [col for col in columns_order if col in df.columns]
            df = df[existing_columns]

            # 保存到Excel
            df.to_excel(filename, index=False, engine="openpyxl")
            print(f"✅ 成功保存 {len(papers)} 篇论文信息到 {filename}")

        except Exception as e:
            print(f"❌ 保存Excel文件时出错: {str(e)}")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """主函数示例"""
    # 使用示例
    author_name = "陈晨"  # 要搜索的作者姓名
    institution = ""  # 作者单位（可选）

    with CNKICrawlerImproved(headless=False) as crawler:
        # 搜索论文
        papers = crawler.search_papers(author_name, institution, max_pages=3)

        # 保存到Excel
        if papers:
            filename = f"{author_name}_papers.xlsx"
            crawler.save_to_excel(papers, filename)
            print(f"\n🎉 搜索完成！找到 {len(papers)} 篇论文")

            # 显示前3篇预览
            print("\n📋 论文预览：")
            for i, paper in enumerate(papers[:3], 1):
                print(f"{i}. {paper.get('标题', 'N/A')}")
                print(f"   作者：{paper.get('作者', 'N/A')}")
                print(f"   期刊：{paper.get('期刊', 'N/A')}")
                print()
        else:
            print("❌ 未找到相关论文")


if __name__ == "__main__":
    main()
