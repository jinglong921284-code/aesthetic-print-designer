# 新用户上手：安装后完成第一次配色匹配

适用版本：**v1.3.0**。主要面向本机 Codex 用户；其他客户端需按各自支持的 Skill 安装方式操作。目标是在环境准备好后，用约十分钟完成一次可核对的小任务；首次安装 Python 或下载依赖可能需要更久。

[下载 Skill ZIP](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.3.0/aesthetic-print-designer-v1.3.0-2026-09-28.zip) · [查看实际运行案例](first-run-example.zh-CN.md) · [返回首页](../README.md)

## 1. 下载并确认文件夹

下载上面的 ZIP，然后解压。打开后应看到：

```text
aesthetic-print-designer/
├── SKILL.md
├── agents/
├── assets/
│   └── colour-libraries/
├── references/
├── scripts/
├── requirements.txt
└── requirements-visual.txt
```

保留整个文件夹。不要只复制 `SKILL.md`，也不要把 GitHub 的整个仓库文件夹当作这个 Skill。公开下载无需 GitHub 登录；如果看见登录页，回到本页的下载链接。

## 2. 安装到 Codex

先下载文件，然后可以把下面这段话发给本机 Codex，并附上解压后文件夹的实际路径：

```text
请把我提供路径中的 aesthetic-print-designer 完整文件夹安装为本机 Codex 的个人 Skill。
先检查是否已有同名 Skill；如果有，告诉我位置和差异，先不要覆盖。
按当前 Codex 支持的用户级 Skill 目录安装，保留所有 assets、references、scripts 和许可文件。
安装后核对 SKILL.md 和 assets/colour-libraries/pantone-tcx-rgb.json 是否存在。
目前只安装，不运行设计或配色任务。
```

也可以手动复制。当前官方文档列出的个人 Skill 目录是 `~/.agents/skills/`。复制完成后的结构应是：

```text
~/.agents/skills/aesthetic-print-designer/SKILL.md
```

- **macOS：**在 Finder 按 `⌘⇧G`，输入 `~/.agents/`。目录不存在时，可让 Codex 按上面的安装请求创建，或在终端执行 `mkdir -p ~/.agents/skills`。把解压后的完整 Skill 文件夹复制进去。
- **Windows 本机：**在资源管理器地址栏输入 `%USERPROFILE%`，进入个人主目录，依次创建或打开 `.agents`、`skills`，再复制完整文件夹。
- **WSL / 远程运行：**文件要放在 Codex 实际运行环境的用户目录里；Windows 主机目录不自动等于 WSL 或远程目录。
- 如果已有同名文件夹，先备份、确认版本再替换；不要合并两套文件。也检查是否有其他目录中的同名 Skill，避免选错版本。

Codex 会自动检测 Skill 变更；若未出现，重启 Codex，再打开一个新对话。以上目录与刷新行为依据 [OpenAI 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)，核对日期为 2026-09-29。本文讲本地文件夹安装，不表示本 Skill 已上架插件目录。

## 3. 确认 Codex 确实读到了它

在新对话中发送：

```text
请使用 aesthetic-print-designer。
先读取实际安装的 SKILL.md，告诉我它的文件位置、支持哪些任务，
并检查内置 TCX JSON 和 CSV 是否存在。此步只检查，不生成图片或文件。
```

**成功表现：**能给出实际文件位置，确认两份 TCX 文件存在，说明可做参考分析、印花方向、循环检查、配色及规格单。只说“可以帮你设计”不算安装验证成功。

## 4. 让 Codex 准备运行环境

参考分析可以先进行；要运行本次配色示例，需要 Python 3.10+、NumPy 和 Pillow。把下面这段发给 Codex：

```text
请检查 aesthetic-print-designer 的配色工具运行环境。
如果已有兼容环境，直接使用；如果没有，请在这个 Skill 文件夹里创建 .venv，
安装 requirements.txt 中的依赖，并用该环境的 Python 执行后续工具。
不要修改全局 Python，也不要安装 PDF 的可选依赖。
若缺少 Python 3.10+ 或需要系统权限，告诉我具体缺什么。
```

如果你选择自己操作，在终端进入安装后的 `aesthetic-print-designer` 文件夹，先检查版本，再执行对应命令：

