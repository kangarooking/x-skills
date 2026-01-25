"""Hook extraction helpers.

This module helps extract and normalize "hooks" (strong opening lines) from generated text.
Standard library only.
"""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

from similarity import normalize_text


_THREAD_HEADER_RE = re.compile(r"^###\s*\d+\/\d+\s*$", re.MULTILINE)


def split_sentences(text: str) -> List[str]:
    # Very lightweight sentence-ish split for zh/en
    parts = re.split(r"[\n。！？!?]+", text)
    out = [p.strip() for p in parts if p.strip()]
    return out


def extract_hook_candidates(text: str, max_candidates: int = 5) -> List[str]:
    """Extract 1-2 opening sentences for short tweets or the first tweet of a thread."""
    if not text:
        return []

    # If it's a thread, try to isolate first tweet block
    m = _THREAD_HEADER_RE.search(text)
    if m:
        start = m.end()
        # find next header
        m2 = _THREAD_HEADER_RE.search(text, start)
        first_block = text[start : m2.start()] if m2 else text[start:]
        base = first_block.strip()
    else:
        base = text.strip()

    sentences = split_sentences(base)
    if not sentences:
        return []

    candidates: List[str] = []
    # Take first 1-2 sentences; also consider first line
    first_line = base.splitlines()[0].strip() if base.splitlines() else ""
    for s in [first_line] + sentences[:2]:
        s = s.strip()
        if not s:
            continue
        if len(s) < 8:
            continue
        if len(s) > 120:
            s = s[:120].rstrip()
        candidates.append(s)

    # Dedup by normalized form
    seen = set()
    deduped: List[str] = []
    for c in candidates:
        k = normalize_text(c)
        if k in seen:
            continue
        seen.add(k)
        deduped.append(c)

    return deduped[:max_candidates]


def guess_tags(hook: str) -> List[str]:
    """Heuristic tags for hooks (optional)."""
    tags: List[str] = []
    if re.search(r"\d", hook):
        tags.append("数字")
    if any(x in hook for x in ["99%", "90%", "没人", "大多数", "真相", "其实"]):
        tags.append("反常识")
    if any(x in hook for x in ["痛点", "困扰", "花了", "浪费", "效率"]):
        tags.append("痛点")
    if any(x in hook for x in ["为什么", "如何", "你知道吗", "结果是"]):
        tags.append("悬念")
    if any(x in hook for x in ["就像", "好比", "如果把"]):
        tags.append("类比")
    return tags


def hooks_json(topic: str, hooks: Sequence[str]) -> Dict:
    return {
        "schema_version": "x_skills.hooks.v1",
        "topic": topic,
        "hooks": [
            {"text": h, "source": "extracted", "tags": guess_tags(h), "score_0_10": None}
            for h in hooks
        ],
    }
