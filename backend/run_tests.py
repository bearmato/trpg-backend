#!/usr/bin/env python
"""
测试运行器 - 用于运行项目中的各种测试
用法：
  python run_tests.py all            # 运行所有测试
  python run_tests.py cloudinary     # 只运行Cloudinary相关测试
  python run_tests.py api            # 只运行API相关测试
  python run_tests.py integration    # 只运行集成测试
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path


def run_module_tests(module_path):
    """运行指定模块中的测试"""
    print(f"\n运行测试: {module_path}\n{'-' * 50}")
    result = subprocess.run([sys.executable, "-m", module_path])
    print(f"{'-' * 50}\n")
    return result.returncode == 0


def find_test_modules(test_dir):
    """查找指定目录中的所有测试模块"""
    modules = []
    for path in Path(test_dir).rglob("test_*.py"):
        # 将文件路径转换为导入路径
        rel_path = path.relative_to(Path("."))
        module_path = str(rel_path).replace(
            "/", ".").replace("\\", ".").replace(".py", "")
        modules.append(module_path)
    return modules


def run_all_tests():
    """运行所有测试"""
    print("\n=== 运行所有测试 ===\n")

    all_tests_passed = True
    test_modules = find_test_modules("tests")

    for module in sorted(test_modules):
        if not run_module_tests(module):
            all_tests_passed = False

    if all_tests_passed:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查详细输出。")

    return all_tests_passed


def run_category_tests(category):
    """运行特定类别的测试"""
    print(f"\n=== 运行 {category} 测试 ===\n")

    category_dir = os.path.join("tests", category)
    if not os.path.exists(category_dir):
        print(f"❌ 错误: 测试类别 '{category}' 不存在")
        return False

    all_passed = True
    test_modules = find_test_modules(category_dir)

    if not test_modules:
        print(f"⚠️ 在 '{category}' 类别中没有找到测试")
        return True

    for module in sorted(test_modules):
        if not run_module_tests(module):
            all_passed = False

    if all_passed:
        print(f"\n🎉 所有 {category} 测试通过!")
    else:
        print(f"\n⚠️ 部分 {category} 测试失败，请检查详细输出。")

    return all_passed


if __name__ == "__main__":
    # 确保当前工作目录是backend
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 处理命令行参数
    if len(sys.argv) < 2:
        print("请指定要运行的测试类别: all, cloudinary, api, 或 integration")
        sys.exit(1)

    category = sys.argv[1].lower()

    if category == "all":
        success = run_all_tests()
    elif category in ["cloudinary", "api", "integration"]:
        success = run_category_tests(category)
    else:
        print(f"未知的测试类别: '{category}'")
        print("可用类别: all, cloudinary, api, integration")
        sys.exit(1)

    # 设置退出代码
    sys.exit(0 if success else 1)
