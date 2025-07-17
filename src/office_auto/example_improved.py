"""
知网论文爬虫使用示例 - 改进版
演示如何使用改进版CNKICrawler爬取论文信息
解决了页面元素定位问题，提高了成功率
"""

import os
from cnki_crawler_improved import CNKICrawlerImproved


def main():
    """主函数"""
    print("=== 知网论文爬虫（改进版）===")
    print("💡 改进功能：")
    print("  - 支持多种搜索策略")
    print("  - 更强的页面元素定位能力")
    print("  - 更好的错误处理机制")
    print("-" * 50)

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

    # 使用改进版爬虫
    try:
        with CNKICrawlerImproved(headless=False, wait_time=15) as crawler:
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

                # 数据统计
                print("\n📊 数据统计：")
                filled_authors = sum(1 for p in papers if p.get("作者"))
                filled_journals = sum(1 for p in papers if p.get("期刊"))
                filled_dates = sum(1 for p in papers if p.get("发表日期"))

                print(
                    f"  - 包含作者信息：{filled_authors}/{len(papers)} ({filled_authors / len(papers) * 100:.1f}%)"
                )
                print(
                    f"  - 包含期刊信息：{filled_journals}/{len(papers)} ({filled_journals / len(papers) * 100:.1f}%)"
                )
                print(
                    f"  - 包含日期信息：{filled_dates}/{len(papers)} ({filled_dates / len(papers) * 100:.1f}%)"
                )

            else:
                print("❌ 未找到相关论文")
                print("\n💡 可能的原因：")
                print("   1. 作者姓名拼写错误")
                print("   2. 该作者在知网上没有发表论文")
                print("   3. 网络连接问题")
                print("   4. 知网网站暂时无法访问")

                # 提供建议
                print("\n🔍 建议：")
                print("   - 检查作者姓名是否正确")
                print("   - 尝试简化搜索条件（如去掉单位限制）")
                print("   - 稍后重试")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 爬取过程中出现错误：{str(e)}")
        print("\n💡 故障排除：")
        print("   1. 检查网络连接")
        print("   2. 确认Chrome浏览器已安装")
        print("   3. 重启程序重试")
        print("   4. 如问题持续，可能是知网网站结构变化")


def quick_test():
    """快速测试功能"""
    print("=== 快速测试模式 ===")

    # 预设测试作者
    test_authors = [
        {"name": "李明", "institution": ""},
        {"name": "张伟", "institution": "清华大学"},
        {"name": "王芳", "institution": "北京大学"},
    ]

    print("选择测试作者：")
    for i, author in enumerate(test_authors, 1):
        print(f"{i}. {author['name']} - {author['institution'] or '无单位限制'}")

    try:
        choice = int(input("请选择（1-3）：")) - 1
        if 0 <= choice < len(test_authors):
            author_info = test_authors[choice]

            output_dir = "test_output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            filename = f"{output_dir}/test_{author_info['name']}.xlsx"

            with CNKICrawlerImproved(headless=False) as crawler:
                papers = crawler.search_papers(
                    author_info["name"],
                    author_info["institution"],
                    max_pages=1,  # 只爬取1页进行测试
                )

                if papers:
                    crawler.save_to_excel(papers, filename)
                    print(f"✅ 测试成功！找到 {len(papers)} 篇论文")
                else:
                    print("❌ 测试未找到结果")
        else:
            print("无效选择")
    except ValueError:
        print("无效输入")
    except Exception as e:
        print(f"测试失败：{str(e)}")


def batch_crawl():
    """批量爬取示例"""
    print("=== 批量爬取论文 ===")

    # 作者列表 - 可以根据需要修改
    authors = [
        {"name": "张三", "institution": "清华大学"},
        {"name": "李四", "institution": "北京大学"},
        {"name": "王五", "institution": "中科院"},
    ]

    print(f"将批量处理 {len(authors)} 个作者...")
    for i, author in enumerate(authors, 1):
        print(f"{i}. {author['name']} - {author['institution']}")

    confirm = input("\n是否继续？(y/N): ").strip().lower()
    if confirm != "y":
        print("已取消")
        return

    # 创建输出目录
    output_dir = "batch_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 记录结果
    results = []

    with CNKICrawlerImproved(headless=True) as crawler:  # 批量处理使用无头模式
        for i, author_info in enumerate(authors, 1):
            try:
                print(
                    f"\n[{i}/{len(authors)}] 正在处理：{author_info['name']} - {author_info['institution']}"
                )

                # 搜索论文
                papers = crawler.search_papers(
                    author_info["name"],
                    author_info["institution"],
                    max_pages=2,  # 批量处理时减少页数
                )

                # 保存结果
                if papers:
                    filename = f"{output_dir}/{author_info['name']}_{author_info['institution']}_papers.xlsx"
                    crawler.save_to_excel(papers, filename)
                    result = f"✅ 找到 {len(papers)} 篇论文，已保存至 {filename}"
                    print(result)
                    results.append(
                        {
                            "author": author_info["name"],
                            "count": len(papers),
                            "status": "成功",
                        }
                    )
                else:
                    result = "❌ 未找到相关论文"
                    print(result)
                    results.append(
                        {"author": author_info["name"], "count": 0, "status": "无结果"}
                    )

            except Exception as e:
                result = f"❌ 处理 {author_info['name']} 时出错：{str(e)}"
                print(result)
                results.append(
                    {"author": author_info["name"], "count": 0, "status": "错误"}
                )
                continue

    # 输出汇总结果
    print("\n" + "=" * 50)
    print("📊 批量处理结果汇总：")
    print("-" * 50)

    total_papers = 0
    for result in results:
        print(f"{result['author']}: {result['count']} 篇论文 - {result['status']}")
        total_papers += result["count"]

    print("-" * 50)
    print(f"总计：{total_papers} 篇论文")
    print(f"成功率：{sum(1 for r in results if r['status'] == '成功')}/{len(results)}")


if __name__ == "__main__":
    # 选择运行模式
    print("请选择运行模式：")
    print("1. 单个作者搜索")
    print("2. 快速测试")
    print("3. 批量搜索")

    choice = input("请输入选择（1-3）：").strip()

    if choice == "1":
        main()
    elif choice == "2":
        quick_test()
    elif choice == "3":
        batch_crawl()
    else:
        print("无效选择，运行单个作者搜索模式")
        main()
