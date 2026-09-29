# 实际运行案例：三个色值到 TCX 屏幕候选

[返回十分钟上手教程](getting-started.zh-CN.md) · [原始工具输出](examples/first-colour-match.json)

这是 2026-09-29 在维护者环境中运行 **v1.3.0 配色工具**的记录。它验证数字配色路径，不代表新用户安装测试或完整印花生图过程。

## 输入

选用三个明确的色值作为练习：底色 `#F3ECE0`、主图色 `#3F6F9F`、强调色 `#DF7327`。输入不涉及客户图片，也不依赖 AI 目测取色。

## 实际操作

安装依赖后，从 Skill 文件夹运行：

```bash
.venv/bin/python scripts/run_print_tool.py pantone-quick \
  --hex '#F3ECE0' --label '底色' \
  --hex '#3F6F9F' --label '主图色' \
  --hex '#DF7327' --label '强调色' --top 1
```

Windows 使用教程中的 `.venv\Scripts\python.exe`，把参数写在同一行。

本次维护者执行使用已有兼容 Python 环境，而非重新安装 .venv。工具自动读取内置 `pantone-tcx-rgb.json`（2,800 条），执行 sRGB → Lab 与 CIEDE2000 最近色匹配。色库 SHA-256：

```text
5e5ac131379a2a934e4291de2f11393e9c7ebcb490b079677ca427292423b7a5
```

## 输出

| 角色 | 源色值 | 候选编号 | 候选名称 | 候选色值 | ΔE00 |
|---|---|---|---|---|---|
| 底色 | #F3ECE0 | 11-0103 | Egret | #F3ECE0 | 0.0000 |
| 主图色 | #3F6F9F | 18-4141 | Campanula | #3272AF | 2.4062 |
| 强调色 | #DF7327 | 16-1255 | Russet Orange | #E47127 | 1.4313 |

实际结果状态为 `screen_computed_candidate`；`physical_review.status` 为 `pending`。原始 JSON 由命令输出保存，未手填候选数据。匹配工具本身只向终端返回结果，不写规格单或外部文档；本页附带的 JSON 是维护者为展示而保存的副本。

## 这次验证说明了什么

内置色库可被工具读取，三个精确输入可产生可复核的数字候选。不需要生图服务或额外色库下载；仍需要本地 Python 依赖。

这次没有验证客户端自动选择 Skill、陌生用户安装、参考图分析、生图审美质量、实体色卡准确性或面料打样。要形成完整设计案例，下一步应使用有权公开的参考图与原创图稿，记录真实执行过程，保留方向选择与修改过程。
