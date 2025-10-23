"""模块说明: HeartLink 环境体检模块，负责执行系统与依赖检测并返回结果。"""
import importlib.util  # 导入 importlib.util 以动态检测模块是否存在
import platform  # 导入 platform 以获取系统信息
import subprocess  # 导入 subprocess 以运行外部命令
import sys  # 导入 sys 以获取当前 Python 信息
from pathlib import Path  # 导入 Path 以处理路径
from typing import Dict, List, Tuple  # 导入类型注解提高可读性

from .config import HeartLinkConfig, load_default_config  # 导入配置加载函数以定位路径

StatusDetail = Dict[str, str]  # 定义状态详情类型别名
DiagnosticResult = Dict[str, StatusDetail]  # 定义诊断结果类型别名

STATUS_PRIORITY: Dict[str, int] = {"OK": 0, "WARN": 1, "FAIL": 2}  # 定义状态优先级以便计算总体状态


def _run_command(command: List[str]) -> Tuple[bool, str]:
    """模块说明: 尝试运行外部命令并返回是否成功及输出。"""
    try:  # 捕获运行过程中可能出现的异常
        completed = subprocess.run(  # 运行命令并捕获标准输出
            command,  # 指定要执行的命令列表
            check=False,  # 禁止因非零退出码抛出异常
            capture_output=True,  # 捕获标准输出与标准错误
            text=True,  # 以文本模式返回输出
            timeout=5,  # 设置命令执行的超时时间（秒）
        )  # 结束 subprocess.run 调用
        success = completed.returncode == 0  # 判断命令是否成功执行
        output = completed.stdout.strip() or completed.stderr.strip()  # 优先选择标准输出，否则使用错误输出
        return success, output  # 返回结果给调用方
    except (FileNotFoundError, subprocess.SubprocessError) as exc:  # 捕获命令不存在或执行失败的情况
        return False, str(exc)  # 返回失败状态与错误描述


def _detect_gpu_status() -> StatusDetail:
    """模块说明: 检测 GPU 是否可用并提供建议。"""
    torch_spec = importlib.util.find_spec("torch")  # 检查是否安装 PyTorch
    if torch_spec is not None:  # 如果检测到 PyTorch
        try:  # 捕获 GPU 检测过程中可能的异常
            import torch  # 动态导入 torch 模块

            if torch.cuda.is_available():  # 判断是否存在可用 GPU
                device_name = torch.cuda.get_device_name(0)  # 获取第一个 GPU 的名称
                return {"status": "OK", "detail": f"检测到 GPU: {device_name}"}  # 返回成功状态与设备名称
            return {  # 返回警告结果字典
                "status": "WARN",  # 标记状态为警告
                "detail": "检测到 PyTorch 但 CUDA 不可用，请检查驱动或 CUDA 版本。",  # 提供修复建议
            }  # 结束字典定义
        except Exception as exc:  # 捕获意外异常
            return {  # 返回警告结果字典
                "status": "WARN",  # 标记状态为警告
                "detail": f"PyTorch 存在但无法获取 GPU 信息: {exc}",  # 记录异常信息
            }  # 结束字典定义
    success, output = _run_command(["nvidia-smi"])  # 尝试通过 nvidia-smi 工具检测 GPU
    if success:  # 如果命令执行成功
        return {"status": "OK", "detail": f"nvidia-smi 输出: {output}"}  # 返回成功并附加输出
    return {  # 默认返回警告结果
        "status": "WARN",  # 标记状态为警告
        "detail": "未检测到 PyTorch 或 nvidia-smi，如需 GPU 请安装相关驱动。",  # 提供安装建议
    }  # 结束字典定义


def _check_env_file(config: HeartLinkConfig) -> StatusDetail:
    """模块说明: 检查 .env 文件及关键字段。"""
    env_path: Path = config.env_path  # 获取配置中的 .env 路径
    if not env_path.exists():  # 判断文件是否存在
        return {  # 返回警告结果
            "status": "WARN",  # 标记状态为警告
            "detail": "未找到 .env 文件，请复制 .env.example 并填写密钥。",  # 提供操作建议
        }  # 结束字典定义
    try:  # 捕获文件读取可能的异常
        content = env_path.read_text(encoding="utf-8")  # 读取文件内容
    except OSError as exc:  # 捕获文件读取错误
        return {  # 返回警告结果
            "status": "WARN",  # 标记状态为警告
            "detail": f"读取 .env 文件失败: {exc}",  # 记录异常信息
        }  # 结束字典定义
    has_key = False  # 标记是否找到密钥
    for line in content.splitlines():  # 遍历文件每一行
        stripped = line.strip()  # 去除行首尾空白
        if stripped.startswith("OPENAI_API_KEY="):  # 检查目标字段
            value = stripped.split("=", 1)[1]  # 分离字段值
            if value:  # 判断是否填写
                has_key = True  # 标记字段有效
            break  # 找到字段即可跳出循环
    if has_key:  # 如果填写了密钥
        return {"status": "OK", "detail": "已检测到 OPENAI_API_KEY 字段。"}  # 返回成功状态
    return {  # 返回警告结果
        "status": "WARN",  # 标记状态为警告
        "detail": "OPENAI_API_KEY 字段缺失或未填写，请更新 .env。",  # 提供修复建议
    }  # 结束字典定义


