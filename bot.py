# bot.py


import os
import random
import traceback
import logging
import re
from urllib.parse import urlparse
from datetime import datetime
from sources import fetch_news_article, fetch_reddit_post
from imaging import download_image_to_path, get_first_valid_image_url_or_none, generate_fallback_image
from posting import post_to_twitter, post_to_instagram, post_to_facebook, post_to_bluesky
from posting import post_to_twitter, post_to_instagram, post_to_facebook, post_to_bluesky

POST_MODE = os.getenv("POST_MODE", "auto").lower()  # auto/news/reddit
HASHTAGS = "#Longevity #Health #Wellness #Biohacking"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
BLOCKLIST_DOMAINS = set(os.getenv("BLOCKLIST_DOMAINS", "").split(","))
BLOCKLIST_KEYWORDS = set(os.getenv("BLOCKLIST_KEYWORDS", "").lower().split(","))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
BLOCKLIST_DOMAINS = set(os.getenv("BLOCKLIST_DOMAINS", "").split(","))
BLOCKLIST_KEYWORDS = set(os.getenv("BLOCKLIST_KEYWORDS", "").lower().split(","))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def trim_caption_for_twitter(text: str, url: str = "") -> str:
    max_len = 280
    url_budget = 25 if url else 0
    body_budget = max_len - url_budget
    text = text.strip()
    if len(text) > body_budget:
        text = text[: body_budget - 1].rstrip() + "…"
    return f"{text} {url}".strip()

def is_blocked(text: str, url: str) -> bool:
    text_lower = text.lower()
    if any(domain in url for domain in BLOCKLIST_DOMAINS if domain):
        return True
    if any(keyword in text_lower for keyword in BLOCKLIST_KEYWORDS if keyword):
        return True
    return False

def is_blocked(text: str, url: str) -> bool:
    text_lower = text.lower()
    if any(domain in url for domain in BLOCKLIST_DOMAINS if domain):
        return True
    if any(keyword in text_lower for keyword in BLOCKLIST_KEYWORDS if keyword):
        return True
    return False

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
        if article and not is_blocked(article.get("title", ""), article.get("url", "")):        
            return {
                "type": "news",
                "caption": build_caption_from_news(article),
                "image_url": get_first_valid_image_url_or_none(article.get("urlToImage")),
                "fallback_query": "health longevity wellness",
                "url": article.get("url"),
                "title": article.get("title", ""),
            }
    post = fetch_reddit_post()
    if post and not is_blocked(post.get("title", ""), post.get("url", "")):    
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
    start_time = datetime.now()
    logger.info(f"[Bot] Starting execution at {start_time}")
    
    start_time = datetime.now()
    logger.info(f"[Bot] Starting execution at {start_time}")
    
    try:
        # Content selection
        # Content selection
        item = choose_item()
        if not item:
            logger.warning("[Bot] No suitable content found today.")
            logger.warning("[Bot] No suitable content found today.")
            return

        # Image handling with better error tracking
        # Image handling with better error tracking
        image_path = "image.jpg"
        image_success = False
        
        image_success = False
        
        if item.get("image_url"):
            image_success = download_image_to_path(item["image_url"], image_path)
            if image_success:
                logger.info(f"[Bot] Downloaded image from: {item['image_url']}")
        
        if not image_success and item.get("fallback_query"):
            image_success = download_image_to_path(None, image_path, query=item["fallback_query"])
            if image_success:
                logger.info(f"[Bot] Downloaded fallback image for query: {item['fallback_query']}")
        
        if not image_success:
            image_success = download_image_to_path(item["image_url"], image_path)
            if image_success:
                logger.info(f"[Bot] Downloaded image from: {item['image_url']}")
        
        if not image_success and item.get("fallback_query"):
            image_success = download_image_to_path(None, image_path, query=item["fallback_query"])
            if image_success:
                logger.info(f"[Bot] Downloaded fallback image for query: {item['fallback_query']}")
        
        if not image_success:
            generate_fallback_image(item.get("title", "Health & Longevity"), image_path)
            logger.info("[Bot] Generated fallback text image")

        if DRY_RUN:
            logger.info(f"[Dry Run] Caption: {item['caption']}")
            logger.info(f"[Dry Run] Image path: {image_path}")
            logger.info("[Dry Run] Would post to: Twitter/X, Instagram, Facebook, Bluesky")
            return

        # Post to platforms with individual error handling
        platforms = [
            ("Twitter/X", post_to_twitter),
            ("Instagram", post_to_instagram),
            ("Facebook", post_to_facebook),
            ("Bluesky", post_to_bluesky)
        ]
        
        success_count = 0
        for platform_name, post_func in platforms:
            try:
                logger.info(f"[Bot] Posting to {platform_name}...")
                post_func(item["caption"], image_path)
                success_count += 1
            except Exception as e:
                logger.error(f"[Bot] Failed to post to {platform_name}: {str(e)}")

        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[Bot] Completed in {execution_time:.2f}s. Posted to {success_count}/4 platforms.")
        logger.info("[Bot] Generated fallback text image")

        if DRY_RUN:
            logger.info(f"[Dry Run] Caption: {item['caption']}")
            logger.info(f"[Dry Run] Image path: {image_path}")
            logger.info("[Dry Run] Would post to: Twitter/X, Instagram, Facebook, Bluesky")
            return

        # Post to platforms with individual error handling
        platforms = [
            ("Twitter/X", post_to_twitter),
            ("Instagram", post_to_instagram),
            ("Facebook", post_to_facebook),
            ("Bluesky", post_to_bluesky)
        ]
        
        success_count = 0
        for platform_name, post_func in platforms:
            try:
                logger.info(f"[Bot] Posting to {platform_name}...")
                post_func(item["caption"], image_path)
                success_count += 1
            except Exception as e:
                logger.error(f"[Bot] Failed to post to {platform_name}: {str(e)}")

        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[Bot] Completed in {execution_time:.2f}s. Posted to {success_count}/4 platforms.")

    except Exception as e:
        logger.error(f"[Bot] Critical error: {str(e)}")
        logger.error(traceback.format_exc())
