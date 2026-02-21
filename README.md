# X-Skills

[English](./README_EN.md) | **简体中文**

> 一套用于 X (Twitter) 内容创作自动化的 Claude Skills，帮助你高效收集素材、筛选选题、创作爆款推文并发布到草稿箱。

[![Version](https://img.shields.io/badge/Version-2.0-green.svg)](./RELEASE_NOTES_v2.0.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai/claude-code)

---

## ✨ 功能特性

```
素材收集 → 选题筛选 → 推文创作 → 发布草稿 → 反馈闭环
   📚         🎯         ✍️         📤         🔄
```

| Skill | 命令 | 功能描述 |
|-------|------|----------|
| **x-collect** | `/x-collect [话题]` | 4轮深度搜索，支持画像增强与探索模式 |
| **x-filter** | `/x-filter` | 多维加权打分 + 负样本过滤 + 多样性衰减 |
| **x-create** | `/x-create [选题]` | 意图路由 + A/B变体 + Critic自检 |
| **x-publish** | `/x-publish` | 自动发布到X草稿箱 + 事件记录 |

### 核心亮点

- **智能推荐算法**：借鉴 X For You 推荐算法，引入多源候选、加权评分、多样性控制
- **A/B 变体 + Critic**：默认生成两个版本并自检打分，低于阈值自动重写一次
- **意图驱动路由**：根据目标动作（收藏/转发/讨论）自动选择最佳创作模式
- **反馈闭环**：支持正/负样本库（liked/rejected topics）+ 事件日志（JSONL）
- **相似度过滤**：基于字符 n-gram 的轻量相似度算法，避免重复低质选题
- **状态持久化**：Python 脚本管理状态文件，支持 hooks 自动收集反馈

---

## 🚀 快速开始

### 1. 安装 Skills

将 skill 文件夹复制到 Claude skills 目录：

```bash
# macOS/Linux
cp -r x-collect x-filter x-create x-publish ~/.claude/skills/

# 或者创建符号链接（推荐，方便更新）
ln -s $(pwd)/x-collect ~/.claude/skills/
ln -s $(pwd)/x-filter ~/.claude/skills/
ln -s $(pwd)/x-create ~/.claude/skills/
ln -s $(pwd)/x-publish ~/.claude/skills/
```

### 2. 首次设置

运行 `/x-create`，回答几个简单问题完成初始化：

- **账号定位**：你主要分享什么内容？（AI/科技、创业、个人成长等）
- **目标受众**：你的读者是谁？（中文用户、英文用户、双语用户）
- **人设风格**：你想塑造什么形象？（专业严肃、轻松幽默、犀利观点等）

### 3. 开始使用

```bash
# 步骤1: 收集素材
/x-collect Claude MCP协议

# 步骤2: 筛选选题
/x-filter

# 步骤3: 创作推文
/x-create "MCP协议详解" --type thread

# 步骤4: 发布到草稿
/x-publish
```

---

## 📖 详细使用

### x-collect 素材收集

使用4轮搜索策略，模拟人类调研思维：

| 轮次 | 策略 | 目标 |
|------|------|------|
| 第1轮 | 官方信息 | 官方文档、GitHub、公告 |
| 第2轮 | 技术解析 | 详细介绍、教程、原理 |
| 第3轮 | 对比评测 | vs竞品、评测、优缺点 |
| 第4轮 | 补充验证 | 填补信息空白、最新动态 |

**输出**：结构化的素材报告，包含来源、摘要、关键点、推荐推文类型

### x-filter 选题筛选

10分制打分系统：

| 维度 | 分值 | 说明 |
|------|------|------|
| 热度/趋势 | 4分 | 当前热门程度、讨论量 |
| 争议性 | 2分 | 是否能引发讨论和对立观点 |
| 高价值 | 3分 | 信息密度、可操作性 |
| 账号相关 | 1分 | 与你账号定位的契合度 |

**≥7分** 进入创作池，推荐优先创作

### x-create 推文创作

支持3种输出格式：
- **短推文**：≤280字符，单条推文
- **Thread**：3-10条串联推文
- **评论回复**：用于蹭热点回复

### x-publish 发布到草稿

使用 Playwright 浏览器自动化：
1. 打开 X 编辑器
2. 填入推文内容
3. 保存到草稿箱
4. **永不自动发布**，用户手动审核

---

## 🎨 推文风格

5种爆款推文模式，可在 `x-create/references/post-patterns.md` 查看详细 prompt：

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| **高价值干货** | 数字开头、清单结构、可收藏 | 教程、工具推荐、方法论 |
| **犀利观点** | 反常识、有立场、引发讨论 | 行业评论、热辣观点 |
| **热点评论** | 快速反应、独特角度 | 新闻点评、事件评论 |
| **故事洞察** | 具体场景、转折、金句 | 案例分析、经验复盘 |
| **技术解析** | 原理拆解、类比解释 | 技术讲解、源码分析 |

### 自定义参考推文

将你喜欢的爆款推文放入对应目录，创作时会优先学习这些风格：

```
x-create/assets/templates/
├── high-value/         # 高价值干货类
├── sharp-opinion/      # 犀利观点类
├── trending-comment/   # 热点评论类
├── story-insight/      # 故事洞察类
└── tech-analysis/      # 技术解析类
```

---

## ⚙️ 配置说明

### 用户配置文件

`x-create/references/user-profile.md`：

```yaml
initialized: true

account:
  domains:
    - AI/科技
    - 创业
    - 个人成长
  target_audience: "中文用户"
  persona_style: "专业严肃、犀利观点、偶尔小幽默"
  language: "zh-CN"

scoring:
  trending: 4      # 热度权重
  controversy: 2   # 争议性权重
  value: 3         # 高价值权重
  relevance: 1     # 相关性权重
  threshold: 7     # 入选阈值

experiments:
  ab_variants: true         # 默认生成 A/B 变体
  critic_enabled: true      # 启用自检打分
  critic_threshold: 7       # 低于阈值触发重写
  auto_rewrite_once: true   # 最多自动重写一次
```

### 状态与反馈闭环

状态文件默认存储在：`~/.claude/skills/x-create/state/`

```bash
state/
├── liked_topics.json      # 正样本库（采纳的选题）
├── rejected_topics.json   # 负样本库（淘汰的选题）
└── events.jsonl           # 事件日志（追加写入）
```

**管理脚本**：`x-create/scripts/x_state.py`

```bash
# 初始化状态文件
python3 ~/.claude/skills/x-create/scripts/x_state.py init

# 记录采纳的选题
python3 ~/.claude/skills/x-create/scripts/x_state.py like --topic-json '{...}'

# 记录淘汰的选题
python3 ~/.claude/skills/x-create/scripts/x_state.py reject --topic-json '{...}'

# 查询相似度（用于过滤重复选题）
python3 ~/.claude/skills/x-create/scripts/x_state.py similarity --against rejected --text "某选题" --topk 3

# 写入事件日志
python3 ~/.claude/skills/x-create/scripts/x_state.py event --event collect.completed --payload-json '{...}'
```


### 环境依赖

**x-publish 需要**：
- Playwright MCP 已配置
- 浏览器已登录 X
- Python 3.9+
  - macOS: `pip install pyobjc-framework-Cocoa`
  - Windows: `pip install pyperclip`

**x-collect 需要**：
- WebSearch 工具可用

---

## 🔄 新增功能（v2.0）

### 1. 智能推荐算法升级

借鉴 **X For You 推荐算法**（参考 `X-For-You-Feed-Algorithm.md`），引入：
- **多源候选**：In-Network（关注源）+ Out-of-Network（探索 20%）
- **加权多维评分**：`FinalScore = Σ(w_i × s_i) - NegPenalty`
- **多样性控制**：来源衰减（`0.6^(N-1)`）+ 话题聚类去重
- **反馈闭环**：正/负样本库 + 事件日志（JSONL）

### 2. A/B 变体 + Critic 自检

- 默认生成 **Variant A** 和 **Variant B**（hook/结构差异）
- Critic 对每个变体打分 0-10，评估：Hook强度、信息密度、可读性、可信度、账号匹配、行动导向
- 若两版都 < 7 分，自动重写一次
- 输出包含 `CREATE_JSON` 和 `HOOKS_JSON` 供状态管理脚本使用

### 3. 意图驱动路由

根据**目标动作**自动选择创作模式：
- 收藏/转发 → 高价值干货
- 讨论/对立 → 犀利观点
- 时效/热点 → 热点评论
- 共鸣/关注 → 故事洞察
- 专业/技术 → 技术解析

### 4. 相似度过滤（无需 Embedding）

基于字符 2/3-gram + 词 Jaccard + 序列相似度：
- 对比候选选题与 `rejected_topics.json`
- 相似度 ≥ 0.85：强扣分或直接淘汰
- 相似度 0.75~0.85：软扣分（-2分）

### 5. 结构化输出（JSON Hooks）

每个 skill 输出末尾追加机器可读的 JSON 块：
- `MATERIALS_JSON`（x-collect）
- `FILTER_JSON`（x-filter）
- `CREATE_JSON` + `HOOKS_JSON`（x-create）
- `PUBLISH_JSON`（x-publish）

便于 hooks 自动收集反馈并调用 `x_state.py` 落盘。

---

## ❓ 常见问题

<details>
<summary><b>Q: 首次使用需要配置什么？</b></summary>

只需运行 `/x-create`，按提示回答3个问题即可完成初始化。配置会自动保存，后续无需再次设置。
</details>

<details>
<summary><b>Q: 如何修改打分权重？</b></summary>

编辑 `x-create/references/user-profile.md` 中的 `scoring` 部分，调整各维度权重和入选阈值。
</details>

<details>
<summary><b>Q: x-publish 会自动发布推文吗？</b></summary>

**不会**。x-publish 只会将内容保存到 X 的草稿箱，需要你手动审核后发布。这是出于安全考虑的设计。
</details>

<details>
<summary><b>Q: 如何添加自己喜欢的爆款推文作为参考？</b></summary>

将推文内容保存为 `.md` 文件，放入 `x-create/assets/templates/` 对应的分类目录中。创作时会优先学习这些风格。
</details>

<details>
<summary><b>Q: 支持英文推文吗？</b></summary>

支持。在用户配置中将 `language` 改为 `en` 或 `target_audience` 改为"英文用户"即可。
</details>

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

- **Bug 反馈**：请描述复现步骤和预期行为
- **功能建议**：请说明使用场景和需求
- **PR 提交**：请确保代码通过 skill-creator 验证

---

## 📄 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。

---

## 🔗 相关链接

- [Claude Code](https://github.com/anthropics/claude-code) - Anthropic 官方 CLI
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) - 浏览器自动化
- [X For You Feed Algorithm](./X-For-You-Feed-Algorithm.md) - X 推荐算法参考文档
- [优化方案文档](./x-skills-optimization.md) - 详细的算法升级方案


---

**Made with ❤️ for X creators**
