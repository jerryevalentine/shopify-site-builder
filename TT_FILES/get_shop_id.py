import os
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv()
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Define headers
headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# Send request to shop endpoint
url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/shop.json"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    shop_info = response.json().get("shop", {})
    print(f"Store ID: {shop_info.get('id')}")
    print(f"Shop Name: {shop_info.get('name')}")
    print(f"Domain: {shop_info.get('domain')}")
else:
    print(f"❌ Failed to fetch store ID: {response.status_code}")
    print(response.text)
