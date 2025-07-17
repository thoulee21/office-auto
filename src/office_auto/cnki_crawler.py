"""
知网论文爬虫模块
根据作者姓名和单位爬取论文信息并保存到Excel
"""

import time
import re
import pandas as pd
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class CNKICrawler:
    """知网论文爬虫类"""

    def __init__(self, headless: bool = True, wait_time: int = 10):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
            wait_time: 页面加载等待时间
        """
        self.base_url = "https://kns.cnki.net"
        self.search_url = "https://kns.cnki.net/kns8/AdvSearch"
        self.wait_time = wait_time
        self.driver = None
        self.setup_driver(headless)

    def setup_driver(self, headless: bool = True):
        """设置Chrome驱动"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
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
            # 访问知网高级搜索页面
            print(f"正在搜索作者: {author_name}, 单位: {institution}")
            self.driver.get(self.search_url)
            time.sleep(3)

            # 填写搜索条件
            self._fill_search_form(author_name, institution)

            # 执行搜索
            self._perform_search()

            # 爬取搜索结果
            papers = self._crawl_search_results(max_pages)

        except Exception as e:
            print(f"搜索过程中出现错误: {str(e)}")

        return papers

    def _fill_search_form(self, author_name: str, institution: str = ""):
        """填写搜索表单"""
        try:
            # 等待页面加载完成
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "input-box"))
            )

            # 选择作者字段
            author_select = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//select[@name='txt_1_sel']"))
            )
            # 选择作者选项
            for option in author_select.find_elements(By.TAG_NAME, "option"):
                if "作者" in option.text:
                    option.click()
                    break

            # 输入作者姓名
            author_input = self.driver.find_element(By.NAME, "txt_1_value1")
            author_input.clear()
            author_input.send_keys(author_name)

            # 如果有单位信息，填写单位
            if institution:
                # 添加第二个搜索条件
                add_button = self.driver.find_element(
                    By.XPATH, "//a[@onclick='addLine()']"
                )
                add_button.click()
                time.sleep(1)

                # 选择单位字段
                institution_select = self.driver.find_element(By.NAME, "txt_2_sel")
                for option in institution_select.find_elements(By.TAG_NAME, "option"):
                    if "单位" in option.text or "机构" in option.text:
                        option.click()
                        break

                # 输入单位信息
                institution_input = self.driver.find_element(By.NAME, "txt_2_value1")
                institution_input.clear()
                institution_input.send_keys(institution)

        except Exception as e:
            print(f"填写搜索表单时出错: {str(e)}")

    def _perform_search(self):
        """执行搜索"""
        try:
            # 点击搜索按钮
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='检索']"))
            )
            search_button.click()

            # 等待搜索结果页面加载
            time.sleep(5)

        except Exception as e:
            print(f"执行搜索时出错: {str(e)}")

    def _crawl_search_results(self, max_pages: int = 5) -> List[Dict]:
        """爬取搜索结果"""
        papers = []
        current_page = 1

        while current_page <= max_pages:
            try:
                print(f"正在爬取第 {current_page} 页...")

                # 等待搜索结果加载
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "result-table-list"))
                )

                # 获取当前页面的论文列表
                page_papers = self._extract_papers_from_page()
                papers.extend(page_papers)

                print(f"第 {current_page} 页获取到 {len(page_papers)} 篇论文")

                # 尝试翻到下一页
                if not self._go_to_next_page():
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
            # 获取论文列表项
            paper_items = self.driver.find_elements(
                By.XPATH, "//table[@class='result-table-list']//tr[position()>1]"
            )

            for item in paper_items:
                try:
                    paper_info = self._extract_paper_info(item)
                    if paper_info:
                        papers.append(paper_info)
                except Exception as e:
                    print(f"提取单篇论文信息时出错: {str(e)}")
                    continue

        except Exception as e:
            print(f"提取页面论文信息时出错: {str(e)}")

        return papers

    def _extract_paper_info(self, item_element) -> Optional[Dict]:
        """提取单篇论文的信息"""
        try:
            # 论文标题
            title_element = item_element.find_element(By.XPATH, ".//a[@class='fz14']")
            title = title_element.text.strip()

            # 作者信息
            authors = ""
            try:
                author_elements = item_element.find_elements(
                    By.XPATH, ".//a[contains(@href, 'author')]"
                )
                authors = "; ".join([author.text.strip() for author in author_elements])
            except Exception:
                pass

            # 期刊信息
            journal = ""
            try:
                journal_element = item_element.find_element(
                    By.XPATH,
                    ".//a[contains(@href, 'journal') or contains(@href, 'magazine')]",
                )
                journal = journal_element.text.strip()
            except Exception:
                pass

            # 发表日期
            date = ""
            try:
                # 查找包含日期的文本
                text_content = item_element.text
                date_pattern = r"(\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}|\d{4}\.\d{2}\.\d{2}|\d{4}年\d{1,2}月|\d{4}年)"
                date_match = re.search(date_pattern, text_content)
                if date_match:
                    date = date_match.group(1)
            except Exception:
                pass

            # 被引次数
            citations = ""
            try:
                citation_element = item_element.find_element(
                    By.XPATH, ".//span[contains(text(), '被引')]"
                )
                citations = citation_element.text.strip()
            except Exception:
                pass

            # 下载次数
            downloads = ""
            try:
                download_element = item_element.find_element(
                    By.XPATH, ".//span[contains(text(), '下载')]"
                )
                downloads = download_element.text.strip()
            except Exception:
                pass

            return {
                "标题": title,
                "作者": authors,
                "期刊": journal,
                "发表日期": date,
                "被引次数": citations,
                "下载次数": downloads,
            }

        except Exception as e:
            print(f"提取论文详细信息时出错: {str(e)}")
            return None

    def _go_to_next_page(self) -> bool:
        """翻到下一页"""
        try:
            # 查找下一页按钮
            next_button = self.driver.find_element(
                By.XPATH, "//a[contains(text(), '下页') or contains(text(), '下一页')]"
            )

            # 检查是否可以点击（是否有下一页）
            if "disabled" in next_button.get_attribute("class"):
                return False

            next_button.click()
            time.sleep(3)
            return True

        except NoSuchElementException:
            # 没有找到下一页按钮
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

            # 保存到Excel
            df.to_excel(filename, index=False, engine="openpyxl")
            print(f"成功保存 {len(papers)} 篇论文信息到 {filename}")

        except Exception as e:
            print(f"保存Excel文件时出错: {str(e)}")

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
    author_name = "张三"  # 要搜索的作者姓名
    institution = "清华大学"  # 作者单位（可选）

    with CNKICrawler(headless=False) as crawler:
        # 搜索论文
        papers = crawler.search_papers(author_name, institution, max_pages=3)

        # 保存到Excel
        if papers:
            filename = f"{author_name}_{institution}_papers.xlsx"
            crawler.save_to_excel(papers, filename)
        else:
            print("未找到相关论文")


if __name__ == "__main__":
    main()
