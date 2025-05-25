# deploy.py

# Load Libraries
import os
import pandas as pd
import requests
from dotenv import load_dotenv

# Load shopify_api Library
from utils.shopify_api import (
    create_product,
    create_collection,
    find_product_id_by_sku,
    find_collection_id_by_title,
    add_product_to_collection,
    upload_local_image_to_product,
    upload_local_image_to_product_with_alt,
    create_page,
    find_navigation_menu_id_by_title,
    find_product_id_by_title,
    find_page_id_by_title,
    add_link_to_navigation_menu,
    upload_theme_asset,
    upload_asset,
    inject_assets_into_theme,
    #inject_scrolling_banner,
    inject_splash_screen,
    upload_hover_snippets_from_csv,
    insert_multiple_snippets_into_theme_file
)

# Step 0: Load environment variables and Shopify REST session
load_dotenv()

SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
SHOPIFY_API_VERSION = os.getenv('SHOPIFY_API_VERSION', '2023-04')
FOLDER = os.getenv('FOLDER')
THEME_ID = os.getenv('THEME_ID')

# Create Shopify REST session
session = requests.Session()
session.headers.update({
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
})
session.shop = SHOPIFY_STORE_URL.replace("https://", "")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
def csv_path(filename): return os.path.join(BASE_DIR, FOLDER, "csv", filename)
def image_path(filename): return os.path.join(BASE_DIR, FOLDER, "images", filename)
def theme_file_path(filename): return os.path.join(BASE_DIR, FOLDER, "theme_files", filename)

# Step 1: Load CSVs
print("\n📂 Loading CSV files...")
products_df = pd.read_csv(csv_path('sku_master.csv'))
collections_df = pd.read_csv(csv_path('page_url.csv'))
page_sku_df = pd.read_csv(csv_path('page_sku.csv'))
images_df = pd.read_csv(csv_path('sku_images.csv'))
pages_df = pd.read_csv(csv_path('pages.csv'))
nav_links_df = pd.read_csv(csv_path('navigation_links.csv'))
images_alt_df = pd.read_csv(csv_path('sku_images_alt.csv'))

# Step 2: Upload Products
print("\n📦 Uploading Products...")
for _, row in products_df.iterrows():
    try:
        create_product(row)
        print(f"✅ Uploaded Product: {row['Product_Name']}")
    except Exception as e:
        print(f"❌ Failed to upload product {row['Product_Name']}: {e}")


# Step 3: Create Collections
print("\n🗂️ Creating Collections...")
for _, row in collections_df.iterrows():
    try:
        create_collection(row)
        print(f"✅ Created Collection: {row['Page Name']}")
    except Exception as e:
        print(f"❌ Failed to create collection {row['Page Name']}: {e}")

# Step 4: Assign Products to Collections
print("\n🔗 Assigning Products to Collections...")
for _, row in page_sku_df.iterrows():
    sku = row['SKU']
    page_name = row['Page Name']
    product_id = find_product_id_by_sku(sku)
    collection_id = find_collection_id_by_title(page_name)

    if product_id and collection_id:
        try:
            add_product_to_collection(product_id, collection_id)
            print(f"✅ Assigned {sku} to {page_name}")
        except Exception as e:
            print(f"❌ Failed to assign {sku} to {page_name}: {e}")
    else:
        print(f"⚠️ Could not find product or collection for SKU {sku}")

# Step 5: Upload Local Product Images
print("\n🖼️ Uploading Product Images...")
for _, row in images_df.iterrows():
    sku = row['SKU']
    product_id = find_product_id_by_sku(sku)
    if product_id:
        position = 1
        for col in row.index:
            if col != 'SKU' and pd.notna(row[col]):
                img_file = row[col]
                img_path = image_path(img_file)
                if os.path.exists(img_path):
                    upload_local_image_to_product(product_id, img_path, position)
                    print(f"📸 Uploaded {img_file} for {sku} at position {position}")
                    position += 1
                else:
                    print(f"⚠️ Image file not found: {img_path}")
    else:
        print(f"⚠️ Product not found for SKU {sku}")

