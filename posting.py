# posting.py

# This file includes full API posting functions for Twitter/X, Instagram, Facebook, and Bluesky.
# Ensure environment variables are set and required packages are installed (tweepy, requests, atproto).
# For testing without posting, set DRY_RUN=true in your environment variables.

import os
import requests
from atproto import Client as BlueskyClient

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# --- Twitter/X ---
import tweepy

def post_to_twitter(caption: str, image_path: str):
    if DRY_RUN:
        print(f"[Dry Run] Would post to Twitter/X with caption: {caption}")
        return
    try:
        # Initialize both v1.1 (for media) and v2 (for posting)
        auth = tweepy.OAuth1UserHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET"),
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_SECRET")
        )
        api_v1 = tweepy.API(auth)
        
        # Upload media using v1.1
        media = api_v1.media_upload(filename=image_path)
        
        # Post using v2
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
        )
        
        client.create_tweet(text=caption, media_ids=[media.media_id])
        print("[Twitter/X] Posted successfully.")
    except Exception as e:
        print("[Twitter/X][ERROR]", e)


# --- Instagram ---
def post_to_instagram(caption: str, image_path: str):
    if DRY_RUN:
        print(f"[Dry Run] Would post to Instagram with caption: {caption}")
        return
    try:
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        ig_user_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        if not access_token or not ig_user_id:
            raise ValueError("Instagram credentials not set in environment variables.")

        image_upload_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        with open(image_path, "rb") as f:
            image_data = f.read()
        files = {"source": image_data}
        params = {"caption": caption, "access_token": access_token}
        r = requests.post(image_upload_url, params=params, files=files)
        r.raise_for_status()
        creation_id = r.json()["id"]

        publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        publish_params = {"creation_id": creation_id, "access_token": access_token}
        requests.post(publish_url, params=publish_params)
        print("[Instagram] Posted successfully.")
    except Exception as e:
        print("[Instagram][ERROR]", e)


# --- Facebook ---
def post_to_facebook(caption: str, image_path: str):
    if DRY_RUN:
        print(f"[Dry Run] Would post to Facebook with caption: {caption}")
        return
    try:
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN") 
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        if not page_access_token or not page_id:
            raise ValueError("Facebook credentials not set in environment variables.")

        url = f"https://graph.facebook.com/{page_id}/photos"
        with open(image_path, "rb") as f:
            files = {"source": f}
            data = {"caption": caption, "access_token": page_access_token}
            r = requests.post(url, files=files, data=data)
        r.raise_for_status()
        print("[Facebook] Posted successfully.")
    except Exception as e:
        print("[Facebook][ERROR]", e)


# --- Bluesky ---
def post_to_bluesky(caption: str, image_path: str):
    if DRY_RUN:
        print(f"[Dry Run] Would post to Bluesky with caption: {caption}")
        return
    try:
        handle = os.getenv("BLUESKY_HANDLE")
        password = os.getenv("BLUESKY_PASSWORD")
        if not handle or not password:
            raise ValueError("Bluesky credentials not set in environment variables.")

        client = BlueskyClient()
        client.login(handle, password)

        with open(image_path, "rb") as f:
            img_data = f.read()
        blob = client.com.atproto.repo.upload_blob(img_data)

        client.com.atproto.repo.create_record(
            repo=client.me.did,
            collection="app.bsky.feed.post",
            record={
                "$type": "app.bsky.feed.post",
                "text": caption,
                "embed": {
                    "$type": "app.bsky.embed.images",
                    "images": [
                        {
                            "alt": caption,
                            "image": blob.blob,
                        }
                    ]
                }
            }
        )
        print("[Bluesky] Posted successfully.")
    except Exception as e:
        print("[Bluesky][ERROR]", e)
