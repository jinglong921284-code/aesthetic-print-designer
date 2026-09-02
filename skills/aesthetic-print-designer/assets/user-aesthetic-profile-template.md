# 印花审美画像｜Canonical Profile

> 权限边界：本模板仅在用户明确要求保存或更新印花审美画像时复制使用。分析权限不等于落盘权限；不得改写原始收藏、已获准的视觉收藏基线或其他来源层。画像可能包含个人路径、偏好和原话；只保存完成任务所需的最少信息，不得把已填写画像随公开 Skill 包发布，分享前必须去标识化。

## 0. 画像元数据

| 字段 | 值 |
|---|---|
| Profile ID | `<required>` |
| Profile version | `v0.1` |
| Summary version | `s0.1` |
| Supersedes | `none / <prior version>` |
| Status | `candidate` |
| Owner | `<user-confirmed>` |
| Scope | `<print categories / project boundary / long-run taste>` |
| Created at | `<ISO-8601 with timezone>` |
| Updated at | `<ISO-8601 with timezone>` |
| Canonical target | `<user-approved target>` |
| Prepared by | `<name or agent identity>` |
| Current manifest-set SHA-256 | `sha256:<64 hex>` |
| Previous manifest-set SHA-256 | `none / sha256:<64 hex>` |
| Source count | `<number>` |
| Current file/attachment count | `<number>` |

`candidate` 是首次生成和每次实质更新后的默认状态。只有用户明确确认当前版本后才可改为 `approved`。

## 1. 来源注册表

| Source ID | 来源类型 | 用户可见名称 | 可配置根目录 / 快照 ID | 本次范围 | 只读 | 快照/获取日期 | 限制 |
|---|---|---|---|---|---|---|---|
| SRC-01 | `attachment / local_collection / saved_collection_baseline / approved_other` |  |  | `included / excluded` | `yes` |  |  |

### 来源层边界

- 附件、本地收藏、已获准的视觉收藏基线（可含 Pinterest）和其他获准证据都是来源层。
- 本文档的版本化当前摘要才是 canonical 汇总层。
- 来源层之间的矛盾必须保留，不得为了得到统一风格而消除证据分歧。

## 2. 来源 Manifest

### Manifest 快照

| 字段 | 值 |
|---|---|
| Snapshot at | `<ISO-8601 with timezone>` |
| Sort rule | `source_id + relative_path` |
| Hash rule | `SHA-256 of deterministic serialized manifest` |
| Previous manifest-set SHA-256 | `none / sha256:<64 hex>` |
| Current manifest-set SHA-256 | `sha256:<64 hex>` |

### 文件/附件清单

| Entry ID | Source ID | 相对路径 / 稳定附件或快照 ID | SHA-256 | Bytes | Mtime | Media type | 状态 | 是否进入当前汇总 | 备注 |
|---|---|---|---|---:|---|---|---|---|---|
| E-0001 | SRC-01 |  | `sha256:<64 hex>` |  | `<ISO-8601 / not_available>` |  | `current / new / modified / deleted / unchanged` | `yes / no` |  |

Manifest 不保存个人绝对路径。`mtime` 只是辅助证据；内容身份以 SHA-256 为准。

## 3. 更新差异

| 类型 | 数量 | Entry IDs / 摘要 |
|---|---:|---|
| New |  |  |
| Modified |  |  |
| Deleted |  |  |
| Unchanged |  |  |
| Probable rename/move |  |  |

删除项保留在历史和变更日志中，不得静默移除。

## 4. 逐图/逐来源证据卡

> 为每个当前或已变更的 Entry 复制本节。可以对视觉收藏基线等汇总性来源使用稳定快照 ID。

### Evidence `<Entry ID>`

| 字段 | 内容 |
|---|---|
| Source / relative path |  |
| Evidence status | `current / new / modified / deleted` |
| Direct observations |  |
| Bounded inferences |  |
| Inference confidence | `high / medium / low` |
| Supporting observation IDs |  |
| Keep |  |
| Avoid |  |
| Protected identifiers |  |
| Provenance / rights note |  |
| Evidence limitations |  |
| Duplicate / near-duplicate relation |  |