# Step 6: Create Pages
print("\n📄 Creating Pages...")
for _, row in pages_df.iterrows():
    try:
        create_page(row)
        print(f"✅ Created Page: {row['Title']}")
    except Exception as e:
        print(f"❌ Failed to create page {row['Title']}: {e}")

# Step 7: Update Navigation Menus
print("\n🧭 Updating Navigation Menus...")
skipped_links = []
for _, row in nav_links_df.iterrows():
    menu_name = row['Menu Name']
    link_title = row['Link Title']
    link_type = row['Link Type']
    target_title = row['Target Title']

    menu_id = find_navigation_menu_id_by_title(menu_name)
    if menu_id:
        destination_id = None
        if link_type == "PAGE":
            destination_id = find_page_id_by_title(target_title)
        elif link_type == "COLLECTION":
            destination_id = find_collection_id_by_title(target_title)
        elif link_type == "PRODUCT":
            destination_id = find_product_id_by_title(target_title)

        if destination_id:
            try:
                add_link_to_navigation_menu(menu_id, link_title, link_type, destination_id)
                print(f"✅ Linked '{link_title}' to {menu_name}")
            except Exception as e:
                print(f"❌ Failed to link '{link_title}' to {menu_name}: {e}")
        else:
            print(f"⚠️ Could not find {link_type} '{target_title}'")
            skipped_links.append((menu_name, link_title, target_title))
    else:
        print(f"⚠️ Menu '{menu_name}' not found")
        skipped_links.append((menu_name, link_title, target_title))

if skipped_links:
    print("\n🚫 Skipped Navigation Links:")
    for menu, title, target in skipped_links:
        print(f" - Menu: {menu}, Link: {title}, Target: {target}")

# Step 8: Upload Theme Template
print("\n🎨 Uploading Theme Files...")
theme_file = theme_file_path('page.festival.liquid')
if os.path.exists(theme_file):
    try:
        with open(theme_file, 'r') as f:
            content = f.read()
        upload_theme_asset(THEME_ID, 'templates/page.festival.liquid', content)
        print("✅ Uploaded page.festival.liquid!")
    except Exception as e:
        print(f"❌ Theme file upload failed: {e}")
else:
    print(f"⚠️ Theme file not found: {theme_file}")

# Step 9: Create Festival Landing Page
print("\n🏕️ Creating Festival Landing Page...")
page_payload = {
    "page": {
        "title": "Festival Landing",
        "handle": "festival-landing",
        "body_html": "<h1>Festival Outfits Are Here!</h1><p>Shop our latest festival fashion collection and stand out!</p>",
        "template_suffix": "festival"
    }
}
response = requests.post(f"{SHOPIFY_STORE_URL}/admin/api/{SHOPIFY_API_VERSION}/pages.json",
                         headers=HEADERS, json=page_payload)
if response.status_code == 201:
    page_data = response.json().get('page', {})
    print(f"✅ Festival Landing Page created at: /pages/{page_data.get('handle')}")
else:
    print(f"❌ Festival Page creation failed: {response.status_code}")
    print(response.json())

# Step 10: Upload Images With ALT Text
print("\n🖼️ Uploading Images with Structured ALT Text...")
for _, row in images_alt_df.iterrows():
    sku = row['SKU']
    base_alt = row['Base ALT Text']
    product_id = find_product_id_by_sku(sku)

    if product_id:
        for i in range(1, 4):
            img_col = f"Image {i} Filename"
            if pd.notna(row.get(img_col)):
                img_file = row[img_col]
                img_path = image_path(img_file)
                if os.path.exists(img_path):
                    upload_local_image_to_product_with_alt(product_id, img_path, i, base_alt)
                    print(f"✅ Uploaded {img_file} for {sku} with ALT text")
                else:
                    print(f"⚠️ Image file not found: {img_path}")
    else:
        print(f"⚠️ Product not found for SKU {sku}")

