# X-Skills

[English](./README_EN.md) | **简体中文**

> 一套用于 X (Twitter) 内容创作自动化的 Claude Skills，帮助你高效收集素材、筛选选题、创作爆款推文并发布到草稿箱。

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai/claude-code)

---

## ✨ 功能特性

```
素材收集 → 选题筛选 → 推文创作 → 发布草稿
   📚         🎯         ✍️         📤
```

| Skill | 命令 | 功能描述 |
|-------|------|----------|
| **x-collect** | `/x-collect [话题]` | 4轮深度搜索，模拟人类调研思维 |
| **x-filter** | `/x-filter` | 10分制打分筛选，≥7分进入创作池 |
| **x-create** | `/x-create [选题]` | 生成短推文/Thread，支持5种爆款风格 |
| **x-publish** | `/x-publish` | 自动发布到X草稿箱，永不自动发布 |

### 核心亮点

- **通用化设计**：首次使用自动问答收集用户信息，支持个性化定制
- **智能打分系统**：热度(4分) + 争议性(2分) + 价值(3分) + 相关性(1分)
- **5种爆款模式**：高价值干货、犀利观点、热点评论、故事洞察、技术解析
- **安全发布**：只保存到草稿箱，用户手动审核后发布

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

- [Claude Code](https://claude.ai/claude-code) - Anthropic 官方 CLI
- [Playwright MCP](https://github.com/anthropics/claude-code) - 浏览器自动化

---

**Made with ❤️ for X creators**