**macOS / Linux**（`python3 --version` 必须为 3.10 或更高）：

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run_print_tool.py pantone-quick --hex '#F3ECE0' --top 1
```

**Windows PowerShell**（`py -3 --version` 必须为 3.10 或更高）：

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_print_tool.py pantone-quick --hex '#F3ECE0' --top 1
```

若版本不符合要求，先准备兼容 Python，再继续。直接调用环境里的 Python，不需要激活脚本。PDF 规格单以后再按[首页说明](../README.md#local-runtime)安装可选依赖。

## 5. 第一次练习：三个色值匹配

复制到已经识别 Skill 的 Codex 对话中：

```text
使用 aesthetic-print-designer 的 pantone-quick 工具，实际运行内置 TCX 色库匹配。
底色 #F3ECE0，主图色 #3F6F9F，强调色 #DF7327，每个取最近的一个候选。
请列出源 HEX、TCX 编号、色名和实际计算的 ΔE00，并注明色库名称与匹配方法。
结果只在对话中展示，保留“屏幕计算候选、实物待确认”状态。
如果工具没跑成功，直接报告错误，不要凭印象填写编号或色差。
```

在 v1.3.0 默认色库下应得到：

| 用途 | 输入 HEX | TCX 候选 | 色名 | ΔE00 |
|---|---|---|---|---|
| 底色 | `#F3ECE0` | `11-0103` | Egret | 0.0000 |
| 主图色 | `#3F6F9F` | `18-4141` | Campanula | 2.4062 |
| 强调色 | `#DF7327` | `16-1255` | Russet Orange | 1.4313 |

这些是[实际工具运行结果](examples/first-colour-match.json)，不是实物颜色保证。即使数字色差为零，也只说明与当前数据库中的 RGB 一致。使用其他色库时结果可能不同。

**完成标准：**Skill 被实际读取、工具执行成功、输出三行候选、说明色库与方法、实物确认仍待处理。

## 6. 下一步换成自己的设计任务

准备一张你有权使用的参考图，附上产品、主题和用途，发送：

```text
使用 aesthetic-print-designer 分析附件参考图。
产品：[填写产品]；主题：[填写主题]；希望用于：[填写用途]。
先分析图案元素、构图、笔触和配色关系，再给我三个有区别的原创印花方向。
说明哪些原则可以借鉴、哪些识别性元素应避开。先不生成图片，等我选方向。
```

这是下一步可执行的提示词，不是已完成的生图案例。后续生图需要客户端具备相应工具；没有生图工具时，可以交付方向与提示词。已有图稿可直接进入[规格单示例](../README.md#3-generate-an-english-print-specification-sheet)。首页展示图仅供参考，不应拿来当练习素材。

## 卡住时怎么处理

| 现象 | 检查或处理 |
|---|---|
| 找不到 Skill | 确认最终路径直接是 `aesthetic-print-designer/SKILL.md`，没有多套一层文件夹；重启后检查同名版本 |
| 找不到 TCX 文件 | 检查是否下载了 v1.3.0 完整 ZIP，是否只复制了 SKILL.md |
| 提示缺少 NumPy / Pillow | 用执行工具的同一个 Python 安装 requirements.txt |
| 配色结果和表格不同 | 查看实际加载的 Skill 路径、色库 SHA-256；检查 `PANTONE_TCX_DB` 或显式参数是否指定了其他色库 |
| 无法生成图片 | 这是客户端生图能力问题；先完成文字分析或配色工具练习 |
| 缺少 ReportLab | 仅 PDF 导出需要；在同一个环境安装 requirements-visual.txt |
| 团队电脑禁止安装或网络下载 | 记录限制，交由管理员处理；不要把权限失败当作 Skill 执行成功 |

## 新用户试用记录

请由首次使用者填写；不要把维护者测试当作真人试用：

```text
日期：
系统与 Codex 版本：
Skill 版本与实际安装位置：
安装耗时 / 首次任务耗时：
Skill 是否被识别：
Python 与依赖是否准备成功：
三行候选是否产生：
卡住的步骤、原始报错及解决方式：
最不清楚的一句说明：
是否需要他人协助：
最终结果：完成 / 未完成
```

目前证据：维护者已实际运行上述配色命令；另一台电脑上的首次安装、Windows 操作和独立设计师试用仍待验证。“约十分钟”是练习安排，不是实测安装时长承诺。反馈可以提交到 [GitHub Issues](https://github.com/jinglong921284-code/aesthetic-print-designer/issues)，请先移除个人路径、客户素材和账号信息。