# Step 11: Inject Aesthetic Enhancements
print("\n✨ Injecting Aesthetic Enhancements...")
aesthetic_assets = [
    "scrolling-banner.css",
    "loader.css",
    "aos.css",
    "aos.js"
]

# Step 12: Upload Scrolling Banner Section
print("\n🧩 Step 12: Uploading Scrolling Banner Section...")

section_file = os.path.join(BASE_DIR, FOLDER, "theme_files", "sections", "scrolling-banner.liquid")

if os.path.exists(section_file):
    try:
        with open(section_file, "r", encoding="utf-8") as f:
            section_content = f.read()
        upload_theme_asset(THEME_ID, "sections/scrolling-banner.liquid", section_content)
        print("✅ scrolling-banner.liquid uploaded successfully")
    except Exception as e:
        print(f"❌ Failed to upload scrolling banner section: {e}")
else:
    print(f"⚠️ Section file not found: {section_file}")

# Step 13: Upload Hover Image Snippets and Assets
print("\n🖼️ Step 13: Uploading Hover Image Snippets and Assets...")

csv_path = 'csv/sku_image.csv'
image_folder = 'images'

try:
    upload_hover_snippets_from_csv(
        session=session,
        THEME_ID=THEME_ID,
        csv_path=csv_path,
        image_folder=image_folder
    )
    print("✅ Hover image snippets uploaded successfully")
except Exception as e:
    print(f"❌ Failed to upload hover snippets: {e}")

# Step 14: Upload Aesthetic Assets (CSS & JS)
print("\n🎨 Step 14: Uploading Aesthetic Assets...")

aesthetic_assets = [
    "scrolling-banner.css",
    "loader.css",
    "aos.css",
    "aos.js"
]

for asset in aesthetic_assets:
    try:
        uploaded = upload_asset(asset)
        if uploaded:
            print(f"✅ Uploaded asset: {asset}")
        else:
            print(f"⚠️ Failed to upload: {asset}")
    except Exception as e:
        print(f"❌ Error uploading {asset}: {e}")

# Step 15: Inject Asset References
try:
    inject_assets_into_theme(aesthetic_assets)
    print("✅ Asset references injected successfully")
except Exception as e:
    print(f"❌ Failed to inject asset references: {e}")

# Optional: Inject Splash Screen
try:
    inject_splash_screen()
    print("✅ Splash screen injected successfully")
except Exception as e:
    print(f"❌ Failed to inject splash screen: {e}")

# Step 16: Inject Multiple Hover Snippets into Theme File
print("\n🧩 Step 16: Injecting Multiple Hover Snippets into Theme File...")

import csv

csv_path = os.path.join(FOLDER, 'csv', 'sku_images.csv')  # uses FOLDER from .env
theme_file_path = "sections/main-product.liquid"  # Update if you want a different target

# Count number of hover snippets based on CSV rows
try:
    with open(csv_path, 'r', encoding='utf-8') as file:
        num_snippets = sum(1 for _ in csv.DictReader(file))
    print(f"🔢 Found {num_snippets} hover snippet(s) in {csv_path}")
except Exception as e:
    print(f"❌ Failed to read CSV for snippet count: {e}")
    num_snippets = 0

# Inject all render tags into the theme file
if num_snippets > 0:
    try:
        insert_multiple_snippets_into_theme_file(
            session=session,
            theme_id=THEME_ID,
            theme_file_path=theme_file_path,
            num_snippets=num_snippets,
            insert_before=None  # Optional: anchor string if you want to inject before a known block
        )
    except Exception as e:
        print(f"❌ Failed to inject snippet tags: {e}")
else:
    print("⚠️ Skipping snippet injection due to missing or empty CSV.")
