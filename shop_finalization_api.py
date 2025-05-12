import os
import csv
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SHOPIFY_DOMAIN = os.getenv("SHOPIFY_STORE_URL").replace("https://", "").rstrip("/")
API_VERSION = os.getenv("SHOPIFY_API_VERSION")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
THEME_ID = os.getenv("THEME_ID")
BASE_FOLDER = os.getenv("FOLDER")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def get_product_id_by_handle(handle):
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/products.json?handle={handle}"
    response = requests.get(url, headers=HEADERS)
    if response.ok and response.json().get("products"):
        return response.json()["products"][0]["id"]
    print(f"⚠️ Product with handle '{handle}' not found.")
    return None

def get_page_id_by_handle(handle):
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/pages.json?handle={handle}"
    response = requests.get(url, headers=HEADERS)
    if response.ok and response.json().get("pages"):
        return response.json()["pages"][0]["id"]
    print(f"⚠️ Page with handle '{handle}' not found.")
    return None

def update_product_seo(product_id, title, description):
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/products/{product_id}.json"
    data = {
        "product": {
            "id": product_id,
            "metafields_global_title_tag": title,
            "metafields_global_description_tag": description
        }
    }
    response = requests.put(url, json=data, headers=HEADERS)
    return response.ok

def update_page_seo(page_id, title, description):
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/pages/{page_id}.json"
    data = {
        "page": {
            "id": page_id,
            "metafields_global_title_tag": title,
            "metafields_global_description_tag": description
        }
    }
    response = requests.put(url, json=data, headers=HEADERS)
    return response.ok

def update_seo_metadata(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            handle = (row.get("handle") or "").strip()
            seo_title = (row.get("seo_title") or "").strip()
            seo_description = (row.get("seo_description") or "").strip()
            object_type = (row.get("type") or "").strip().lower()

            if object_type == "product":
                product_id = get_product_id_by_handle(handle)
                if product_id:
                    success = update_product_seo(product_id, seo_title, seo_description)
                    if success:
                        print(f"✅ Updated SEO for product: {handle}")
            elif object_type == "page":
                page_id = get_page_id_by_handle(handle)
                if page_id:
                    success = update_page_seo(page_id, seo_title, seo_description)
                    if success:
                        print(f"✅ Updated SEO for page: {handle}")
            else:
                print(f"⚠️ Unknown type '{object_type}' for handle '{handle}'")

if __name__ == "__main__":
    CSV_FILE = os.path.join(BASE_FOLDER, "csv", "seo_metadata.csv")
    update_seo_metadata(CSV_FILE)