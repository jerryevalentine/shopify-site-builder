import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
THEME_ID = os.getenv('THEME_ID')
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2023-10")

# Set headers for authentication
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# ------------------ AESTHETIC ENHANCEMENTS ------------------

def upload_asset(filename):
    """
    Upload a static file (CSS, JS, image, font, etc.) to Shopify's theme assets.

    Args:
        filename (str): The filename to upload (must exist inside ASSET_FOLDER).

    Returns:
        bool: True if upload successful, False otherwise.
    """
    asset_folder = os.getenv("ASSET_FOLDER", "assets")
    full_path = os.path.join(asset_folder, filename)

    if not os.path.isfile(full_path):
        print(f"❌ File not found: {full_path}")
        return False

    try:
        with open(full_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to read file: {filename} ({e})")
        return False

    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    payload = {
        "asset": {
            "key": f"assets/{filename}",
            "attachment": encoded
        }
    }

    response = requests.put(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print(f"✅ Uploaded asset: {filename}")
        return True
    else:
        print(f"❌ Upload failed: {filename} ({response.status_code})")
        try:
            print(response.json())
        except:
            print(response.text)
        return False


def inject_assets_into_theme(asset_filenames):
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    get_resp = requests.get(url, headers=HEADERS, params={"asset[key]": "layout/theme.liquid"})
    if get_resp.status_code != 200:
        print("❌ Failed to get theme.liquid")
        return False
    content = get_resp.json()["asset"]["value"]
    injection_block = "\n".join([
        f'<link href="{{{{ \"/assets/{f}\" | asset_url }}}}" rel="stylesheet">' if f.endswith(".css")
        else f'<script src="{{{{ \"/assets/{f}\" | asset_url }}}}" defer></script>' for f in asset_filenames
    ])
    if injection_block not in content:
        content = content.replace("</head>", f"{injection_block}\n</head>")
        payload = {"asset": {"key": "layout/theme.liquid", "value": content}}
        put_resp = requests.put(url, headers=HEADERS, json=payload)
        print("✅ Injected assets into theme.liquid")
        return put_resp.status_code == 200
    print("ℹ️ Assets already present in theme.liquid")
    return True

def inject_scrolling_banner():
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    get_resp = requests.get(url, headers=HEADERS, params={"asset[key]": "templates/index.liquid"})
    if get_resp.status_code != 200:
        print("❌ Failed to fetch index.liquid")
        return False
    content = get_resp.json()["asset"]["value"]
    banner_html = '''
<!-- Scrolling Text Banner Start -->
<div class="scrolling-text-banner">
  <div class="scrolling-text-inner">
    {% for i in (1..30) %}<span>WORLDWIDE WHOLESALE & DROP SHIPPING</span>{% endfor %}
  </div>
</div>
<!-- Scrolling Text Banner End -->
'''
    if "scrolling-text-banner" not in content:
        content = content.replace("</body>", f"{banner_html}\n</body>")
        payload = {"asset": {"key": "templates/index.liquid", "value": content}}
        put_resp = requests.put(url, headers=HEADERS, json=payload)
        print("✅ Injected scrolling banner")
        return put_resp.status_code == 200
    print("ℹ️ Scrolling banner already exists")
    return True

def inject_splash_screen():
    url = f"{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"
    get_resp = requests.get(url, headers=HEADERS, params={"asset[key]": "layout/theme.liquid"})
    if get_resp.status_code != 200:
        print("❌ Failed to fetch theme.liquid")
        return False
    content = get_resp.json()["asset"]["value"]
    splash_html = '''
<!-- Splash Screen Loader Start -->
<div class="splash-screen"><span class="loader-text">Loading</span></div>
<!-- Splash Screen Loader End -->
'''
    if "splash-screen" not in content:
        content = content.replace("<body", "<body class=\"transition-body\"")
        content = content.replace("</body>", f"{splash_html}\n</body>")
        payload = {"asset": {"key": "layout/theme.liquid", "value": content}}
        put_resp = requests.put(url, headers=HEADERS, json=payload)
        print("✅ Injected splash screen")
        return put_resp.status_code == 200
    print("ℹ️ Splash screen already exists")
    return True

# ------------------ PRODUCT & COLLECTION ------------------

def create_product(product_data):
    """Create a new product if SKU doesn't exist."""
    existing_product_id = find_product_id_by_sku(product_data["SKU"])
    if existing_product_id:
        print(f"Product with SKU {product_data['SKU']} exists. Skipping.")
        return {"status": "exists", "product_id": existing_product_id}

    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products.json"
    payload = {
        "product": {
            "title": product_data["Product Name"],
            "body_html": product_data.get("Description", ""),
            "vendor": product_data.get("Brand", ""),
            "product_type": product_data.get("Category", ""),
            "variants": [
                {
                    "sku": product_data["SKU"],
                    "price": str(product_data["Price"])
                }
            ]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

def find_product_id_by_sku(sku):
    """Find product ID by SKU."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products.json?fields=id,variants"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        for product in response.json().get('products', []):
            for variant in product.get('variants', []):
                if variant['sku'] == sku:
                    return product['id']
    return None

def create_collection(collection_data):
    """Create a custom collection."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/custom_collections.json"
    payload = {
        "custom_collection": {
            "title": collection_data["Page Name"],
            "handle": collection_data["URL Slug"]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

def find_collection_id_by_title(title):
    """Find collection ID by title."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/custom_collections.json?fields=id,title"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        for collection in response.json().get('custom_collections', []):
            if collection['title'].lower() == title.lower():
                return collection['id']
    return None

def add_product_to_collection(product_id, collection_id):
    """Add product to collection."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/collects.json"
    payload = {
        "collect": {
            "product_id": product_id,
            "collection_id": collection_id
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

# ------------------ IMAGE MANAGEMENT ------------------

def upload_local_image_to_product(product_id, image_path, position):
    """Upload a local image with positional ALT text."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}/images.json"

    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
        return

    alt_text = {
        1: "Front View",
        2: "Back View",
        3: "Side View",
        4: "Detail View"
    }.get(position, f"View {position}")

    payload = {
        "image": {
            "attachment": encoded,
            "position": position,
            "alt": alt_text
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    print(f"Uploaded {image_path} (Position {position}, ALT: {alt_text})")
    return response.json()

def upload_local_image_to_product_with_alt(product_id, image_path, position, base_alt_text):
    """Upload image with structured ALT text."""
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
        return

    view_name = {
        1: "Front View",
        2: "Back View",
        3: "Side View",
        4: "Detail View"
    }.get(position, f"View {position}")

    structured_alt = f"{base_alt_text} - {view_name}"

    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}/images.json"
    payload = {
        "image": {
            "attachment": encoded,
            "position": position,
            "alt": structured_alt
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    print(f"Uploaded {image_path} with ALT '{structured_alt}'")
    return response.json()

# ------------------ PAGE MANAGEMENT ------------------

def create_page(page_data):
    """Create a Shopify page."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/pages.json"
    payload = {
        "page": {
            "title": page_data["Title"],
            "body_html": page_data["Body"]
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

# ------------------ THEME FILES ------------------

def upload_theme_asset(theme_id, asset_key, asset_value):
    """Upload a theme file to Shopify."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/themes/{theme_id}/assets.json"
    payload = {
        "asset": {
            "key": asset_key,
            "value": asset_value
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    print(f"Uploaded asset: {asset_key} (Status: {response.status_code})")
    return response.json()

# ------------------ GRAPHQL HELPERS ------------------

def graphql_query(query, variables=None):
    """Send a GraphQL query."""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/graphql.json"
    payload = {"query": query, "variables": variables or {}}

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ GraphQL error: {e}")
        return {"errors": [{"message": str(e)}]}

# ------------------ MENU MANAGEMENT (GRAPHQL) ------------------

def find_navigation_menu_id_by_title(title):
    """Find navigation menu ID by title."""
    query = """
    {
      navigationMenus(first: 50) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
    """
    result = graphql_query(query)
    if "errors" in result:
        print(f"❌ GraphQL error: {result['errors']}")
        return None

    for edge in result["data"]["navigationMenus"]["edges"]:
        if edge["node"]["title"].lower() == title.lower():
            return edge["node"]["id"]
    return None

def add_link_to_navigation_menu(menu_id, link_title, link_type, destination_id=None):
    """Add a link to a menu."""
    query = """
    mutation menuItemCreate($menuItem: MenuItemInput!) {
      menuItemCreate(menuItem: $menuItem) {
        menuItem { id }
        userErrors { field message }
      }
    }
    """
    menu_item = {
        "title": link_title,
        "menuId": menu_id
    }

    if link_type == "URL":
        menu_item["url"] = destination_id
    else:
        menu_item["resourceId"] = destination_id

    variables = {"menuItem": menu_item}
    result = graphql_query(query, variables)

    if "errors" in result:
        print(f"❌ Error adding link: {result['errors']}")
    else:
        print(f"✅ Added link: {link_title}")

    return result

def find_product_id_by_title(title):
    """Find product ID by title using GraphQL."""
    query = """
    {
      products(first: 50) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
    """
    result = graphql_query(query)
    if "errors" in result:
        print("❌ Product query failed:", result["errors"])
        return None

    for edge in result["data"]["products"]["edges"]:
        if edge["node"]["title"].lower() == title.lower():
            return edge["node"]["id"]
    return None

def find_page_id_by_title(title):
    """Find page ID by title using GraphQL."""
    query = """
    {
      pages(first: 50) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
    """
    result = graphql_query(query)
    if "errors" in result:
        print("❌ Page query failed:", result["errors"])
        return None

    for edge in result["data"]["pages"]["edges"]:
        if edge["node"]["title"].lower() == title.lower():
            return edge["node"]["id"]
    return None

def create_navigation_menu(title):
    """Create a new navigation menu (GraphQL)."""
    query = """
    mutation menuCreate($menu: MenuInput!) {
      menuCreate(menu: $menu) {
        menu {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "menu": {
            "title": title
        }
    }
    return graphql_query(query, variables)

