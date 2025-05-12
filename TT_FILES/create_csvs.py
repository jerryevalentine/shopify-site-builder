import pandas as pd
import os

# Ensure the output folder exists
output_folder = os.path.join(os.getcwd(), "csv")
os.makedirs(output_folder, exist_ok=True)

# 1. page_url.csv
page_url_df = pd.DataFrame({
    "Page Name": ["Festival Wear"],
    "URL Slug": ["festival-wear"]
})

# 2. sku_images_alt.csv
sku_images_alt_df = pd.DataFrame({
    "SKU": ["JV-2001"],
    "Base ALT Text": ["J Valentine Gold Sequin Dress"],
    "Image 1 Filename": ["JV-2001-front.jpg"],
    "Image 2 Filename": ["JV-2001-front.jpg"],
    "Image 3 Filename": [""]
})

# 3. sku_master.csv
sku_master_df = pd.DataFrame({
    "SKU": ["JV-2001"],
    "Product Name": ["Gold Sequin Dress"],
    "Brand": ["J Valentine"],
    "Category": ["Festival Wear"],
    "Subcategory": ["Dress"],
    "Description": ["Sparkling gold sequin dress perfect for festivals."],
    "Price": [79.99],
    "Image Filename": ["JV-2001-front.jpg"]
})

# 4. navigation_links.csv
navigation_links_df = pd.DataFrame({
    "Menu Name": ["Main Menu", "Main Menu", "Main Menu"],
    "Link Title": ["Home", "Festival Wear", "Contact"],
    "Link Type": ["URL", "COLLECTION", "PAGE"],
    "Target Title": ["/", "Festival Wear", "Contact"]
})

# 5. page_sku.csv
page_sku_df = pd.DataFrame({
    "Page Name": ["Festival Wear"],
    "SKU": ["JV-2001"]
})

# 6. pages.csv
pages_df = pd.DataFrame({
    "Title": ["About Us", "Contact"],
    "Body": [
        "<h1>About Us</h1><p>We are passionate about fashion and festivals.</p>",
        "<h1>Contact Us</h1><p>Email: support@example.com | Call: 1-800-555-1234</p>"
    ]
})

# 7. sku_images.csv
sku_images_df = pd.DataFrame({
    "SKU": ["JV-2001"],
    "Image Filename 1": ["JV-2001-front.jpg"],
    "Image Filename 2": ["JV-2001-front.jpg"]
})

# Save all CSVs
csv_files = {
    "page_url.csv": page_url_df,
    "sku_images_alt.csv": sku_images_alt_df,
    "sku_master.csv": sku_master_df,
    "navigation_links.csv": navigation_links_df,
    "page_sku.csv": page_sku_df,
    "pages.csv": pages_df,
    "sku_images.csv": sku_images_df
}

for filename, df in csv_files.items():
    full_path = os.path.join(output_folder, filename)
    df.to_csv(full_path, index=False)
    print(f"✅ Saved: {filename}")
