# X-Skills v2.0 Release Notes

> **借鉴 X For You 推荐算法的智能内容创作系统升级**

---

## 核心升级

### 1. 智能推荐算法

借鉴 X (Twitter) 的 For You 推荐算法架构，实现了完整的推荐流水线：

| 组件 | 实现方式 |
|------|----------|
| **多源候选** | In-Network (正样本库) + Out-of-Network (20% 探索模式) |
| **加权评分** | `FinalScore = Σ(w_i × s_i) - NegPenalty` |
| **多样性控制** | 来源衰减 `0.6^(N-1)` + 话题聚类去重 |
| **负向过滤** | rejected_topics.json 相似度过滤 |

### 2. A/B 变体 + Critic 自检系统

- 默认生成 **两个变体** (Variant A: 强Hook / Variant B: 结构化)
- **7 维度 Critic 评分**：Hook强度、信息密度、可读性、可信度、账号匹配、行动导向、AI味控制
- 评分 < 7 时自动重写一次
- 输出包含 `CREATE_JSON` + `HOOKS_JSON` 供状态管理使用

### 3. 意图驱动路由

根据目标动作自动选择最佳创作模式：

| 目标动作 | 创作模式 | 重点要素 |
|---------|---------|---------|
| 收藏/转发 | 高价值干货 | 清单结构、可执行步骤 |
| 讨论/对立 | 犀利观点 | 强立场、反常识、对比 |
| 时效/热点 | 热点评论 | 快速反应、独特角度 |
| 共鸣/关注 | 故事洞察 | 具体场景+转折+金句 |
| 专业/技术 | 技术解析 | 原理讲解、机制拆解 |

### 4. 相似度过滤 (零外部依赖)

纯 Python 标准库实现的相似度算法：

```python
score = 0.30 * char_2gram + 0.35 * char_3gram + 0.15 * word_jaccard + 0.20 * sequence_ratio
```

- 相似度 ≥ 0.85：强扣分或直接淘汰
- 相似度 0.75~0.85：软扣分 (-2分)

### 5. 反馈闭环基础设施

新增 `x_state.py` 状态管理脚本：

```bash
python3 x_state.py init                    # 初始化
python3 x_state.py like --topic-json '{...}'    # 记录正样本
python3 x_state.py reject --topic-json '{...}'  # 记录负样本
python3 x_state.py similarity --against rejected --text "选题"  # 相似度查询
python3 x_state.py event --event create.completed --payload-json '{...}'
```

状态文件存储：
- `liked_topics.json` - 正样本库
- `rejected_topics.json` - 负样本库
- `events.jsonl` - 事件日志 (追加写入)

### 6. 结构化输出

每个 Skill 输出末尾追加机器可读的 JSON 块：

```
MATERIALS_JSON { "schema_version": "x_skills.materials.v1", ... }
FILTER_JSON { "schema_version": "x_skills.filter.v1", ... }
CREATE_JSON { "schema_version": "x_skills.create.v1", ... }
HOOKS_JSON { "schema_version": "x_skills.hooks.v1", ... }
PUBLISH_JSON { "schema_version": "x_skills.publish.v1", ... }
```

便于 hooks 自动收集反馈并调用状态管理脚本。

---

## 文件变更

| 类型 | 数量 |
|------|------|
| 文件修改 | 16 |
| 代码新增 | 2144 行 |
| 代码删除 | 77 行 |

### 新增文件

- `x-create/scripts/x_state.py` - 状态管理 CLI
- `x-create/scripts/similarity.py` - 相似度算法
- `x-create/scripts/hooks.py` - Hook 抽取工具
- `x-create/scripts/schemas.py` - Schema 校验
- `X-For-You-Feed-Algorithm.md` - X 推荐算法参考文档
- `x-skills-optimization.md` - 详细优化方案

### 修改文件

- `x-collect/SKILL.md` - 双通道检索 + 结构化输出
- `x-filter/SKILL.md` - 增强评分 + 负向过滤 + 多样性控制
- `x-create/SKILL.md` - A/B 变体 + Critic 自检 + 意图路由
- `x-publish/SKILL.md` - 事件记录 + 结构化输出
- `x-create/references/user-profile.md` - 新增实验配置
- `x-create/references/post-patterns.md` - 模式优化

---

## 技术亮点

| 特点 | 说明 |
|------|------|
| **零外部依赖** | 所有 Python 脚本仅用标准库 |
| **原子写入** | 临时文件 + rename 保证数据一致性 |
| **可解释性** | 无黑盒 embedding，算法完全透明 |
| **Schema 版本控制** | 所有 JSON 输出都有 `schema_version` |
| **人机协同** | 永不自动发布，保存到草稿箱供人工审核 |

---

## 升级指南

### 从 v1.x 升级

1. 拉取最新代码：
   ```bash
   git pull origin main
   ```

2. 重新安装 skills（如果使用符号链接则无需操作）：
   ```bash
   cp -r x-collect x-filter x-create x-publish ~/.claude/skills/
   ```

3. 初始化状态文件（首次使用）：
   ```bash
   python3 ~/.claude/skills/x-create/scripts/x_state.py init
   ```

4. 更新用户配置（可选）：
   - 编辑 `x-create/references/user-profile.md`
   - 添加 `experiments` 配置块启用 A/B 变体和 Critic

### 兼容性

- 完全向后兼容 v1.x 工作流
- 新功能默认启用，可通过配置关闭
- 状态文件不存在时自动创建

---

## 贡献者

感谢所有为 v2.0 贡献想法和反馈的朋友们！

---

**Full Changelog**: https://github.com/kangarooking/x-skills/compare/v1.0...v2.0
