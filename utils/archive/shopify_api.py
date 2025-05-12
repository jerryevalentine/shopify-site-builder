import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Set headers for authentication
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

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
