"""模块说明: HeartLink 后端配置模块，集中管理项目根路径与默认目录。"""
from dataclasses import dataclass  # 引入 dataclass 装饰器用于定义简单配置数据结构
from pathlib import Path  # 引入 Path 类以跨平台处理文件路径

PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]  # 解析当前文件路径并定位到项目根目录

@dataclass  # 使用 dataclass 简化配置对象的定义
class HeartLinkConfig:
    """模块说明: 用于描述 HeartLink 默认路径配置的数据结构。"""
    env_path: Path  # 记录 .env 文件的路径
    data_dir: Path  # 记录数据目录路径


def load_default_config() -> HeartLinkConfig:
    """模块说明: 构建并返回默认配置实例。"""
    env_path: Path = PROJECT_ROOT / ".env"  # 拼接项目根路径与 .env 文件名
    data_dir: Path = PROJECT_ROOT / "data"  # 拼接项目根路径与数据目录
    return HeartLinkConfig(env_path=env_path, data_dir=data_dir)  # 返回配置实例供其他模块使用