Observations 只记可直接看见的色彩关系、motif grammar、构图、尺度层级、密度、负空间、边缘/笔触和纹理。情绪、偏好、用途和稳定性判断必须放在 inferences。

## 5. 当前 Canonical 摘要

| 字段 | 值 |
|---|---|
| Summary version | `s0.1` |
| Summary status | `candidate` |
| Based on manifest-set SHA-256 | `sha256:<64 hex>` |
| Source coverage | `<included sources and entry counts>` |
| Supersedes summary | `none / <summary version>` |
| Effective date | `<ISO-8601 with timezone>` |

### 审美结构

| 维度 | 当前结论 | 证据 Entry IDs | 置信度 | 状态 |
|---|---|---|---|---|
| 情绪与美学张力 |  |  | `high / medium / low` | `candidate / approved / disputed` |
| 配色关系 |  |  |  |  |
| Motif / 符号偏好 |  |  |  |  |
| 构图与动势 |  |  |  |  |
| 尺度层级、密度与负空间 |  |  |  |  |
| 边缘、笔触与纹理 DNA |  |  |  |  |
| 材料感与印花建筑倾向 |  |  |  |  |
| 稳定锚点 |  |  |  |  |
| 可变偏好 |  |  |  |  |
| 拒绝信号 |  |  |  |  |
| 未解冲突 |  |  |  |  |

### 一句话审美 DNA

`<candidate synthesis; do not present as approved until confirmed>`

### 下游使用边界

- 当前 Brief 和用户明确反馈永远高于本画像。
- `candidate` 字段只可用于探索，不得写成已确认个人审美或生产基准。
- 视觉收藏基线和本地收藏结论需经 canonical 汇总与用户批准后才能作为 `approved personal aesthetic profile`。

## 6. 权利与原创筛查

| 检查项 | 结论 | 证据 | 处理 |
|---|---|---|---|
| Logo / 品牌识别元素 | `none / present / uncertain` |  | `exclude / investigate` |
| 角色、艺术家签名或受保护图形 |  |  |  |
| 可识别原作构图/布局 |  |  |  |
| 来源不明或截图风险 |  |  |  |
| 可转译的一般原则 |  |  |  |
| 不可进入下游设计的标识 |  |  |  |

## 7. 置信度与证据完整性

| 项目 | 记录 |
|---|---|
| High-confidence conclusions |  |
| Medium-confidence conclusions |  |
| Low-confidence / single-source signals |  |
| Source conflicts |  |
| Missing or inaccessible evidence |  |
| Duplicate-content effect |  |
| Coverage limitations |  |
| Recheck condition |  |

置信度必须同时考虑证据数量、来源独立性、时间跨度、内容重复和反向证据；不能用图片数量单独推导高置信度。

## 8. 批准记录

| Profile/Summary version | 决定 | 批准范围 | 用户原话/决定证据 | Approver | 日期 | Manifest-set SHA-256 |
|---|---|---|---|---|---|---|
| v0.1 / s0.1 | `candidate` | `none` |  |  |  | `sha256:<64 hex>` |

只有明确确认当前版本或指定字段才能记录 `approved`。部分批准不得自动推广到其他字段。

## 9. Append-only Change Log

> 本表只能追加。不得修改、覆盖或删除历史行。

| Change ID | Timestamp | From -> To | Previous manifest SHA | Current manifest SHA | New / Modified / Deleted | 当前摘要变化 | 保留结论 | 置信度变化 | 用户决定 | Actor |
|---|---|---|---|---|---|---|---|---|---|---|
| CHG-0001 |  | `none -> v0.1/s0.1` | `none` | `sha256:<64 hex>` |  | Initial candidate synthesis |  |  | `awaiting confirmation` |  |

## 10. 本次交付与读回

| 检查项 | 结果 |
|---|---|
| 用户明确授权落盘/更新 | `yes / no` |
| 目标路径已确认 | `yes / no / not applicable` |
| Profile/Summary version 已读回 | `yes / no / not applicable` |
| Status 已读回 | `yes / no / not applicable` |
| Manifest-set SHA-256 已读回 | `yes / no / not applicable` |
| Source/entry counts 已读回 | `yes / no / not applicable` |
| 批准记录已读回 | `yes / no / not applicable` |
| 最新 change-log 行已读回 | `yes / no / not applicable` |
