# C:\Users\jerry\ecommerce\shopify_deploy
# deploy.py

import os
import pandas as pd
import requests
from dotenv import load_dotenv
from utils.shopify_api import (
    create_product, create_collection, find_product_id_by_sku, find_collection_id_by_title,
    add_product_to_collection, upload_image_to_product, upload_local_image_to_product,
    upload_local_image_to_product_with_alt, create_page,
    find_navigation_menu_id_by_title, add_link_to_navigation_menu, upload_theme_asset
)



# Step 0: Load environment variables
load_dotenv()

SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

theme_id = 138732503085  # <-- Your real theme ID

# Step 1: Load your CSV files
print("\nLoading CSV files...")
products_df = pd.read_csv('csv/sku_master.csv')
collections_df = pd.read_csv('csv/page_url.csv')
page_sku_df = pd.read_csv('csv/page_sku.csv')
images_df = pd.read_csv('csv/sku_images.csv')
pages_df = pd.read_csv('csv/pages.csv')
nav_links_df = pd.read_csv('csv/navigation_links.csv')

# Step 2: Upload Products
print("\nUploading Products...")
for idx, row in products_df.iterrows():
    result = create_product(row)
    print(f"Uploaded Product: {row['Product Name']}")

# Step 3: Upload Collections
print("\nCreating Collections...")
for idx, row in collections_df.iterrows():
    result = create_collection(row)
    print(f"Created Collection: {row['Page Name']}")

# Step 4: Assign Products to Collections
print("\nAssigning Products to Collections...")
for idx, row in page_sku_df.iterrows():
    sku = row['SKU']
    page_name = row['Page Name']
    product_id = find_product_id_by_sku(sku)
    collection_id = find_collection_id_by_title(page_name)

    if product_id and collection_id:
        add_product_to_collection(product_id, collection_id)
        print(f"Assigned {sku} to {page_name}")
    else:
        print(f"Could not find product or collection for SKU {sku}")

# Step 5: Upload Local Product Images
print("\nUploading Product Images...")
for idx, row in images_df.iterrows():
    sku = row['SKU']
    product_id = find_product_id_by_sku(sku)
    if product_id:
        position = 1
        for col in row.index:
            if col != 'SKU' and pd.notna(row[col]):
                image_filename = row[col]
                image_path = os.path.join('images', image_filename)
                upload_local_image_to_product(product_id, image_path, position)
                print(f"Uploaded {image_filename} for {sku} at position {position}")
                position += 1
    else:
        print(f"Could not find product for SKU {sku}")

# Step 6: Create Pages
print("\nCreating Pages...")
for idx, row in pages_df.iterrows():
    result = create_page(row)
    print(f"Created Page: {row['Title']}")


# Step 8: Upload Theme Files (Custom Templates, CSS, JS)
print("\nUploading Theme Files...")
try:
    with open('theme_files/page.festival.liquid', 'r') as f:
        festival_page_content = f.read()
    upload_theme_asset(theme_id, 'templates/page.festival.liquid', festival_page_content)
    print("✅ Uploaded page.festival.liquid successfully!")
except Exception as e:
    print(f"❌ Failed to upload theme assets: {e}")

# Step 9: Create Festival Landing Page (Auto-Assigned Template)
print("\nCreating Festival Landing Page...")

festival_page_payload = {
    "page": {
        "title": "Festival Landing",
        "handle": "festival-landing",
        "body_html": "<h1>Festival Outfits Are Here!</h1><p>Shop our latest festival fashion collection and stand out!</p>",
        "template_suffix": "festival"
    }
}

create_page_url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/pages.json"
response = requests.post(create_page_url, headers={
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}, json=festival_page_payload)

if response.status_code == 201:
    page_data = response.json().get('page', {})
    print(f"✅ Festival Landing Page created at: /pages/{page_data.get('handle')}")
else:
    print(f"❌ Failed to create Festival Landing Page: {response.status_code}")
    print(response.json())

# Step 5: Upload Local Product Images WITH Auto-Structured ALT Text
print("\nUploading Product Images with Structured ALT Text...")
images_alt_df = pd.read_csv('csv/sku_images_alt.csv')

for idx, row in images_alt_df.iterrows():
    sku = row['SKU']
    base_alt_text = row['Base ALT Text']
    product_id = find_product_id_by_sku(sku)

    if product_id:
        for i in range(1, 4):  # Assuming up to 3 images
            image_filename_col = f"Image {i} Filename"
            
            if pd.notna(row.get(image_filename_col)):
                image_filename = row[image_filename_col]
                image_path = os.path.join('images', image_filename)

                # Upload with structured ALT text
                upload_local_image_to_product_with_alt(product_id, image_path, i, base_alt_text)
                print(f"Uploaded {image_filename} for {sku} with structured ALT text")
    else:
        print(f"Could not find product for SKU {sku}")
