"""x_state.py - Minimal state manager for x-skills feedback loop.

Designed to run from: ~/.claude/skills/x-create/scripts/x_state.py
Standard library only.

State directory default: ~/.claude/skills/x-create/state/
Files:
- liked_topics.json
- rejected_topics.json
- events.jsonl

This script is intentionally lightweight: it stores what happened, not how LLM produced it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from similarity import normalize_text, topk_similarity


SCHEMA_LIKED = "x_skills.liked_topics.v1"
SCHEMA_REJECTED = "x_skills.rejected_topics.v1"
SCHEMA_EVENT = "x_skills.event.v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_state_dir() -> Path:
    return Path(os.path.expanduser("~/.claude/skills/x-create/state"))


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass


def read_json_or_default(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False))
        f.write("\n")


def make_id(prefix: str, text: str) -> str:
    norm = normalize_text(text)
    h = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}_{h}"


def state_paths(state_dir: Path) -> Tuple[Path, Path, Path]:
    return (
        state_dir / "liked_topics.json",
        state_dir / "rejected_topics.json",
        state_dir / "events.jsonl",
    )


def cmd_init(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    liked_path, rejected_path, events_path = state_paths(state_dir)
    ensure_dir(state_dir)

    liked = read_json_or_default(
        liked_path, {"schema_version": SCHEMA_LIKED, "updated_at": utc_now(), "items": []}
    )
    rejected = read_json_or_default(
        rejected_path,
        {"schema_version": SCHEMA_REJECTED, "updated_at": utc_now(), "items": []},
    )

    # Ensure schema keys exist
    if "schema_version" not in liked:
        liked["schema_version"] = SCHEMA_LIKED
    if "items" not in liked:
        liked["items"] = []
    liked["updated_at"] = utc_now()

    if "schema_version" not in rejected:
        rejected["schema_version"] = SCHEMA_REJECTED
    if "items" not in rejected:
        rejected["items"] = []
    rejected["updated_at"] = utc_now()

    atomic_write_json(liked_path, liked)
    atomic_write_json(rejected_path, rejected)

    # Touch events file
    ensure_dir(events_path.parent)
    if not events_path.exists():
        events_path.write_text("", encoding="utf-8")

    print(json.dumps({"ok": True, "state_dir": str(state_dir)}, ensure_ascii=False))
    return 0


def _append_event(state_dir: Path, event: str, payload: Dict[str, Any], run_id: Optional[str]) -> str:
    _, _, events_path = state_paths(state_dir)
    rid = run_id or make_id("run", utc_now())
    evt = {
        "schema_version": SCHEMA_EVENT,
        "ts": utc_now(),
        "run_id": rid,
        "event": event,
        "payload": payload,
    }
    append_jsonl(events_path, evt)
    return rid


def cmd_event(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    payload = json.loads(args.payload_json) if args.payload_json else {}
    rid = _append_event(state_dir=state_dir, event=args.event, payload=payload, run_id=args.run_id)
    print(json.dumps({"ok": True, "event": args.event, "run_id": rid}, ensure_ascii=False))
    return 0


def _upsert_item(items: List[Dict[str, Any]], item: Dict[str, Any], key: str = "id") -> None:
    for i, it in enumerate(items):
        if it.get(key) == item.get(key):
            items[i] = item
            return
    items.append(item)


def cmd_like(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    liked_path, _, _ = state_paths(state_dir)

    topic = json.loads(args.topic_json)
    title = topic.get("title") or topic.get("topic") or ""
    if not title:
        raise SystemExit("topic_json must include 'title' or 'topic'")

    tid = topic.get("id") or make_id("topic", title)
    now = utc_now()

    liked = read_json_or_default(
        liked_path, {"schema_version": SCHEMA_LIKED, "updated_at": now, "items": []}
    )
    items = liked.get("items", [])

    item = {
        "id": tid,
        "created_at": topic.get("created_at") or now,
        "updated_at": now,
        "title": title,
        "norm": normalize_text(title),
        "language": topic.get("language") or "zh-CN",
        "signals": {
            "adopted": True,
            "posted": bool(topic.get("posted", False)),
            "manual_rating_0_10": topic.get("rating") or topic.get("manual_rating_0_10"),
            "reason": topic.get("reason"),
        },
        "creation": {
            "post_type": topic.get("post_type"),
            "post_style": topic.get("post_style"),
            "selected_variant": topic.get("selected") or topic.get("selected_variant"),
            "critic_score": topic.get("critic_score") or topic.get("critic_score_0_10"),
        },
        "sources": topic.get("sources", []),
        "keywords": topic.get("keywords", []),
        "entities": topic.get("entities", []),
        "hooks": topic.get("hooks", []),
    }

    _upsert_item(items, item)
    liked["items"] = items
    liked["updated_at"] = now
    atomic_write_json(liked_path, liked)

    # also append event (silent)
    _append_event(
        state_dir=state_dir,
        event="feedback.adopted",
        payload={"topic_id": tid, "title": title},
        run_id=args.run_id,
    )

    print(json.dumps({"ok": True, "topic_id": tid}, ensure_ascii=False))
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    _, rejected_path, _ = state_paths(state_dir)

    topic = json.loads(args.topic_json)
    title = topic.get("title") or topic.get("topic") or ""
    if not title:
        raise SystemExit("topic_json must include 'title' or 'topic'")

    rid = topic.get("id") or make_id("rej", title)
    now = utc_now()

    rejected = read_json_or_default(
        rejected_path,
        {"schema_version": SCHEMA_REJECTED, "updated_at": now, "items": []},
    )
    items = rejected.get("items", [])

    item = {
        "id": rid,
        "created_at": topic.get("created_at") or now,
        "updated_at": now,
        "title": title,
        "norm": normalize_text(title),
        "language": topic.get("language") or "zh-CN",
        "stage": topic.get("stage") or "filter",
        "reason": topic.get("reason") or "rejected",
        "metadata": topic.get("metadata", {}),
    }

    _upsert_item(items, item)
    rejected["items"] = items
    rejected["updated_at"] = now
    atomic_write_json(rejected_path, rejected)

    # also append event (silent)
    _append_event(
        state_dir=state_dir,
        event="feedback.rejected",
        payload={"rejected_id": rid, "title": title},
        run_id=args.run_id,
    )

    print(json.dumps({"ok": True, "rejected_id": rid}, ensure_ascii=False))
    return 0


def cmd_similarity(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    _, rejected_path, _ = state_paths(state_dir)

    against = args.against
    if against != "rejected":
        raise SystemExit("--against currently only supports 'rejected'")

    rejected = read_json_or_default(
        rejected_path,
        {"schema_version": SCHEMA_REJECTED, "updated_at": utc_now(), "items": []},
    )
    corpus = [(it.get("id", ""), it.get("title", "")) for it in rejected.get("items", [])]

    hits = topk_similarity(args.text, corpus=corpus, topk=args.topk)
    out = {
        "query": args.text,
        "max_similarity": hits[0].score if hits else 0.0,
        "matched": [{"id": h.id, "title": h.title, "score": h.score} for h in hits],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_hook_ingest(args: argparse.Namespace) -> int:
    """Ingest HOOKS_JSON into liked_topics.json.

    Expected hooks-json shape:
    {
      "schema_version": "x_skills.hooks.v1",
      "topic": "..." | "topic_id": "topic_xxx",
      "hooks": [{"text":"...", ...}]
    }
    """
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    liked_path, _, _ = state_paths(state_dir)

    payload = json.loads(args.hooks_json)
    topic_id = payload.get("topic_id")
    topic_title = payload.get("topic")
    hooks = payload.get("hooks", [])
    if not hooks:
        raise SystemExit("hooks_json must include non-empty 'hooks'")

    liked = read_json_or_default(
        liked_path,
        {"schema_version": SCHEMA_LIKED, "updated_at": utc_now(), "items": []},
    )
    items = liked.get("items", [])

    target = None
    if topic_id:
        for it in items:
            if it.get("id") == topic_id:
                target = it
                break
    if target is None and topic_title:
        tnorm = normalize_text(topic_title)
        for it in items:
            if it.get("norm") == tnorm:
                target = it
                break

    if target is None:
        raise SystemExit("No matching liked topic found. Provide topic_id or ensure topic title matches an existing liked entry.")

    existing = target.get("hooks", [])
    # de-dup by normalized text
    seen = {normalize_text(h.get("text", "")) for h in existing if isinstance(h, dict)}
    for h in hooks:
        if not isinstance(h, dict):
            continue
        t = h.get("text", "")
        if not t:
            continue
        k = normalize_text(t)
        if k in seen:
            continue
        seen.add(k)
        existing.append(h)

    target["hooks"] = existing
    target["updated_at"] = utc_now()
    liked["items"] = items
    liked["updated_at"] = utc_now()
    atomic_write_json(liked_path, liked)

    _append_event(
        state_dir=state_dir,
        event="hook.ingested",
        payload={"topic_id": target.get("id"), "hooks_added": len(hooks)},
        run_id=args.run_id,
    )

    print(json.dumps({"ok": True, "topic_id": target.get("id"), "hooks_total": len(existing)}, ensure_ascii=False))
    return 0


def _add_common(subp: argparse.ArgumentParser) -> None:
    # Support placing these options BEFORE or AFTER subcommand.
    subp.add_argument(
        "--state-dir",
        default=None,
        help="Override state dir (default ~/.claude/skills/x-create/state)",
    )
    subp.add_argument("--run-id", default=None, help="Optional run id for event correlation")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="x_state.py")
    _add_common(p)

    sub = p.add_subparsers(dest="cmd", required=True)

    sub_init = sub.add_parser("init", help="Initialize state files")
    _add_common(sub_init)
    sub_init.set_defaults(func=cmd_init)

    sub_event = sub.add_parser("event", help="Append an event to events.jsonl")
    _add_common(sub_event)
    sub_event.add_argument("--event", required=True)
    sub_event.add_argument("--payload-json", default="{}")
    sub_event.set_defaults(func=cmd_event)

    sub_like = sub.add_parser("like", help="Upsert a liked topic")
    _add_common(sub_like)
    sub_like.add_argument("--topic-json", required=True)
    sub_like.set_defaults(func=cmd_like)

    sub_reject = sub.add_parser("reject", help="Upsert a rejected topic")
    _add_common(sub_reject)
    sub_reject.add_argument("--topic-json", required=True)
    sub_reject.set_defaults(func=cmd_reject)

    sub_sim = sub.add_parser("similarity", help="Compute similarity against a corpus")
    _add_common(sub_sim)
    sub_sim.add_argument("--against", required=True, choices=["rejected"])
    sub_sim.add_argument("--text", required=True)
    sub_sim.add_argument("--topk", type=int, default=3)
    sub_sim.set_defaults(func=cmd_similarity)

    sub_hook = sub.add_parser("hook-ingest", help="Ingest HOOKS_JSON into liked topics")
    _add_common(sub_hook)
    sub_hook.add_argument("--hooks-json", required=True)
    sub_hook.set_defaults(func=cmd_hook_ingest)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
