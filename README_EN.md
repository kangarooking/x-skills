# X-Skills

**English** | [简体中文](./README.md)

> A collection of Claude Skills for X (Twitter) content creation automation. Efficiently collect materials, filter topics, create viral posts, and publish to drafts.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai/claude-code)

---

## ✨ Features

```
Collect → Filter → Create → Publish
   📚       🎯        ✍️       📤
```

| Skill | Command | Description |
|-------|---------|-------------|
| **x-collect** | `/x-collect [topic]` | 4-round deep research mimicking human workflow |
| **x-filter** | `/x-filter` | 10-point scoring system, ≥7 enters creation pool |
| **x-create** | `/x-create [topic]` | Generate tweets/threads in 5 viral styles |
| **x-publish** | `/x-publish` | Publish to X drafts, NEVER auto-publish |

### Key Highlights

- **Universal Design**: Auto-onboarding for first-time users, fully customizable
- **Smart Scoring**: Trending(4) + Controversy(2) + Value(3) + Relevance(1)
- **5 Viral Patterns**: High-value, Sharp opinions, Trending comments, Story insights, Tech analysis
- **Safe Publishing**: Only saves to drafts, manual review before posting

---

## 🚀 Quick Start

### 1. Install Skills

Copy skill folders to your Claude skills directory:

```bash
# macOS/Linux
cp -r x-collect x-filter x-create x-publish ~/.claude/skills/

# Or create symlinks (recommended for easy updates)
ln -s $(pwd)/x-collect ~/.claude/skills/
ln -s $(pwd)/x-filter ~/.claude/skills/
ln -s $(pwd)/x-create ~/.claude/skills/
ln -s $(pwd)/x-publish ~/.claude/skills/
```

### 2. First-Time Setup

Run `/x-create` and answer a few simple questions:

- **Account Focus**: What content do you share? (AI/Tech, Startup, Personal Growth, etc.)
- **Target Audience**: Who are your readers? (Chinese, English, Bilingual)
- **Persona Style**: What image do you want? (Professional, Humorous, Sharp, etc.)

### 3. Start Using

```bash
# Step 1: Collect materials
/x-collect AI Agent trends

# Step 2: Filter topics
/x-filter

# Step 3: Create posts
/x-create "Best AI tools 2025" --type thread

# Step 4: Publish to draft
/x-publish
```

---

## 📖 Detailed Usage

### x-collect: Material Collection

Uses 4-round search strategy mimicking human research:

| Round | Strategy | Goal |
|-------|----------|------|
| 1st | Official Sources | Docs, GitHub, announcements |
| 2nd | Technical Analysis | Tutorials, how-it-works |
| 3rd | Comparisons | vs competitors, reviews, pros/cons |
| 4th | Supplementary | Fill gaps, latest updates |

**Output**: Structured report with sources, summaries, key points, recommended post types

### x-filter: Topic Filtering

10-point scoring system:

| Dimension | Points | Description |
|-----------|--------|-------------|
| Trending | 4 | Current popularity, discussion volume |
| Controversy | 2 | Can spark debates and different views |
| Value | 3 | Information density, actionability |
| Relevance | 1 | Fit with your account positioning |

**≥7 points** enters creation pool, prioritized for content creation

### x-create: Post Creation

Supports 3 output formats:
- **Short Tweet**: ≤280 characters, single post
- **Thread**: 3-10 connected tweets
- **Reply**: For engaging with trending posts

### x-publish: Publish to Drafts

Uses Playwright browser automation:
1. Opens X compose editor
2. Fills in post content
3. Saves to drafts
4. **NEVER auto-publishes**, user reviews manually

---

## 🎨 Post Styles

5 viral post patterns, see `x-create/references/post-patterns.md` for detailed prompts:

| Style | Characteristics | Best For |
|-------|-----------------|----------|
| **High-Value** | Numbers, lists, actionable | Tutorials, tool lists, methodologies |
| **Sharp Opinion** | Contrarian, takes a stand | Hot takes, industry commentary |
| **Trending Comment** | Quick reaction, unique angle | News, event commentary |
| **Story Insight** | Specific scene, twist, golden quote | Case studies, lessons learned |
| **Tech Analysis** | Principle breakdown, analogies | Technical deep-dives, code analysis |

### Custom Reference Posts

Add your favorite viral posts to the corresponding directories:

```
x-create/assets/templates/
├── high-value/         # High-value content
├── sharp-opinion/      # Sharp opinions
├── trending-comment/   # Trending comments
├── story-insight/      # Story insights
└── tech-analysis/      # Tech analysis
```

---

## ⚙️ Configuration

### User Profile

`x-create/references/user-profile.md`:

```yaml
initialized: true

account:
  domains:
    - AI/Tech
    - Startup
    - Personal Growth
  target_audience: "English users"
  persona_style: "Professional, sharp insights, occasional humor"
  language: "en"

scoring:
  trending: 4      # Trending weight
  controversy: 2   # Controversy weight
  value: 3         # Value weight
  relevance: 1     # Relevance weight
  threshold: 7     # Entry threshold
```

### Dependencies

**For x-publish**:
- Playwright MCP configured
- Logged into X in browser
- Python 3.9+
  - macOS: `pip install pyobjc-framework-Cocoa`
  - Windows: `pip install pyperclip`

**For x-collect**:
- WebSearch tool available

---

## ❓ FAQ

<details>
<summary><b>Q: What do I need to configure for first use?</b></summary>

Just run `/x-create` and answer 3 questions. Configuration is auto-saved for future use.
</details>

<details>
<summary><b>Q: How do I adjust scoring weights?</b></summary>

Edit the `scoring` section in `x-create/references/user-profile.md` to adjust weights and threshold.
</details>

<details>
<summary><b>Q: Will x-publish auto-post my tweets?</b></summary>

**No**. x-publish only saves to X's drafts. You must manually review and publish. This is by design for safety.
</details>

<details>
<summary><b>Q: How do I add my own reference posts?</b></summary>

Save post content as `.md` files in the appropriate `x-create/assets/templates/` subdirectory. They'll be used as style references.
</details>

<details>
<summary><b>Q: Does it support Chinese posts?</b></summary>

Yes. Change `language` to `zh-CN` or `target_audience` to "Chinese users" in the config.
</details>

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

- **Bug Reports**: Please describe reproduction steps and expected behavior
- **Feature Requests**: Please explain use case and requirements
- **PR Submissions**: Please ensure code passes skill-creator validation

---

## 📄 License

This project is licensed under [Apache License 2.0](LICENSE).

---

## 🔗 Related Links

- [Claude Code](https://github.com/anthropics/claude-code) - Anthropic's Official CLI
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) - Browser Automation

---

**Made with ❤️ for X creators**
