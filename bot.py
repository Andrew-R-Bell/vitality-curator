# bot.py
import os
import random
import traceback
from sources import fetch_news_article, fetch_reddit_post
from imaging import download_image_to_path, get_first_valid_image_url_or_none, generate_fallback_image
from posting import post_to_twitter

POST_MODE = os.getenv("POST_MODE", "auto").lower()  # auto/news/reddit
HASHTAGS = "#Longevity #Health #Wellness #Biohacking"

def trim_caption_for_twitter(text: str, url: str = "") -> str:
    max_len = 280
    url_budget = 25 if url else 0
    body_budget = max_len - url_budget
    text = text.strip()
    if len(text) > body_budget:
        text = text[: body_budget - 1].rstrip() + "…"
    return f"{text} {url}".strip()

def build_caption_from_news(article: dict) -> str:
    title = article.get("title") or "Interesting health article"
    source = (article.get("source") or {}).get("name") or ""
    base = f"📰 {title}"
    if source:
        base += f" — {source}"
    base += f"\n{HASHTAGS}"
    return trim_caption_for_twitter(base, article.get("url", ""))

def build_caption_from_reddit(post: dict) -> str:
    title = post.get("title") or "Trending on Reddit"
    base = f"🔥 {title}\n{HASHTAGS}"
    return trim_caption_for_twitter(base, post.get("url", ""))

def choose_item():
    mode = POST_MODE
    if mode == "auto":
        mode = random.choice(["news", "reddit"])

    if mode == "news":
        article = fetch_news_article()
        if article:
            return {
                "type": "news",
                "caption": build_caption_from_news(article),
                "image_url": get_first_valid_image_url_or_none(article.get("urlToImage")),
                "fallback_query": "health longevity wellness",
                "url": article.get("url"),
                "title": article.get("title", ""),
            }
    post = fetch_reddit_post()
    if post:
        return {
            "type": "reddit",
            "caption": build_caption_from_reddit(post),
            "image_url": get_first_valid_image_url_or_none(post.get("image_url")),
            "fallback_query": "health longevity",
            "url": post.get("url"),
            "title": post.get("title", ""),
        }
    return None

def run_once():
    try:
        print("[Bot] Selecting item…")
        item = choose_item()
        if not item:
            print("[Bot] No content found today.")
            return

        image_path = "image.jpg"
        ok = False
        if item.get("image_url"):
            ok = download_image_to_path(item["image_url"], image_path)

        if not ok:
            ok = download_image_to_path(None, image_path, query=item.get("fallback_query", "health"))

        if not ok:
            generate_fallback_image(item.get("title", "Health & Longevity"), image_path)

        print("[Bot] Posting to Twitter/X…")
        post_to_twitter(item["caption"], image_path)
        print("[Bot] Done.")
    except Exception as e:
        print("[Bot][ERROR]", e)
        traceback.print_exc()