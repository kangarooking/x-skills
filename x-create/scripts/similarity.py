"""Lightweight similarity utilities (no embeddings).

Goal: provide explainable similarity in [0,1] for Chinese/English mixed text.
Standard library only.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, List, Sequence, Set, Tuple


_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_WS_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    t = text.strip().lower()
    t = _URL_RE.sub(" ", t)

    # Replace punctuation with spaces (keep CJK chars)
    punct = string.punctuation
    trans = str.maketrans({c: " " for c in punct})
    t = t.translate(trans)

    t = _WS_RE.sub(" ", t).strip()
    return t


def char_ngrams(text: str, n: int) -> Set[str]:
    t = normalize_text(text)
    t = t.replace(" ", "")
    if len(t) < n:
        return set()
    return {t[i : i + n] for i in range(0, len(t) - n + 1)}


def word_tokens(text: str) -> Set[str]:
    t = normalize_text(text)
    return set(_WORD_RE.findall(t))


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
    if not a or not b:
        return 0.0
    inter = len(a.intersection(b))
    union = len(a.union(b))
    return inter / union if union else 0.0


def similarity(a_text: str, b_text: str) -> float:
    """Return similarity score in [0,1]."""
    a_norm = normalize_text(a_text)
    b_norm = normalize_text(b_text)

    # Mixed strategy:
    # - char 2/3-gram for short & CJK text
    # - word tokens for English
    # - sequence ratio for overall string closeness
    c2 = jaccard(char_ngrams(a_norm, 2), char_ngrams(b_norm, 2))
    c3 = jaccard(char_ngrams(a_norm, 3), char_ngrams(b_norm, 3))
    wj = jaccard(word_tokens(a_norm), word_tokens(b_norm))
    seq = SequenceMatcher(None, a_norm, b_norm).ratio() if a_norm and b_norm else 0.0

    score = 0.30 * c2 + 0.35 * c3 + 0.15 * wj + 0.20 * seq
    # guard
    if score < 0:
        return 0.0
    if score > 1:
        return 1.0
    return score


@dataclass(frozen=True)
class SimilarityHit:
    id: str
    title: str
    score: float


def topk_similarity(query: str, corpus: Sequence[Tuple[str, str]], topk: int = 5) -> List[SimilarityHit]:
    """corpus items are (id, title)."""
    hits: List[SimilarityHit] = []
    for cid, title in corpus:
        s = similarity(query, title)
        hits.append(SimilarityHit(id=cid, title=title, score=s))
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[: max(1, topk)]
