# C:\Users\jerry\Shopify_API\Shopify_api_aesthetics.py
# Next item: extend the function to support uploading fonts, JavaScript, or SVG icons too?

# Step 1: Import libraries
import os
import base64
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Step 2: Load environment variables from .env in the current directory
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)

ASSET_FOLDER = os.getenv("ASSET_FOLDER", "images")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
THEME_ID = os.getenv("THEME_ID")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2023-10")

# Step 3: Set request headers
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# Step 4: Upload asset
def upload_asset(filename, subfolder="assets"):
    allowed_extensions = (
        ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg",
        ".ttf", ".woff", ".woff2", ".otf",
        ".js", ".css"
    )
    if not filename.lower().endswith(allowed_extensions):
        print(f"❌ File type not supported: {filename}")
        return False

    path = os.path.join(ASSET_FOLDER, filename)
    print(f"📂 Looking for file at: {path}")
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return False

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    asset_key = f"{subfolder}/{filename}"
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    payload = {
        "asset": {
            "key": asset_key,
            "attachment": encoded
        }
    }

    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"✅ Uploaded {filename} to {subfolder}/")
        return True
    else:
        print(f"❌ Failed to upload {filename}: {response.status_code}")
        print(response.text)
        return False

# Step 5: Get theme.liquid
def get_theme_liquid():
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    response = requests.get(url, headers=HEADERS, params={"asset[key]": "layout/theme.liquid"})
    if response.status_code == 200:
        return response.json().get("asset", {}).get("value", "")
    else:
        print(f"❌ Failed to fetch theme.liquid: {response.status_code}")
        return None

# Step 6: Inject background image and refresh script
def inject_background_and_prompt(content, version="v2"):
    style = f"""<style>
  html, body {{
    height: 100%;
    margin: 0;
    padding: 0;
    background-image: url('{{{{ "background.jpg" | asset_url }}}}?{version}');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center center;
  }}
</style>"""

    script = f"""<script>
  const v = '{version}';
  if (localStorage.getItem('store_version') !== v) {{
    if (confirm("We've updated our store design. Refresh now?")) {{
      localStorage.setItem('store_version', v);
      location.reload(true);
    }}
  }}
</script>"""

    lines = content.splitlines()
    lines = [line for line in lines if "background.jpg" not in line]
    content = "\n".join(lines)

    if "</head>" in content:
        content = content.replace("</head>", f"{style}\n</head>")
    if "</body>" in content:
        content = content.replace("</body>", f"{script}\n</body>")

    return content

# Step 7: Inject favicon
def inject_favicon_into_theme(content, filename="favicon.ico"):
    favicon_link = f'<link rel="icon" href="{{{{ "{filename}" | asset_url }}}}" type="image/x-icon">'
    if favicon_link not in content:
        content = content.replace("</head>", f"{favicon_link}\n</head>")
        print("✅ Favicon link injected.")
    else:
        print("ℹ️ Favicon already present.")
    return content

# Step 8: Inject Google Fonts
def inject_google_fonts(content, font_url="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"):
    font_tag = f'<link href="{font_url}" rel="stylesheet">'
    if font_tag not in content:
        content = content.replace("</head>", f"{font_tag}\n</head>")
        print("✅ Google Font injected.")
    else:
        print("ℹ️ Google Font already present.")
    return content

# Step 9: Inject button styles
def inject_button_styles(content):
    button_css = """<style>
  .btn {
    background-color: #111111;
    color: #ffffff;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-weight: bold;
    text-decoration: none;
    transition: background-color 0.3s ease;
  }
  .btn:hover {
    background-color: #444444;
  }
</style>"""
    if ".btn" not in content:
        content = content.replace("</head>", f"{button_css}\n</head>")
        print("✅ Button style injected.")
    else:
        print("ℹ️ Button styles already present.")
    return content

