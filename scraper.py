#!/usr/bin/env python3
"""
Ghibli Landscapes API - Image Scraper

This script collects landscape images from the Studio Ghibli website
and creates a structured database for the API.
"""

import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urljoin

# Constants
BASE_URL = "https://www.ghibli.jp/works/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")

# Film codes from the website
FILM_CODES = [
    "kimitachi",    # 君たちはどう生きるか
    "aya",          # アーヤと魔女
    "red",          # レッドタートル
    "marnie",       # 思い出のマーニー
    "kaguyahime",   # かぐや姫の物語
    "kazetachinu",  # 風立ちぬ
    "kokurikozaka", # コクリコ坂から
    "karigurashi",  # 借りぐらしのアリエッティ
    "ponyo",        # 崖の上のポニョ
    "ged",          # ゲド戦記
    "howl",         # ハウルの動く城
    "baron",        # 猫の恩返し
    "ghiblies",     # ギブリーズ
    "chihiro",      # 千と千尋の神隠し
    "yamada",       # ホーホケキョ となりの山田くん
    "mononoke",     # もののけ姫
    "mimi",         # 耳をすませば
    "onmark",       # On Your Mark
    "tanuki",       # 平成狸合戦ぽんぽこ
    "umi",          # 海がきこえる
    "porco",        # 紅の豚
    "omoide",       # おもひでぽろぽろ
    "majo",         # 魔女の宅急便
    "totoro",       # となりのトトロ
    "hotaru",       # 火垂るの墓
    "laputa",       # 天空の城ラピュタ
    "nausicaa",     # 風の谷のナウシカ
]

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to determine if an image is a landscape (not character-focused)
def is_landscape_image(image_url):
    """
    Heuristic to determine if an image is a landscape/background.
    This is a simplified approach - in a production environment, 
    you might want to use image classification models.
    """
    # For this implementation, we'll use a simple heuristic:
    # Images with characters often have specific patterns in their filenames
    # or might be in portrait orientation
    
    # This is a simplified approach - in reality, you'd want to use
    # image analysis to determine if an image is a landscape
    
    # For now, we'll assume all images are potential landscapes
    # A more sophisticated approach would analyze the image content
    return True

# Function to get all image URLs from a film's page
def get_film_images(film_code):
    """Get all image URLs from a film's still images page."""
    url = f"{BASE_URL}{film_code}/#frame"
    print(f"Fetching images from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all image links
        image_links = []
        for a_tag in soup.find_all('a'):
            img_tag = a_tag.find('img')
            if img_tag and img_tag.get('alt') and film_code in img_tag.get('alt', ''):
                # Get the full-size image URL
                # The pattern seems to be: https://www.ghibli.jp/gallery/[film_code][number].jpg
                img_alt = img_tag.get('alt')
                if re.match(f"{film_code}\\d+", img_alt):
                    image_number = img_alt.replace(film_code, '')
                    full_image_url = f"https://www.ghibli.jp/gallery/{film_code}{image_number}.jpg"
                    image_links.append(full_image_url)
        
        # Filter for landscape images
        landscape_images = [url for url in image_links if is_landscape_image(url)]
        
        print(f"Found {len(landscape_images)} landscape images for {film_code}")
        return landscape_images
    
    except Exception as e:
        print(f"Error fetching images for {film_code}: {e}")
        return []

# Function to generate a consistent ID for an image URL
def generate_image_id(image_url):
    """Generate a consistent ID for an image URL using SHA-256."""
    return hashlib.sha256(image_url.encode()).hexdigest()[:16]

# Main function to collect all images
def collect_all_images():
    """Collect all landscape images from all films and create a database."""
    database = {
        "images": [],
        "film_codes": FILM_CODES
    }
    
    for film_code in FILM_CODES:
        print(f"Processing film: {film_code}")
        image_urls = get_film_images(film_code)
        
        for image_url in image_urls:
            image_id = generate_image_id(image_url)
            
            # Extract film name and image number from URL
            match = re.search(r'/([^/]+)(\d+)\.jpg$', image_url)
            if match:
                film_name = match.group(1)
                image_number = match.group(2)
            else:
                film_name = film_code
                image_number = "unknown"
            
            database["images"].append({
                "id": image_id,
                "url": image_url,
                "film_code": film_code,
                "film_name": film_name,
                "image_number": image_number
            })
        
        # Be nice to the server
        time.sleep(1)
    
    # Save the database to a JSON file
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"Database created with {len(database['images'])} images")
    return database

if __name__ == "__main__":
    print("Starting Ghibli landscape image collection...")
    database = collect_all_images()
    print(f"Collection complete. Found {len(database['images'])} landscape images.")
    print(f"Database saved to {DATABASE_FILE}")
