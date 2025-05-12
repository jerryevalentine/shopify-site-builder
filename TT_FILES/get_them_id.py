import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/themes.json"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    themes = response.json().get('themes', [])
    for theme in themes:
        print(f"Theme ID: {theme['id']}, Name: {theme['name']}, Role: {theme['role']}")
else:
    print(f"Failed to fetch themes: {response.status_code}")
    print(response.text)
