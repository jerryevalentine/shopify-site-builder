# test_shopify_connection.py
import shopify
import os
from dotenv import load_dotenv

load_dotenv()

shop_url = os.getenv("SHOPIFY_STORE_URL")
api_version = "2023-10"
token = os.getenv("SHOPIFY_ADMIN_API_TOKEN")

shopify.Session.setup(api_key=os.getenv("SHOPIFY_API_KEY"), secret=os.getenv("SHOPIFY_API_SECRET"))
session = shopify.Session(shop_url, api_version, token)
shopify.ShopifyResource.activate_session(session)

shop = shopify.Shop.current()
print(f"Connected to store: {shop.name}")
