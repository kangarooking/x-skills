# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Repository purpose
X-Skills provides four Claude Skills to automate X (Twitter) content creation: collect materials, filter topics, create posts, and publish to drafts.

## Common commands (from README/SKILL docs)

### Install the skills into Claude
```bash
# macOS/Linux
cp -r x-collect x-filter x-create x-publish ~/.claude/skills/

# or symlink for easier updates
ln -s $(pwd)/x-collect ~/.claude/skills/
ln -s $(pwd)/x-filter ~/.claude/skills/
ln -s $(pwd)/x-create ~/.claude/skills/
ln -s $(pwd)/x-publish ~/.claude/skills/
```

### Run the skills
```bash
/x-collect [topic]
/x-filter
/x-create "[topic]" --type thread
/x-publish
```

### x-publish clipboard helper
```bash
# Copy text directly
python x-publish/scripts/copy_to_clipboard.py text "Tweet content here"

# Copy from file
python x-publish/scripts/copy_to_clipboard.py text --file /tmp/tweet.txt
```

### Requirements called out in docs
- x-collect requires the WebSearch tool.
- x-publish requires Playwright MCP and the user to be logged into X.
- x-publish/scripts/copy_to_clipboard.py is cross-platform; the SKILL.md notes Python 3.9+ and:
  - macOS: `pip install Pillow pyobjc-framework-Cocoa`
  - Windows: `pip install Pillow pywin32`
  (README lists `pyobjc-framework-Cocoa` on macOS and `pyperclip` on Windows; follow x-publish/SKILL.md for the current runbook.)

### Build/test/lint
No build, test, or lint configuration files are present in this repository.

## High-level architecture

### Top-level structure
- `x-collect/` — Skill for 4-round web research using WebSearch.
- `x-filter/` — Skill for scoring and filtering topics (10-point system).
- `x-create/` — Skill for creating posts/threads using patterns and user profile.
- `x-publish/` — Skill for saving posts to X drafts via Playwright MCP.

Each skill’s main entry point is its `SKILL.md` file.

### End-to-end workflow
1. **Collect**: `/x-collect` performs 4 rounds of research and outputs a structured materials report.
2. **Filter**: `/x-filter` scores each topic (trending/controversy/value/relevance); ≥7 enters the creation pool.
3. **Create**: `/x-create` generates short tweets, threads, or replies based on user profile and patterns.
4. **Publish**: `/x-publish` saves the content to X drafts (never auto-publishes).

### Shared configuration and content sources
- `x-create/references/user-profile.md` — user persona and scoring weights shared across skills.
- `x-create/references/post-patterns.md` — default prompts for five post styles.
- `x-create/assets/templates/` — optional user-provided examples per style (high-value, sharp-opinion, trending-comment, story-insight, tech-analysis). If present, x-create prioritizes these over default patterns.

### Publishing implementation details
- `x-publish/scripts/copy_to_clipboard.py` provides a clipboard utility used by the publish workflow to paste content into the X compose UI.

记住：永远用中文跟我对话！！
