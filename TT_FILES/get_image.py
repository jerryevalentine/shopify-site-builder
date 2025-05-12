#python get_image.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
THEME_ID = "138732503085"

url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/themes/{THEME_ID}/assets.json"
headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}
params = {
    "asset[key]": "assets/background.jpg"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    print("✅ Asset exists in theme assets.")
else:
    print(f"❌ Asset not found. Status: {response.status_code}")