# Step 10: Push updated theme.liquid
def update_theme_liquid(new_content):
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    payload = {
        "asset": {
            "key": "layout/theme.liquid",
            "value": new_content
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print("✅ theme.liquid updated.")
    else:
        print(f"❌ theme.liquid update failed: {response.status_code}")
        print(response.text)

# Step 11: Create promo section
def create_seasonal_sale_section(image_filename="summer_sale_banner.jpg"):
    section_key = "sections/seasonal-sale.liquid"
    promo_html = f"""
<div class=\"seasonal-sale-block\" style=\"position: relative; text-align: center;\">
  <img src=\"{{{{ '{image_filename}' | asset_url }}}}\" alt=\"Summer sale promotion banner\" style=\"width: 100%; height: auto;\">
  <div style=\"position: absolute; top: 30%; left: 50%; transform: translate(-50%, -30%); background: rgba(0, 0, 0, 0.5); padding: 2rem; border-radius: 12px;\">
    <h2 style=\"color: white; font-size: 2.5rem; margin-bottom: 0.5rem;\">Summer Sale is On!</h2>
    <p style=\"color: white; font-size: 1.2rem; margin-bottom: 1rem;\">Up to 50% off selected items</p>
    <a href=\"/collections/summer-sale\" class=\"btn\">Shop the Sale</a>
  </div>
</div>
    """
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    payload = {
        "asset": {
            "key": section_key,
            "value": promo_html
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print("✅ Seasonal Sale section created.")
    else:
        print(f"❌ Failed to create section: {response.status_code}")
        print(response.text)

# Step 12: Inject promo section into homepage
def inject_seasonal_sale_into_index():
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    response = requests.get(url, headers=HEADERS, params={"asset[key]": "templates/index.json"})
    if response.status_code != 200:
        print(f"❌ Failed to fetch index.json: {response.status_code}")
        print(response.text)
        return

    index_data = response.json().get("asset", {}).get("value", "")
    if not index_data:
        print("❌ index.json is empty.")
        return

    index_json = json.loads(index_data)
    section_id = "seasonal-sale"
    if section_id not in index_json.get("sections", {}):
        index_json["sections"][section_id] = { "type": "seasonal-sale" }
        index_json["order"].append(section_id)
    else:
        print("ℹ️ seasonal-sale already exists.")

    payload = {
        "asset": {
            "key": "templates/index.json",
            "value": json.dumps(index_json, indent=2)
        }
    }
    put_response = requests.put(url, headers=HEADERS, json=payload)
    if put_response.status_code == 200:
        print("✅ seasonal-sale added to homepage.")
    else:
        print(f"❌ Failed to update index.json: {put_response.status_code}")
        print(put_response.text)

# Step 13: Inject scrolling text banner
def inject_scrolling_text():
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    response = requests.get(url, headers=HEADERS, params={"asset[key]": "templates/index.liquid"})
    if response.status_code != 200:
        print("❌ Failed to fetch index.liquid")
        return

    content = response.json().get("asset", {}).get("value", "")
    banner_html = '''
<!-- Scrolling Text Banner Start -->
<div class="scrolling-text-banner">
  <div class="scrolling-text-inner">
    {% for i in (1..30) %}
    <span>WORLDWIDE WHOLESALE & DROP SHIPPING</span>
    {% endfor %}
  </div>
</div>
<!-- Scrolling Text Banner End -->
'''
    if 'scrolling-text-banner' not in content:
        content = content.replace("</body>", f"{banner_html}\n</body>")
        payload = {
            "asset": {
                "key": "templates/index.liquid",
                "value": content
            }
        }
        put_response = requests.put(url, headers=HEADERS, json=payload)
        if put_response.status_code == 200:
            print("✅ Scrolling banner injected.")
        else:
            print("❌ Failed to inject scrolling banner")
    else:
        print("ℹ️ Scrolling banner already exists.")

# Step 14: Inject splash screen loader
def inject_loader():
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    response = requests.get(url, headers=HEADERS, params={"asset[key]": "layout/theme.liquid"})
    if response.status_code != 200:
        print("❌ Failed to fetch theme.liquid")
        return

    content = response.json().get("asset", {}).get("value", "")
    loader_html = '''
<!-- Splash Screen Loader Start -->
<div class="splash-screen"><span class="loader-text">Loading</span></div>
<!-- Splash Screen Loader End -->
'''
    if 'splash-screen' not in content:
        content = content.replace("<body", "<body class=\"transition-body\"")
        content = content.replace("</body>", f"{loader_html}\n</body>")
        update_theme_liquid(content)
        print("✅ Splash screen loader injected.")
    else:
        print("ℹ️ Splash screen already exists.")

# Step 15: Upload animation/styling assets
def upload_animation_assets():
    files = ["scrolling-banner.css", "loader.css", "aos.css", "aos.js"]
    for file in files:
        upload_asset(file)

    theme = get_theme_liquid()
    if theme:
        injection_block = "\n".join([
            f'<link href="{{{{ "/assets/{f}" | asset_url }}}}" rel="stylesheet">' if f.endswith(".css")
            else f'<script src="{{{{ "/assets/{f}" | asset_url }}}}" defer></script>' for f in files
        ])
        if injection_block not in theme:
            updated = theme.replace("</head>", f"{injection_block}\n</head>")
            update_theme_liquid(updated)
            print("✅ Animation assets injected.")
        else:
            print("ℹ️ Animation assets already present.")

# Step 16: Run full process
if __name__ == "__main__":
    upload_asset("background.jpg")
    upload_asset("favicon.ico")
    upload_asset("summer_sale_banner.jpg")

    current = get_theme_liquid()
    if current:
        updated = inject_background_and_prompt(current, version="v2")
        updated = inject_favicon_into_theme(updated, "favicon.ico")
        updated = inject_google_fonts(updated)
        updated = inject_button_styles(updated)
        update_theme_liquid(updated)

    create_seasonal_sale_section("summer_sale_banner.jpg")
    inject_seasonal_sale_into_index()
    inject_scrolling_text()
    inject_loader()
    upload_animation_assets()
