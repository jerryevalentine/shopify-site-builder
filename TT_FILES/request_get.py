import os
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
THEME_ID = "138732503085"  # Your known theme ID

# Define the asset you want to check
asset_key = "assets/background.jpg"
url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/themes/{THEME_ID}/assets.json"
params = {
    "asset[key]": asset_key
}
headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# Make the GET request
response = requests.get(url, headers=headers, params=params)

# Handle response
if response.status_code == 200:
    print(f"✅ Asset found: {asset_key}")
    print(response.json())
elif response.status_code == 404:
    print(f"❌ Asset NOT found: {asset_key}")
else:
    print(f"⚠️ Unexpected response: {response.status_code}")
    print(response.text)
