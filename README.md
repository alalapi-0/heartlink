<!-- 模块说明: HeartLink 项目总览文档，涵盖目标、安装步骤、环境体检示例与迭代进度。 -->
<!-- 行级注释: 一级标题标记项目介绍开端。 -->
# HeartLink 项目简介
<!-- 行级注释: 段落概述当前轮次核心目标。 -->
HeartLink 聚焦于打造智能协作平台，本轮目标是完成项目骨架与可运行的环境体检 CLI。所有生成文件均为纯文本，且以跨平台兼容为原则。

<!-- 行级注释: 二级标题引出安装指导。 -->
## 安装与运行
<!-- 行级注释: 说明代码块用途。 -->
下方命令演示在 bash 环境中创建虚拟环境并运行 CLI，PowerShell 版本以注释形式给出。
<!-- 行级注释: 代码块展示具体命令。 -->
```bash
# 创建虚拟环境（bash）
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell 可使用: .venv\Scripts\Activate.ps1
# 安装后端依赖（当前为空占位，可随后追加）
pip install -r backend/requirements.txt
# 启动 CLI 并进入菜单
python backend/app/cli/heartlink_cli.py
```

<!-- 行级注释: 二级标题引出体检逻辑说明。 -->
## 环境体检逻辑与输出示例
<!-- 行级注释: 段落说明检测范围与状态含义。 -->
环境体检涵盖系统信息、Python 版本、Node/npm/pip 可用性、GPU 状态以及 `.env` 关键字段。检测结果以 `OK`、`WARN`、`FAIL` 三级呈现，并以 ANSI 颜色强化提示。
<!-- 行级注释: 代码块展示执行命令与示例输出。 -->
```bash
$ python backend/app/cli/heartlink_cli.py --auto-check
===============================
    HeartLink 主程序入口
===============================
1. 环境体检（系统与依赖）
2. 退出
===============================
请选择操作：\033[92msystem     [OK] Linux-6.1.0-...\033[0m
\033[92mpython     [OK] 3.11.8 (...)\033[0m
\033[93mnode       [WARN] 未检测到 Node.js，请安装 LTS 版本以支持前端。\033[0m
\033[93mnpm        [WARN] 未检测到 npm，请随 Node.js 一并安装。\033[0m
\033[92mpip        [OK] pip 23.2.1 from ...\033[0m
\033[93mgpu        [WARN] 未检测到 PyTorch 或 nvidia-smi，如需 GPU 请安装相关驱动。\033[0m
\033[93menv_file   [WARN] 未找到 .env 文件，请复制 .env.example 并填写密钥。\033[0m
\033[93msummary    [WARN] 部分检测存在警告，请根据提示完善环境。\033[0m
报告已保存至: /workspace/heartlink/data/env_report.txt
```

<!-- 行级注释: 三级标题引出状态解读。 -->
### 检测结果说明
<!-- 行级注释: 列表逐项解释状态。 -->
- `OK`：检测通过，无需额外操作。
- `WARN`：存在风险或缺失项，建议后续修复。
- `FAIL`：关键能力缺失，请立即处理并重试。

<!-- 行级注释: 二级标题呈现项目进度。 -->
## 项目进度
<!-- 行级注释: 列表总结本轮成果与计划。 -->
- 当前轮次：**Round 1 - 项目初始化与环境体检**。
- 新增目录：`backend/`（后端代码与依赖）、`frontend/`（前端占位）、`scripts/`（启动脚本）、`docs/`（设计与日志）、`data/`（运行期数据）。
- 本轮使用命令：`python -m venv .venv`、`pip install -r backend/requirements.txt`、`python backend/app/cli/heartlink_cli.py`。
- 下一轮预告：**Round 2 - 角色创建初步**，计划引入核心业务模型及相关交互。
