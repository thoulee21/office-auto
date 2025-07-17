"""
知网爬虫快速启动脚本
运行此脚本可以快速开始爬取论文
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# 必须在路径设置后导入
try:
    from office_auto.example import main
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包：")
    print("poetry install")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"运行错误: {e}")
        print("请检查系统环境和网络连接")
