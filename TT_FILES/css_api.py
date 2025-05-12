# C:\Users\jerry\ecommerce\shopify_deploy
# python css_api.py

import ssl
import certifi
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['SSL_CERT_FILE'] = certifi.where()

import csv
import requests
import json

# -------------------------------------------
# Shopify Admin API credentials
# -------------------------------------------
SHOP_NAME = "ifzmze-sz.myshopify.com"  # Correct store from .env
ACCESS_TOKEN = "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"
API_VERSION = "2023-10"





# -------------------------------------------
# File paths
# -------------------------------------------
STYLE_FOLDER = "style"
STYLE_CSV_FILE = "theme_variables.csv"
GENERATED_CSS_FILE = "custom_theme.css"

CSV_PATH = os.path.join(STYLE_FOLDER, STYLE_CSV_FILE)
CSS_PATH = os.path.join(STYLE_FOLDER, GENERATED_CSS_FILE)
ASSET_KEY = f"assets/{GENERATED_CSS_FILE}"

# -------------------------------------------
# Convert CSV to CSS string
# -------------------------------------------
def build_css_from_csv(csv_path):
    css_lines = [":root {"]
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            variable = row["variable"].strip()
            value = row["value"].strip()
            css_lines.append(f"  {variable}: {value};")
    css_lines.append("}")
    return "\n".join(css_lines)

# -------------------------------------------
# Save CSS content to file
# -------------------------------------------
def save_css_file(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# -------------------------------------------
# Get active theme ID (debugging included)
# -------------------------------------------
def get_active_theme_id():
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/themes.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch themes: {response.status_code}\n{response.text}")

    themes = response.json().get("themes", [])
    if not themes:
        raise Exception("No themes returned from Shopify.")

    print("\nAvailable Themes:")
    for theme in themes:
        print(f"- Name: {theme['name']}, ID: {theme['id']}, Role: {theme['role']}")

    for theme in themes:
        if theme.get("role") == "main":
            return theme["id"]

    raise Exception("Active theme with role='main' not found.")

# -------------------------------------------
# Upload CSS to Shopify
# -------------------------------------------
def upload_css_to_shopify(css_path):
    with open(css_path, "r", encoding="utf-8") as file:
        css_content = file.read()

    theme_id = get_active_theme_id()
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/themes/{theme_id}/assets.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "asset": {
            "key": ASSET_KEY,
            "value": css_content
        }
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload), verify=False)
    if response.status_code == 200:
        print("✅ CSS uploaded successfully.")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.json())

# -------------------------------------------
# Main script
# -------------------------------------------
if __name__ == "__main__":
    try:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")

        css_content = build_css_from_csv(CSV_PATH)
        save_css_file(css_content, CSS_PATH)
        upload_css_to_shopify(CSS_PATH)

    except Exception as e:
        print(f"Error: {e}")
