"""Optional GetXAPI evidence helper for x-collect."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://api.getxapi.com"
DEFAULT_TIMEOUT_SECONDS = 30
MAX_LIMIT = 25


@dataclass(frozen=True)
class TweetEvidence:
    text: str
    author: str
    url: str
    likes: int | None
    reposts: int | None
    replies: int | None
    created_at: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def env_api_key() -> str:
    return os.getenv("GETXAPI_API_KEY") or os.getenv("GETXAPI_KEY") or ""


def env_base_url() -> str:
    return (os.getenv("GETXAPI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/") + "/"


def build_headers(api_key: str) -> dict[str, str]:
    if not api_key:
        return {}
    return {"authorization": f"Bearer {api_key}"}


def clamp_limit(value: int) -> int:
    return max(1, min(value, MAX_LIMIT))


def request_json(path: str, query: dict[str, str], *, timeout: int) -> dict[str, Any]:
    key = env_api_key()
    if not key:
        return {
            "success": False,
            "skipped": True,
            "error": "Set GETXAPI_API_KEY to collect X evidence.",
        }

    url = urljoin(env_base_url(), path.lstrip("/"))
    if query:
        url = f"{url}?{urlencode(query)}"
    request = Request(url=url, headers=build_headers(key), method="GET")

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "success": False,
            "status_code": exc.code,
            "error": "API request failed.",
            "response": safe_json(body),
        }
    except URLError as exc:
        return {"success": False, "error": f"Network error: {exc.reason}"}

    parsed = safe_json(payload)
    if isinstance(parsed, dict):
        return parsed
    return {"success": True, "data": parsed}


def safe_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}


def find_first(value: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in value:
            return value[name]
    return None


def as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return None


def walk_lists(value: Any) -> list[Any]:
    output: list[Any] = []
    if isinstance(value, list):
        output.extend(value)
        for item in value:
            output.extend(walk_lists(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {
                "data",
                "tweets",
                "results",
                "items",
                "entries",
                "timeline",
                "replies",
            }:
                output.extend(walk_lists(item))
    return output


def normalize_author(item: dict[str, Any]) -> str:
    author = find_first(item, ("author", "user", "core", "account"))
    if isinstance(author, dict):
        value = find_first(author, ("username", "screen_name", "handle", "name", "id"))
        if value:
            return str(value).lstrip("@")
    value = find_first(item, ("username", "screen_name", "author_username", "authorId", "userId"))
    if value:
        return str(value).lstrip("@")
    return ""


def normalize_url(item: dict[str, Any], author: str) -> str:
    value = find_first(item, ("url", "tweet_url", "link", "permalink"))
    if value:
        return str(value)
    tweet_id = find_first(item, ("id", "tweet_id", "tweetId", "rest_id"))
    if tweet_id and author:
        return f"https://x.com/{author}/status/{tweet_id}"
    if tweet_id:
        return f"https://x.com/i/web/status/{tweet_id}"
    return ""


def normalize_metrics(item: dict[str, Any], *names: str) -> int | None:
    value = find_first(item, names)
    if value is not None:
        return as_int(value)
    metrics = find_first(item, ("metrics", "public_metrics", "counts", "stats"))
    if isinstance(metrics, dict):
        value = find_first(metrics, names)
        if value is not None:
            return as_int(value)
    return None


def normalize_tweet(item: Any) -> TweetEvidence | None:
    if not isinstance(item, dict):
        return None
    text = find_first(item, ("text", "full_text", "fullText", "content", "body"))
    if not isinstance(text, str) or not text.strip():
        return None
    author = normalize_author(item)
    return TweetEvidence(
        text=" ".join(text.split()),
        author=author,
        url=normalize_url(item, author),
        likes=normalize_metrics(item, "likes", "like_count", "favorite_count", "favorites"),
        reposts=normalize_metrics(item, "reposts", "retweets", "retweet_count", "repost_count"),
        replies=normalize_metrics(item, "replies", "reply_count", "comments"),
        created_at=str(find_first(item, ("created_at", "createdAt", "date", "time")) or ""),
    )


def extract_tweets(payload: Any, *, limit: int) -> list[TweetEvidence]:
    tweets: list[TweetEvidence] = []
    seen: set[tuple[str, str]] = set()
    for item in walk_lists(payload):
        tweet = normalize_tweet(item)
        if tweet is None:
            continue
        key = (tweet.url, tweet.text)
        if key in seen:
            continue
        seen.add(key)
        tweets.append(tweet)
        if len(tweets) >= limit:
            break
    return tweets


def evidence_payload(kind: str, source: str, raw: dict[str, Any], tweets: list[TweetEvidence]) -> dict[str, Any]:
    return {
        "schema_version": "x_skills.getxapi_evidence.v1",
        "kind": kind,
        "source": source,
        "timestamp": utc_now(),
        "skipped": bool(raw.get("skipped")),
        "success": raw.get("success", True) is not False and not raw.get("skipped"),
        "error": raw.get("error"),
        "items": [
            {
                "text": item.text,
                "author": item.author,
                "url": item.url,
                "likes": item.likes,
                "reposts": item.reposts,
                "replies": item.replies,
                "created_at": item.created_at,
            }
            for item in tweets
        ],
    }


def markdown_table(payload: dict[str, Any]) -> str:
    if payload["skipped"]:
        return f"X evidence skipped: {payload['error']}"
    if not payload["success"]:
        return f"X evidence unavailable: {payload['error'] or 'request failed'}"
    if not payload["items"]:
        return "X evidence returned no tweet-like items."
    lines = [
        f"## X Evidence ({payload['kind']})",
        "",
        "| Author | Engagement | Evidence |",
        "| --- | ---: | --- |",
    ]
    for item in payload["items"]:
        engagement = sum(v or 0 for v in (item["likes"], item["reposts"], item["replies"]))
        text = item["text"][:140] + ("..." if len(item["text"]) > 140 else "")
        source = f"[source]({item['url']})" if item["url"] else "source unavailable"
        author = f"@{item['author']}" if item["author"] else "unknown"
        lines.append(f"| {author} | {engagement} | {text} ({source}) |")
    return "\n".join(lines)


def print_payload(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(markdown_table(payload))


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")


def command_search(args: argparse.Namespace) -> int:
    limit = clamp_limit(args.limit)
    raw = request_json(
        "/twitter/tweet/advanced_search",
        {"q": args.query, "queryType": args.query_type, "limit": str(limit)},
        timeout=args.timeout,
    )
    tweets = extract_tweets(raw, limit=limit)
    print_payload(evidence_payload("tweet_search", args.query, raw, tweets), args.format)
    return 0 if raw.get("success", True) is not False or raw.get("skipped") else 1


def command_replies(args: argparse.Namespace) -> int:
    limit = clamp_limit(args.limit)
    raw = request_json(
        "/twitter/tweet/advanced_search",
        {"q": f"conversation_id:{args.tweet_id}", "limit": str(limit)},
        timeout=args.timeout,
    )
    tweets = extract_tweets(raw, limit=limit)
    print_payload(evidence_payload("tweet_replies", args.tweet_id, raw, tweets), args.format)
    return 0 if raw.get("success", True) is not False or raw.get("skipped") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect optional X evidence for x-collect via GetXAPI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search public X posts.")
    search.add_argument("query")
    search.add_argument("--query-type", choices=("Top", "Latest"), default="Top")
    add_common_arguments(search)
    search.set_defaults(func=command_search)

    replies = subparsers.add_parser("replies", help="Collect replies for one post via conversation_id search.")
    replies.add_argument("tweet_id")
    add_common_arguments(replies)
    replies.set_defaults(func=command_replies)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
