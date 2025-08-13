# imaging.py
import os
import requests
from PIL import Image, ImageDraw, ImageFont

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def get_first_valid_image_url_or_none(url: str | None) -> str | None:
    if not url:
        return None
    return url.replace("&amp;","&")

def _unsplash_random(query: str) -> str | None:
    if not UNSPLASH_ACCESS_KEY:
        return None
    try:
        r = requests.get("https://api.unsplash.com/photos/random", params={"query":query,"client_id":UNSPLASH_ACCESS_KEY}, timeout=15)
        r.raise_for_status()
        data = r.json()
        return (data.get("urls") or {}).get("regular")
    except Exception:
        return None

def download_image_to_path(url: str | None, path: str, query: str | None = None) -> bool:
    try:
        candidate = url
        if not candidate and query:
            candidate = _unsplash_random(query)
        if not candidate:
            return False
        resp = requests.get(candidate, timeout=20)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception:
        return False

def generate_fallback_image(text: str, path: str, size=(1200,675)):
    img = Image.new("RGB", size, color=(240,247,245))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    margin = 60
    max_width = size[0] - 2*margin

    wrapped = []
    line = ""
    for word in text.split():
        test = (line + " " + word).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            line = test
        else:
            if line:
                wrapped.append(line)
            line = word
    if line:
        wrapped.append(line)

    y = size[1]//3
    for ln in wrapped:
        bbox = draw.textbbox((0,0), ln, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (size[0]-w)//2
        draw.text((x,y), ln, fill=(30,45,40), font=font)
        y += h + 10

    footer = "Health & Longevity Daily"
    bbox = draw.textbbox((0,0), footer, font=font)
    fw = bbox[2] - bbox[0]
    fh = bbox[3] - bbox[1]
    draw.text((size[0]-fw-16, size[1]-fh-12), footer, fill=(80,100,95), font=font)

    img.save(path, format="JPEG", quality=88)
