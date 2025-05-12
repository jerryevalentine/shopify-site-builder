import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
BASE_FOLDER = os.getenv("FOLDER")
CSV_FOLDER = os.path.join(BASE_FOLDER, "csv")

REQUIRED_FILES = {
    "sku_master.csv": ["SKU", "Product Name", "Brand", "Category", "Subcategory", "Description", "Price", "Image Filename"],
    "sku_images.csv": ["SKU", "Image Filename 1", "Image Filename 2"],
    "sku_images_alt.csv": ["SKU", "Base ALT Text", "Image 1 Filename", "Image 2 Filename", "Image 3 Filename"],
    "pages.csv": ["Title", "Body"],
    "page_url.csv": ["Page Name", "URL Slug"],
    "page_sku.csv": ["Page Name", "SKU"],
    "navigation_links.csv": ["Menu Name", "Link Title", "Link Type", "Target Title"]
}

def validate_csv_headers(folder, filename, required_columns):
    path = os.path.join(folder, filename)
    if not os.path.isfile(path):
        return [f"❌ Missing required file: {filename}"]
    
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return [f"❌ Error reading {filename}: {str(e)}"]

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        return [f"❌ {filename} is missing columns: {missing_columns}"]
    
    return []

def validate_relationships(folder):
    errors = []
    try:
        sku_master = pd.read_csv(os.path.join(folder, "sku_master.csv"))
        sku_images = pd.read_csv(os.path.join(folder, "sku_images.csv"))
        sku_images_alt = pd.read_csv(os.path.join(folder, "sku_images_alt.csv"))
        pages = pd.read_csv(os.path.join(folder, "pages.csv"))
        page_url = pd.read_csv(os.path.join(folder, "page_url.csv"))
        page_sku = pd.read_csv(os.path.join(folder, "page_sku.csv"))
        navigation = pd.read_csv(os.path.join(folder, "navigation_links.csv"))
    except Exception as e:
        return [f"❌ Error loading CSVs: {str(e)}"]

    for df, name in [(sku_images, "sku_images.csv"), (sku_images_alt, "sku_images_alt.csv"), (page_sku, "page_sku.csv")]:
        missing = set(df["SKU"]) - set(sku_master["SKU"])
        if missing:
            errors.append(f"❌ {name} contains unknown SKUs: {missing}")

    for df, col, name in [(page_url, "Page Name", "page_url.csv"), (page_sku, "Page Name", "page_sku.csv")]:
        missing = set(df[col]) - set(pages["Title"])
        if missing:
            errors.append(f"❌ {name} has unknown Page Names: {missing}")

    valid_targets = set(pages["Title"]).union(set(sku_master["Product Name"])).union(set(sku_master["Category"]))
    bad_targets = set(navigation["Target Title"]) - valid_targets
    if bad_targets:
        errors.append(f"❌ navigation_links.csv has invalid Target Titles: {bad_targets}")

    return errors

def validate_all_csvs(folder):
    all_errors = []

    print(f"🔍 Validating CSVs in: {folder}")
    for filename, required_columns in REQUIRED_FILES.items():
        errors = validate_csv_headers(folder, filename, required_columns)
        all_errors.extend(errors)

    rel_errors = validate_relationships(folder)
    all_errors.extend(rel_errors)

    if not all_errors:
        print("✅ All CSVs passed validation.")
    else:
        print("\n".join(all_errors))

if __name__ == "__main__":
    validate_all_csvs(CSV_FOLDER)