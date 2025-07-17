"""
知网论文爬虫使用示例
演示如何使用CNKICrawler爬取论文信息
"""

import os
from cnki_crawler import CNKICrawler


def main():
    """主函数"""
    print("=== 知网论文爬虫 ===")

    # 获取用户输入
    author_name = input("请输入作者姓名: ").strip()
    if not author_name:
        print("作者姓名不能为空！")
        return

    institution = input("请输入作者单位（可选，直接回车跳过）: ").strip()

    try:
        max_pages = int(input("请输入要爬取的最大页数（默认3页）: ") or "3")
    except ValueError:
        max_pages = 3

    # 创建输出目录
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 生成输出文件名
    if institution:
        filename = f"{output_dir}/{author_name}_{institution}_papers.xlsx"
    else:
        filename = f"{output_dir}/{author_name}_papers.xlsx"

    print(f"\n开始搜索作者：{author_name}")
    if institution:
        print(f"单位：{institution}")
    print(f"最大页数：{max_pages}")
    print(f"输出文件：{filename}")
    print("-" * 50)

    # 使用爬虫
    try:
        with CNKICrawler(headless=False) as crawler:
            # 搜索论文
            papers = crawler.search_papers(author_name, institution, max_pages)

            # 保存结果
            if papers:
                crawler.save_to_excel(papers, filename)
                print(f"\n✅ 成功！共找到 {len(papers)} 篇论文")
                print(f"📁 文件已保存至：{filename}")

                # 显示前5篇论文预览
                print("\n📋 论文预览（前5篇）：")
                print("-" * 80)
                for i, paper in enumerate(papers[:5], 1):
                    print(f"{i}. {paper.get('标题', 'N/A')}")
                    print(f"   作者：{paper.get('作者', 'N/A')}")
                    print(f"   期刊：{paper.get('期刊', 'N/A')}")
                    print(f"   日期：{paper.get('发表日期', 'N/A')}")
                    print()

                if len(papers) > 5:
                    print(f"... 还有 {len(papers) - 5} 篇论文，详情请查看Excel文件")

            else:
                print("❌ 未找到相关论文，请检查作者姓名和单位是否正确")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 爬取过程中出现错误：{str(e)}")
        print("💡 可能的原因：")
        print("   1. 网络连接问题")
        print("   2. 知网网站结构变化")
        print("   3. Chrome浏览器或驱动问题")
        print("   4. 反爬虫机制触发")


def batch_crawl():
    """批量爬取示例"""
    print("=== 批量爬取论文 ===")

    # 作者列表
    authors = [
        {"name": "张三", "institution": "清华大学"},
        {"name": "李四", "institution": "北京大学"},
        {"name": "王五", "institution": "中科院"},
    ]

    # 创建输出目录
    output_dir = "batch_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with CNKICrawler(headless=True) as crawler:
        for i, author_info in enumerate(authors, 1):
            try:
                print(
                    f"\n[{i}/{len(authors)}] 正在处理：{author_info['name']} - {author_info['institution']}"
                )

                # 搜索论文
                papers = crawler.search_papers(
                    author_info["name"], author_info["institution"], max_pages=2
                )

                # 保存结果
                if papers:
                    filename = f"{output_dir}/{author_info['name']}_{author_info['institution']}_papers.xlsx"
                    crawler.save_to_excel(papers, filename)
                    print(f"✅ 找到 {len(papers)} 篇论文，已保存至 {filename}")
                else:
                    print("❌ 未找到相关论文")

            except Exception as e:
                print(f"❌ 处理 {author_info['name']} 时出错：{str(e)}")
                continue


if __name__ == "__main__":
    # 选择运行模式
    print("请选择运行模式：")
    print("1. 单个作者搜索")
    print("2. 批量搜索示例")

    choice = input("请输入选择（1或2）：").strip()

    if choice == "1":
        main()
    elif choice == "2":
        batch_crawl()
    else:
        print("无效选择，运行单个作者搜索模式")
        main()