def run_env_diagnostics() -> DiagnosticResult:
    """模块说明: 执行完整环境体检并返回详细结果。"""
    config: HeartLinkConfig = load_default_config()  # 加载默认配置以获得路径
    results: DiagnosticResult = {}  # 初始化结果字典
    status_records: List[str] = []  # 初始化状态列表用于统计

    system_detail = platform.platform()  # 获取系统详细信息
    results["system"] = {"status": "OK", "detail": system_detail}  # 记录系统信息
    status_records.append("OK")  # 将状态加入统计

    python_version = sys.version.replace("\n", " ")  # 获取 Python 版本并清除换行符
    results["python"] = {"status": "OK", "detail": python_version}  # 记录 Python 版本
    status_records.append("OK")  # 添加状态

    node_success, node_output = _run_command(["node", "--version"])  # 检测 Node.js
    if node_success:  # 如果检测成功
        results["node"] = {"status": "OK", "detail": node_output}  # 记录成功信息
        status_records.append("OK")  # 状态统计
    else:  # 如果检测失败
        results["node"] = {  # 记录警告信息
            "status": "WARN",  # 标记状态为警告
            "detail": "未检测到 Node.js，请安装 LTS 版本以支持前端。",  # 提供安装建议
        }  # 结束字典定义
        status_records.append("WARN")  # 状态统计

    npm_success, npm_output = _run_command(["npm", "--version"])  # 检测 npm
    if npm_success:  # 检测成功时
        results["npm"] = {"status": "OK", "detail": npm_output}  # 记录 npm 版本
        status_records.append("OK")  # 状态统计
    else:  # 检测失败时
        results["npm"] = {  # 记录警告信息
            "status": "WARN",  # 标记状态为警告
            "detail": "未检测到 npm，请随 Node.js 一并安装。",  # 提供修复建议
        }  # 结束字典定义
        status_records.append("WARN")  # 状态统计

    pip_success, pip_output = _run_command([sys.executable, "-m", "pip", "--version"])  # 检测 pip
    if pip_success:  # 如果命令执行成功
        results["pip"] = {"status": "OK", "detail": pip_output}  # 记录 pip 信息
        status_records.append("OK")  # 记录状态
    else:  # 命令失败
        results["pip"] = {  # 记录失败信息
            "status": "FAIL",  # 标记状态为失败
            "detail": "未检测到 pip，请使用官方安装程序修复 Python。",  # 提供修复建议
        }  # 结束字典定义
        status_records.append("FAIL")  # 状态统计

    gpu_result = _detect_gpu_status()  # 获取 GPU 检测结果
    results["gpu"] = gpu_result  # 保存 GPU 结果
    status_records.append(gpu_result["status"])  # 记录状态

    env_result = _check_env_file(config)  # 检查 .env 文件
    results["env_file"] = env_result  # 保存环境文件检查结果
    status_records.append(env_result["status"])  # 记录状态

    highest_status = max(status_records, key=lambda status: STATUS_PRIORITY.get(status, 2))  # 根据优先级获取最严重状态
    summary_messages = {  # 定义整体状态对应的消息
        "OK": "所有检测通过，环境准备就绪。",  # 完全通过的总结
        "WARN": "部分检测存在警告，请根据提示完善环境。",  # 存在警告时的总结
        "FAIL": "检测存在失败项，请优先解决关键问题。",  # 存在失败时的总结
    }  # 结束字典定义
    summary_detail = summary_messages.get(highest_status, "部分检测存在未知状态，请人工确认。")  # 获取总结描述
    results["summary"] = {"status": highest_status, "detail": summary_detail}  # 写入总结信息

    return results  # 返回完整诊断结果
