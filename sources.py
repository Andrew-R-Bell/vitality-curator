# sources.py
import os
import random
import requests
import praw

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "longevity-curator/1.0")

NEWS_QUERY = "(longevity OR \"healthspan\" OR \"anti-aging\" OR \"healthy aging\" OR nutrition OR exercise OR sleep) AND (study OR research OR science OR evidence OR trial)"
NEWS_SOURCES_ENDPOINT = "https://newsapi.org/v2/everything"
REDDIT_SUBS = ["Longevity","Nutrition","Biohackers","HealthyFood","Fitness"]

def fetch_news_article() -> dict | None:
    if not NEWSAPI_KEY:
        return None
    try:
        r = requests.get(NEWS_SOURCES_ENDPOINT, params={"q": NEWS_QUERY,"language":"en","sortBy":"publishedAt","pageSize":20,"apiKey":NEWSAPI_KEY}, timeout=15)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        if not articles:
            return None
        with_img = [a for a in articles if a.get("urlToImage")] or articles
        return random.choice(with_img)
    except Exception:
        return None

def _reddit_client():
    if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET):
        return None
    return praw.Reddit(client_id=REDDIT_CLIENT_ID,client_secret=REDDIT_CLIENT_SECRET,user_agent=REDDIT_USER_AGENT)

def fetch_reddit_post() -> dict | None:
    reddit = _reddit_client()
    if not reddit:
        return None
    try:
        sub = reddit.subreddit(random.choice(REDDIT_SUBS))
        candidates = list(sub.top(time_filter="week", limit=25))
        if not candidates:
            return None
        def extract_img(p):
            try:
                if hasattr(p, "preview"):
                    return p.preview["images"][0]["source"]["url"]
            except Exception:
                pass
            if str(p.url).lower().endswith((".jpg", ".jpeg", ".png")):
                return p.url
            return None
        enriched = [{"title":p.title,"url":p.url,"image_url":extract_img(p),"score":getattr(p,"score",0)} for p in candidates]
        enriched.sort(key=lambda x:x.get("score",0),reverse=True)
        top = enriched[:8] if len(enriched)>=8 else enriched
        return random.choice(top) if top else None
    except Exception:
        return None