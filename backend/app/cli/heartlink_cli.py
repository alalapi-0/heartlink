"""模块说明: HeartLink 主程序 CLI，提供菜单交互与环境体检入口。"""
import argparse  # 导入 argparse 用于解析命令行参数
import sys  # 导入 sys 以便动态调整模块搜索路径
from datetime import datetime  # 导入 datetime 以生成报告时间戳
from pathlib import Path  # 导入 Path 以跨平台处理路径
from typing import Dict  # 导入 Dict 类型注解增强可读性

CURRENT_FILE: Path = Path(__file__).resolve()  # 获取当前文件的绝对路径
PROJECT_ROOT: Path = CURRENT_FILE.parents[3]  # 计算项目根目录位置
if str(PROJECT_ROOT) not in sys.path:  # 若项目根目录尚未添加至模块搜索路径
    sys.path.append(str(PROJECT_ROOT))  # 将项目根目录添加到 sys.path 以支持绝对导入

from backend.app.core.env_check import run_env_diagnostics  # noqa: E402  # 延迟导入以避免循环依赖警告

COLOR_MAP: Dict[str, str] = {  # 定义状态对应的终端颜色
    "OK": "\033[92m",  # 成功状态使用绿色
    "WARN": "\033[93m",  # 警告状态使用黄色
    "FAIL": "\033[91m",  # 失败状态使用红色
    "RESET": "\033[0m",  # 重置颜色到默认
}  # 字典定义结束

MENU_BANNER: str = (
    "===============================\n"  # 绘制菜单标题的上边框
    "    HeartLink 主程序入口\n"  # 显示项目标题
    "===============================\n"  # 绘制菜单标题的下边框
    "1. 环境体检（系统与依赖）\n"  # 列出环境体检选项
    "2. 退出\n"  # 列出退出选项
    "==============================="  # 绘制菜单底部分隔线
)  # 完成菜单文本定义


def parse_args() -> argparse.Namespace:
    """模块说明: 解析命令行参数以支持快速执行。"""
    parser = argparse.ArgumentParser(description="HeartLink 命令行入口")  # 创建参数解析器
    parser.add_argument(  # 添加自动执行环境检测的布尔开关
        "--auto-check",  # 定义触发自动体检的参数名称
        action="store_true",  # 设置参数为存在即为 True 的布尔开关
        help="跳过菜单直接执行环境体检",  # 描述参数用途
    )  # 结束参数定义
    return parser.parse_args()  # 返回解析结果


def ensure_data_directory() -> Path:
    """模块说明: 确保数据目录存在并返回其路径。"""
    data_dir = PROJECT_ROOT / "data"  # 计算数据目录路径
    data_dir.mkdir(parents=True, exist_ok=True)  # 创建目录（若已存在则忽略）
    return data_dir  # 返回目录路径供后续使用


def format_report_lines(results: Dict[str, Dict[str, str]]) -> str:
    """模块说明: 将体检结果格式化为文本字符串。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 生成当前时间戳
    lines = ["HeartLink 环境体检报告", f"生成时间: {timestamp}", "----------------------------------------"]  # 构建报告标题
    for name, detail in results.items():  # 遍历所有检测结果
        line = f"{name}: [{detail['status']}] {detail['detail']}"  # 构造单行文本
        lines.append(line)  # 将单行文本添加到列表
    return "\n".join(lines)  # 将所有行合并为一个字符串


def display_results(results: Dict[str, Dict[str, str]]) -> None:
    """模块说明: 在终端打印彩色的检测结果。"""
    for name, detail in results.items():  # 遍历结果字典
        status = detail["status"]  # 获取状态字符串
        color = COLOR_MAP.get(status, COLOR_MAP["RESET"])  # 根据状态选择颜色
        reset = COLOR_MAP["RESET"]  # 获取颜色重置代码
        print(f"{color}{name:<10} [{status}] {detail['detail']}{reset}")  # 打印彩色文本


def run_environment_check() -> None:
    """模块说明: 执行环境体检流程并保存报告。"""
    ensure_data_directory()  # 确保数据目录存在
    results = run_env_diagnostics()  # 调用后端检测逻辑获取结果
    display_results(results)  # 在终端输出彩色报告
    report_text = format_report_lines(results)  # 将结果格式化为文本
    report_path = PROJECT_ROOT / "data" / "env_report.txt"  # 计算报告文件路径
    report_path.write_text(report_text + "\n", encoding="utf-8")  # 写入报告文本并补充换行符
    print(f"报告已保存至: {report_path}")  # 提示用户报告位置


def interactive_menu() -> None:
    """模块说明: 显示菜单并根据用户输入执行操作。"""
    while True:  # 进入无限循环以处理连续输入
        print(MENU_BANNER)  # 打印菜单标题
        choice = input("请选择操作：").strip()  # 获取用户输入并去除空白
        if choice == "1":  # 判断是否选择环境体检
            run_environment_check()  # 执行环境体检流程
        elif choice == "2":  # 判断是否选择退出
            print("感谢使用 HeartLink，欢迎下次再来！")  # 输出告别信息
            break  # 跳出循环结束程序
        else:  # 处理无效输入
            print("无效选项，请输入 1 或 2。")  # 提示用户重新输入


def main() -> None:
    """模块说明: 程序入口，先解析参数再执行相应流程。"""
    args = parse_args()  # 解析命令行参数
    if args.auto_check:  # 如果用户指定自动检测
        run_environment_check()  # 直接执行环境体检
    else:  # 否则进入交互式菜单
        interactive_menu()  # 启动菜单循环


if __name__ == "__main__":  # 检测脚本是否被直接执行
    main()  # 调用主函数启动程序
