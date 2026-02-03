#!/usr/bin/env python3
"""
测试脚本 - 验证AI博客自动化系统
"""

import os
import sys
import subprocess
import datetime

def check_file_exists(path, description):
    """检查文件是否存在"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: 文件不存在")
        return False

def check_directory_exists(path, description):
    """检查目录是否存在"""
    if os.path.isdir(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: 目录不存在")
        return False

def run_command(cmd, description):
    """运行命令并检查结果"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout:
                print(f"   输出: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description}失败")
            print(f"   错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 AI博客自动化系统 - 完整性测试")
    print("=" * 60)
    
    # 记录开始时间
    start_time = datetime.datetime.now()
    
    # 测试1：检查目录结构
    print("\n📁 测试1：检查目录结构")
    print("-" * 40)
    
    dirs_to_check = [
        ("content/posts", "博客文章目录"),
        ("data/raw", "原始数据目录"),
        ("data/analysis", "分析数据目录"),
        ("logs", "日志目录"),
        ("config", "配置目录"),
        ("scripts", "脚本目录"),
        (".github/workflows", "工作流目录"),
    ]
    
    dir_results = []
    for path, desc in dirs_to_check:
        dir_results.append(check_directory_exists(path, desc))
    
    # 测试2：检查关键文件
    print("\n📄 测试2：检查关键文件")
    print("-" * 40)
    
    files_to_check = [
        ("scripts/simple_automation.py", "自动化主脚本"),
        ("config/config.yaml", "配置文件"),
        ("requirements.txt", "依赖文件"),
        (".github/workflows/daily-automation.yml", "每日自动化工作流"),
        ("AUTOMATION_SETUP.md", "设置指南"),
        ("SOLUTION_SUMMARY.md", "解决方案总结"),
    ]
    
    file_results = []
    for path, desc in files_to_check:
        file_results.append(check_file_exists(path, desc))
    
    # 测试3：检查Python环境
    print("\n🐍 测试3：检查Python环境")
    print("-" * 40)
    
    env_results = []
    env_results.append(run_command("python --version", "检查Python版本"))
    env_results.append(run_command("pip --version", "检查pip版本"))
    
    # 测试4：检查依赖安装
    print("\n📦 测试4：检查依赖安装")
    print("-" * 40)
    
    deps_results = []
    deps_results.append(run_command("pip install requests pyyaml --quiet", "安装核心依赖"))
    
    # 测试5：运行自动化脚本（测试模式）
    print("\n🤖 测试5：运行自动化脚本（测试模式）")
    print("-" * 40)
    
    # 设置测试环境变量
    os.environ['TEST_MODE'] = 'true'
    
    script_results = []
    script_results.append(run_command(
        "python scripts/simple_automation.py", 
        "运行自动化脚本"
    ))
    
    # 测试6：检查生成的文件
    print("\n📊 测试6：检查生成的文件")
    print("-" * 40)
    
    generated_files = []
    
    # 检查是否有新文章生成
    if os.path.isdir("content/posts"):
        posts = os.listdir("content/posts")
        if posts:
            print(f"✅ 找到 {len(posts)} 篇博客文章")
            for post in posts[:3]:  # 显示前3篇
                print(f"   📝 {post}")
            generated_files.append(True)
        else:
            print("⚠️  未找到博客文章")
            generated_files.append(False)
    
    # 检查数据文件
    if os.path.isdir("data/raw"):
        raw_files = os.listdir("data/raw")
        if raw_files:
            print(f"✅ 找到 {len(raw_files)} 个原始数据文件")
            generated_files.append(True)
        else:
            print("⚠️  未找到原始数据文件")
            generated_files.append(False)
    
    if os.path.isdir("data/analysis"):
        analysis_files = os.listdir("data/analysis")
        if analysis_files:
            print(f"✅ 找到 {len(analysis_files)} 个分析数据文件")
            generated_files.append(True)
        else:
            print("⚠️  未找到分析数据文件")
            generated_files.append(False)
    
    # 测试7：检查Git配置
    print("\n🔧 测试7：检查Git配置")
    print("-" * 40)
    
    git_results = []
    git_results.append(run_command("git status", "检查Git状态"))
    git_results.append(run_command("git config --list | grep user", "检查Git用户配置"))
    
    # 生成测试报告
    print("\n📋 测试报告")
    print("=" * 60)
    
    total_tests = (
        len(dir_results) + len(file_results) + len(env_results) + 
        len(deps_results) + len(script_results) + len(generated_files) + len(git_results)
    )
    
    passed_tests = (
        sum(dir_results) + sum(file_results) + sum(env_results) + 
        sum(deps_results) + sum(script_results) + sum(generated_files) + sum(git_results)
    )
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 总体统计:")
    print(f"   总测试项: {total_tests}")
    print(f"   通过项: {passed_tests}")
    print(f"   失败项: {total_tests - passed_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    
    # 测试耗时
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"   测试耗时: {duration:.1f}秒")
    
    print("\n🎯 测试结果:")
    if success_rate >= 80:
        print("✅ 系统测试通过！AI博客自动化系统已准备就绪。")
        print("\n🚀 下一步:")
        print("   1. 配置GitHub Secrets (DEEPSEEK_API_KEY)")
        print("   2. 提交代码到GitHub仓库")
        print("   3. 在GitHub Actions中运行工作流")
        print("   4. 访问 https://gsaecy.github.io 查看结果")
    elif success_rate >= 50:
        print("⚠️  系统部分测试通过，需要进一步检查。")
        print("\n🔧 需要检查:")
        print("   1. 缺失的文件或目录")
        print("   2. Python环境配置")
        print("   3. 依赖安装")
    else:
        print("❌ 系统测试失败，需要重新设置。")
        print("\n🛠️ 建议:")
        print("   1. 重新运行设置脚本")
        print("   2. 检查文件权限")
        print("   3. 验证Python环境")
    
    print("\n📝 详细建议:")
    print("   1. 完整设置指南: AUTOMATION_SETUP.md")
    print("   2. 解决方案总结: SOLUTION_SUMMARY.md")
    print("   3. 工作流配置: .github/workflows/daily-automation.yml")
    
    print("\n" + "=" * 60)
    print("🧪 测试完成时间:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()